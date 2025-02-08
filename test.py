import logging
import logging

from helpers import extract_shortcode, from_shortcode
from cookie_manager import extract_cookies, check_instagram_login
from update_params import fetch_instagram_data
from actions.like import like_post, get_latest_post_media_id
from actions.comment import get_instagram_comments, print_first_comment_details_and_reply
from actions.login import instagram_login
from request_service import create_instagram_session

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def main():
    """Main function to create a session and like a post."""
    cookies = extract_cookies("cookies.json")
    is_logged_in = check_instagram_login(cookies)
    
    if not is_logged_in:
        print(
            """
You are not logged in to Instagram. Please follow one of the options below to proceed:
1) Log in using your Instagram username and password.
   - If you choose this, I will guide you to log in to your account so I can proceed with your requests.
   
2) If you already have valid cookies, you can update the cookies.json file manually.
   - Export your cookies from your browser and save them in cookies.json, then re-run the program.

To continue, please choose option 1 or 2 by entering the corresponding number.
"""
        )
        try:
            choice = int(input("Please enter the number of your choice: "))
        except ValueError:
            print("❌ Invalid input. Please enter 1 or 2.")
            return

        if choice == 1:
            username = input("Please enter your Instagram username: ")
            password = input("Please enter your Instagram password: ")
            instagram_login(username = username, password= password)
            cookies = extract_cookies("cookies.json")
        else:
            print("Please re-run the program after updating the cookies.json file with valid cookies")
            return

    session = create_instagram_session(cookies)
    if not session:
        print("❌ Failed to create an Instagram session.")
        return

    fetch_instagram_data()

    print("Hello! I can do two things for you: ")
    while True:
        print(
            """
    1) Like a post by providing its URL (e.g., https://www.instagram.com/p/DFkx8PAJOX0/)
    - I will like the post for you.

    2) Like the highest post from a specific Instagram page by entering the page username (e.g., "nike").
    - I will automatically find and like the hightest post from that page.

    3) Reply to the top comment of a specific post by entering its URL (e.g., https://www.instagram.com/p/DFkx8PAJOX0/).
    - I will automatically reply to the top comment on the post with a random text.

    4) Reply the topest comment of the highest post from a page using its username (e.g., "nike")
        - I will automatically reply to the top comment on the topest post with a random text.

    0)⚠️  Please enter zero to exit  ⚠️
    """
        )

        try:
            choice = int(input("Please enter the number of your choice: "))
        except ValueError:
            logging.error("❌ Invalid input. Please enter the number of one the options")
            return

        if choice == 1:
            post_url = input("Enter the post URL: ")
            shortcode = extract_shortcode(post_url)
            media_id = from_shortcode(shortcode) if shortcode else None

            if media_id:
                success, response = like_post(session, media_id)
                if success:
                    logging.info(f"🎉 Successfully liked post {media_id}")
                else:
                    logging.error(f"❌ Failed to like post {media_id}. Reason: {response}")

        elif choice == 2:
            page_name = input("Enter the username of the page: ")
            media_id = get_latest_post_media_id(session, page_name)
            if media_id:
                print("In proccess")
                success, response = like_post(session, media_id)
                if success:
                    logging.info(f"🎉 Successfully liked the latest post from {page_name}")
                else:
                    logging.error(f"❌ Failed to like post from {page_name}. Reason: {response}")
        
        elif choice == 3:
            post_url = input("Enter the post URL: ")
            shortcode = extract_shortcode(post_url)
            media_id = from_shortcode(shortcode) if shortcode else None

            if media_id:
                get_instagram_comments(media_id)
                print_first_comment_details_and_reply(media_id=media_id)

        elif choice == 4:
            page_name = input("Enter the username of the page: ")
            media_id = get_latest_post_media_id(session, page_name)

            if media_id:
                get_instagram_comments(media_id)
                print_first_comment_details_and_reply(media_id=media_id)
        elif choice == 0:
            logging.info("Exiting the program")
            break
        else:
            logging.error("❌ Invalid choice. Please enter a number between 1 and 4.")
        print("What else can I do for you? ")

if __name__ == "__main__":
    main()