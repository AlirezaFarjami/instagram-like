import requests
import json
import re
import logging
from cookie_manager import extract_cookies, save_cookies_to_file
from request_service import get_standard_headers


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def extract_parameters(html_content, cookies):
    """Extracts required Instagram parameters using regex and cookies."""
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


def fetch_instagram_data(url:str = "https://www.instagram.com/", parameters_file = "extracted_params.json"):
    """Fetches Instagram page HTML and extracts required parameters."""
    session = requests.Session()

    # Load cookies into the session
    cookies = extract_cookies()
    if not cookies:
        logging.error("❌ No valid cookies found. Exiting.")
        return
    session.cookies.update(cookies)

    try:
        response = session.get(url, headers=get_standard_headers())
        response.raise_for_status()

        # Extract necessary parameters
        extracted_data = extract_parameters(response.text, cookies)

        # Save parameters to JSON
        with open(parameters_file, "w", encoding="utf-8") as outfile:
            json.dump(extracted_data, outfile, indent=4)
        logging.info(f"✅ Extracted parameters saved to {parameters_file}")

        # Save updated cookies
        save_cookies_to_file(session)

    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Request failed: {e}")
