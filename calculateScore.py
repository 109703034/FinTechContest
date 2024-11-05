import json
import argparse

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def compare_retrieve(ground_truth_json, prediction_json):
    ground_truths = ground_truth_json.get('ground_truths', [])
    predictions = prediction_json.get('answers', [])
    
    if not isinstance(ground_truths, list) or not isinstance(predictions, list):
        raise ValueError("The 'answers' key must contain a list of dictionaries.")
    
    categories = {
        "insurance": {"total": 0, "matches": 0},
        "finance": {"total": 0, "matches": 0},
        "faq": {"total": 0, "matches": 0}
    }
    
    ground_truth_dict = {item['qid']: item['retrieve'] for item in ground_truths}
    prediction_dict = {item['qid']: item['retrieve'] for item in predictions}
    
    for qid, ground_truth_retrieve in ground_truth_dict.items():
        if 1 <= qid <= 50:
            category = "insurance"
        elif 51 <= qid <= 100:
            category = "finance"
        elif 101 <= qid <= 150:
            category = "faq"
        else:
            continue
        
        categories[category]["total"] += 1
        if qid in prediction_dict and ground_truth_retrieve == prediction_dict[qid]:
            categories[category]["matches"] += 1
        # else:
        #     print(f"Question {qid} was not answered correctly, type: {category}, ground truth: {ground_truth_retrieve}, prediction: {prediction_dict.get(qid)}")
    
    return {cat: (data["matches"] / data["total"] if data["total"] > 0 else 0) for cat, data in categories.items()}

def main(ground_truths_file, predictions_file):
    ground_truth_json = load_json(ground_truths_file)
    prediction_json = load_json(predictions_file)
    
    category_accuracies = compare_retrieve(ground_truth_json, prediction_json)
    
    for category, accuracy in category_accuracies.items():
        print(f"{category} accuracy: {accuracy:.2%}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate retrieval predictions against ground truths.")
    parser.add_argument('-gt', '--ground_truths_file', required=True, help='Path to the ground truths JSON file')
    parser.add_argument('-pr', '--prediction_file', required=True, help='Path to the predictions JSON file')
    
    args = parser.parse_args()
    
    main(args.ground_truths_file, args.prediction_file)