from fastapi import FastAPI

from .v2.routers.register_routers import register_routers


def create_app() -> FastAPI:
    app = FastAPI()
    register_routers(app=app)
    return app
