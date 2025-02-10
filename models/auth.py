from pydantic import BaseModel, Field

class LoginRequest(BaseModel):
    """
    Pydantic model for validating Instagram login request input.
    """
    username: str = Field(..., min_length=1, description="Instagram username")
    password: str = Field(..., min_length=6, description="Instagram password")
