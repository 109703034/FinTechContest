# 使用方法及模型介紹

我們使用三種方法，分別得到三種不同的 retrieve prediction，  
再用 (FAISS) * 0.3 + (LCS+Bert) * 0.3 + (GPT-4o) * 0.4  的權重做 ensemble，  
取得最終版本的 prediction 結果。

## 1. FAISS (Facebook AI Similarity Search)

1. **初始化**:  
    用 Sentence-BERT 模型來生成句子嵌入，並設定參數，例如 window_size。

2. **文本前處理**:
    * 移除多餘的空白和非中文字符。
    * 使用 Jieba 進行分詞，提取文本中的關鍵詞。

3. **計算分數**:  
    | 項目           | 描述                                         | 權重 |
    |----------------|----------------------------------------------|------|
    | 語義相似度     | 使用**內積**，計算問題與選項文檔，word embeddings 的相似度   | 0.5  |
    | 關鍵詞匹配得分 | 計算問題關鍵字，與文檔關鍵詞之間的重疊程度     | 0.4  |
    | 長度懲罰        | 避免過短的文本                               | 0.1  |

依據計算出的分數，inference 出最佳答案，輸出為 `faiss.json`


## 2. LCS + Bert

1. **LCS (Longest Common Subsequence)**:  
    先用 LCS 計算問題與選項文檔的共同子序列，篩選出最長的文檔

2. **BERT**:  
    當多個文檔子序列長度相同時，利用預訓練的中文 BERT 模型，挑選出與問題最相關的文檔


## 3. GPT-4o  

1. **使用 ChatGPT API**  
    使用 `chatgpt-4.0-latest` 及預先寫好的 prompt。

2. **Inference**  
    分次處理不同類別的資料，並用 prompt 讓模型預測出最佳答案及 "模擬信心指數"。
    - **insurance data**：輸出為 `pred_GPT_insurance.json`  
    - **faq data**：輸出為 `pred_GPT_faq.json`  
    - **finance data**  
        - 先匹配問題與選項文檔的標籤，輸出 `pred_GPT_fin_select.json`  
        - 不匹配直接處理，輸出 `pred_GPT_fin_all.json`  
        - 以模擬信心指數高低合併結果，輸出 `pred_GPT_fin_merge.json`

3. **整合**  
    直接合併所有結果 (`pred_GPT_insurance.json`、`pred_GPT_faq.json`、`pred_GPT_fin_merge.json`)，輸出為 `gpt.json`

-------

# How to get the retrieve prediction

