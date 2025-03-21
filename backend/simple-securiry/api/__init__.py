from contextlib import asynccontextmanager

from fastapi import FastAPI

from .routers.database.database import init_database
from .routers.register_routers import register_routers


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        init_database()
        yield
    finally:
        print("Done")


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    register_routers(app=app)
    return app
