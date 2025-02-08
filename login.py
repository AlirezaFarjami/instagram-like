import requests
import json
import logging
import time

def instagram_login(username: str, password: str, output_file="cookies.json"):
    """
    Logs into Instagram using the provided credentials and saves session cookies.
    
    Parameters:
        username (str): The Instagram username.
        password (str): The Instagram password.
        output_file (str): The file path to save the session cookies.
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
            return
        
        # Step 2: Generate properly formatted enc_password
        timestamp = int(time.time())  # Correct timestamp
        enc_password = f"#PWD_INSTAGRAM_BROWSER:0:{timestamp}:{password}"
        
        # Step 3: Prepare headers and payload
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
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
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "https://www.instagram.com",
            "Referer": "https://www.instagram.com/",
            "DNT": "1",
            "Sec-GPC": "1",
            "Connection": "keep-alive"
        }
        
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
            logging.info("✅ Login successful! Saving cookies.")
            cookies = {name: value for name, value in session.cookies.items()}
            
            with open(output_file, "w", encoding="utf-8") as file:
                json.dump(cookies, file, indent=4)
        else:
            logging.error("❌ Login failed. Please check your credentials.")
    
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Error during login: {e}")

# Example usage
if __name__ == "__main__":
    user = "Zare_shoes_Shop"
    pwd = "YojxatWNPtcLd223"
    instagram_login(user, pwd)