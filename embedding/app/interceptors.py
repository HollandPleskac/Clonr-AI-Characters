import grpc

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.grpc._aio_server import (
    OpenTelemetryAioServerInterceptor,
)
from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
)
from google.rpc import status_pb2, code_pb2
from grpc_status import rpc_status
from grpc_interceptor.server import AsyncServerInterceptor
from loguru import logger
from typing import Callable, Any


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


class UDSOpenTelemetryAioServerInterceptor(OpenTelemetryAioServerInterceptor):
    def __init__(self):
        super().__init__(trace.get_tracer(__name__))

    def _start_span(self, handler_call_details, context, set_status_on_exception=False):
        """
        Rewrite _start_span method to support Unix Domain Socket gRPC contexts
        """

        # standard attributes
        attributes = {
            SpanAttributes.RPC_SYSTEM: "grpc",
            SpanAttributes.RPC_GRPC_STATUS_CODE: grpc.StatusCode.OK.value[0],
        }

        # if we have details about the call, split into service and method
        if handler_call_details.method:
            service, method = handler_call_details.method.lstrip("/").split("/", 1)
            attributes.update(
                {
                    SpanAttributes.RPC_METHOD: method,
                    SpanAttributes.RPC_SERVICE: service,
                }
            )

        # add some attributes from the metadata
        metadata = dict(context.invocation_metadata())
        if "user-agent" in metadata:
            attributes["rpc.user_agent"] = metadata["user-agent"]

        # We use gRPC over a UNIX socket
        # FixMe (Jonny): we're not using unix, couldn't figure it out
        # This needs to be simplified and tested. Check out here:
        # https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/grpc/grpc.html
        attributes.update({SpanAttributes.NET_TRANSPORT: "unix"})

        return self._tracer.start_as_current_span(
            name=handler_call_details.method,
            kind=trace.SpanKind.SERVER,
            attributes=attributes,
            set_status_on_exception=set_status_on_exception,
        )


def setup_tracing(otlp_endpoint: str, shard: int = 0):
    resource = Resource.create(attributes={"service.name": f"embedding.server-{shard}"})
    span_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
    span_processor = BatchSpanProcessor(span_exporter)

    trace.set_tracer_provider(TracerProvider(resource=resource))
    trace.get_tracer_provider().add_span_processor(span_processor)
