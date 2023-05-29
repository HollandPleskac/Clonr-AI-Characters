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


class APIKeyBase(BaseModel):
    key: str
    is_active: bool
    user_id: uuid.UUID
    clone_id: uuid.UUID


class APIKeyCreate(APIKeyBase):
    pass


class APIKey(CommonMixin, APIKeyBase):
    class Config:
        orm_mode = True


class CloneBase(BaseModel):
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


# class CloneBase(BaseModel):
#     train_audio_minutes: float
#     audio_bucket: str
#     user_id: uuid.UUID


# class CloneCreate(CloneBase):
#     pass


# class Clone(CommonMixin, CloneBase):
#     active: bool

#     class Config:
#         orm_mode = True


# class ConversationBase(BaseModel):
#     user_id: uuid.UUID
#     clone_id: uuid.UUID


# class ConversationCreate(ConversationBase):
#     pass


# class MessageBase(BaseModel):
#     content: str
#     clone_id: uuid.UUID
#     user_id: uuid.UUID
#     conversation_id: uuid.UUID


# class MessageCreate(MessageBase):
#     pass


# class Message(CommonMixin, MessageBase):
#     class Config:
#         orm_mode = True


# class Conversation(CommonMixin, ConversationBase):
#     messages: Optional[list[Message]] = None

#     class Config:
#         orm_mode = True


# class DocumentCollectionBase(BaseModel):
#     name: str
#     user_id: uuid.UUID
#     clone_id: str
#     vector_db: str  # vector DB (pgvector, faiss, etc)


# class DocumentCollectionCreate(DocumentCollectionBase):
#     pass


# class DocumentBase(BaseModel):
#     document_id: str  # same as vector DB id
#     url: str
#     document_metadata: str


# class DocumentCreate(DocumentBase):
#     pass


# class Document(CommonMixin, DocumentBase):
#     class Config:
#         orm_mode = True


# class DocumentCollection(CommonMixin, DocumentCollectionBase):
#     documents: Optional[list[Document]] = None

#     class Config:
#         orm_mode = True
