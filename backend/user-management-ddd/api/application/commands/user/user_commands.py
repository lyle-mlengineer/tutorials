from ..base_command import BaseCommand


class CreateUserCommand(BaseCommand):
    name: str
    email: str
