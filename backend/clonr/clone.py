from pydantic import BaseModel
from typing import List, Optional
from clonr.llms import LLM
from clonr.templates.summarize import Summarize, SummarizeWithContext
from clonr.templates.memory import (
    MemoryRating,
    ReflectionRetrieval,
    ReflectionGeneration,
)

from backend.data.core import Document
from clonr.embedding.encoder import EmbeddingModel
from clonr.embedding.types import ModelEnum
from datetime import datetime
from sqlalchemy.orm import Session
from backend.app.models import Clone, Memory, Conversation, Message, ExampleDialogue
from backend.app.models import Document as DBDocument


def document_to_texts(documents):
    texts = ""
    for i, document in enumerate(documents):
        if i == 0:
            texts += "- " + document.content
        else:
            texts += "\n- " + document.content
    return texts


class AuthenticatedDB:
    def __init__(
        self,
        session: Session,
        clone_id: str,
        api_key: str,
        user_id: str,
        conversation_id: str,
    ):
        self.session = session
        self.clone_id = clone_id
        self.api_key = api_key
        self.user_id = user_id
        self.conversation_id = conversation_id

    def get_clone(self):
        return self.session.query(Clone).filter(Clone.id == self.clone_id).first()


# class Retriever(BaseModel):
#     memory_stream: List[Document]
#     vectordb: None

#     def get_relevant_documents(self, query: str):
#         # TODO: run similarity query on vector db
#         # TODO: weighting logic
#         return

#     def add_document(self, document: Document, **kwargs):
#         if "created_at" not in document.metadata:
#             document.metadata["created_at"] = datetime.now()
#         self.memory_stream.append(document)
#         ## TODO: add documents to vector db
#         return


class PersonalClone(BaseModel):
    def __init__(self, db: AuthenticatedDB, llm: LLM, embedding_model: EmbeddingModel):
        self.db = db
        self.llm = llm
        self.embedding_model = embedding_model
        self.conversation_list = []

    def get_summary(self, passage: str):
        summarize = Summarize()
        return summarize.render(llm=self.llm, passage=passage)

    def get_description(self):
        return self.db.get_clone().description

    def get_motivation(self):
        return self.db.get_clone().motivation

    def get_example_dialogues(self):
        return (
            self.db.session.query(ExampleDialogue)
            .filter_by(clone_id=self.db.clone_id)
            .all()
        )

    def add_to_conversation_list(self, message: str):
        self.conversation_list.append(message)
        # add message to Conversation table
        conversation_id = self.db.conversation_id
        conversation = self.db.session.query(Conversation).filter_by(id=conversation_id)
        conversation.messages.append(
            Message(
                content=message,
                sender_name=self.db.user_id,
                from_clone=False,
                conversation_id=conversation_id,
            )
        )
        self.db.session.commit()
        return

    def get_current_conversation(self):
        return "\n".join(self.conversation_list)

    def get_summary(self, passage: str):
        summarize = Summarize()
        return summarize.render(llm=self.llm, passage=passage)

    def get_memories(self):
        return self.db.session.query(Memory).filter_by(clone_id=self.db.clone_id).all()

    def get_latest_memories(self, k: int):
        return (
            self.db.session.query(Memory)
            .filter_by(clone_id=self.db.clone_id)
            .order_by(Memory.timestamp.desc())
            .limit(k)
            .all()
        )

    def create_memory(self, observation: str):
        memory_rating = MemoryRating()
        importance = memory_rating.render(self.llm, memory=observation)
        summary = self.get_summary(observation)
        content_embedding = self.embedding_model.encode(observation)
        summary_embedding = self.embedding_model.encode(summary)
        memory = Memory(
            content=observation,
            content_embedding=content_embedding,
            timestamp=datetime.now(),
            last_accessed_at=datetime.now(),
            importance=importance,
            is_shared=False,
            conversation_id=self.db.conversation_id,
        )
        document = DBDocument(
            content=observation,
            content_embedding=content_embedding,
            num_tokens=len(observation.split()),
            summary=self.get_summary(observation),
            summary_embedding=summary_embedding,
        )

        self.db.session.add(memory)
        self.db.session.add(document)
        self.db.session.commit()

        # self.retriever.add_document(document)
        return

    def get_reflection_queries(self, k: int):
        recent_k = self.get_latest_memories(k)
        recent_memories = [memory.content for memory in recent_k]
        reflection_retrieval = ReflectionRetrieval()
        return reflection_retrieval.render(
            llm=self.llm, recent_memories=recent_memories
        )

    def get_relevant_memories(self, query: str, k: int):
        query_embedding = self.embedding_model.encode(query)
        query = f"""
        SELECT * FROM memories 
        ORDER BY embedding <-> '{query_embedding}'
        LIMIT {k}
        """
        relevant_memories = self.db.session.execute(query).fetchall()
        print("this is get_relevant_memories: ", relevant_memories)
        return relevant_memories

    def generate_reflection(self):
        questions = self.get_reflection_queries(k=5)
        total_relevant_memories = []
        for question in questions:
            relevant_memories = self.get_relevant_memories(query=question, k=5)
            total_relevant_memories.append(relevant_memories)

        total_relevant_memories_text = document_to_texts(total_relevant_memories)
        reflection_generation = ReflectionGeneration()
        reflections = reflection_generation.render(
            llm=self.llm, relevant_memories=total_relevant_memories_text
        )
        for reflection in reflections:
            self.create_memory(reflection)
        return
