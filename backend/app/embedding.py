import logging

import grpc
from loguru import logger
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_exponential

from app.settings import settings
from pb import embed_pb2, embed_pb2_grpc


class EmbeddingClient:
    def __init__(
        self,
        port: int = settings.EMBEDDINGS_GRPC_PORT,
        host: str = settings.EMBEDDINGS_GRPC_HOST,
    ):
        self.port = port
        self.host = host
        self.addr = f"{host}:{port}"

    async def __aenter__(self):
        self.channel = grpc.aio.insecure_channel(self.addr)
        self.stub = embed_pb2_grpc.EmbedStub(self.channel)
        return self

    async def __aexit__(self, *args, **kwargs):
        await self.channel.close()

    async def encode_query(self, text: str | list[str]) -> list[list[float]]:
        if isinstance(text, str):
            text = [text]
        request = embed_pb2.EncodeQueryRequest(text=text)
        r = await self.stub.EncodeQueries(request=request)
        embedding = [[y for y in x.embedding] for x in r.embeddings]
        return embedding

    async def encode_passage(self, text: str | list[str]) -> list[list[float]]:
        if isinstance(text, str):
            text = [text]
        request = embed_pb2.EncodePassageRequest(text=text)
        r = await self.stub.EncodePassages(request=request)
        embedding = [[y for y in x.embedding] for x in r.embeddings]
        return embedding

    async def rerank_score(self, query: str, passages: list[str]) -> list[float]:
        request = embed_pb2.RankingScoreRequest(query=query, passages=passages)
        r = await self.stub.GetRankingScores(request=request)
        return [x for x in r.scores]

    async def is_normalized(self) -> bool:
        request = embed_pb2.Empty()
        response = await self.stub.IsNormalized(request=request)
        return response.is_normalized

    async def encoder_name(self) -> str:
        request = embed_pb2.Empty()
        response = await self.stub.GetEncoderName(request=request)
        return response.name


@retry(
    stop=stop_after_attempt(8),
    wait=wait_exponential(multiplier=1, min=1, max=2),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
async def wait_for_embedding():
    async with EmbeddingClient() as client:
        logger.info(f"Attempting to connect to gRPC server at addr: {client.addr}")
        return await client.encoder_name()
