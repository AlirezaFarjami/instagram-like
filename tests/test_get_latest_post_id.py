from utils.helpers import get_latest_post_media_id, load_extracted_parameters
from services.cookie_manager import check_instagram_login
import requests

def test_get_latest_post_media_id(extract_username, target_username):
    """
    Test to check the functionality of fetching the latest post media ID for a given target username.
    
    Parameters:
    - extract_username: The username from which we extract parameters to use in the request.
    - target_username: The Instagram username for which we want to fetch the latest post media ID.
    """
    
    # Check if the extract_username is logged in (this will fetch session cookies)
    if check_instagram_login(extract_username):
        # Create a session and load the cookies from the extract_username
        session = requests.Session()
        session.cookies.update(load_extracted_parameters(extract_username))  # Load extracted parameters as cookies

        # Fetch the latest post media ID for the target username
        post_id = get_latest_post_media_id(session, extract_username, target_username)

        # Print out the latest post media ID
        if post_id:
            print(f"✅ Latest post media ID for {target_username}: {post_id}")
        else:
            print(f"❌ Could not fetch latest post media ID for {target_username}.")
    else:
        print(f"❌ {extract_username} is not logged in.")

# Input the usernames
extract_username = input("Enter the username to extract parameters from: ")
target_username = input("Enter the target username to fetch the latest post: ")

# Run the test
test_get_latest_post_media_id(extract_username, target_username)
