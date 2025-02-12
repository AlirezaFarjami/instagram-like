import requests
import logging
from services.cookie_manager import extract_cookies_from_db

def get_standard_headers(custom_headers: dict = {}) -> dict:
    """
    Returns the standard Instagram headers. Optionally merges with custom headers.
    
    Parameters:
        custom_headers (dict): A dictionary of custom headers to add or override.
    
    Returns:
        dict: The final headers for the request.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Referer": "https://www.instagram.com/",
        "X-Requested-With": "XMLHttpRequest"
    }


    if custom_headers:
        headers.update(custom_headers)

    return headers


def create_instagram_session(account_username: str, extra_headers: dict = None) -> requests.Session:
    """
    Creates a session with Instagram cookies stored in MongoDB.

    Parameters:
        username (str): The username of the Instagram account.
        extra_headers (dict, optional): Additional headers to include in the session.

    Returns:
        requests.Session or None: A session with Instagram cookies, or None if cookies are missing.
    """
    # Retrieve cookies from MongoDB
    cookies = extract_cookies_from_db(account_username)

    if not cookies:
        logging.error(f"❌ Cannot create session: No valid cookies found for user {account_username}.")
        return None

    # Get standard headers and merge with extra headers
    headers = get_standard_headers(extra_headers)

    # Include CSRF token if available
    csrf_token = cookies.get("csrftoken", "")
    if csrf_token:
        headers["X-CSRFToken"] = csrf_token

    # Create session and update with cookies & headers
    session = requests.Session()
    session.cookies.update(cookies)
    session.headers.update(headers)

    logging.info(f"✅ Instagram session created successfully for user {account_username}.")
    return session


def check_session_validity(instagram_session: requests.Session) -> bool:
    """
    Checks if the Instagram session is still valid by making a request.

    Parameters:
        session (requests.Session): The session to validate.

    Returns:
        bool: True if session is valid, False otherwise.
    """
    try:
        response = instagram_session.get("https://www.instagram.com/")
        if response.status_code == 200 and "sessionid" in instagram_session.cookies:
            logging.info("✅ Session is valid.")
            return True
        else:
            logging.error("❌ Session is invalid or expired.")
            return False
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Error while validating session: {e}")
        return False
