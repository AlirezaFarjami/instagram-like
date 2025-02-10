import requests
import logging
from models.user import UserCredentials
from database.repositories import save_user_credentials, get_user_credentials

def save_cookies_to_db(session: requests.Session, username: str):
    """
    Saves the updated cookies from the session to MongoDB.

    Parameters:
        session (requests.Session): The active session containing cookies.
        username (str): The username of the logged-in user.
    """
    try:
        # Extract cookies as a dictionary
        cookies_dict = {name: value for name, value in session.cookies.items()}

        # Validate with Pydantic model
        validated_data = UserCredentials(username=username, cookies=cookies_dict)

        # Save to MongoDB
        save_user_credentials(validated_data.model_dump())

        logging.info(f"✅ Cookies saved to MongoDB for user: {username}")

    except Exception as e:
        logging.error(f"❌ Failed to save cookies to MongoDB: {e}")


def extract_cookies_from_db(username: str):
    """
    Fetches cookies for a given user from MongoDB.

    Parameters:
        username (str): The username of the logged-in user.

    Returns:
        dict: A dictionary of validated cookies, or None if not found.
    """
    try:
        user_data = get_user_credentials(username)
        if user_data:
            validated_user = UserCredentials.from_dict(user_data)
            return validated_user.cookies.model_dump()
        else:
            logging.error(f"❌ No cookies found for user: {username}")
            return None
    except Exception as e:
        logging.error(f"❌ Failed to fetch cookies from MongoDB: {e}")
        return None
    

def check_instagram_login(username: str) -> bool:
    """
    Checks if the Instagram session is valid using stored cookies.

    Parameters:
        username (str): The username of the Instagram account.

    Returns:
        bool: True if logged in, False otherwise.
    """
    from utils.request_service import get_standard_headers  # Avoid circular imports

    # Retrieve cookies from MongoDB
    cookies = extract_cookies_from_db(username)

    if not cookies:
        logging.error(f"❌ Cannot check login status: No cookies found for user {username}.")
        return False

    # Create a session and add cookies
    session = requests.Session()
    session.cookies.update(cookies)

    # Include CSRF token if available
    csrf_token = cookies.get("csrftoken", "")
    headers = get_standard_headers({"X-CSRFToken": csrf_token} if csrf_token else {})

    # Define Instagram homepage URL
    url = "https://www.instagram.com/"

    try:
        # Make a GET request to verify login status
        response = session.get(url, headers=headers)

        if response.status_code == 200 and "sessionid" in session.cookies:
            logging.info(f"✅ User {username} is logged in.")
            return True
        else:
            logging.info(f"❌ User {username} is not logged in.")
            return False

    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Network error while checking login status for {username}: {e}")
        return False

