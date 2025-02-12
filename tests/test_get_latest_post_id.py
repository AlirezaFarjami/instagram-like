from utils.helpers import get_latest_post_media_id
from services.cookie_manager import check_instagram_login, extract_cookies_from_db
from utils.request_service import create_instagram_session

import requests

def test_get_latest_post_media_id(logged_in_username, target_username):
    """
    Test to check the functionality of fetching the latest post media ID for a given target username.
    
    Parameters:
    - logged_in_username: The username used to extract cookies from the database for creating the session.
    - target_username: The Instagram username for which we want to fetch the latest post media ID.
    """
    
    # Check if the logged-in username is valid (this will fetch session cookies)
    if check_instagram_login(logged_in_username):
        # Extract the cookies for the logged-in username from MongoDB
        cookies = extract_cookies_from_db(logged_in_username)
        if not cookies:
            print("❌ No valid cookies found for the logged-in username.")
            return

        # Create a session with the extracted cookies
        session = create_instagram_session(logged_in_username)
        if not session:
            print("❌ Failed to create Instagram session. Exiting.")
            return

        # Fetch the latest post media ID for the target page
        post_id = get_latest_post_media_id(session, logged_in_username, target_username)

        # Print out the latest post media ID
        if post_id:
            print(f"✅ Latest post media ID for {target_username}: {post_id}")
        else:
            print(f"❌ Could not fetch latest post media ID for {target_username}.")
    else:
        print(f"❌ {logged_in_username} is not logged in.")

# Input the usernames for the test
logged_in_username = input("Enter the logged-in username to extract cookies from: ")
target_username = input("Enter the target username to fetch the latest post: ")

# Run the test
test_get_latest_post_media_id(logged_in_username, target_username)
