from actions.instagram import get_post_data
from services.cookie_manager import extract_cookies_from_db
import requests
import requests
import logging
import json
import re
from typing import Optional, Dict
from database.repositories import load_extracted_parameters
from services.cookie_manager import extract_cookies_from_db
from utils.request_service import create_instagram_session, get_standard_headers

def test_get_post_data():
    """
    Test to check the functionality of fetching post data for a given media ID.
    """
    
    # Define the account username (logged-in user) and the post URL (target post)
    logged_in_username = "Zare_shoes_Shop"  # Example logged-in username
    post_url = "https://www.instagram.com/p/DGEzQ7yPser/"  # Example post URL
    media_id = "DGEzQ7yPser"  # Example media ID extracted from the URL
    
    # Simulate the cookies and session for the logged-in user
    cookies = extract_cookies_from_db(logged_in_username)
    if not cookies:
        print("❌ No valid cookies found for the logged-in username.")
        return

    session = create_instagram_session(logged_in_username)
    if not session:
        print("❌ Failed to create Instagram session.")
        return
    
    # Call the function to fetch post data
    post_data = get_post_data(media_id, logged_in_username, post_url)

    # Verify if the post data is correctly returned
    if post_data:
        print(f"✅ Post data retrieved for {post_url}:")
        print(f"  User PK: {post_data['user_pk']}")
        print(f"  Username: {post_data['username']}")
        print(f"  Full Name: {post_data['full_name']}")
        print(f"  Profile Pic URL: {post_data['profile_pic_url']}")
        print(f"  Is Private: {post_data['is_private']}")
    else:
        print("❌ Failed to fetch post data.")

# Run the test
test_get_post_data()
