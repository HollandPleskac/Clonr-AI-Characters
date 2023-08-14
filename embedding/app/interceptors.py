from typing import Any, Callable

import grpc
from google.rpc import code_pb2, status_pb2
from grpc_interceptor.server import AsyncServerInterceptor
from grpc_status import rpc_status
from loguru import logger
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


class ExceptionInterceptor(AsyncServerInterceptor):
    async def intercept(
        self,
        method: Callable,
        request_or_iterator: Any,
        context: grpc.ServicerContext,
        method_name: str,
    ) -> Any:
        try:
            response = method(request_or_iterator, context)
            return await response
        except Exception as err:
            method_name = method_name.split("/")[-1]
            logger.exception(f"Method {method_name} encountered an error.")

            await context.abort_with_status(
                rpc_status.to_status(
                    status_pb2.Status(code=code_pb2.INTERNAL, message=str(err))
                )
            )


def setup_tracing(otlp_endpoint: str | None = None):
    resource = Resource.create(attributes={"service.name": "embedding.server"})
    span_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
    span_processor = BatchSpanProcessor(span_exporter)

    trace.set_tracer_provider(TracerProvider(resource=resource))
    trace.get_tracer_provider().add_span_processor(span_processor)
