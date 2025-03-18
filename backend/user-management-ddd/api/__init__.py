from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import \
    OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from starlette.datastructures import MutableHeaders

from .routers.register_routes import register_routers

origins = [
    "http://localhost",
    "http://localhost:8080",
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        yield
    finally:
        print("Done")


def initialize_open_telemetry(app: FastAPI) -> None:
    # Initialize OpenTelemetry
    trace.set_tracer_provider(TracerProvider())
    tracer = trace.get_tracer(__name__)

    # Set up OTLP exporter
    otlp_exporter = OTLPSpanExporter(endpoint="your-otlp-endpoint")
    span_processor = BatchSpanProcessor(otlp_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)

    # Instrument FastAPI with OpenTelemetry
    FastAPIInstrumentor.instrument_app(app)
    return tracer


def create_app():
    app = FastAPI(lifespan=lifespan)
    # tracer = initialize_open_telemetry(app)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def add_idempotency_key_header(request: Request, call_next):
        header: str = f"IDMP-{str(uuid4())}"
        new_header = MutableHeaders(request.headers)
        new_header["X-IDMP-Key"] = header
        request._headers = new_header
        request.scope.update(headers=request.headers.raw)
        response = await call_next(request)
        return response

    register_routers(app=app)

    return app
