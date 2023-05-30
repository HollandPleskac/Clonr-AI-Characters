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


class CloneBase(BaseModel):
    greeting_message: Optional[str] = None
    is_active: bool = True
    is_public: bool = False
    user_id: Optional[uuid.UUID] = None


class CloneCreate(CloneBase):
    pass


class CloneUpdate(CloneBase):
    pass


class Clone(CommonMixin, CloneBase):
    class Config:
        orm_mode = True


class APIKeyCreate(BaseModel):
    clone_id: uuid.UUID
    name: Optional[str] = None
    user_id: Optional[uuid.UUID] = None


class APIKey(CommonMixin, BaseModel):
    name: str
    user_id: uuid.UUID
    clone_id: uuid.UUID

    class Config:
        orm_mode = True


class APIKeyDB(APIKey):
    key: str


class MessageCreate(BaseModel):
    message: str


class MessageCreateDB(MessageCreate):
    conversation_id: Optional[uuid.UUID]
    user_id: Optional[uuid.UUID] = None
    clone_id: Optional[uuid.UUID] = None


class Message(CommonMixin, MessageCreateDB):
    class Config:
        orm_mode = True


class ConversationCreate(BaseModel):
    user_id: uuid.UUID
    clone_id: uuid.UUID


class Conversation(CommonMixin, ConversationCreate):
    messages: Optional[list[Message]] = None

    class Config:
        orm_mode = True
