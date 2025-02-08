import logging
import requests
import json

def extract_cookies(file_path="cookies.json") -> dict:
    """
    Reads a JSON file containing cookies and returns a dictionary where
    the keys are cookie names and the values are cookie values.
    
    Supports two formats:
    1. A list of dictionaries with "name" and "value" keys.
    2. A flat dictionary with cookie names as keys.

    Parameters:
        file_path (str): The path to the JSON file containing the cookies.
        
    Returns:
        dict: A dictionary mapping cookie names to their values.
    """
    try:
        # Read the input JSON file
        with open(file_path, "r", encoding="utf-8") as infile:
            cookies = json.load(infile)
        
        # Check if the format is a list of dictionaries
        if isinstance(cookies, list) and all(isinstance(cookie, dict) and "name" in cookie and "value" in cookie for cookie in cookies):
            filtered_cookies = {cookie["name"]: cookie["value"] for cookie in cookies}
        elif isinstance(cookies, dict):  # Check if it's a dictionary
            filtered_cookies = cookies
        else:
            logging.error("❌ Unsupported cookie format in cookies.json")
            return {}

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


def check_instagram_login(cookies: dict) -> bool:
    """
    Makes a request to Instagram's homepage and checks if the user is logged in.
    
    Parameters:
        cookies (dict): The cookies dictionary for the Instagram session.
        
    Returns:
        bool: True if logged in, False otherwise.
    """
    # Create a session
    session = requests.Session()
    
    # Add cookies to the session
    session.cookies.update(cookies)
    
    # Define the Instagram homepage URL
    url = "https://www.instagram.com/"
    
    try:
        # Make a GET request to the homepage
        response = session.get(url)
        
        # If we have a successful response, check for login status
        if response.status_code == 200:
            # Check for the presence of 'sessionid' cookie or other logged-in indicators
            if 'sessionid' in session.cookies:
                logging.info("✅ User is logged in.")
                return True
            else:
                logging.info("❌ User is not logged in.")
                return False
        else:
            logging.error(f"❌ Failed to load Instagram homepage. Status Code: {response.status_code}")
            return False
    
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Network error while checking login status: {e}")
        return False