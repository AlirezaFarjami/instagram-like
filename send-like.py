import requests
import logging
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def extract_cookies(file_path="cookies.json") -> dict:
    """
    Reads a JSON file containing cookies and returns a dictionary where
    the keys are cookie names and the values are cookie values.
    
    Parameters:
        file_path (str): The path to the JSON file containing the cookies.
        
    Returns:
        dict: A dictionary mapping cookie names to their values.
        
    Raises:
        FileNotFoundError: If the specified file does not exist.
        json.JSONDecodeError: If the file is not a valid JSON.
    """
    try:
        # Read the input JSON file
        with open(file_path, "r", encoding="utf-8") as infile:
            cookies = json.load(infile)
        
        # Extract relevant cookies: assuming cookies is a list of dictionaries
        filtered_cookies = {cookie["name"]: cookie["value"] for cookie in cookies}

        # Validate essential cookies
        required_cookies = ["csrftoken", "sessionid"]
        missing_cookies = [cookie for cookie in required_cookies if cookie not in filtered_cookies]

        if missing_cookies:
            logging.error(f"❌ Missing essential cookies: {', '.join(missing_cookies)}")
            return {}  # Return an empty dictionary to prevent execution

        return filtered_cookies

    except FileNotFoundError:
        logging.error(f"❌ Cookie file '{file_path}' not found.")
        return {}  # Return an empty dictionary so script doesn't crash

    except json.JSONDecodeError:
        logging.error(f"❌ Failed to parse '{file_path}', invalid JSON format.")
        return {}  # Return an empty dictionary so script doesn't crash

def save_cookies_to_file(session: requests.Session, file_path="cookies.json"):
    """
    Saves the updated cookies from the session back to the JSON file.

    Parameters:
        session (requests.Session): The active session containing updated cookies.
        file_path (str): The path to the JSON file to save cookies.
    """
    updated_cookies = [{"name": name, "value": value} for name, value in session.cookies.items()]

    try:
        with open(file_path, "w", encoding="utf-8") as outfile:
            json.dump(updated_cookies, outfile, indent=4)
        logging.info("✅ Updated cookies saved to cookies.json")
    except Exception as e:
        logging.error(f"❌ Failed to save cookies: {e}")


def create_instagram_session(cookies: dict, extra_headers: dict = None):
    """
    Creates a session with Instagram cookies and headers.
    
    Parameters:
        cookies (dict): A dictionary of Instagram cookies.
        extra_headers (dict, optional): Additional headers to include in the session.
    
    Returns:
        requests.Session or None: A session with Instagram cookies, or None if cookies are missing.
    """
    if not cookies:
        logging.error("❌ Cannot create session: No valid cookies provided.")
        return None  # Prevent execution if cookies are missing

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Referer": "https://www.instagram.com/",
        "X-CSRFToken": cookies.get("csrftoken", "")  # Get CSRF token if it exists
    }

    # Merge extra headers if provided
    if extra_headers:
        headers.update(extra_headers)

    session = requests.Session()
    session.cookies.update(cookies)
    session.headers.update(headers)

    logging.info("✅ Instagram session created successfully.")
    return session


