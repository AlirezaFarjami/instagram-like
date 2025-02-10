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
        """
        cookie_dict = {cookie["name"]: cookie["value"] for cookie in cookies_list}
        return cls(**cookie_dict)
