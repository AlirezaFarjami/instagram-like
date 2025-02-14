from pydantic import BaseModel, Field
from typing import Optional

class Liker(BaseModel):
    """
    Pydantic model for validating Instagram likers before storing them in MongoDB.
    """
    username: str = Field(..., min_length=3, description="Instagram username")
    user_id: str = Field(..., min_length=5, description="Instagram numeric user ID")
    full_name: Optional[str] = Field(None, description="Full name of the user")
    is_private: bool = Field(..., description="Whether the account is private or not")
    profile_pic_url: Optional[str] = Field(None, description="Profile picture URL")
