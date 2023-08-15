import time

from fastapi import FastAPI
from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Match
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from starlette.types import ASGIApp

from app.settings import settings

# Default value is http://localhost:4317, and described here:
# https://opentelemetry.io/docs/concepts/sdk-configuration/otlp-exporter-configuration/
# and it creates routes at /v1/metrics, /v1/traces. /v1/logs


meter = metrics.get_meter(__name__)

info_meter = meter.create_up_down_counter(
    name="fastapi_app_info", description="FastAPI application information."
)
req_meter = meter.create_counter(
    name="fastapi_requests_total",
    description="Total count of requests by method and path.",
    unit="responses",
)
resp_meter = meter.create_counter(
    name="fastapi_responses_total",
    description="Total count of responses by method, path and status codes.",
)
req_processing_time_meter = meter.create_histogram(
    name="fastapi_requests_duration_seconds",
    description="Histogram of requests processing time by path (in seconds)",
    unit="s",
)
exc_meter = meter.create_counter(
    name="fastapi_exceptions_total",
    description="Total count of exceptions raised by path and exception type",
)
reqs_in_progress_meter = meter.create_up_down_counter(
    name="fastapi_requests_in_progress",
    description="Gauge of requests by method and path currently being processed",
)


app = FastAPI()


def get_path(request: Request) -> tuple[str, bool]:
    for route in request.app.routes:
        match, _ = route.matches(request.scope)
        if match == Match.FULL:
            return route.path, True
    return request.url.path, False


# Adapted from: https://github.com/blueswen/fastapi-observability/blob/main/fastapi_app/utils.py
class PrometheusMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, app_name: str = "fastapi-app") -> None:
        super().__init__(app)
        self.app_name = app_name
        info_meter.add(1, attributes=dict(app_name=app_name))

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        method = request.method
        path, is_handled_path = get_path(request)

        if not is_handled_path:
            return await call_next(request)

        reqs_in_progress_meter.add(
            amount=1, attributes=dict(method=method, path=path, app_name=self.app_name)
        )
        req_meter.add(
            amount=1, attributes=dict(method=method, path=path, app_name=self.app_name)
        )

        before_time = time.perf_counter()
        try:
            response = await call_next(request)
        except BaseException as e:
            status_code = HTTP_500_INTERNAL_SERVER_ERROR
            exception_type = type(e).__name__
            exc_meter.add(
                amount=1,
                attributes=dict(
                    method=method,
                    path=path,
                    exception_type=exception_type,
                    app_name=self.app_name,
                ),
            )
            raise e from None
        else:
            status_code = response.status_code
            after_time = time.perf_counter()
            span = trace.get_current_span()  # retrieve trace id for exemplar
            trace_id = trace.format_trace_id(span.get_span_context().trace_id)

            duration = after_time - before_time
            req_processing_time_meter.record(
                amount=duration,
                attributes=dict(
                    method=method,
                    path=path,
                    app_name=self.app_name,
                    TraceID=trace_id,  # removed an exemplar, whatever tf that is
                ),
            )
        finally:
            resp_meter.add(
                amount=1,
                attributes=dict(
                    method=method,
                    path=path,
                    status_code=status_code,
                    app_name=self.app_name,
                ),
            )
            reqs_in_progress_meter.add(
                amount=-1,
                attributes=dict(method=method, path=path, app_name=self.app_name),
            )

        return response


def setup_tracing(
    app: FastAPI,
    endpoint: str | None = settings.OTEL_EXPORTER_OTLP_ENDPOINT,
    service_name: str = "clonr-server",
):
    # Service name is required for most backends
    resource = Resource(attributes={SERVICE_NAME: service_name})

    provider = TracerProvider(resource=resource)
    processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint, insecure=True))
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)

    reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(endpoint=endpoint, insecure=True)
    )
    provider = MeterProvider(resource=resource, metric_readers=[reader])
    metrics.set_meter_provider(provider)

    app.add_middleware(PrometheusMiddleware, app_name=service_name)
    LoggingInstrumentor().instrument()
    FastAPIInstrumentor.instrument_app(app)
