from typing import Optional

from ..base_command import BaseCommand


class CreateUserCommand(BaseCommand):
    name: str
    email: str
    password: str


class UpdateUserCommand(BaseCommand):
    id: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None


class DeleteUserCommand(BaseCommand):
    id: str


class ActivateUserAccountCommand(BaseCommand):
    token: str
    id: str = None


class LogoutUserCommand(BaseCommand):
    id: str


class ResetPasswordCommand(BaseCommand):
    id: str
    password: str
