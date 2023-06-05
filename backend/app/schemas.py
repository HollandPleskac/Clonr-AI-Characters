import datetime
import uuid
from typing import Optional, List, Dict

from fastapi_users.schemas import BaseUser, BaseUserCreate, BaseUserUpdate
from pydantic import BaseModel, validator
from pgvector.sqlalchemy import Vector


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
    description: str
    motivation: str
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


class DocumentCreate(BaseModel):
    content: str
    content_embedding: List[float]
    num_tokens: int
    summary: str
    summary_embedding: List[float]
    is_shared: bool = True


class DocumentUpdate(DocumentCreate):
    pass


class Document(CommonMixin, DocumentCreate):
    clone_id: uuid.UUID

    class Config:
        orm_mode = True


class ExampleDialogueCreate(BaseModel):
    content: str
    content_embedding: List[float]
    num_tokens: int
    summary: str
    summary_embedding: List[float]
    chunk_index: int
    is_shared: bool = True
    conversation_id: uuid.UUID


class ExampleDialogueUpdate(ExampleDialogueCreate):
    pass


class ExampleDialogue(ExampleDialogueCreate):
    class Config:
        orm_mode = True


class MemoryCreate(BaseModel):
    content: str
    content_embedding: List[float]
    timestamp: datetime.datetime = datetime.datetime.utcnow()
    last_accessed_at: datetime.datetime = datetime.datetime.utcnow()
    importance: float = 0.0
    is_shared: bool = False
    conversation_id: uuid.UUID


class MemoryUpdate(BaseModel):
    content: str
    content_embedding: List[float]
    last_accessed_at: datetime.datetime
    importance: float
    is_shared: bool


class Memory(CommonMixin, MemoryCreate):
    class Config:
        orm_mode = True
