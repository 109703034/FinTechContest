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
    "合併財務報表|合併財務報告表|合併公司財務報表": [],
    "合併綜合損益表": [],
    "合併資產負債表": [],
    "合併權益變動表": [],
    "合併現金流量表|合併現⾦流量表": []
}

# 讀取資料夾中的所有 .txt 文件
for filename in os.listdir(folder_path):
    if filename.endswith('.txt'):
    # if filename == "450.txt":
        file_path = os.path.join(folder_path, filename) 
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            filename = int(filename[:-4])
            for key in match_files.keys():
                matches = re.search(key, content)
                if matches:
                    match_files[key].append(filename)
            # matches = re.findall(r'合\s*併\s*\S\s*\S\s*\S\s*\S{,2}\s*表', content)
            # for match in matches:
            #     # print(f"Match: {match}")
            #     form = re.sub(r'\s*', '', match)
            #     # print(f"Match: {match}, filename: {filename}")
            #     if form in match_files:
            #         if filename not in match_files[form]:
            #             match_files[form].append(filename)
            #     else:
            #         match_files[form] = [filename]
                # print(f"match_files[{form}]: {match_files[form]}")

# 將每個 match_files[form] 排序
for form in match_files:
    match_files[form] = sorted(match_files[form]) #, key=int)

print(f"keys: {match_files.keys()}")

# 將匹配結果寫入 financeFormList.json
with open('financeFormList.json', 'w', encoding='utf-8') as output_file:
    json.dump(match_files, output_file, ensure_ascii=False, indent=4)
    # print(f"file saved as financeFormList_new.json")