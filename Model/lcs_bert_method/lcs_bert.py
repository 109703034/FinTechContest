import os
import torch
from tqdm import tqdm
from transformers.utils import logging
from transformers import BertTokenizer, BertForMultipleChoice

def load_data_from_txt(source_path):
    """
    Loads text data from files in a directory and stores it in a dictionary.

    Args:
        source_path (str): The path to the directory containing text files.

    Returns:
        dict: A dictionary where each key is the file name (as an integer) and the value is the file content as a string.
    """
    masked_file_ls = os.listdir(source_path)  # 獲取資料夾中的檔案列表
    corpus_dict = {int(file.replace('.txt', '')): open(os.path.join(source_path, file), 'r', encoding='utf-8').read() for file in tqdm(masked_file_ls)} 
    # corpus_dict = {int(file.replace('.txt', '')): open(os.path.join(source_path, file), 'r', encoding='utf-8').read().replace("\n","") for file in tqdm(masked_file_ls)} 
    return corpus_dict

def top_n_longest_common_substrings(str1, str2, N):
    """
    Finds the top N longest common substrings between two strings.

    Args:
        str1 (str): The first string.
        str2 (str): The second string.
        N (int): The number of longest substrings to return.

    Returns:
        list: A list of the top N longest common substrings.
    """
    m, n = len(str1), len(str2)
    lcs_matrix = [[0] * (n + 1) for _ in range(m + 1)]
    substring_dict = {}

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if str1[i - 1] == str2[j - 1]:
                lcs_matrix[i][j] = lcs_matrix[i - 1][j - 1] + 1
                length = lcs_matrix[i][j]
                substring = str1[i - length:i]

                if length in substring_dict:
                    substring_dict[length].add(substring)
                else:
                    substring_dict[length] = {substring}

    top_n_substrings = []
    for length in sorted(substring_dict.keys(), reverse=True):
        for substring in substring_dict[length]:
            top_n_substrings.append(substring)
            if len(top_n_substrings) >= N:
                return top_n_substrings

    return top_n_substrings

def lcs_bert_calculation(question: str, source: list[int], corpus_dict: dict[int, str]):
    """
    Calculates the best matching document ID based on longest common substrings and BERT scoring.

    Args:
        question (str): The question text.
        source (list[int]): A list of document IDs to consider.
        corpus_dict (dict[int, str]): A dictionary with document IDs as keys and document texts as values.

    Returns:
        int: The document ID that best matches the question.
    """
    max_total_length, index_list = 0, []
    for i, doc in enumerate([corpus_dict[file] for file in source]):
        doc = doc.replace(" ", "")
        top_N = top_n_longest_common_substrings(question, doc, 10)
        # remove the substring which is less than 2 words
        top_N = [sub for sub in top_N if len(sub) > 1]
        total_length = sum([len(sub) for sub in top_N])
        if total_length > max_total_length:
            max_total_length = total_length
            index_list = [i]
        elif total_length == max_total_length:
            index_list.append(i)
    if len(index_list) == 1:
        return source[index_list[0]]

    logging.set_verbosity_error() 
    seed = 42
    torch.manual_seed(seed)
    device = torch.device("cuda")
    # ckiplab/bert-base-chinese-qa
    # uer/roberta-base-chinese-extractive-qa
    # wptoux/albert-chinese-large-qa
    # liam168/qa-roberta-base-chinese-extractive
    # IDEA-CCNL/Randeng-T5-784M-QA-Chinese
    tokenizer = BertTokenizer.from_pretrained('ckiplab/bert-base-chinese-qa')
    model = BertForMultipleChoice.from_pretrained('ckiplab/bert-base-chinese-qa').to(device)

    raw_texts = [corpus_dict[source[index]] for index in index_list]

    choices = []
    choice_index = dict()

    for i, raw_text in enumerate(raw_texts):
        raw_texts_list = raw_text.split("\n")
        for j in range(len(raw_texts_list)):
            if len(raw_texts_list[j]) > 0:
                raw_texts_list[j] = raw_texts_list[j] + "。"
                choices.append(raw_texts_list[j])
                choice_index[len(choices)-1] = source[index_list[i]]

    choices_input = [[question, choices[i]] for i in range(len(choices))]

    inputs = tokenizer(choices_input, padding=True, truncation=True, return_tensors="pt").to(device)
    with torch.no_grad():
        model.eval()
        labels = torch.tensor(0).unsqueeze(0).to(device) 
        outputs = model(**{k: v.unsqueeze(0) for k, v in inputs.items()}, labels=labels)  
    
    logits = outputs.logits  
    prediction = torch.argmax(logits, dim=1).item() 
    return choice_index[prediction]