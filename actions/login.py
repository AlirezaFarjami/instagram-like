import requests
import logging
import time
from utils.request_service import get_standard_headers
from services.cookie_manager import save_cookies_to_db

def instagram_login(username: str, password: str):
    """
    Logs into Instagram using the provided credentials and saves session cookies to MongoDB.

    Parameters:
        username (str): The Instagram username.
        password (str): The Instagram password.
    """
    login_url = "https://www.instagram.com/api/v1/web/accounts/login/ajax/"
    session = requests.Session()

    try:
        # Step 1: Get initial CSRF token
        response = session.get("https://www.instagram.com/accounts/login/")
        response.raise_for_status()
        csrf_token = session.cookies.get("csrftoken")

        if not csrf_token:
            logging.error("❌ Failed to fetch CSRF token.")
            return False

        # Step 2: Generate properly formatted enc_password
        timestamp = int(time.time())  # Correct timestamp
        enc_password = f"#PWD_INSTAGRAM_BROWSER:0:{timestamp}:{password}"

        # Step 3: Prepare headers and payload
        custom_headers = {
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": csrf_token,
            "X-Instagram-AJAX": "1019852061",
            "X-IG-App-ID": "936619743392459",
            "X-ASBD-ID": "129477",
            "X-IG-WWW-Claim": "0",
            "X-Web-Device-Id": "D812B79E-35E6-4027-8B0B-A497DE00DA4E",
            "X-Web-Session-ID": "::vdgles",
            "Origin": "https://www.instagram.com",
            "DNT": "1",
            "Sec-GPC": "1",
            "Connection": "keep-alive"
        }
        headers = get_standard_headers(custom_headers=custom_headers)

        payload = {
            "username": username,
            "enc_password": enc_password,
            "queryParams": "{}",
            "trustedDeviceRecords": "{}",
            "optIntoOneTap": "false",
            "loginAttemptSubmissionCount": "0"
        }

        # Step 4: Send login request
        login_response = session.post(login_url, headers=headers, data=payload)
        login_response.raise_for_status()

        result = login_response.json()
        if result.get("authenticated"):
            logging.info(f"✅ Login successful for user: {username}")

            # Save cookies to MongoDB instead of JSON
            save_cookies_to_db(session, username)

            return True
        else:
            logging.error("❌ Login failed. Please check your credentials.")
            return False

    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Error during login: {e}")
        return False
