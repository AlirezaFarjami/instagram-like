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
    
    if not is_logged_in:
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

    print("Hello! I can do the following for you: ")
    while True:
        print(
            """
    1) Like a post by providing its URL (e.g., https://www.instagram.com/p/DFkx8PAJOX0/)
       - I will like the post for you.

    2) Like the latest post from a specific Instagram page by entering the page username (e.g., "nike").
       - I will automatically find and like the latest post from that page.

    3) Reply to the top comment of a specific post by entering its URL (e.g., https://www.instagram.com/p/DFkx8PAJOX0/).
       - I will automatically reply to the top comment on the post with a random text.

    4) Reply to the top comment of the latest post from a page using its username (e.g., "nike")
       - I will automatically reply to the top comment on the latest post with a random text.

    5) Get Likers of an account

    0) ⚠️ Please enter zero to exit ⚠️
    """
        )

        try:
            choice = int(input("Please enter the number of your choice: "))
        except ValueError:
            logging.error("❌ Invalid input. Please enter a number between 0 and 5.")
            continue

        if choice == 0:
            logging.info("Exiting the program")
            break

        # Check if the session is valid before every action
        if not check_session_validity(session):
            print("Your session has expired. Please log in again.")
            password = input("Enter your Instagram password: ")
            if not instagram_login(username=username, password=password):
                print("❌ Login failed. Exiting.")
                return
            session = create_instagram_session(username)
            continue

        if choice == 1:
            post_url = input("Enter the post URL: ").strip()
            shortcode = extract_shortcode(post_url)
            media_id = from_shortcode(shortcode) if shortcode else None

            if media_id:
                success, response = like_post(session, media_id)
                if success:
                    logging.info(f"🎉 Successfully liked post {media_id}")
                    save_cookies_to_db(session, username)
                else:
                    logging.error(f"❌ Failed to like post {media_id}. Reason: {response}")

        elif choice == 2:
            # Here the logged-in user (username) is used to extract parameters.
            page_name = input("Enter the username of the page: ").strip()
            media_id = get_latest_post_media_id(session, username, page_name)
            if media_id:
                success, response = like_post(session, media_id)
                if success:
                    logging.info(f"🎉 Successfully liked the latest post from {page_name}")
                    save_cookies_to_db(session, username)
                else:
                    logging.error(f"❌ Failed to like post from {page_name}. Reason: {response}")

        elif choice == 3:
            post_url = input("Enter the post URL: ").strip()
            shortcode = extract_shortcode(post_url)
            media_id = from_shortcode(shortcode) if shortcode else None

            if media_id:
                get_instagram_comments(media_id=media_id, username=username)
                print_first_comment_details_and_reply(media_id=media_id, account_username=username)
                save_cookies_to_db(session, username)

        elif choice == 4:
            page_name = input("Enter the username of the page: ").strip()  # Page username like 'ducati'
            media_id = get_latest_post_media_id(session, username, page_name)  # Get media ID from the page
            if media_id:
                # Pass both logged-in username and target page username
                print_first_comment_details_and_reply(media_id=media_id, account_username=username, page_username=page_name)  # Reply to the first comment
                save_cookies_to_db(session, username)  # Save updated cookies for logged-in user
        if choice == 5:
            page_name = input("Enter the username of the page: ").strip()
            print("""
    Choose one of the options:
    1) Enter a specific post URL of the page of the username you entered to scrape it's likers.
    2) Continue with the username (I will retreive the latest post likers)
""")
            try:
                sub_choice = int(input("Please enter the number of your choice: "))
            except ValueError:
                logging.error("❌ Invalid input. Please enter a number between 0 and 2.")
                continue
    
            if sub_choice == 1:
                post_url = input("Enter the post URL: ").strip()
                shortcode = extract_shortcode(post_url)
                media_id = from_shortcode(shortcode) if shortcode else None
            
                if media_id:
                    get_likers_of_post(media_id=media_id, account_username=username, post_url=post_url)
                    #Implement the rest of the logic here

            elif sub_choice == 2:
                media_id = get_latest_post_media_id(session, username, page_name)
                if media_id:
                    get_likers_of_post(media_id=media_id, account_username=username)

        print("What else can I do for you? ")

if __name__ == "__main__":
    main()
