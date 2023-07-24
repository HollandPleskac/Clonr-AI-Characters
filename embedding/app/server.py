import os
import asyncio
import logging

import grpc
from grpc_reflection.v1alpha import reflection
from loguru import logger
from app.pb import embed_pb2
from app.pb import embed_pb2_grpc

from app.encoder import EmbeddingModel, CrossEncoder
from app.interceptors import ExceptionInterceptor, UDSOpenTelemetryAioServerInterceptor


HOST = os.environ.get("EMBEDDINGS_GRPC_HOST", "localhost")
PORT = os.environ.get("EMBEDDINGS_GRPC_PORT", 50051)


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

    async def IsNormalized(self, *args, **kwargs) -> embed_pb2.IsNormalizedResponse:
        logger.info("Received IsNormalized request")
        return embed_pb2.IsNormalized(is_normalized=self.encoder.normalized)

    async def GetEncoderName(self, *args, **kwargs) -> embed_pb2.EncoderNameResponse:
        return embed_pb2.EncoderNameResponse(name=self.encoder.name)


async def serve(port: int = 50051) -> None:
    server = grpc.aio.server()
    # unix_socket_template = "unix://{}-{}"
    # local_url = unix_socket_template.format(uds_path, 0)
    local_url = f"[::]:{port}"
    # local_url = f"unix://{uds_path}"

    server = grpc.aio.server(
        interceptors=[
            ExceptionInterceptor(),
            UDSOpenTelemetryAioServerInterceptor(),
        ]
    )
    embed_pb2_grpc.add_EmbedServicer_to_server(EmbedServicer(), server)

    SERVICE_NAMES = (
        embed_pb2.DESCRIPTOR.services_by_name["Embed"].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)
    server.add_insecure_port(local_url)

    await server.start()

    logger.info("Server started at {}".format(local_url))

    try:
        await server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Signal received. Shutting down.")
        await server.stop(0)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(serve())
