from fastapi import APIRouter, HTTPException, status

from ...application.commands.user.user_commands import CreateUserCommand
from ...application.responses.user_responses import UserCreatedResponse
from ..dependencies import user_service

router = APIRouter(tags=["User"], prefix="/users")


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(command: CreateUserCommand):
    return user_service.create_entity(command=command)
