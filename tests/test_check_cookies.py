from services.cookie_manager import extract_cookies_from_db

def check_user_cookies():
    """
    Fetch and display stored cookies for debugging.
    """
    username = input("Enter your Instagram username: ").strip()

    cookies = extract_cookies_from_db(username)
    if not cookies:
        print(f"❌ No cookies found for user {username}.")
        return

    print(f"✅ Stored cookies for {username}:")
    for key, value in cookies.items():
        print(f"{key}: {value}")

# Run the test
if __name__ == "__main__":
    check_user_cookies()
