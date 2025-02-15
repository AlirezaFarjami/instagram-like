import requests
import re
import logging
from database.repositories import update_mongo, get_user_credentials
from services.cookie_manager import extract_cookies_from_db
from utils.request_service import get_standard_headers
from models.parameters import InstagramParameters

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def extract_parameters(html_content, cookies):
    """
    Extracts required Instagram parameters using regex and cookies.
    This is using the old working regex logic to extract parameters.
    """
    parameters = {}

    # Extract av (User ID)
    av_patterns = [
        r'"NON_FACEBOOK_USER_ID":"(\d+)"',  # First occurrence
        r'"actorID":"(\d+)"',               # Second occurrence
        r'"fbid":"(\d+)"',                  # Third occurrence
        r'"qeid":"(\d+)"'                   # Fourth occurrence
    ]
    for pattern in av_patterns:
        match = re.search(pattern, html_content)
        if match:
            parameters["av"] = match.group(1)
            break  # Stop searching once found

    # Extract __user
    user_pattern = re.search(r'"USER_ID":"(\d+)"', html_content)
    if user_pattern:
        parameters["__user"] = user_pattern.group(1)

    # Extract __hs
    hs_pattern = re.search(r'"haste_session":"(.*?)"', html_content)
    if hs_pattern:
        parameters["__hs"] = hs_pattern.group(1)

    # Extract __ccg
    ccg_pattern = re.search(r'"connectionClass":"(.*?)"', html_content)
    if ccg_pattern:
        parameters["__ccg"] = ccg_pattern.group(1)

    # Extract __rev
    rev_patterns = [
        r'"rev":(\d+)',                   # JSON key occurrence
        r'"client_revision":(\d+)',        # Alternative key occurrence
        r'data-btmanifest="(\d+)_main"'    # HTML attribute occurrence
    ]
    for pattern in rev_patterns:
        match = re.search(pattern, html_content)
        if match:
            parameters["__rev"] = match.group(1)
            break  # Stop searching once found

    # Extract __comet_req
    comet_pattern = re.search(r'__comet_req=(\d+)', html_content)
    if comet_pattern:
        parameters["__comet_req"] = comet_pattern.group(1)

    # Extract jazoest from the API request pattern
    jazoest_pattern = re.search(r'__comet_req=\d+&jazoest=(\d+)', html_content)
    if jazoest_pattern:
        parameters["jazoest"] = jazoest_pattern.group(1)

    # Extract __spin_r, __spin_b, __spin_t
    spin_pattern = re.search(r'"__spin_r":(\d+),"__spin_b":"(.*?)","__spin_t":(\d+)', html_content)
    if spin_pattern:
        parameters["__spin_r"], parameters["__spin_b"], parameters["__spin_t"] = spin_pattern.groups()

    # Extract fb_dtsg
    fb_dtsg_pattern = re.search(r'"DTSGInitialData",\[\],{"token":"(.*?)"', html_content)
    if fb_dtsg_pattern:
        parameters["fb_dtsg"] = fb_dtsg_pattern.group(1)

    # Extract values from cookies
    parameters["csrftoken"] = cookies.get("csrftoken", "")
    parameters["sessionid"] = cookies.get("sessionid", "")
    parameters["dpr"] = cookies.get("dpr", "")

    return parameters


def fetch_instagram_data(username: str, url: str = "https://www.instagram.com/"):
    """
    Fetches Instagram page HTML, extracts required parameters, and stores them in MongoDB.

    Parameters:
        username (str): The Instagram username.
        url (str): The URL to fetch data from.

    Returns:
        dict: Extracted parameters if successful, None otherwise.
    """
    session = requests.Session()

    # Load cookies from the database
    cookies = extract_cookies_from_db(username)
    if not cookies:
        logging.error(f"❌ No valid cookies found for user {username}. Exiting.")
        return None

    session.cookies.update(cookies)

    try:
        response = session.get(url, headers=get_standard_headers())
        response.raise_for_status()

        # Extract necessary parameters
        extracted_data = extract_parameters(response.text, cookies)

        # Validate with Pydantic model
        validated_parameters = InstagramParameters(**extracted_data)

        # Fetch existing user data
        user_data = get_user_credentials(username)
        if not user_data:
            logging.error(f"❌ User {username} does not exist in the database.")
            return None

        # Update user document with parameters
        update_mongo("user_credentials", {"username": username}, {"parameters": validated_parameters.model_dump()})

        logging.info(f"✅ Extracted parameters for {username} saved to MongoDB.")

        return validated_parameters.model_dump()

    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Request failed for {username}: {e}")
        return None
