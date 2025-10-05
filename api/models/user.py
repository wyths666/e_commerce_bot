from datetime import datetime
from pydantic import BaseModel


class UserProfile(BaseModel):
    user_id: int
    user_name: str
    user_phone: str
    user_address: str

class ResponseBase(BaseModel):
    success: bool
    message: str = ""

class SendMessageRequest(BaseModel):
    text: str

class SendMessageResponse(ResponseBase):
    user: int | None = None

class SendToUserRequest(BaseModel):
    user_id: int
    text: str