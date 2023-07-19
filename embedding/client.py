import asyncio
import logging
import random
from typing import Iterable, List

import grpc
from embedding.app.pb import embed_pb2
from embedding.app.pb import embed_pb2_grpc


PORT = 50051


class Client:
    def __init__(self, port: int = PORT, host: str = "localhost"):
        self.port = port
        self.addr = f"{host}:{port}"
        self.channel = grpc.aio.insecure_channel(self.addr)
        self.stub = embed_pb2_grpc.EmbedStub(self.channel)

    def __del__(self, *args, **kwargs):
        self.channel.close()

    async def encode_query(self, text: list[str]) -> list[list[float]]:
        request = embed_pb2.EncodeQueryRequest(text=text)
        r = await self.stub.EncodeQueries(request=request)
        embedding = [[y for y in x.embedding] for x in r.embeddings]
        return embedding

    async def encode_passage(self, text: list[str]) -> list[list[float]]:
        request = embed_pb2.EncodePassageRequest(text=text)
        r = await self.stub.EncodeQueries(request=request)
        embedding = [[y for y in x.embedding] for x in r.embeddings]
        return embedding

    async def rerank_score(self, query: str, passages: list[str]) -> list[float]:
        request = embed_pb2.RankingScoreRequest(query=query, passages=passages)
        r = await self.stub.GetRankingScores(request=request)
        return [x for x in r.scores]
