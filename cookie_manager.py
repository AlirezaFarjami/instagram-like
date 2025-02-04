import logging
import requests
import json

def extract_cookies(file_path="cookies.json") -> dict:
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
    try:
        # Read the input JSON file
        with open(file_path, "r", encoding="utf-8") as infile:
            cookies = json.load(infile)
        
        # Extract relevant cookies: assuming cookies is a list of dictionaries
        filtered_cookies = {cookie["name"]: cookie["value"] for cookie in cookies}

        # Validate essential cookies
        required_cookies = ["csrftoken", "sessionid"]
        missing_cookies = [cookie for cookie in required_cookies if cookie not in filtered_cookies]

        if missing_cookies:
            logging.error(f"❌ Missing essential cookies: {', '.join(missing_cookies)}")
            return {}  # Return an empty dictionary to prevent execution

        return filtered_cookies

    except FileNotFoundError:
        logging.error(f"❌ Cookie file '{file_path}' not found.")
        return {}  # Return an empty dictionary so script doesn't crash

    except json.JSONDecodeError:
        logging.error(f"❌ Failed to parse '{file_path}', invalid JSON format.")
        return {}  # Return an empty dictionary so script doesn't crash

def save_cookies_to_file(session: requests.Session, file_path="cookies.json"):
    """
    Saves the updated cookies from the session back to the JSON file.

    Parameters:
        session (requests.Session): The active session containing updated cookies.
        file_path (str): The path to the JSON file to save cookies.
    """
    updated_cookies = [{"name": name, "value": value} for name, value in session.cookies.items()]

    try:
        with open(file_path, "w", encoding="utf-8") as outfile:
            json.dump(updated_cookies, outfile, indent=4)
        logging.info("✅ Updated cookies saved to cookies.json")
    except Exception as e:
        logging.error(f"❌ Failed to save cookies: {e}")