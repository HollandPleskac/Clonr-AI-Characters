""" 
Scaffolding. delete all of this code later.
"""
import datetime
import uuid

from pydantic import BaseModel


class User(BaseModel):
    id: uuid.UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime
    email: str
    active: bool
    is_superuser: bool

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    email: str


class ElevenClone(BaseModel):
    id: uuid.UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime
    clone_id: str
    active: bool
    min_training_audio: float
    audio_bucket: str
    user_id: uuid.UUID

    class Config:
        orm_mode = True
