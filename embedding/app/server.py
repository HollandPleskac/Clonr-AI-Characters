import asyncio
import logging
import os
import time

import grpc
from grpc_reflection.v1alpha import reflection
from loguru import logger
from opentelemetry import metrics

from app.encoder import CrossEncoder, EmbeddingModel
from app.pb import embed_pb2, embed_pb2_grpc
from app.tracing import setup_tracing

HOST = os.environ.get("EMBEDDINGS_GRPC_HOST", "localhost")
PORT = os.environ.get("EMBEDDINGS_GRPC_PORT", 50051)
OTLP_ENDPOINT = os.environ.get("OTLP_ENDPOINT")

APP_NAME = "embeddings.server"

meter = metrics.get_meter(APP_NAME)

info_meter = meter.create_up_down_counter(
    name="embedding_app_info", description="FastAPI application information."
)
req_meter = meter.create_counter(
    name="embedding_requests", description="Number of embeddings requests"
)
req_processing_time_meter = meter.create_histogram(
    name="embedding_requests_duration_seconds",
    description="Histogram of requests processing time by path (in seconds)",
    unit="s",
)
reqs_in_progress_meter = meter.create_up_down_counter(
    name="embedding_requests_in_progress",
    description="Gauge of requests by method currently being processed",
)


class EmbedServicer(embed_pb2_grpc.EmbedServicer):
    """Provides methods that implement functionality of route guide server."""

    def __init__(self) -> None:
        self.encoder = EmbeddingModel.default()
        self.cross_encoder = CrossEncoder.default()
        info_meter.add(amount=1, attributes=dict(app_name=APP_NAME))

    async def EncodeQueries(
        self, request: embed_pb2.EncodeQueryRequest, unused_context
    ) -> embed_pb2.EmbeddingResponse:
        bsz = len(request.text) or 1
        chars = sum(len(x) for x in request.text)
        logger.info(f"EncodeQueries request. Batch size: {bsz}. Chars: {chars}")

        st = time.perf_counter()
        attributes: dict[str, str | int] = dict(
            method="EncodeQueries", batch_size=bsz, n_chars=chars, app_name=APP_NAME
        )
        req_meter.add(amount=1, attributes=attributes)
        reqs_in_progress_meter.add(amount=1, attributes=attributes)

        encodings = self.encoder.encode_query([x for x in request.text])
        embeddings = [embed_pb2.Embedding(embedding=x) for x in encodings]
        res = embed_pb2.EmbeddingResponse(embeddings=embeddings)

        duration = time.perf_counter() - st
        req_processing_time_meter.record(amount=duration, attributes=attributes)
        reqs_in_progress_meter.add(amount=-1, attributes=attributes)

        return res

    async def EncodePassages(
        self, request: embed_pb2.EncodePassageRequest, unused_context
    ) -> embed_pb2.EmbeddingResponse:
        bsz = len(request.text)
        chars = sum(len(x) for x in request.text)
        logger.info(f"EncodePassages request. Batch size: {bsz}. Chars: {chars}")

        st = time.perf_counter()
        attributes: dict[str, str | int] = dict(
            method="EncodePassages", batch_size=bsz, n_chars=chars, app_name=APP_NAME
        )
        req_meter.add(amount=1, attributes=attributes)
        reqs_in_progress_meter.add(amount=1, attributes=attributes)

        encodings = self.encoder.encode_passage([x for x in request.text])
        embeddings = [embed_pb2.Embedding(embedding=x) for x in encodings]
        res = embed_pb2.EmbeddingResponse(embeddings=embeddings)

        duration = time.perf_counter() - st
        req_processing_time_meter.record(amount=duration, attributes=attributes)
        reqs_in_progress_meter.add(amount=-1, attributes=attributes)

        return res

    async def GetRankingScores(
        self, request: embed_pb2.RankingScoreRequest, unused_context
    ) -> embed_pb2.RankingScoreResponse:
        bsz = len(request.passages)
        chars = sum(len(x) for x in request.passages)
        logger.info(
            (
                f"GetRankingScores request. Batch size: {bsz}. Query: {request.query}. "
                f"Passage chars: {chars}"
            )
        )

        st = time.perf_counter()
        attributes: dict[str, str | int] = dict(
            method="GetRankingScores", batch_size=bsz, n_chars=chars, app_name=APP_NAME
        )
        req_meter.add(amount=1, attributes=attributes)
        reqs_in_progress_meter.add(amount=1, attributes=attributes)

        scores = self.cross_encoder.similarity_score(
            query=request.query, passages=[p for p in request.passages]
        )
        res = embed_pb2.RankingScoreResponse(scores=scores)

        duration = time.perf_counter() - st
        req_processing_time_meter.record(amount=duration, attributes=attributes)
        reqs_in_progress_meter.add(amount=-1, attributes=attributes)

        return res

    async def IsNormalized(self, *args, **kwargs) -> embed_pb2.IsNormalizedResponse:
        logger.info(f"IsNormalized request. Value: {self.encoder.normalized}")
        return embed_pb2.IsNormalizedResponse(is_normalized=self.encoder.normalized)

    async def GetEncoderName(self, *args, **kwargs) -> embed_pb2.EncoderNameResponse:
        return embed_pb2.EncoderNameResponse(name=self.encoder.name)


async def serve(port: int = 50051) -> None:
    server = grpc.aio.server()
    local_url = f"[::]:{port}"

    server = setup_tracing(server=server, otlp_endpoint=OTLP_ENDPOINT)
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
