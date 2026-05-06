from pydantic import BaseModel
from typing import Optional, List

class Message(BaseModel):
    role: str          # "user" | "assistant"
    content: str


class SendMessageRequest(BaseModel):
    conv_id: str
    message: str
    model: Optional[str] = None
    override_messages: Optional[List[Message]] = None


class CreateConvRequest(BaseModel):
    title: Optional[str] = "New Chat"


class RenameConvRequest(BaseModel):
    title: str


class UpdateAvatarRequest(BaseModel):
    color: str


class UpdateConfigRequest(BaseModel):
    provider: Optional[str] = None
    model: Optional[str]    = None
    base_url: Optional[str] = None
    api_key: Optional[str]  = None

from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    username: str = Field(..., min_length=5, max_length=20, pattern="^[a-zA-Z0-9_]+$")
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    username: str
    password: str
