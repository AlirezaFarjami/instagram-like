import logging
import random
import requests
from services.cookie_manager import extract_cookies_from_db, save_cookies_to_db
from utils.helpers import from_shortcode, extract_shortcode
from utils.request_service import create_instagram_session, get_standard_headers

neutral_comments = [
    "That's interesting! 🤔",
    "Good to know! 👍",
    "I see what you mean!",
    "That makes sense!",
    "Nice perspective! 👏",
    "I appreciate your input!",
    "Hmm, that's something to think about!",
    "Well said! 😊",
    "Thanks for sharing your thoughts!",
    "I can understand that!",
    "That’s an interesting take!",
    "Noted! 📌",
    "Fair point!",
    "I hear you!",
    "That's a good observation!",
    "Definitely something to consider!",
    "I see your point!",
    "Makes sense to me!",
    "Thanks for the insight!",
    "Interesting thought! 🤯"
]

def get_instagram_comments(media_id: str, account_username: str, page_username: str):
    """
    Fetches comments for a given Instagram media ID and returns them.
    
    Parameters:
        media_id (str): The Instagram media ID of the post.
        logged_in_username (str): The logged-in username used to fetch cookies from MongoDB.
        target_page_username (str): The username of the target page whose media we are interacting with.
    
    Returns:
        list: A list of comments from the Instagram post.
    """
    # Extract cookies from the database using the logged-in username
    cookies = extract_cookies_from_db(account_username)
    if not cookies:
        logging.error(f"❌ No valid cookies found for user {account_username}. Exiting.")
        return []
    
    # Create a session using the stored cookies of the logged-in user
    session = create_instagram_session(account_username)
    if not session:
        logging.error("❌ Failed to create Instagram session. Exiting.")
        return []
    
    # Define request headers (using the cookies of the logged-in user)
    custom_headers = {
        "X-CSRFToken": cookies.get("csrftoken", ""),
        "X-IG-App-ID": "936619743392459",
        "X-ASBD-ID": "129477",
        "X-IG-WWW-Claim": "hmac.AR1Xz_ywrmFEWg9tAlsQAsXKobwAjYkuzkZhbfPwOkkeZoew",
    }
    headers = get_standard_headers(custom_headers=custom_headers)
    session.headers.update(headers)
    
    # Construct the API URL for fetching comments from the target page's media post
    url = f"https://www.instagram.com/api/v1/media/{media_id}/comments/?can_support_threading=true"
    
    try:
        response = session.get(url)
        response.raise_for_status()  # Raise an error for HTTP errors
        
        # Return the comments directly (no file saving)
        comments = response.json().get('comments', [])
        logging.info(f"✅ Retrieved {len(comments)} comments from post by {page_username}")
        return comments
        
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Failed to fetch comments for {page_username}: {e}")
        return []


def reply_to_comment(session: requests.Session, media_id: str, comment_pk: str, commenter_username: str):
    """
    Replies to a given Instagram comment with a random text from neutral_comments.
    
    Parameters:
        session (requests.Session): Authenticated Instagram session.
        media_id (str): The Instagram media ID.
        comment_pk (str): The PK of the comment to reply to.
        commenter_username (str): The username of the comment author.
    """
    url = f"https://www.instagram.com/api/v1/web/comments/{media_id}/add/"
    payload = {
        "comment_text": f"@{commenter_username} {random.choice(neutral_comments)}",
        "replied_to_comment_id": comment_pk
    }
    
    try:
        response = session.post(url, data=payload)
        response.raise_for_status()
        logging.info(f"✅ Successfully replied to comment {comment_pk} by {commenter_username}")
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Failed to reply to comment: {e}")


def print_first_comment_details_and_reply(media_id: str, account_username: str, page_username: str):
    """
    Fetches the first comment from the Instagram post, prints its details, and replies to it.
    
    Parameters:
        media_id (str): The Instagram media ID.
        username (str): The username used to fetch cookies and create the session.
        target_page_username (str): The username of the target page whose post we are interacting with.
    """
    comments = get_instagram_comments(media_id, account_username, page_username)
    if not comments:
        logging.error("❌ No comments found or failed to fetch comments.")
        return
    
    # Extract the first comment
    first_comment = comments[0]
    comment_pk = first_comment.get('pk')
    commenter_username = first_comment.get('user', {}).get('username')
    
    if comment_pk and commenter_username:
        logging.info(f"First Commenter PK: {comment_pk}, Username: {commenter_username}")
        
        # Create a session using the stored cookies for the provided username
        session = create_instagram_session(account_username)
        if session:
            reply_to_comment(session, media_id, comment_pk, commenter_username)
    else:
        logging.error("❌ No valid comment found to reply to.")


if __name__ == "__main__":
    # Example usage (Replace with actual media ID)
    post_url = "https://www.instagram.com/p/DDdvcjbxoi1/"
    shortcode = extract_shortcode(post_url)  
    media_id = from_shortcode(shortcode) if shortcode else None
    if media_id:
        test_username = input("Enter your Instagram username for testing: ").strip()
        print_first_comment_details_and_reply(media_id=media_id, account_username=test_username)
