from database.repositories import get_user_credentials

def check_user_parameters():
    """
    Check if extracted Instagram parameters exist in MongoDB.
    """
    username = input("Enter your Instagram username: ").strip()
    
    user_data = get_user_credentials(username)
    if not user_data:
        print(f"❌ No user data found for {username}. Have you logged in?")
        return
    
    if "parameters" in user_data and user_data["parameters"]:
        print(f"✅ Parameters found for {username}:")
        print(user_data["parameters"])
    else:
        print(f"❌ No parameters found for {username}. Try running parameter extraction again.")

# Run the test
if __name__ == "__main__":
    check_user_parameters()
