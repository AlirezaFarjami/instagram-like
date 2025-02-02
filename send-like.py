import requests
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

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

# Function to create a session with cookies and headers
def create_instagram_session(cookies: dict):
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Referer": "https://www.instagram.com/",
    "X-CSRFToken": cookies["csrftoken"]
    }
    session = requests.Session()
    session.cookies.update(cookies)
    session.headers.update(headers)
    return session

# Function to like a post
def like_post(session: requests.Session, media_id: str):
    post_url = f"https://www.instagram.com/api/v1/web/likes/{media_id}/like/"

    try:
        response = session.post(post_url)

        # Check if response is valid
        if response.status_code == 200:
            response_json = response.json()
            if response_json.get("status") == "ok":
                logging.info(f"✅ Post {media_id} liked successfully.")
                return (True, response.status_code)
            else:
                logging.warning(f"⚠️ Instagram returned an error: {response_json}")
                return (False, response_json)
        else:
            logging.error(f"❌ Failed to like the post. Status Code: {response.status_code}")
            return (False, response.status_code)

    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Network error: {e}")
        return (False, str(e))

# Create session and like a post
cookies = extract_cookies(file_path="raw-cookies.json")
session = create_instagram_session(cookies)
like_post(session, "3474505257687952484")
