import logging
import requests
import json
import re
# We now import the DB version of cookie saving, but the caller (main.py) handles cookie updates.
from services.cookie_manager import save_cookies_to_db

def like_post(instagram_session: requests.Session, media_id: str):
    """
    Sends a POST request to like an Instagram post.

    Parameters:
        session (requests.Session): The active session with Instagram authentication.
        media_id (str): The media ID of the Instagram post to like.

    Returns:
        tuple: (success (bool), message (str) or status_code (int))
    """
    if instagram_session is None:
        logging.error("❌ Session is not initialized. Cannot like post.")
        return (False, "Session is None")

    post_url = f"https://www.instagram.com/api/v1/web/likes/{media_id}/like/"

    try:
        response = instagram_session.post(post_url)

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
            return (True, response.status_code)
        else:
            logging.warning(f"⚠️ Instagram responded with an unexpected message: {response_json}")
            return (False, response_json)

    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Network error: {e}")
        return (False, str(e))
