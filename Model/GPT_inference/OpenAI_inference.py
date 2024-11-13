from openai import OpenAI
import json
import os
import sys
import time
import re

# Set API key
key_file = "/home/acaac/FinTech/MidProject_competition/preliminary/config/api_key.json"
keys = json.loads(open(key_file, "r").read())
api_key = keys["OpenAI"]
client = OpenAI(api_key = api_key)

# def get_embeddings(prompt):
#     response = client.embeddings.create(
#         model="text-embedding-3-small",
#         input=prompt
#     )
#     return response
#     # response.data[0].embedding

def create_messages(prompt):
    messages = [
        {"role": "system", "content": "你是擅長擷取/分析文章資訊的人，回答簡短而正確"}, #的dictionary格式回覆，只有一個answer(integer)、confidence(integer%)"},
        {
            "role": "user", 
            "content": [
              {"type": "text", "text": prompt}
            ]
        }
    ]
    return messages

def get_completion(prompt):
    completion = client.chat.completions.create(
        # model="gpt-4o-mini",
        model="chatgpt-4o-latest",
        messages=create_messages(prompt),
        temperature=0.5,  # 0~2, higher is more creative, lower is more deterministic
        max_tokens=20,  # Max tokens to generate
        # response_format={
        #     "type": "json_schema",
        #     "json_schema": {
        #         "name": "answer_confidence",
        #         "schema": {
        #             "answer": "number",
        #             "confidence": "number"
        #         }
        #     }
        # }
    )
    return completion
    # completion.choices[0].message

if __name__ == "__main__":
    prompt = "Your prompt here"  # Replace with your actual prompt
    result = get_completion(prompt)
    print(result)