[1. Get prediction by FAISS](#how-to-run-faiss_retrievepy-in-faiss-method)

[2. Get prediction by lcs+bert](#how-to-run-lcs_retrievepy-in-lcs_bert_method)

[3. Get prediction by chatGPT](#how-to-run-gpt_retrievepy-to-get-prediction-of-chatgpt)

[4. Get final best ensemble result - `ensemble.json`](#how-to-run-ensemblepy-to-get-the-best-ensemble-result)

## Architecture and Explanation
```
Model
├── insurance (TXT data parsed from official reference PDF, and is moved from Preprocess folder)
│   ├── 1.txt
│   ├── ...
│   └── 643.txt
├── finance (TXT data parsed from official reference PDF, and is moved from Preprocess folder)
│   ├── 0.txt
│   ├── ...
│   └── 1034.txt
├── finance_noBlank (finance data without any whitespace characters, and is moved from Preprocess folder)
│   ├── 0.txt
│   ├── ...
│   └── 1034.txt
├── faq (official reference JSON, and is moved from Preprocess folder)
│   └── pid_map_content.json
├── label (labels of finance files)
│   ├── financeCompanyList.json
│   ├── financeFormList.json
│   ├── financeYearList.json
│   └── produce_label (codes to produce labels)
│       ├── financeCompany3.py
│       ├── financeForm3.py
│       └── financeYear.py
├── preliminary (official preliminary questions and example)
│   ├── pred_retrieve_example 2.json
│   └── questions_preliminary.json
├── faiss_retrieve.py (code of faiss method)
├── lcs_bert_method (codes and result of lcs+bert method)
│   ├── lcs_bert.py
│   ├── lcs_bert_retrieve.py
│   └── lcs.json
├── GPT_inference (codes and result of chatGPT method)
│   ├── GPT_retrieve.py (main code)
│   ├── OpenAI_inference.py (code of function)
│   ├── finance_emsemble.py (integrate finance predictions of two ways)
│   ├── mergeJSON.py (integrate all catogories of predictions)
│   ├── pred_GPT_insurance.json
│   ├── pred_GPT_faq.json
│   ├── pred_GPT_fin_select.json
│   ├── pred_GPT_fin_all.json
│   └── pred_GPT_fin_merge.json
├── result (predictions)
│   ├── faiss.json
│   ├── gpt.json
│   └── lcs.json
├── ensemble.py (code of ensemble)
├── ensemble.json (final result - ensemble of three predictions)
└── README.md
```

# How to run faiss_retrieve.py in FAISS method 

```bash
python3 faiss_retrieve.py --question_path prelimilary/questions_preliminary.json --source_path ./ --output_path result/faiss.json
```

positional arguments: [REQUIRED]
- question_path: path to questions_preliminary.json
- source_path: path to the folder that contains finance_noBlank folder and insurance folder
- output_path: path to the output json  


# How to run lcs_retrieve.py in lcs_bert_method
## Steps
1. place `finance`, `insurance` and `faq` folder (dataset in txt) in the `Model` directory
2. place questions (questions_preliminary.json) in `preliminary` folder
3. cd `/lcs_bert_method`
4. run the following codes:
    ```
    python3 lcs_bert_retrieve.py --question_path ../preliminary/questions_preliminary.json --source_path ../ --output_path ./lcs.json
    ```
5. get `lcs.json` as the result of using lcs and bert-based method

# How to run GPT_retrieve.py to get prediction of ChatGPT

### Step 1. Run GPT_retrieve.py

(1) Insurance:
```bash
python3 GPT_inference/GPT_retrieve.py -q preliminary/questions_preliminary.json -s . -l label/ -o GPT_inference/ -c insurance
```
-> Get prediction of insurance at `GPT_inference/pred_GPT_insurance.json`

(2) Finance
```bash
python3 GPT_inference/GPT_retrieve.py -q preliminary/questions_preliminary.json -s . -l label/ -o GPT_inference/ -c fin_select
```
-> Get prediction of finance (mapping the labels of question and sources first) at `GPT_inference/pred_GPT_fin_select.json`

```bash
python3 GPT_inference/GPT_retrieve.py -q preliminary/questions_preliminary.json -s . -l label/ -o GPT_inference/ -c fin_all
```
-> Get prediction of finance at `GPT_inference/pred_GPT_fin_all.json`

(3) FAQ
```bash
python3 GPT_inference/GPT_retrieve.py -q preliminary/questions_preliminary.json -s . -l label/ -o GPT_inference/ -c faq
```
-> Get prediction of faq at `GPT_inference/pred_GPT_faq.json`

### Step 2. Combine finance prediction result by two different ways

```bash
cd GPT_inference
```
```bash
python3 finance_emsemble.py
```
-> Get integrated prediction of finance at `GPT_inference/pred_GPT_fin_merge.json`

### Step 3. Combine all catogory results

```bash
python3 mergeJSON.py
```

Finally, the ChatGPT prediction JSON file will be in `result/gpt.json`

# How to run ensemble.py to get the best ensemble result
## Steps
1. place `faiss.json`, `lcs.json` and `gpt.json` folder (result of the three methods) in the `result` directory
2. place questions (questions_preliminary.json) in `preliminary` folder
3. cd `Model/`
4. run the following codes:
    ```
    python3 ensemble.py
    ```
5. get `ensemble.json` as the final best result