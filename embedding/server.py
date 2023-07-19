import asyncio
import logging

import grpc
from loguru import logger
from embedding.pb import embed_pb2
from embedding.pb import embed_pb2_grpc

from embedding.encoder import EmbeddingModel, CrossEncoder
from embedding.shared import PORT


class EmbedServicer(embed_pb2_grpc.EmbedServicer):
    """Provides methods that implement functionality of route guide server."""

    def __init__(self) -> None:
        self.encoder = EmbeddingModel.default()
        self.cross_encoder = CrossEncoder.default()

    async def EncodeQueries(
        self, request: embed_pb2.EncodeQueryRequest, unused_context
    ) -> embed_pb2.EmbeddingResponse:
        logger.info("Received EncodeQueries request")
        encodings = self.encoder.encode_query(request.text)
        embeddings = [embed_pb2.Embedding(embedding=x) for x in encodings]
        return embed_pb2.EmbeddingResponse(embeddings=embeddings)

    async def EncodePassages(
        self, request: embed_pb2.EncodePassageRequest, unused_context
    ) -> embed_pb2.EmbeddingResponse:
        logger.info("Received EncodePassages request")
        encodings = self.encoder.encode_passage(request.text)
        embeddings = [embed_pb2.Embedding(embedding=x) for x in encodings]
        return embed_pb2.EmbeddingResponse(embeddings=embeddings)

    async def GetRankingScores(
        self, request: embed_pb2.RankingScoreRequest, unused_context
    ) -> embed_pb2.RankingScoreResponse:
        logger.info("Received GetRankingScores request")
        scores = self.cross_encoder.similarity_score(
            query=request.query, passages=[p for p in request.passages]
        )
        return embed_pb2.RankingScoreResponse(scores=scores)


async def serve() -> None:
    server = grpc.aio.server()
    embed_pb2_grpc.add_EmbedServicer_to_server(EmbedServicer(), server)
    server.add_insecure_port(f"[::]:{PORT}")
    logger.info(f"Starting server on port: {PORT}")
    await server.start()
    await server.wait_for_termination()
    logger.info("Server shutting down.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.get_event_loop().run_until_complete(serve())
