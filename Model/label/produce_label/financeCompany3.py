import os
import re
import argparse
import json

# 使用 argparse 解析命令行參數
parser = argparse.ArgumentParser(description='Process some text files.')
parser.add_argument('-i', '--input_path', required=True, help='Path to the input folder')
args = parser.parse_args()

# 設定資料夾路徑
folder_path = args.input_path

# 初始化 match_files 字典
match_files = {
    "智邦": [],
    "華碩": [],
    "聯發科": [],
    "鴻海": [],
    "中鋼|中國鋼鐵": [],
    "台達電|Delta|delta": [],
    "國巨": [],
    "光寶科": [],
    "和泰車|和泰汽車": [],
    "中華電信": [],
    "台泥|台灣水泥": [],
    "瑞昱": [],
    "研華": [],
    "長榮": [],
    "台化|台灣化學": [],
    "聯電|聯華電子": [],
    "亞德客": [],
    "台積|台灣積體電路|TSMC": [],
    "統一企業|統一集團": [],
    "台塑|台灣塑膠": [],
    "otherCompany": []
}

# 讀取資料夾中的所有 .txt 文件
for filename in os.listdir(folder_path):
    if filename.endswith('.txt'):
    # if filename == "450.txt":
        file_path = os.path.join(folder_path, filename)
        match_company = False
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            filename = int(filename[:-4])
            for key in match_files.keys():
                matches = re.search(key, content)
                if matches:
                    match_files[key].append(filename)
                    if not match_company:
                        match_company = True
            if not match_company and ("公司" in content or "本集團" in content):
                match_files["otherCompany"].append(filename)

# 將每個 match_files[key] 排序
for key in match_files:
    match_files[key] = sorted(match_files[key]) #, key=int)

print(f"keys: {match_files.keys()}")

# 將匹配結果寫入 financeCompanyList.json
with open('financeCompanyList.json', 'w', encoding='utf-8') as output_file:
    json.dump(match_files, output_file, ensure_ascii=False, indent=4)
    # print(f"file saved as financeCompanyList_new.json")