""" 
Scaffolding. delete all of this code later.
"""
import datetime
import uuid

from pydantic import BaseModel


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: uuid.UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime
    active: bool
    is_superuser: bool

    class Config:
        orm_mode = True


class CloneBase(BaseModel):
    clone_id: str
    min_training_audio: float
    audio_bucket: str
    user_id: uuid.UUID


class CloneCreate(CloneBase):
    pass


class Clone(CloneBase):
    created_at: datetime.datetime
    updated_at: datetime.datetime
    active: bool

    class Config:
        orm_mode = True


class ConversationBase(BaseModel):
    conversation_id: str
    user_id: uuid.UUID
    clone_id: str
    start_time: datetime.datetime
    end_time: datetime.datetime


class ConversationCreate(ConversationBase):
    pass


class Conversation(ConversationBase):
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        orm_mode = True


class MessageBase(BaseModel):
    message_id: str
    content: str
    clone_id: str
    user_id: uuid.UUID


class MessageCreate(MessageBase):
    pass


class Message(MessageBase):
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        orm_mode = True


class DocumentCollectionBase(BaseModel):
    document_collection_id: str
    name: str
    user_id: uuid.UUID
    clone_id: str
    vector_db: str  # vector DB (pgvector, faiss, etc)


class DocumentCollectionBCreate(DocumentCollectionBase):
    pass


class DocumentCollection(DocumentCollectionBase):
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        orm_mode = True


class DocumentBase(BaseModel):
    document_id: str  # same as vector DB id
    url: str
    document_metadata: str


class DocumentCreate(DocumentBase):
    pass


class Document(DocumentBase):
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        orm_mode = True
