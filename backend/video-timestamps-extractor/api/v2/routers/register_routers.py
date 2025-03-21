from fastapi import FastAPI

from .playlist import playlist_router
from .videos import video_router


def register_routers(app: FastAPI) -> None:
    app.include_router(video_router)
    app.include_router(playlist_router)
