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
    id: uuid.UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime
    active: bool

    class Config:
        orm_mode = True
