# How to get the retrieve prediction

[1. Get prediction by FAISS](#how-to-run-faiss_retrievepy-in-faiss-method)

[2. Get prediction by lcs+bert](#how-to-run-lcs_retrievepy-in-lcs_bert_method)

[3. Get prediction by chatGPT](#how-to-run-gpt_retrievepy-to-get-prediction-of-chatgpt)

[4. Get final best ensemble result - `ensemble.json`](#how-to-run-ensemblepy-to-get-the-best-ensemble-result)

## Architecture and Explanation
```
Parse_data
├── insurance (TXT data parsed from official reference PDF)
│   ├── 0.txt
│   ├── ...
│   └── 643.txt
├── finance (TXT data parsed from official reference PDF)
│   ├── 0.txt
│   ├── ...
│   └── 1034.txt
├── finance_noBlank (finance data without any whitespace characters)
│   ├── 0.txt
│   ├── ...
│   └── 1034.txt
├── faq (official reference JSON)
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
python faiss_retrieve.py --question_path prelimilary/questions_preliminary.json --source_path ./ --output_path result/faiss.json
```

positional arguments: [REQUIRED]
- question_path: path to questions_preliminary.json
- source_path: path to the folder that contains finance_noBlank folder and insurance folder
- output_path: path to the output json  




# How to run lcs_retrieve.py in lcs_bert_method
## Versions and Packages
* python3==3.10.12
* tqdm==4.66.4
* torch==2.3.0
* transformers==4.46.1
## Architecture
```
upper directory
├── finance (txt data folder)
├── insurance (txt data folder)
├── faq (txt data folder)
├── preliminary 
│   └── questions_preliminary.json (questions of preliminary)
├── lcs_bert_method
│   ├── lcs_bert_retrieve.py
│   └── lcs_bert.py
└── lcs.json (output when finish running the codes)
```
## Steps
1. place `finance`, `insurance` and `faq` folder (dataset in txt) in the upper directory
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
python GPT_inference/GPT_retrieve.py -q preliminary/questions_preliminary.json -s . -l label/ -o GPT_inference/ -c insurance
```
-> Get prediction of insurance at `GPT_inference/pred_GPT_insurance.json`

(2) Finance
```bash
python GPT_inference/GPT_retrieve.py -q preliminary/questions_preliminary.json -s . -l label/ -o GPT_inference/ -c fin_select
```
-> Get prediction of finance (mapping the labels of question and sources first) at `GPT_inference/pred_GPT_fin_select.json`

```bash
python GPT_inference/GPT_retrieve.py -q preliminary/questions_preliminary.json -s . -l label/ -o GPT_inference/ -c fin_all
```
-> Get prediction of finance at `GPT_inference/pred_GPT_fin_all.json`

(3) FAQ
```bash
python GPT_inference/GPT_retrieve.py -q preliminary/questions_preliminary.json -s . -l label/ -o GPT_inference/ -c faq
```
-> Get prediction of faq at `GPT_inference/pred_GPT_faq.json`

### Step 2. Combine finance prediction result by two different ways

```bash
cd GPT_inference
```
```bash
python finance_emsemble.py
```
-> Get integrated prediction of finance at `GPT_inference/pred_GPT_fin_merge.json`

### Step 3. Combine all catogory results

```bash
python mergeJSON.py
```

Finally, the ChatGPT prediction JSON file will be in `result/gpt.json`




# How to run ensemble.py to get the best ensemble result
## Versions and Packages
* python3==3.10.12
* tqdm==4.66.4
## Architecture
```
upper directory
├── preliminary 
│   └── questions_preliminary.json (questions of preliminary)
├── result
│   ├── faiss.json
│   ├── lcs.json
│   └── gpt.json
└── ensemble.json (output when finish running the codes)
```
## Steps
1. place `faiss.json`, `lcs.json` and `gpt.json` folder (result of the three methods) in the `result` directory
2. place questions (questions_preliminary.json) in `preliminary` folder
3. cd `/upper directory`
4. run the following codes:
    ```
    python3 ensemble.py
    ```
5. get `ensemble.json` as the final best result