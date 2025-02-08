import logging
import random
import requests
from cookie_manager import extract_cookies, save_cookies_to_file
from helpers import from_shortcode, extract_shortcode
from request_service import create_instagram_session, get_standard_headers

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

def get_instagram_comments(media_id: str):
    """
    Fetches comments for a given Instagram media ID and returns them.
    
    Parameters:
        media_id (str): The Instagram media ID of the post.
    
    Returns:
        list: A list of comments from the Instagram post.
    """
    # Extract cookies
    cookies = extract_cookies()
    if not cookies:
        logging.error("❌ No valid cookies found. Exiting.")
        return []
    
    # Create a session with cookies
    session = create_instagram_session(cookies)
    if not session:
        logging.error("❌ Failed to create Instagram session. Exiting.")
        return []
    
    # Define request headers (some headers from the provided curl request)
    custom_headers = {
        "X-CSRFToken": cookies.get("csrftoken", ""),
        "X-IG-App-ID": "936619743392459",
        "X-ASBD-ID": "129477",
        "X-IG-WWW-Claim": "hmac.AR1Xz_ywrmFEWg9tAlsQAsXKobwAjYkuzkZhbfPwOkkeZoew",
    }
    headers = get_standard_headers(custom_headers=custom_headers)
    session.headers.update(headers)
    
    # Construct the API URL
    url = f"https://www.instagram.com/api/v1/media/{media_id}/comments/?can_support_threading=true"
    
    try:
        response = session.get(url)
        response.raise_for_status()  # Raise an error for HTTP errors
        
        # Return the comments directly (no file saving)
        comments = response.json().get('comments', [])
        logging.info(f"✅ Retrieved {len(comments)} comments")
        return comments
        
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Failed to fetch comments: {e}")
        return []

def reply_to_comment(session: requests.Session, media_id: str, comment_pk: str, username: str):
    """
    Replies to a given Instagram comment with a random text from neutral_comments.
    
    Parameters:
        session (requests.Session): Authenticated Instagram session.
        media_id (str): The Instagram media ID.
        comment_pk (str): The PK of the comment to reply to.
        username (str): The username of the comment author.
    """
    url = f"https://www.instagram.com/api/v1/web/comments/{media_id}/add/"
    payload = {
        "comment_text": f"@{username} {random.choice(neutral_comments)}",
        "replied_to_comment_id": comment_pk
    }
    
    try:
        response = session.post(url, data=payload)
        response.raise_for_status()
        logging.info(f"✅ Successfully replied to comment {comment_pk} by {username}")
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Failed to reply to comment: {e}")

def print_first_comment_details_and_reply(media_id: str):
    """
    Fetches the first comment from the Instagram post, prints its details, and replies to it.
    
    Parameters:
        media_id (str): The Instagram media ID.
    """
    comments = get_instagram_comments(media_id)
    if not comments:
        logging.error("❌ No comments found or failed to fetch comments.")
        return
    
    # Extract the first comment
    first_comment = comments[0]
    comment_pk = first_comment.get('pk')
    username = first_comment.get('user', {}).get('username')
    
    if comment_pk and username:
        logging.info(f"First Commenter PK: {comment_pk}, Username: {username}")
        
        # Extract cookies and create session
        cookies = extract_cookies()
        session = create_instagram_session(cookies)
        if session:
            reply_to_comment(session, media_id, comment_pk, username)
    else:
        logging.error("❌ No valid comment found to reply to.")

if __name__ == "__main__":
    # Example usage (Replace with actual media ID)
    post_url = "https://www.instagram.com/p/DDdvcjbxoi1/"
    shortcode = extract_shortcode(post_url)  
    media_id = from_shortcode(shortcode) if shortcode else None
    if media_id:
        print_first_comment_details_and_reply(media_id=media_id)
