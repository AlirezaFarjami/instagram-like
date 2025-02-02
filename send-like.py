import requests

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
    "sessionid": "72329672386%3A5WRQrbjRCGZJKv%3A8%3AAYe20gK0aSELDEVVx54_rmkD75pntnd7919DtHqJTw",
    "rur": "\"RVA\\05472329672386\\0541770022853:01f7fc422e9dca86d00aef0c53fa0405e9658806e52d83903a32e2024cd47a7f9141f672\""
}
# Headers to mimic a real browser request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Referer": "https://www.instagram.com/",
    "X-CSRFToken": cookies["csrftoken"]
}

# Create a session to persist cookies
session = requests.Session()
session.cookies.update(cookies)
session.headers.update(headers)


post_url = "https://www.instagram.com/api/v1/web/likes/3548151302196011754/like/"


try:
    response = session.post(post_url)

    # Check if request was successful
    if response.status_code == 200:
        print("✅ Post was like successfully")
    else:
        print(f"⚠️ Failed to like the post. Status Code: {response.status_code}")

except requests.exceptions.RequestException as e:
    print("❌ An error occurred:", e)
