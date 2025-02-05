import logging
import logging

from helpers import extract_shortcode, from_shortcode
from cookie_manager import extract_cookies, create_instagram_session
from instagram import like_post, get_latest_post_media_id
from update_params import fetch_instagram_data
from comment import get_instagram_comments, print_first_comment_details_and_reply
# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def main():
    """Main function to create a session and like a post."""
    cookies = extract_cookies("cookies.json")
    session = create_instagram_session(cookies)
    fetch_instagram_data()
    if not session:
        return

    print(
        """
Hello! I can do two things for you:
1) Like a post using its URL (e.g., https://www.instagram.com/p/DFkx8PAJOX0/)
2) Like the latest post from a page using its username (e.g., "nike")
3) Reply the topest comment of a post using its URL (e.g., https://www.instagram.com/p/DFkx8PAJOX0/)
4) Reply the topest comment of the latest post from a page using its username (e.g., "nike")
"""
    )

    try:
        choice = int(input("Please enter the number of your choice: "))
    except ValueError:
        logging.error("❌ Invalid input. Please enter 1 or 2.")
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
        get_instagram_comments(media_id)
        print_first_comment_details_and_reply(media_id=media_id)

    elif choice == 4:
        page_name = input("Enter the username of the page: ")
        media_id = get_latest_post_media_id(session, page_name) 
        get_instagram_comments(media_id)
        print_first_comment_details_and_reply(media_id=media_id)

if __name__ == "__main__":
    main()

