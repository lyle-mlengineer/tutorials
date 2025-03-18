from fastapi import FastAPI

from .routers.register_routers import register_routers


def create_app() -> FastAPI:
    app = FastAPI()
    register_routers(app=app)
    return app
