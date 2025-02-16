import json
import logging
from typing import Optional
from services.cookie_manager import extract_cookies_from_db
from utils.request_service import create_instagram_session, get_standard_headers
from models.liker import Liker
from database.repositories import save_to_mongo

def get_likers_of_post(media_id: str, account_username: str, post_url: Optional[str] = "https://instagram.com") -> list:
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
        "Referer": post_url,
    }
    
    headers = get_standard_headers(custom_headers=custom_headers)
    session.headers.update(headers)
    
    post_url = f"https://www.instagram.com/api/v1/media/{media_id}/likers/"

    response = session.get(post_url, headers=headers)

    if response.status_code == 200:
        try:
            # Parse the response as JSON
            data = response.json()

            # Extract users (likers)
            likers_data = data.get('users', [])
            if not likers_data:
                print("No likers found.")
                return []
            
            # Convert each liker to a Liker Pydantic model
            likers = []
            for liker_data in likers_data:
                liker = Liker(
                    username=liker_data.get("username"),
                    user_pk=liker_data.get("pk"),
                    full_name=liker_data.get("full_name"),
                    is_private=liker_data.get("is_private"),
                    profile_pic_id=liker_data.get("profile_pic_id"),
                    profile_pic_url=liker_data.get("profile_pic_url")
                )
                likers.append(liker.dict())  # Store the liker as a dictionary

            # Save likers to MongoDB
            for liker in likers:
                save_to_mongo(collection_name="likers", data=liker)

            print(f"✅ Successfully saved {len(likers)} likers to MongoDB.")
        
        except json.JSONDecodeError:
            print("Failed to parse JSON. Saving raw response as text.")
            with open("liker_response.txt", "w", encoding="utf-8") as file:
                file.write(response.text)
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        print("Response content:", response.text)  # Print raw content for debugging