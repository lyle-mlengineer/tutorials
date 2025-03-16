from contextlib import asynccontextmanager
from uuid import UUID, uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
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


def create_app():
    app = FastAPI(lifespan=lifespan)
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
