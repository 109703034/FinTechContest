import os
import torch
from tqdm import tqdm
from transformers.utils import logging
from transformers import BertTokenizer, BertForMultipleChoice

def load_data_from_txt(source_path):
    masked_file_ls = os.listdir(source_path)  # 獲取資料夾中的檔案列表
    corpus_dict = {int(file.replace('.txt', '')): open(os.path.join(source_path, file), 'r', encoding='utf-8').read() for file in tqdm(masked_file_ls)} 
    # corpus_dict = {int(file.replace('.txt', '')): open(os.path.join(source_path, file), 'r', encoding='utf-8').read().replace("\n","") for file in tqdm(masked_file_ls)} 
    return corpus_dict

def remove_substrings(strings):
    strings.sort(key=len, reverse=True)
    result = []
    
    for string in strings:
        if not any(string in other for other in result):
            result.append(string)
    
    return result

def top_n_longest_common_substrings(str1, str2, N):
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
                top_n_substrings = remove_substrings(top_n_substrings)
                print(top_n_substrings)
                return top_n_substrings

    top_n_substrings = remove_substrings(top_n_substrings)
    print(top_n_substrings)
    return top_n_substrings

def lcs_bert_calculation(question: str, source: list[int], corpus_dict: dict[int, str]):
    max_total_length, index_list = 0, []
    for i, doc in enumerate([corpus_dict[file] for file in source]):
        doc = doc.replace(" ", "")
        top_N = top_n_longest_common_substrings(question, doc, 10)
        # remove the substring which is less than 2 words
        top_N = [sub for sub in top_N if len(sub) > 3]
        total_length = sum([len(sub) for sub in top_N])
        if total_length > max_total_length:
            max_total_length = total_length
            index_list = [i]
        elif total_length == max_total_length:
            index_list.append(i)
    if len(index_list) == 1:
        print(source)
        print(index_list)
        print(source[index_list[0]])
        return source[index_list[0]]
    print(source)
    print(index_list)
    print(source[index_list[0]])
    return source[index_list[0]]

    logging.set_verbosity_error() 
'''
def lcs_bert_calculation(question: str, source: list[int], corpus_dict: dict[int, str]):
    lists = []
    for i, doc in enumerate([corpus_dict[file] for file in source]):
        doc = doc.replace(" ", "")
        top_N = top_n_longest_common_substrings(question, doc, 10)
        # remove the substring which is less than 2 words
        top_N = [sub for sub in top_N if len(sub) > 1]
        lists.append(top_N)
    print(lists)
    cur_idx = 0
    while len(lists)>1:
        print(cur_idx)
        lists = [l for l in lists if len(l)>=(cur_idx+1)]
        print(lists)
        lists = sorted(lists, key=lambda x: len(x[cur_idx]),reverse=True)
        lists = [l for l in lists if len(l[cur_idx])>=len(lists[0][cur_idx])]
        cur_idx+=1
        unq = []
        for l in lists:
            if l not in unq:
                unq.append(l)
        lists = unq
        print(lists)
    print(lists[0])

    return lists[0]
def lcs_bert_calculation(question: str, source: list[int], corpus_dict: dict[int, str]):
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
    #if len(index_list) == 1:
    #    return source[index_list[0]]
    print(source)
    print(index_list)
    print(source[index_list[0]])
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
'''
