import requests
import logging
import json
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

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


def create_instagram_session(cookies: dict, extra_headers: dict = None):
    """
    Creates a session with Instagram cookies and headers.
    
    Parameters:
        cookies (dict): A dictionary of Instagram cookies.
        extra_headers (dict, optional): Additional headers to include in the session.
    
    Returns:
        requests.Session or None: A session with Instagram cookies, or None if cookies are missing.
    """
    if not cookies:
        logging.error("❌ Cannot create session: No valid cookies provided.")
        return None  # Prevent execution if cookies are missing

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Referer": "https://www.instagram.com/",
        "X-CSRFToken": cookies.get("csrftoken", "")  # Get CSRF token if it exists
    }

    # Merge extra headers if provided
    if extra_headers:
        headers.update(extra_headers)

    session = requests.Session()
    session.cookies.update(cookies)
    session.headers.update(headers)

    logging.info("✅ Instagram session created successfully.")
    return session


def like_post(session: requests.Session, media_id: str):
    """
    Sends a POST request to like an Instagram post.

    Parameters:
        session (requests.Session): The active session with Instagram authentication.
        media_id (str): The media ID of the Instagram post to like.

    Returns:
        tuple: (success (bool), message (str) or status_code (int))
    """
    if session is None:
        logging.error("❌ Session is not initialized. Cannot like post.")
        return (False, "Session is None")

    post_url = f"https://www.instagram.com/api/v1/web/likes/{media_id}/like/"

    try:
        response = session.post(post_url)

        # Handle rate limiting
        if response.status_code == 429:
            logging.warning("⚠️ Instagram is rate-limiting requests. Try again later.")
            return (False, "Rate limited by Instagram")

        # Handle authentication issues
        if response.status_code == 403:
            logging.error("❌ Authentication error (403 Forbidden). Check if sessionid is expired.")
            return (False, "Authentication error")

        # Handle unexpected errors
        if response.status_code >= 400:
            logging.error(f"❌ Request failed. Status Code: {response.status_code}")
            return (False, response.status_code)

        # Ensure response is in JSON format
        try:
            response_json = response.json()
        except requests.exceptions.JSONDecodeError:
            logging.error("❌ Instagram returned a non-JSON response. Likely an error page.")
            return (False, "Invalid response format")

        # Check if Instagram confirmed the like
        if response_json.get("status") == "ok":
            logging.info(f"✅ Post {media_id} liked successfully.")
            save_cookies_to_file(session)
            return (True, response.status_code)
        else:
            logging.warning(f"⚠️ Instagram responded with an unexpected message: {response_json}")
            return (False, response_json)

    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Network error: {e}")
        return (False, str(e))


def extract_shortcode(instagram_url) -> str:
    """
    Extracts and returns the shortcode from an Instagram post or reel URL.
    
    Works for:
    - Posts: "https://www.instagram.com/p/DFiLS_II0aa/"
    - Reels: "https://www.instagram.com/username/reel/DFiIwE6u9ga/"
    
    Returns:
    - The shortcode (e.g., "DFiLS_II0aa" or "DFiIwE6u9ga") if found.
    - None if the URL does not match the expected format.
    """
    match = re.search(r'/(?:p|reel)/([^/]+)/', instagram_url)
    return match.group(1) if match else None

def from_shortcode(shortcode) -> str :
    """
    Converts an Instagram-style shortcode back into its media id (as a decimal string).
    """
    lower = 'abcdefghijklmnopqrstuvwxyz'
    upper = lower.upper()
    numbers = '0123456789'
    ig_alphabet = upper + lower + numbers + '-_'
    bigint_alphabet = numbers + lower

    def repl(match):
        ch = match.group(0)
        idx = ig_alphabet.index(ch)
        return bigint_alphabet[idx] if idx < len(bigint_alphabet) else f"<{idx}>"

    intermediate = re.sub(r'\S', repl, shortcode)
    tokens = re.findall(r'<(\d+)>|(\w)', intermediate)

    total = 0
    for token in tokens:
        value = int(token[0]) if token[0] != '' else bigint_alphabet.index(token[1])
        total = total * 64 + value

    return str(total)

def get_latest_post_media_id(session: requests.Session, page_name: str) -> str:
    """
    Fetches the latest post media ID for a given Instagram page.
    """
    payload = {
        "av": "17841472251591209",
        "__d": "www",
        "__user": "0",
        "__a": "1",
        "__req": "7",
        "__hs": "20122.HYP:instagram_web_pkg.2.1...1",
        "dpr": "1",
        "__ccg": "MODERATE",
        "__rev": "1019779322",
        "__s": "ogbayt:tcez1o:es29r3",
        "__hsi": "7467142648817593542",
        "__comet_req": "7",
        "fb_dtsg": "NAcMw7_GPycNRsJBCXi-B0BVEjmR39pFQ_tOBb7Zsa1nHc2axd4YsGQ:17864721031021537:1738415853",
        "jazoest": "26113",
        "lsd": "o2qh5hkPEiMagabLkmLGw2",
        "__spin_r": "1019779322",
        "__spin_b": "trunk",
        "__spin_t": "1738579629",
        "fb_api_caller_class": "RelayModern",
        "fb_api_req_friendly_name": "PolarisProfilePostsQuery",
        "variables": json.dumps({
            "data": {
                "count": 12,
                "include_reel_media_seen_timestamp": True,
                "include_relationship_info": True,
                "latest_besties_reel_media": True,
                "latest_reel_media": True
            },
            "username": page_name, 
            "__relay_internal__pv__PolarisIsLoggedInrelayprovider": True
        }),
        "server_timestamps": "true",
        "doc_id": "8934560356598281"
    }

    response = session.post(url="https://www.instagram.com/graphql/query",  data=payload)

    if response.status_code == 200:
            response_text = response.text  # Get raw text

            # Regular expression to find the first occurrence of "pk":"some_number"
            match = re.search(r'"pk":"(\d+)"', response_text)
            
            if match:
                print(match.group(1))
                return match.group(1)  # Extract and return the first PK found
            else:
                return None  # Return None if no PK is found
    else:
            return None  # Return None if request fails

import logging

def main():
    """Main function to create a session and like a post."""
    cookies = extract_cookies("cookies.json")
    session = create_instagram_session(cookies)

    if not session:
        return

    print(
        """
Hello! I can do two things for you:
1) Like a post using its URL (e.g., https://www.instagram.com/p/DFkx8PAJOX0/)
2) Like the latest post from a page using its username (e.g., "nike")
"""
    )

    try:
        choice = int(input("Please enter the number of your choice: "))
    except ValueError:
        logging.error("❌ Invalid input. Please enter 1 or 2.")
        return

    if choice == 1:
        post_url = input("Enter the post URL: ")
        shortcode = extract_shortcode(post_url)
        media_id = from_shortcode(shortcode) if shortcode else None

        if media_id:
            success, response = like_post(session, media_id)
            if success:
                logging.info(f"🎉 Successfully liked post {media_id}")
            else:
                logging.error(f"❌ Failed to like post {media_id}. Reason: {response}")

    elif choice == 2:
        page_name = input("Enter the username of the page: ")
        media_id = get_latest_post_media_id(session, page_name)

        if media_id:
            success, response = like_post(session, media_id)
            if success:
                logging.info(f"🎉 Successfully liked the latest post from {page_name}")
            else:
                logging.error(f"❌ Failed to like post from {page_name}. Reason: {response}")

if __name__ == "__main__":
    main()
