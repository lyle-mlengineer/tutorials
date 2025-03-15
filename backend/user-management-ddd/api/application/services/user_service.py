from ...domain.entities.user import User
from ...infrastructure.mediators.base_mediator import BaseMediator
from ..commands.user.user_commands import CreateUserCommand
from ..responses.user_responses import UserCreatedResponse
from .base_service import BaseService


class UserService(BaseService):
    def __init__(self, mediator: BaseMediator):
        super().__init__()
        self.mediator = mediator

    def create_entity(self, command: CreateUserCommand) -> UserCreatedResponse:
        user: User = self.mediator.handle_command(command=command)
        return UserCreatedResponse(id=user.id, name=user.name, email=user.email)

    def get_entity(self, query):
        return super().get_entity(query)

    def delete_entity(self, command):
        return super().delete_entity(command)

    def update_entity(self, command):
        return super().update_entity(command)

    def list_entities(self, query):
        return super().list_entities(query)
