# GPT inference

### Step 1. Run GPT_retrieve.py

(1) insurance:
```bash
python GPT_inference/GPT_retrieve.py -q preliminary/questions_preliminary.json -s . -l label/ -o GPT_inference/ -c insurance
```
(2) finance
```bash
python GPT_inference/GPT_retrieve.py -q preliminary/questions_preliminary.json -s . -l label/ -o GPT_inference/ -c fin_select
```
```bash
python GPT_inference/GPT_retrieve.py -q preliminary/questions_preliminary.json -s . -l label/ -o GPT_inference/ -c fin_all
```
(3) faq
```bash
python GPT_inference/GPT_retrieve.py -q preliminary/questions_preliminary.json -s . -l label/ -o GPT_inference/ -c faq
```

### Step 2. Combine finance prediction result by two different ways

```bash
cd GPT_inference
```
```bash
python finance_emsemble.py
```

### Step 3. Combine all catogory results

```bash
python mergeJSON.py
```

Than, the prediction JSON file will be in result/gpt.json