def like_post(session: requests.Session, media_id: str):
    """
    Sends a POST request to like an Instagram post.

    Parameters:
        session (requests.Session): The active session with Instagram authentication.
        media_id (str): The media ID of the Instagram post to like.

    Returns:
        tuple: (success (bool), message (str) or status_code (int))
    """
    if session is None:
        logging.error("❌ Session is not initialized. Cannot like post.")
        return (False, "Session is None")

    post_url = f"https://www.instagram.com/api/v1/web/likes/{media_id}/like/"

    try:
        response = session.post(post_url)

        # Handle rate limiting
        if response.status_code == 429:
            logging.warning("⚠️ Instagram is rate-limiting requests. Try again later.")
            return (False, "Rate limited by Instagram")

        # Handle authentication issues
        if response.status_code == 403:
            logging.error("❌ Authentication error (403 Forbidden). Check if sessionid is expired.")
            return (False, "Authentication error")

        # Handle unexpected errors
        if response.status_code >= 400:
            logging.error(f"❌ Request failed. Status Code: {response.status_code}")
            return (False, response.status_code)

        # Ensure response is in JSON format
        try:
            response_json = response.json()
        except requests.exceptions.JSONDecodeError:
            logging.error("❌ Instagram returned a non-JSON response. Likely an error page.")
            return (False, "Invalid response format")

        # Check if Instagram confirmed the like
        if response_json.get("status") == "ok":
            logging.info(f"✅ Post {media_id} liked successfully.")
            save_cookies_to_file(session)
            return (True, response.status_code)
        else:
            logging.warning(f"⚠️ Instagram responded with an unexpected message: {response_json}")
            return (False, response_json)

    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Network error: {e}")
        return (False, str(e))


def fetch_post_html(post_url: str, cookies_file="cookies.json", output_file="post.html"):
    """
    Fetches the fully rendered HTML content of an Instagram post using Selenium with authentication cookies
    and saves it to a file.

    Parameters:
        post_url (str): The URL of the Instagram post.
        cookies_file (str): The filename where Instagram cookies are stored.
        output_file (str): The filename to save the HTML content.

    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    logging.info(f"🔄 Fetching Instagram post: {post_url}")

    # Load cookies from JSON file
    try:
        with open(cookies_file, "r", encoding="utf-8") as infile:
            cookies = json.load(infile)
    except FileNotFoundError:
        logging.error(f"❌ Cookie file '{cookies_file}' not found.")
        return False
    except json.JSONDecodeError:
        logging.error(f"❌ Failed to parse '{cookies_file}', invalid JSON format.")
        return False

    # Configure Selenium to run headless (no visible browser window)
    options = Options()
    options.add_argument("--headless")  # Run without GUI
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("start-maximized")
    options.add_argument("disable-infobars")
    options.add_argument("--disable-blink-features=AutomationControlled")  # Prevent bot detection

    # Start Selenium WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # Open Instagram homepage first to set cookies
        driver.get("https://www.instagram.com/")

        # Inject cookies into the browser
        for cookie in cookies:
            driver.add_cookie({"name": cookie["name"], "value": cookie["value"], "domain": ".instagram.com"})

        logging.info("✅ Cookies loaded successfully.")

        # Open the Instagram post URL (after setting cookies)
        driver.get(post_url)

        # Wait for JavaScript to load completely
        time.sleep(5)  # Increase if needed for slow networks

        # Get the fully rendered HTML source
        page_source = driver.page_source

        # Save the HTML content to a file
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(page_source)

        logging.info(f"✅ Post HTML saved to {output_file}")
        return True

    except Exception as e:
        logging.error(f"❌ Error while fetching post HTML: {e}")
        return False

    finally:
        driver.quit()  # Close the browser

# def main():
#     """Main function to create a session and like a post."""
#     cookies = extract_cookies(file_path="cookies.json")
#     session = create_instagram_session(cookies)

#     if session:
#         media_id = "3556140434868244822"  # Example media ID, can be changed
#         success, response = like_post(session, media_id)

#         if success:
#             logging.info(f"🎉 Successfully liked post {media_id}")
#         else:
#             logging.error(f"❌ Failed to like post {media_id}. Reason: {response}")


def main():
    """Main function to fetch an Instagram post HTML using Selenium with authentication cookies."""
    post_url = "https://www.instagram.com/p/DE9kM94u6Lq/"  # Replace with any post URL
    success = fetch_post_html(post_url, cookies_file="cookies.json")

    if success:
        logging.info(f"🎉 Successfully saved HTML for {post_url}")
    else:
        logging.error(f"❌ Failed to fetch and save HTML for {post_url}")

if __name__ == "__main__":
    main()
