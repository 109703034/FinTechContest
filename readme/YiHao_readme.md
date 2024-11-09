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