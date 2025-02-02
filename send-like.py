import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# User's Instagram cookies (Replace with actual values)
cookies = {
    "ps_n": "1",
    "datr": "sfidZyOdcaaRYJ1f1Hx8FZgr",
    "ds_user_id": "72329672386",
    "csrftoken": "nFfvwXCZf2fOuqDT1nAwVd6MJ7rqRz0d",
    "ig_did": "58E116AC-AFCD-45C1-B079-324774AC0572",
    "ps_l": "1",
    "wd": "1920x955",
    "mid": "Z534sQALAAGT4_d6MvhRhUua9Sc8",
    "sessionid": "72329672386%3A5WRQrbjRCGZJKv%3A8%3AAYdJbnjbkg9tNAJpye0C2eDIYhYyI6I7n0OVAfdfsQ",
    "rur": "\"RVA\\05472329672386\\0541770032979:01f75840508127211e67656658f206085b94958979c3de8ed1a708f62837b261a5651423\""
}

# Headers to mimic a real browser request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Referer": "https://www.instagram.com/",
    "X-CSRFToken": cookies["csrftoken"]
}

# Function to create a session with cookies and headers
def create_instagram_session():
    session = requests.Session()
    session.cookies.update(cookies)
    session.headers.update(headers)
    return session

# Function to like a post
def like_post(session: requests.Session, media_id: str):
    post_url = f"https://www.instagram.com/api/v1/web/likes/{media_id}/like/"

    try:
        response = session.post(post_url)

        # Check if response is valid
        if response.status_code == 200:
            response_json = response.json()
            if response_json.get("status") == "ok":
                logging.info(f"✅ Post {media_id} liked successfully.")
                return (True, response.status_code)
            else:
                logging.warning(f"⚠️ Instagram returned an error: {response_json}")
                return (False, response_json)
        else:
            logging.error(f"❌ Failed to like the post. Status Code: {response.status_code}")
            return (False, response.status_code)

    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Network error: {e}")
        return (False, str(e))

# Create session and like a post
session = create_instagram_session()
like_post(session, "3558933350313189864")
