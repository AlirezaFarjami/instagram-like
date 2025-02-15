import requests
import re
import logging
from services.cookie_manager import extract_cookies_from_db
from utils.request_service import create_instagram_session, get_standard_headers
import json
from utils.request_service import create_instagram_session, check_session_validity

def get_instagram_owner(post_url, account_username):
    # Send a GET request to the Instagram post URL
    cookies = extract_cookies_from_db(account_username)
    if not cookies:
        logging.error(f"❌ No valid cookies found for user {account_username}. Exiting.")
        return []
    
    # Create a session using the stored cookies of the logged-in user
    session = create_instagram_session(account_username)
    if not session:
        logging.error("❌ Failed to create Instagram session. Exiting.")
        return []
    if not check_session_validity(session):
            print("Your session has expired. Please log in again.")
    else:
        print("session is valid")
    # Define request headers (using the cookies of the logged-in user)
    custom_headers = {
        "X-CSRFToken": cookies.get("csrftoken", ""),
        "X-IG-App-ID": "936619743392459",
        "X-ASBD-ID": "129477",
        "X-IG-WWW-Claim": "hmac.AR1Xz_ywrmFEWg9tAlsQAsXKobwAjYkuzkZhbfPwOkkeZoew",
        "Referer": "https://www.instagram.com/",
    }
    headers = get_standard_headers(custom_headers=custom_headers)
    session.headers.update(headers)
    response = session.get(post_url, headers=headers)
    
    if response.status_code != 200:
        return "Error fetching the page"
    
    # Save the response to a file for debugging purposes
    with open('test.html', 'w', encoding='utf-8') as file:
        file.write(response.text)
    
    # Use regex to search for the username in the page content
    match = re.search(r'{"pk":"\d+","username":"([^"]+)",', response.text)

    if match:
        # Extract the username from the match
        owner_username = match.group(1)
        return owner_username
    else:
        return "Username not found"

def fetch_detailed_post_info(shortcode):
    query_hash = "2b0673e0dc4580674a88d426fe00ea90"
    variables = {
        "shortcode": shortcode
    }
    variables_json = json.dumps(variables, separators=(',', ':'))
    url = f"https://www.instagram.com/graphql/query/?query_hash={query_hash}&variables={variables_json}"
    response = requests.get(url)
    data = None
    if response.status_code == 200:
        data = response.json()
        # two examples, there is a lot more data fields in the response:
        user_data = data['data']['shortcode_media']['owner']
        video_media_url = data['data']['shortcode_media'].get('video_url', None)
        # etc...
    return data

# Example usage
post_url = 'https://www.instagram.com/p/DGDRzmvALJW/'  # Replace with your Instagram post URL
owner = get_instagram_owner(post_url, "Zare_shoes_Shop")
print(f"The owner of the post is: {owner}")
