import os
import json
import argparse
from tqdm import tqdm
import re
from OpenAI_inference import *
import sys

# 載入參考資料，返回一個字典，key為檔案名稱，value為txt檔內容的文本
def load_data(source_path):
    masked_file_ls = os.listdir(source_path)  # 獲取資料夾中的檔案列表
    corpus_dict = {}
    for file in tqdm(masked_file_ls):
        # print(f"正在處理檔案 {file}...")
        if file.endswith('.txt'):
            try:
                file_key = int(file.replace('.txt', ''))
                # print(f"file_key: {file_key}")
                corpus_dict[file_key] = read_txt(os.path.join(source_path, file))
            except ValueError:
                print(f"跳過檔案 {file}，因為它無法轉換為整數。")
    return corpus_dict


# 讀取單個TXT文件並返回其文本內容
def read_txt(txt_loc, page_infos: list = None):
    with open(txt_loc, 'r', encoding='utf-8') as file:
        txt_content = file.read()  # 讀取TXT文件的全部內容
    return txt_content  # 返回讀取的文本內容

# 讀取標籤文件並返回其內容
def load_label(label_path):
    with open(label_path, 'r', encoding='utf-8') as file:
        label_dict = json.load(file)
    return label_dict

def source_select(qs, source, corpus_dict, label_dict):
    qs_keys = []
    for key in label_dict.keys():
        if re.search(key, qs):
            qs_keys.append(key)
    # print(f"qs: {qs}, qs_keys: {qs_keys}")
    for key in qs_keys:
        selected_source = []
        for name in label_dict[key]:
            if name in source:
                selected_source.append(name)
        source = selected_source
        # print(f"after key: {key}, selected_source: {selected_source}")

    return selected_source

def get_prompt(qs, source, corpus_dict):
    source_content = "\n".join([f'{file}:\n{corpus_dict[int(file)]}\n' for file in source])
    prompt = f'''
Q:{qs}

which source-ID is most related to the above question? Only respond with "one source-ID's number" and "confidence index", response format:
{{
    "answer": "number",  (source-ID)
    "confidence": "number" (%)
}}

If you think none of the sources can provide the correct answer, please lower the confidence index accordingly.

source format:
source-ID:
content

Note: The source content has been processed to remove irrelevant information such as amounts (e.g., numbers, prices, percentages).

source:

{source_content}
    '''
    return prompt

def get_GPTanswer(prompt):
    is_success = True
    try:
        result = get_completion(prompt)
        response = json.loads(result.choices[0].message.content)
        confidence = response.get("confidence")
        
        try:
            answer = int(response.get("answer"))
        except (ValueError, TypeError):
            if any(char.isdigit() for char in response.get("answer", "")):
                answer = int(''.join(filter(str.isdigit, response.get("answer"))))
            else:
                print(f"Error: answer: {response.get('answer')} is not a number or cannot be converted to a number.")
                answer = -1
                is_success = False

        if confidence.endswith('%'):
            confidence = int(confidence.replace('%', ''))
        else:
            print("Error: confidence is not a percentage.")
            confidence = int(float(confidence) * 100)
            is_success = False

    except Exception as e:
        print(f"Error: {e}")
        answer = -1
        confidence = 0
        is_success = False
    # print(f"Answer: {answer}, Confidence: {confidence}")
    return answer, confidence, is_success

