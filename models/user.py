from pydantic import BaseModel, Field
from typing import Optional
from models.cookies import InstagramCookies
from models.parameters import InstagramParameters

class UserCredentials(BaseModel):
    """
    Pydantic model for validating Instagram user credentials before storing them in MongoDB.
    """
    username: str = Field(..., min_length=3, description="Instagram username")
    cookies: InstagramCookies
    parameters: Optional[InstagramParameters] = None

    @classmethod
    def from_dict(cls, data: dict):
        """
        Convert a dictionary to a validated UserCredentials instance.
        """
        return cls(
            username=data["username"],
            cookies=InstagramCookies(**data["cookies"])
        )
