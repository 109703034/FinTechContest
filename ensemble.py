import json
from tqdm import tqdm

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

if __name__ == "__main__":
    gpt_json = load_json("./result/example/gpt.json") # 采妍
    lcs_json = load_json("./result/example/lcs.json") # 翊豪
    embedding_json = load_json("./result/example/embedding.json") # 詠絜
    lcs_adv_json = load_json("./result/example/lcs_adv.json") # 靖芸
    questions = load_json("./dataset/preliminary/questions_example.json")["questions"]
    output_json = {"answers": []}
    for question in tqdm(questions):
    # for question in questions:
        qid = question["qid"]
        category = question["category"]
        ans_gpt = gpt_json["answers"][qid-1]["retrieve"]
        ans_lcs = lcs_json["answers"][qid-1]["retrieve"]
        ans_embedding = embedding_json["answers"][qid-1]["retrieve"]
        ans_lcs_adv = lcs_adv_json["answers"][qid-1]["retrieve"]
        if category == "finance":
            ans = {}
            ans["qid"] = qid
            ans["retrieve"] = ans_gpt
            output_json["answers"].append(ans)
        elif category == "insurance" or category == "faq":
            # insurance: GPT*0.4+LCS*0.3+Embedding*0.3
            ans, vote = {}, {}
            ans["qid"] = qid
            for (option, weight) in [(ans_gpt, 0.4), (ans_lcs, 0.3), (ans_embedding, 0.3)]:
                if option not in vote:
                    vote[option] = weight
                else:
                    vote[option] += weight
            # pick the option with the highest vote, if two highest votes are the same, pick the one with GPT
            sorted_vote = sorted(vote.items(), key=lambda x:x[1])
            ans["retrieve"] = sorted_vote[-1][0]
            output_json["answers"].append(ans)
        # elif category == "faq":
        #     pass
    # dump the output_json to a file
    with open("pred_retrieve.json", "w", encoding="utf-8") as file:
        json.dump(output_json, file, ensure_ascii=False, indent=2)

