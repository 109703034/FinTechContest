import json

# Load the JSON file
with open('../result/gpt.json', 'r') as file:
    data = json.load(file)

# Convert the integer value of "retrieve" to a string
if "retrieve" in data and isinstance(data["retrieve"], int):
    data["retrieve"] = str(data["retrieve"])

# Save the modified JSON back to the file
with open('../result/gpt_string.json', 'w') as file:
    json.dump(data, file, indent=4)