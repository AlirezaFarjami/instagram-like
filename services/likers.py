import requests
import logging
import json
from typing import List
from utils.helpers import extract_shortcode, from_shortcode
from services.cookie_manager import extract_cookies_from_db
from utils.request_service import create_instagram_session

def get_likers_from_post(username: str, post_url: str, limit: int = 20) -> List[dict]:
    """
    Simplified version of extracting likers from a given Instagram post and saving the result to a JSON file.
    
    Parameters:
        username (str): The username of the logged-in Instagram account.
        post_url (str): The URL of the post to extract likers from.
        limit (int): Maximum number of likers to extract.

    Returns:
        List[dict]: A list of likers.
    """
    session = create_instagram_session(username)
    if not session:
        logging.error("❌ Failed to create Instagram session.")
        return []

    # Extract media ID
    shortcode = extract_shortcode(post_url)
    if not shortcode:
        logging.error("❌ Failed to extract shortcode from post URL.")
        return []

    media_id = from_shortcode(shortcode)
    if not media_id:
        logging.error("❌ Failed to convert shortcode to media ID.")
        return []

    logging.info(f"✅ Extracted media ID: {media_id}")

    # Fetch cookies
    cookies = extract_cookies_from_db(username)
    if not cookies:
        logging.error(f"❌ No valid cookies found for user {username}.")
        return []

    # Prepare headers based on cURL command
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "X-CSRFToken": cookies.get("csrftoken", ""),
        "X-IG-App-ID": "936619743392459",  # Static ID for Instagram Web
        "X-ASBD-ID": "129477",  # App ID
        "X-Requested-With": "XMLHttpRequest",  # Standard header for AJAX requests
        "X-Web-Session-ID": cookies.get("sessionid", ""),  # Session ID
        "Referer": post_url,
        "Connection": "keep-alive",
        "Cookie": f"csrftoken={cookies.get('csrftoken', '')}; sessionid={cookies.get('sessionid', '')}; ds_user_id={cookies.get('ds_user_id', '')};"
    }

    # API endpoint to fetch likers
    likers_url = f"https://www.instagram.com/api/v1/media/{media_id}/likers/"

    try:
        # Send GET request with correct headers and cookies
        response = session.get(likers_url, headers=headers)

        # Log the raw response content
        logging.info(f"🔍 Raw Response Content: {response.text}")

        response.raise_for_status()  # Raise an exception for non-200 status codes
        likers_data = response.json().get("users", [])

        if not likers_data:
            logging.warning("⚠️ No likers found for this post.")
            return []

        # Limit the number of likers scraped
        likers_data = likers_data[:limit]

        # Save the data to a JSON file
        with open(f"likers_{media_id}.json", "w") as f:
            json.dump(likers_data, f, indent=4)

        logging.info(f"✅ Likers data saved to likers_{media_id}.json.")
        return likers_data

    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Failed to fetch likers: {e}")
        return []
