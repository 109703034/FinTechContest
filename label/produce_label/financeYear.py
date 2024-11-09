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

# 儲存匹配結果的字典
match_files = {}

# 讀取資料夾中的所有 .txt 文件
for filename in os.listdir(folder_path):
    if filename.endswith('.txt'):
    # if filename == "450.txt":
        file_path = os.path.join(folder_path, filename) 
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            filename = int(filename[:-4])
            matches = re.findall(r'(2\s*0\s*\d\s*\d)\s*年', content)
            for match in matches:
                # print(f"Match: {match}")
                year = int(re.sub(r'\s*', '', match))
                # print(f"Match: {match}, filename: {filename}")
                if year in match_files:
                    if filename not in match_files[year]:
                        match_files[year].append(filename)
                else:
                    match_files[year] = [filename]
                # print(f"match_files[{year}]: {match_files[year]}")

# 將每個 match_files[year] 排序
for year in match_files:
    match_files[year] = sorted(match_files[year]) #, key=int)

# 將匹配結果寫入 financeYearList.json
with open('financeYearList.json', 'w', encoding='utf-8') as output_file:
    json.dump(match_files, output_file, ensure_ascii=False, indent=4)
