import datetime
import uuid
from typing import Optional

from fastapi_users.schemas import BaseUser, BaseUserCreate, BaseUserUpdate
from pydantic import BaseModel


class UserRead(BaseUser[uuid.UUID]):
    pass


class UserCreate(BaseUserCreate):
    pass


class UserUpdate(BaseUserUpdate):
    pass


class CommonMixin(BaseModel):
    id: uuid.UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime


class CloneCreate(BaseModel):
    name: str
    greeting_message: str
    is_active: bool = True
    is_public: bool = False


class CloneUpdate(CloneCreate):
    pass


class Clone(CommonMixin, CloneCreate):
    user_id: uuid.UUID

    class Config:
        orm_mode = True


class APIKeyCreate(BaseModel):
    clone_id: uuid.UUID
    name: Optional[str] = None
    user_id: Optional[uuid.UUID] = None


class APIKey(CommonMixin, APIKeyCreate):
    name: str

    class Config:
        orm_mode = True


class APIKeyOnce(APIKey):
    key: str


class MessageCreate(BaseModel):
    content: str
    sender_name: str


class Message(CommonMixin, MessageCreate):
    from_clone: bool
    conversation_id: uuid.UUID

    class Config:
        orm_mode = True


class ConversationCreate(BaseModel):
    clone_id: uuid.UUID
    name: Optional[str] = None


class Conversation(CommonMixin, ConversationCreate):
    ## This raises an error when fastapi tries to convert
    ## sqlalchemy.exc.MissingGreenlet: greenlet_spawn has not been called
    # messages: Optional[list[Message]] = None

    class Config:
        orm_mode = True
