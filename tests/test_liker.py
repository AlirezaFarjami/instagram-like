import unittest
import logging
import json
from actions.likers import get_likers_from_post

class TestLikerFunction(unittest.TestCase):
    def setUp(self):
        """ Setup logging before each test """
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    def test_get_likers_from_post(self):
        """ Test fetching likers from a valid Instagram post URL """
        username = input("Enter your Instagram username: ").strip()
        post_url = input("Enter the post URL: ").strip()

        likers = get_likers_from_post(username, post_url, limit=20)

        # Validate response
        self.assertIsInstance(likers, list, "Likers should be a list")
        self.assertTrue(len(likers) > 0, "There should be at least one liker")

        # Check for required fields in the response
        for liker in likers:
            self.assertIn("username", liker, "Each liker must have a username")
            self.assertIn("pk", liker, "Each liker must have a user ID")
            self.assertIn("is_private", liker, "Each liker must have a privacy status")
            self.assertIn("profile_pic_url", liker, "Each liker must have a profile picture URL")

        # Save response to JSON file for review
        with open("test_likers_result.json", "w") as f:
            json.dump(likers, f, indent=4)
        
        logging.info("✅ Test passed! Likers data saved to test_likers_result.json.")

if __name__ == "__main__":
    unittest.main()
