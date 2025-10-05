from datetime import datetime
from pydantic import BaseModel


class UserProfile(BaseModel):
    user_id: int
    user_name: str
    user_phone: str
    user_address: str