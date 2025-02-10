import requests
import logging
from cookie_manager import extract_cookies

def create_instagram_session(cookies: dict, extra_headers: dict = None) -> requests.Session:
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

    # Get standard headers and merge with extra headers
    headers = get_standard_headers(extra_headers)

    # Include CSRF token in the headers if it exists in cookies
    csrf_token = cookies.get("csrftoken", "")
    if csrf_token:
        headers["X-CSRFToken"] = csrf_token

    session = requests.Session()
    session.cookies.update(cookies)
    session.headers.update(headers)

    logging.info("✅ Instagram session created successfully.")
    return session


def get_standard_headers(custom_headers: dict = None) -> dict:
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


def check_session_validity(session):
    """Check if the session is still valid by making a simple request (e.g., accessing the Instagram homepage)."""
    try:
        response = session.get("https://www.instagram.com/")
        if response.status_code == 200 and 'sessionid' in session.cookies:
            return True
        else:
            logging.error("❌ Session is invalid or expired.")
            return False
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Error while validating session: {e}")
        return False