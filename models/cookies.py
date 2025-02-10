from pydantic import BaseModel, Field
from typing import Dict

class InstagramCookies(BaseModel):
    """
    Pydantic model for validating Instagram cookies before storing them in MongoDB.
    """
    csrftoken: str = Field(..., min_length=10, description="CSRF token for Instagram session")
    sessionid: str = Field(..., min_length=10, description="Session ID for the authenticated user")
    ds_user_id: str = Field(..., min_length=5, description="Instagram user ID")
    mid: str = Field(..., min_length=5, description="Machine ID")
    ig_did: str = Field(..., min_length=5, description="Device ID")

    @classmethod
    def from_list(cls, cookies_list: list):
        """
        Convert a list of cookies into a dictionary and validate it.
        Handles missing cookies by setting them to an empty string.
        """
        required_keys = {"csrftoken", "sessionid", "ds_user_id", "mid", "ig_did"}
        cookie_dict = {cookie["name"]: cookie["value"] for cookie in cookies_list}

        # Ensure all required keys are present, fill missing ones with empty string
        complete_data = {key: cookie_dict.get(key, "") for key in required_keys}

        return cls(**complete_data)

