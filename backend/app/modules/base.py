from abc import ABC, abstractmethod
from app.settings import settings
from sqlalchemy import Column, Integer, String, sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from app.models import Base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from app.db import wait_for_db, get_async_session
from clonr.embeddings import VectorEncoder, ReRanker


class Module(ABC):
    def __init__(self):
        self.session = None
        self.encoder = VectorEncoder.from_pretrained()
        self.ranker = ReRanker.from_pretrained()

    async def connect(self):
        await wait_for_db()
        async for session in get_async_session():
            self.session = session

    @abstractmethod
    def add(self, **kwargs):
        pass

    @abstractmethod
    def get(self, **kwargs):
        pass
