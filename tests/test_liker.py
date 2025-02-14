from services.likers import get_likers_from_post

def test_get_likers_from_post():
    """
    Test the function to extract likers from a post and save the result to a JSON file.
    """
    username = input("Enter your Instagram username: ").strip()
    post_url = input("Enter the post URL: ").strip()

    # Extract likers and save to JSON
    likers = get_likers_from_post(username, post_url, limit=5)

    if likers:
        print("✅ Successfully extracted likers and saved to JSON file.")
    else:
        print("❌ Failed to extract likers.")

# Run the test
if __name__ == "__main__":
    test_get_likers_from_post()
