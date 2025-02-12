import logging
from services.update_params import fetch_instagram_data
from services.cookie_manager import check_instagram_login
from database.repositories import get_user_credentials

def test_fetch_instagram_data():
    """
    Test fetching Instagram data and extracting parameters.
    """

    username = input("Enter your Instagram username: ")

    # Step 1: Check if the user is logged in
    if not check_instagram_login(username):
        print("❌ User is not logged in. Run login first!")
        return

    # Step 2: Fetch parameters
    print("\n🔍 Fetching Instagram parameters...")
    extracted_params = fetch_instagram_data(username)

    if extracted_params:
        print("✅ Successfully extracted parameters:")
        for key, value in extracted_params.items():
            print(f"{key}: {value}")

        # Step 3: Check if parameters were stored in MongoDB
        user_data = get_user_credentials(username)
        if user_data and "parameters" in user_data:
            print("✅ Extracted parameters were successfully saved to MongoDB!")
        else:
            print("❌ Parameters were NOT found in the database.")

    else:
        print("❌ Failed to extract parameters.")

# Run the test
if __name__ == "__main__":
    test_fetch_instagram_data()
