from fastapi import FastAPI

from .videos import video_router


def register_routers(app: FastAPI) -> None:
    app.include_router(video_router)
