import json
from tqdm import tqdm

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

if __name__ == "__main__":
    gpt_json = load_json("./result/gpt.json") 
    lcs_json = load_json("./result/lcs.json") 
    embedding_json = load_json("./result/faiss.json") 
    questions = load_json("./preliminary/questions_preliminary.json")["questions"]
    output_json = {"answers": []}
    for question in tqdm(questions):
    # for question in questions:
        qid = question["qid"]
        category = question["category"]
        ans_gpt = gpt_json["answers"][qid-1]["retrieve"]
        ans_lcs = lcs_json["answers"][qid-1]["retrieve"]
        ans_embedding = embedding_json["answers"][qid-1]["retrieve"]
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
        ans["retrieve"] = str(sorted_vote[-1][0])
        output_json["answers"].append(ans)

    # dump the output_json to a file
    with open("ensemble.json", "w", encoding="utf-8") as file:
        json.dump(output_json, file, ensure_ascii=False, indent=4)

