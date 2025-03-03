import json
from tqdm import tqdm

def load_json(file_path):
    """
    Loads JSON data from a file.

    Args:
        file_path (str): The path to the JSON file to load.

    Returns:
        dict: The data loaded from the JSON file.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

if __name__ == "__main__":
    select_json = load_json("pred_GPT_fin_select.json")
    all_json = load_json("pred_GPT_fin_all.json")
    merge_json = {"answers": []}

    for qid in tqdm(range(301, 601)):
        ans_select = next(item["retrieve"] for item in select_json["answers"] if item["qid"] == qid)
        ans_all = next(item["retrieve"] for item in all_json["answers"] if item["qid"] == qid)

        confidence_select = next(item["confidence"] for item in select_json["answers"] if item["qid"] == qid)
        confidence_all = next(item["confidence"] for item in all_json["answers"] if item["qid"] == qid)

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

