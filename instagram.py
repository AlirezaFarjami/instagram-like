import logging
import requests
import json
import re

from cookie_manager import save_cookies_to_file

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


def load_extracted_parameters(file_path="extracted_params.json") -> dict:
    """Loads extracted parameters from JSON file."""
    try:
        with open(file_path, "r", encoding="utf-8") as infile:
            parameters = json.load(infile)
        return parameters
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"❌ Error loading extracted parameters: {e}")
        return {}

def get_latest_post_media_id(session: requests.Session, page_name: str) -> str:
    """
    Fetches the latest post media ID for a given Instagram page.
    """
    
    extracted_params = load_extracted_parameters()

    if not extracted_params:
        logging.error("❌ Extracted parameters are missing or invalid.")
        return None

    payload = {
        "av": extracted_params.get("av", "17841472251591209"),
        "__d": "www",
        "__user": extracted_params.get("__user", "0"),
        "__a": "1",
        "__req": extracted_params.get("__req", "7"),
        "__hs": extracted_params.get("__hs", "20123.HYP:instagram_web_pkg.2.1...1"),
        "dpr": extracted_params.get("dpr", "1"),
        "__ccg": extracted_params.get("__ccg", "MODERATE"),
        "__rev": extracted_params.get("__rev", "1019814589"),
        "__s": extracted_params.get("__s", "ogbayt:tcez1o:es29r3"),
        "__hsi": extracted_params.get("__hsi", "7467142648817593542"),
        "__comet_req": extracted_params.get("__comet_req", "7"),
        "fb_dtsg": extracted_params.get("fb_dtsg", "NAcMw7_GPycNRsJBCXi-B0BVEjmR39pFQ_tOBb7Zsa1nHc2axd4YsGQ:17864721031021537:1738415853"),
        "jazoest": extracted_params.get("jazoest", "26113"),
        "lsd": extracted_params.get("lsd", "o2qh5hkPEiMagabLkmLGw2"),
        "__spin_r": extracted_params.get("__spin_r", "1019812100"),
        "__spin_b": extracted_params.get("__spin_b", "trunk"),
        "__spin_t": extracted_params.get("__spin_t", "1738659746"),
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
        "doc_id": extracted_params.get("doc_id", "8934560356598281")
    }
    response = session.post(url="https://www.instagram.com/graphql/query", data=payload)

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
        logging.error(f"❌ Request failed with status code: {response.status_code}")
        return None  # Return None if request fails
