import json
from tqdm import tqdm

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

if __name__ == "__main__":
    select_json = load_json("pred_GPT_fin_select.json.json")
    all_json = load_json("pred_GPT_fin_all.json")
    merge_json = {"answers": []}

    for question in tqdm(questions):
        qid = question["qid"]

        ans_select = select_json["answers"][qid-1]["retrieve"]
        ans_all = all_json["answers"][qid-1]["retrieve"]

        confidence_select = select_json["answers"][qid-1]["confidence"]
        confidence_all = all_json["answers"][qid-1]["confidence"]

        if confidence_select >= confidence_all:
            ans = {}
            ans["qid"] = qid
            ans["retrieve"] = ans_select
            ans["confidence"] = confidence_select
            ans["other_retrieve"] = ans_all
            ans["other_confidence"] = confidence_all
            merge_json["answers"].append(ans)
        else:
            ans = {}
            ans["qid"] = qid
            ans["retrieve"] = ans_all
            ans["confidence"] = confidence_all
            ans["other_retrieve"] = ans_select
            ans["other_confidence"] = confidence_select
            merge_json["answers"].append(ans)
      
    with open("pred_GPT_fin_merge.json", "w", encoding="utf-8") as file:
        json.dump(merge_json, file, ensure_ascii=False, indent=4)

