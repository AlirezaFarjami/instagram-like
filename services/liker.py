from pydantic import BaseModel, HttpUrl
from datetime import datetime

class Liker(BaseModel):
    username: str
    user_id: int
    creation_date: datetime
    is_private: bool
    profile_picture_url: HttpUrl
