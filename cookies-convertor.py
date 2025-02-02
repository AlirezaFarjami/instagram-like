import json

# Read the input.json file
try:
    with open("raw-cookies.json", "r", encoding="utf-8") as infile:
        cookies = json.load(infile)
except FileNotFoundError:
    print("Error: raw-cookies.json file not found!")
    exit(1)
except json.JSONDecodeError:
    print("Error: raw-cookies.json is not a valid JSON file!")
    exit(1)

# Extract relevant cookies
filtered_cookies = {cookie["name"]: cookie["value"] for cookie in cookies}

# Write the filtered cookies to output.json
with open("output.json", "w", encoding="utf-8") as outfile:
    json.dump(filtered_cookies, outfile, indent=4)

print("Cookies have been successfully extracted and saved to output.json!")
