import requests
import logging
import json
import re
import logging

from helpers import extract_shortcode, from_shortcode
from cookie_manager import extract_cookies
from instagram import create_instagram_session, like_post, get_latest_post_media_id
from update_params import fetch_instagram_data

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

if __name__ == "__main__":
    main()

https://www.instagram.com/api/v1/media/3560850072297154417/comments/?can_support_threading=true&min_id=%7B%22cached_comments_cursor%22%3A%20%2218481217383028960%22%2C%20%22bifilter_token%22%3A%20%22KIEBAMPfvV9ohT8ACkbi-25MQADL_sZS5SVAAE0H2J_jM0AAD4yPV6c_QABb3RpCTEpAAGRQmHjvuj8AZnT4iWSrQQAo4lfZkLg_AG2-eOmnP0AA8K35Ce4jQACxU7NkiZA_ADLGMI4RJ0AAtBkUakQnQQA8JoD5sJY_AD8uxbs0FEAAAA%3D%3D%22%7D&sort_order=popular