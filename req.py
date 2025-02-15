import logging
from utils.helpers import extract_shortcode, from_shortcode
from actions.instagram import get_latest_post_media_id
from services.cookie_manager import (
    extract_cookies_from_db,
    check_instagram_login,
    save_cookies_to_db
)
from services.update_params import fetch_instagram_data
from actions.like import like_post
from actions.comment import get_instagram_comments, print_first_comment_details_and_reply
from actions.login import instagram_login
from utils.request_service import create_instagram_session, check_session_validity
from actions.likers import get_likers_of_post
# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def main():
    """Main function to create a session and perform Instagram actions."""
    # Prompt for the username (the key used for MongoDB cookie storage)
    # username = input("Enter your Instagram username: ").strip()
    username = "Zare_shoes_Shop"
    # Check login status via stored cookies in the database
    is_logged_in = check_instagram_login(username)
    
    print(
            """
You are not logged in to Instagram. Please follow one of the options below to proceed:
1) Log in using your Instagram username and password.
   - I will guide you to log in to your account so I can proceed with your requests.
   
2) Ensure that valid cookies are stored in the database.
"""
        )
    try:
        choice = int(input("Please enter the number of your choice: "))
    except ValueError:
        print("❌ Invalid input. Please enter 1 or 2.")
        return

    if choice == 1:
        password = input("Please enter your Instagram password: ")
        login_success = instagram_login(username=username, password=password)
        if not login_success:
            print("❌ Login failed. Exiting.")
            return
    else:
        print("Please ensure your cookies are stored in the database, then re-run the program.")
        return

    # Create Instagram session (cookies are fetched from MongoDB using the username)
    session = create_instagram_session(username)
    if not session:
        print("❌ Failed to create an Instagram session.")
        return

    # Fetch initial parameters and update them in MongoDB
    fetch_instagram_data(username)

    response = session.get(url="https://www.instagram.com/p/DGDRzmvALJW/")

    with open("page.html", "w", encoding="utf-8") as file:
        file.write(response.text)

if __name__ == "__main__":
    main()
