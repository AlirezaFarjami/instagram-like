import json

def extract_cookies(file_path="raw-cookies.json") -> dict:
    """
    Reads a JSON file containing cookies and returns a dictionary where
    the keys are cookie names and the values are cookie values.
    
    Parameters:
        file_path (str): The path to the JSON file containing the cookies.
        
    Returns:
        dict: A dictionary mapping cookie names to their values.
        
    Raises:
        FileNotFoundError: If the specified file does not exist.
        json.JSONDecodeError: If the file is not a valid JSON.
    """
    # Read the input JSON file
    with open(file_path, "r", encoding="utf-8") as infile:
        cookies = json.load(infile)
    
    # Extract relevant cookies: assuming cookies is a list of dictionaries
    filtered_cookies = {cookie["name"]: cookie["value"] for cookie in cookies}
    
    return filtered_cookies

# Example usage:
if __name__ == "__main__":
    try:
        cookies_dict = extract_cookies()
        print("Extracted Cookies:", cookies_dict)
    except FileNotFoundError:
        print("Error: raw-cookies.json file not found!")
    except json.JSONDecodeError:
        print("Error: raw-cookies.json is not a valid JSON file!")
