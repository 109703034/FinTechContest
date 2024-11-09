import os
import json
import argparse

from tqdm import tqdm
from lcs_bert import load_data_from_txt, lcs_bert_calculation

if __name__ == "__main__":
    # 使用argparse解析命令列參數
    parser = argparse.ArgumentParser(description='Process some paths and files.')
    parser.add_argument('--question_path', type=str, required=True, help='讀取發布題目路徑')  # 問題文件的路徑
    parser.add_argument('--source_path', type=str, required=True, help='讀取參考資料路徑')  # 參考資料的路徑
    parser.add_argument('--output_path', type=str, required=True, help='輸出符合參賽格式的答案路徑')  # 答案輸出的路徑

    args = parser.parse_args()  # 解析參數

    answer_dict = {"answers": []}  # 初始化字典

    with open(args.question_path, 'rb') as f:
        qs_ref = json.load(f)  # 讀取問題檔案

    source_path_insurance = os.path.join(args.source_path, 'insurance')  # 設定參考資料路徑
    corpus_dict_insurance = load_data_from_txt(source_path_insurance)

    source_path_finance = os.path.join(args.source_path, 'finance')  # 設定參考資料路徑
    corpus_dict_finance = load_data_from_txt(source_path_finance)

    with open(os.path.join(args.source_path, 'faq/pid_map_content.json'), 'rb') as f_s:
        key_to_source_dict = json.load(f_s)  # 讀取參考資料文件
        key_to_source_dict = {int(key): value for key, value in key_to_source_dict.items()}

    for q_dict in tqdm(qs_ref['questions']):
        if q_dict['category'] == 'finance':
            # 進行檢索
            retrieved = lcs_bert_calculation(q_dict['query'], q_dict['source'], corpus_dict_finance)

            # 將結果加入字典
            answer_dict['answers'].append({"qid": q_dict['qid'], "retrieve": retrieved})

        elif q_dict['category'] == 'insurance':
            retrieved = lcs_bert_calculation(q_dict['query'], q_dict['source'], corpus_dict_insurance)

            answer_dict['answers'].append({"qid": q_dict['qid'], "retrieve": retrieved})

        elif q_dict['category'] == 'faq':
            corpus_dict_faq = {key: str(value) for key, value in key_to_source_dict.items() if key in q_dict['source']}
            retrieved = lcs_bert_calculation(q_dict['query'], q_dict['source'], corpus_dict_faq)

            answer_dict['answers'].append({"qid": q_dict['qid'], "retrieve": retrieved})

        else:
            raise ValueError("Something went wrong")  # 如果過程有問題，拋出錯誤

    # 將答案字典保存為json文件
    with open(args.output_path, 'w', encoding='utf8') as f:
        json.dump(answer_dict, f, ensure_ascii=False, indent=4)  # 儲存檔案，確保格式和非ASCII字符
