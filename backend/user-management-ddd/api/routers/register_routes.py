from fastapi import FastAPI

from .user.user import router as user_router


def register_routers(app: FastAPI) -> None:
    app.include_router(router=user_router)