if __name__ == "__main__":
    # 使用argparse解析命令列參數
    parser = argparse.ArgumentParser(description='Process some paths and files.')
    parser.add_argument('-q', '--question_path', type=str, required=True, help='讀取發布題目路徑')  # 問題文件的路徑
    parser.add_argument('-s', '--source_path', type=str, required=True, help='讀取參考資料路徑')  # 參考資料的路徑
    parser.add_argument('-o', '--output_path', type=str, required=True, help='輸出符合參賽格式的答案路徑')  # 答案輸出的路徑
    parser.add_argument('-l', '--label_path', type=str, required=True, help='讀取標籤文件路徑')  # 標籤文件的路徑
    parser.add_argument('-c', '--category', type=str, required=True, help='選擇要處理的類別 - fin_select, fin_all, insurance, faq')
    args = parser.parse_args()  # 解析參數

    selected_category = args.category  # 讀取選擇的類別
    if selected_category not in ['fin_select', 'fin_all', 'insurance', 'faq']:
        print("Error: category should be one of 'fin_select', 'fin_all', 'insurance', 'faq'.")
        exit(1)

    answer_dict = {"answers": []}  # 初始化字典

    with open(args.question_path, 'rb') as f:
        qs_ref = json.load(f)  # 讀取問題檔案

    source_path_insurance = os.path.join(args.source_path, 'insurance')  # 設定參考資料路徑
    corpus_dict_insurance = load_data(source_path_insurance)

    source_path_finance = os.path.join(args.source_path, 'finance')  # 設定參考資料路徑
    corpus_dict_finance = load_data(source_path_finance)

    with open(os.path.join(args.source_path, 'faq/pid_map_content.json'), 'rb') as f_s:
        key_to_source_dict = json.load(f_s)  # 讀取參考資料文件
        key_to_source_dict = {int(key): value for key, value in key_to_source_dict.items()}

    # 將標籤文件讀取為字典
    label_dict_finance = {}  # Initialize as an empty dictionary
    for file in os.listdir(args.label_path):
        if file.endswith('.json'):
            label_dict = load_label(os.path.join(args.label_path, file))
            # print(f"keys: {label_dict.keys()}")
            if 'otherCompany' in label_dict:
                otherCompany = label_dict['otherCompany']
            for key, value in label_dict.items():
                if re.match(r'^\d+$', key):
                    key = f"{key}年"
                if key == "otherCompany":
                    continue
                if key in label_dict_finance:
                    label_dict_finance[key] += value
                    if not "表" in key and not "年" in key:
                        label_dict_finance[key] += otherCompany
                else:
                    label_dict_finance[key] = value
                    if not "表" in key and not "年" in key:
                        label_dict_finance[key] += otherCompany

    # print(f"label keys: {label_dict_finance.keys()}")

    for q_dict in qs_ref['questions']:
        if q_dict['category'] == 'finance' and selected_category == 'fin_select':
            print(f"qid: {q_dict['qid']}")

            # select source
            selected_source = source_select(q_dict['query'], q_dict['source'], corpus_dict_finance, label_dict_finance)
            unselected_source = list(set(q_dict['source']) - set(selected_source))
            
            prompt = get_prompt(q_dict['query'], selected_source, corpus_dict_finance)
            # print(f"prompt: {prompt}")
            
            answer, confidence, is_success = get_GPTanswer(prompt)
            while not is_success:
                retry = input("The GPT answer was not successful. Do you want to try again? (yes/no): ")
                if retry.lower() == 'yes':
                    answer, confidence, is_success = get_GPTanswer(prompt)
                else:
                    answer = random.choice(selected_source)
                    break
            if confidence < 70:
                print(f"selected confidence: {confidence} < 70")
                unseleted_prompt = get_prompt(q_dict['query'], unselected_source, corpus_dict_finance)
                unseleted_answer, unseleted_confidence, unseleted_is_success = get_GPTanswer(unseleted_prompt)
                while not unseleted_is_success:
                    retry = input("The GPT answer was not successful. Do you want to try again? (yes/no): ")
                    if retry.lower() == 'yes':
                        unseleted_answer, unseleted_confidence, unseleted_is_success = get_GPTanswer(unseleted_prompt)
                    else:
                        answer = random.choice(unselected_source)
                        break
                if unseleted_confidence < 70:
                    print(f"unselected confidence: {unseleted_confidence} < 70")
                if unseleted_confidence > confidence:
                    answer = unseleted_answer
                    confidence = unseleted_confidence

            # 將結果加入字典
            answer_dict['answers'].append({"qid": q_dict['qid'], "retrieve": answer, "confidence": confidence, "source": selected_source})

        elif q_dict['category'] == 'finance' and selected_category == 'fin_all':
            
            # if q_dict['qid'] != 64:
            #     continue
            
            print(f"qid: {q_dict['qid']}")
            
            prompt = get_prompt(q_dict['query'], q_dict['source'], corpus_dict_finance)
            # print(f"prompt: {prompt}")

            answer, confidence, is_success = get_GPTanswer(prompt)
            while not is_success:
                retry = input("The GPT answer was not successful. Do you want to try again? (yes/no): ")
                if retry.lower() == 'yes':
                    answer, confidence, is_success = get_GPTanswer(prompt)
                else:
                    answer = random.choice(q_dict['source'])
                    break
            if confidence < 70:
                print(f"confidence: {confidence} < 70")
                

            # 將結果加入字典
            answer_dict['answers'].append({"qid": q_dict['qid'], "retrieve": answer, "confidence": confidence})

        elif q_dict['category'] == 'insurance' and selected_category == 'insurance':
            print(f"qid: {q_dict['qid']}")

            prompt = get_prompt(q_dict['query'], q_dict['source'], corpus_dict_insurance)
            # print(f"prompt: {prompt}")
            
            answer, confidence, is_success = get_GPTanswer(prompt)
            while not is_success:
                retry = input("The GPT answer was not successful. Do you want to try again? (yes/no): ")
                if retry.lower() == 'yes':
                    answer, confidence, is_success = get_GPTanswer(prompt)
                else:
                    answer = random.choice(q_dict['source'])
                    break
            if confidence < 70:
                print(f"confidence: {confidence} < 70")

            answer_dict['answers'].append({"qid": q_dict['qid'], "retrieve": answer, "confidence": confidence})

        elif q_dict['category'] == 'faq' and selected_category == 'faq':
            print(f"qid: {q_dict['qid']}")
            corpus_dict_faq = {key: str(value) for key, value in key_to_source_dict.items() if key in q_dict['source']}

            prompt = get_prompt(q_dict['query'], q_dict['source'], corpus_dict_faq)
            # print(f"prompt: {prompt}")

            answer, confidence, is_success = get_GPTanswer(prompt)
            while not is_success:
                retry = input("The GPT answer was not successful. Do you want to try again? (yes/no): ")
                if retry.lower() == 'yes':
                    answer, confidence, is_success = get_GPTanswer(prompt)
                else:
                    answer = random.choice(q_dict['source'])
                    break
            if confidence < 70:
                print(f"confidence: {confidence} < 70")
            
            # print(f"answer: {answer}, confidence: {confidence}")

            answer_dict['answers'].append({"qid": q_dict['qid'], "retrieve": answer, "confidence": confidence})

        else:
            continue
            # raise ValueError("Something went wrong")  # 如果過程有問題，拋出錯誤

    # 將答案字典保存為json文件
    output_name = f"pred_GPT_{selected_category}.json"
    output_path = os.path.join(args.output_path, output_name)
    with open(output_path, 'w', encoding='utf8') as f:
        json.dump(answer_dict, f, ensure_ascii=False, indent=4)  # 儲存檔案，確保格式和非ASCII字符
        print(f"file saved to {output_path}")

### usage:
### cd /home/acaac/FinTech/MidProject_competition
### python GPT_inference/GPT_retrieve.py -q <Q_path> -s . -l label/ -o . 
### 
### example
### cd /home/acaac/FinTech/MidProject_competition/Parse_data/GPT_inference
### python GPT_retrieve.py -q ../../Data/dataset/preliminary/questions_example.json -s ../ -l ../label/ -o . -c fin_all
### fin_select, fin_all, insurance, faq
