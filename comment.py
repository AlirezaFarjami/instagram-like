import logging
import json
import requests
from cookie_manager import extract_cookies, create_instagram_session, save_cookies_to_file
from helpers import from_shortcode, extract_shortcode

import random

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

def get_instagram_comments(media_id: str, output_file="comments.json"):
    """
    Fetches comments for a given Instagram media ID and saves them to a JSON file.
    
    Parameters:
        media_id (str): The Instagram media ID of the post.
        output_file (str): The file path to save the comments response.
    """
    # Extract cookies
    cookies = extract_cookies()
    if not cookies:
        logging.error("❌ No valid cookies found. Exiting.")
        return
    
    # Create a session with cookies
    session = create_instagram_session(cookies)
    if not session:
        logging.error("❌ Failed to create Instagram session. Exiting.")
        return
    
    # Define request headers (some headers from the provided curl request)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Referer": "https://www.instagram.com/",
        "X-CSRFToken": cookies.get("csrftoken", ""),
        "X-IG-App-ID": "936619743392459",
        "X-ASBD-ID": "129477",
        "X-IG-WWW-Claim": "hmac.AR1Xz_ywrmFEWg9tAlsQAsXKobwAjYkuzkZhbfPwOkkeZoew",
        "X-Requested-With": "XMLHttpRequest"
    }
    session.headers.update(headers)
    
    # Construct the API URL
    url = f"https://www.instagram.com/api/v1/media/{media_id}/comments/?can_support_threading=true"
    
    try:
        response = session.get(url)
        response.raise_for_status()  # Raise an error for HTTP errors
        
        # Save the response to a file
        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(response.json(), file, indent=4)
        
        logging.info(f"✅ Comments saved to {output_file}")
        
        # Save updated cookies
        save_cookies_to_file(session)
        
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Failed to fetch comments: {e}")

def reply_to_comment(session: requests.Session, media_id: str, comment_pk: str, username: str):
    """
    Replies to a given Instagram comment with the text "yes".
    
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

def print_first_comment_details_and_reply(comments_file="comments.json", media_id="3551475337331657365"):
    """
    Reads the first comment from the saved JSON file, prints the commenter's pk and username, 
    and replies to the comment.
    
    Parameters:
        comments_file (str): The file path of the saved comments JSON.
        media_id (str): The Instagram media ID.
    """
    try:
        with open(comments_file, "r", encoding="utf-8") as file:
            data = json.load(file)
        
        # Extract the first comment
        first_comment = data.get("comments", [])[0]
        if first_comment:
            comment_pk = first_comment.get('pk')
            username = first_comment.get('user', {}).get('username')
            print(f"First Commenter PK: {comment_pk}, Username: {username}")
            
            # Extract cookies and create session
            cookies = extract_cookies()
            session = create_instagram_session(cookies)
            if session:
                reply_to_comment(session, media_id, comment_pk, username)
        else:
            print("No comments found in the file.")
    
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"❌ Error reading comments file: {e}")

if __name__ == "__main__":
    # Example usage (Replace with actual media ID)
    post_url = "https://www.instagram.com/p/DDdvcjbxoi1/"
    shortcode = extract_shortcode(post_url)  
    media_id = from_shortcode(shortcode) if shortcode else None
    get_instagram_comments(media_id)
    print_first_comment_details_and_reply(media_id=media_id)
