from pydantic import BaseModel, Field
from typing import List, Optional

class TargetUser(BaseModel):
    """
    Pydantic model for validating Instagram target user before storing them in MongoDB.
    """
    username: str = Field(..., description="Instagram username")
    user_pk: str = Field(..., description="Instagram numeric user ID")
    full_name: Optional[str] = Field(None, description="Full name of the user")
    is_private: bool = Field(..., description="Whether the account is private or not")
    profile_pic_id: str = Field(..., description="Profile picture ID")
    profile_pic_url: str = Field(..., description="Profile picture URL")
    user_pk: Optional[str] = Field(None, description="Instagram numeric user ID")
    likers: List[str] = Field([], description="List of MongoDB _id references to likers")