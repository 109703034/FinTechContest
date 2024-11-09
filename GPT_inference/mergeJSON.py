import json
from tqdm import tqdm

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

if __name__ == "__main__":
    finance_json = load_json("pred_GPT_fin_merge.json")
    insurance_json = load_json("pred_GPT_insurance.json")
    faq_json = load_json("pred_GPT_faq.json")

    merge_json = {"answers": []}

    for answer in insurance_json["answers"]:
        merge_json["answers"].append(answer)

    for answer in finance_json["answers"]:
        merge_json["answers"].append(answer)

    for answer in faq_json["answers"]:
        merge_json["answers"].append(answer)
    
    for answer in merge_json["answers"]:
        answer.pop("confidence", None)
        answer.pop("other_retrieve", None)
        answer.pop("other_confidence", None)
      
    with open("../result/gpt.json", "w", encoding="utf-8") as file:
        json.dump(merge_json, file, ensure_ascii=False, indent=4)