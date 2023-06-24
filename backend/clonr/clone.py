from pydantic import BaseModel
from typing import List, Optional
from clonr.llms import LLM
from clonr.templates import (
    BasicChat,
    Summarize,
    SummarizeWithContext,
    Memory,
    ReflectionRetrieval,
    ReflectionGeneration,
)
from backend.data.core import Document
from clonr.embedding.encoder import EmbeddingModel
from clonr.embedding.types import ModelEnum
from datetime import datetime


def document_to_texts(documents):
    texts = ""
    for i, document in enumerate(documents):
        if i == 0:
            texts += "- " + document.content
        else:
            texts += "\n- " + document.content
    return texts


class Retriever(BaseModel):
    memory_stream: List[Document]
    vectordb: None

    def get_relevant_documents(self, query: str):
        # TODO: run similarity query on vector db
        # TODO: weighting logic
        return

    def add_document(self, document: Document, **kwargs):
        if "created_at" not in document.metadata:
            document.metadata["created_at"] = datetime.now()
        self.memory_stream.append(document)
        ## TODO: add documents to vector db
        return


class Clone(BaseModel):
    llm: LLM
    embedding_model: EmbeddingModel
    retriever: Retriever
    conversation_list: List[str]

    def get_example_dialogues(self):
        # TODO
        return

    def add_to_conversation_list(self, message: str):
        self.conversation_list.append(message)
        return

    def get_current_conversation(self):
        return "\n".join(self.conversation_list)

    def get_summary(self, passage: str):
        summarize = Summarize()
        return summarize.render(llm=self.llm)

    def create_memory(self, observation: str):
        memory = Memory()
        score = memory.render(self.llm, memory=observation)
        document = Document(
            content=observation,
            content_embedding=self.embedding_model.encode(observation),
            metadata={"score": score, "created_at": datetime.now()},
        )
        self.retriever.add_document(document)
        return

    def get_reflection_queries(self, k: int):
        recent_k = self.retriever.memory_stream[-k:]
        recent_memories = document_to_texts(recent_k)
        reflection_retrieval = ReflectionRetrieval()
        return reflection_retrieval.render(
            llm=self.llm, recent_memories=recent_memories
        )

    def generate_reflection(self):
        questions = self.get_reflection_queries(k=5)
        total_relevant_memories = []
        for question in questions:
            relevant_memories = self.retriever.get_relevant_documents(question)
            total_relevant_memories.append(relevant_memories)

        total_relevant_memories_text = document_to_texts(total_relevant_memories)
        reflection_generation = ReflectionGeneration()
        reflections = reflection_generation.render(
            llm=self.llm, relevant_memories=total_relevant_memories_text
        )
        for reflection in reflections:
            self.create_memory(reflection)
        return
