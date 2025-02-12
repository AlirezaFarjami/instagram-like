import logging
import getpass
from services.cookie_manager import check_instagram_login
from services.login import instagram_login

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

    # Step 1: Log in
