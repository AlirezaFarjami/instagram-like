import logging
import getpass
from services.cookie_manager import check_instagram_login, save_cookies_to_db
from actions.login import instagram_login

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def test_instagram_login_and_check_session():
    """
    Test the Instagram login functionality and session validation.
    1. Prompt the user for username and password.
    2. Attempt to log in and store cookies in MongoDB.
    3. Validate if the session is still active using saved cookies.
    """

    # Ask user for credentials (password is hidden for security)
    username = input("Enter your Instagram username: ")
    password = getpass.getpass("Enter your Instagram password: ")  # Hides password input

    # Step 1: Log in and store cookies in MongoDB
    print("\n🔄 Attempting to log in...")
    success = instagram_login(username, password)

    if not success:
        print("❌ Login failed. Please check your credentials.")
        return

    # Step 2: Check if the stored cookies allow a valid session
    print("\n🔍 Checking if the session is still valid...")
    is_logged_in = check_instagram_login(username)

    if is_logged_in:
        print("✅ User is successfully logged in with stored cookies!")
    else:
        print("❌ Session is invalid or expired.")

# Run the test
if __name__ == "__main__":
    test_instagram_login_and_check_session()
