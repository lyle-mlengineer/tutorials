from typing import Optional

from ...domain.entities.user import User
from ...infrastructure.mediators.base_mediator import BaseMediator
from ..commands.user.user_commands import (CreateUserCommand,
                                           DeleteUserCommand,
                                           UpdateUserCommand)
from ..queries.user.user_queries import GetUserQuery, ListUsersQuery
from ..responses.user_responses import (CreateUserResponse, GetUserResponse,
                                        ListUsersResponse, UpdateUserResponse)
from .base_service import BaseService


class UserService(BaseService):
    def __init__(self, mediator: BaseMediator):
        super().__init__()
        self.mediator = mediator

    def create_entity(self, command: CreateUserCommand) -> CreateUserResponse:
        user: User = self.mediator.handle_command(command=command)
        return CreateUserResponse(id=user.id, name=user.name, email=user.email)

    def get_entity(self, query: GetUserQuery) -> Optional[GetUserResponse]:
        user: User = self.mediator.handle_query(query=query)
        return GetUserResponse(id=user.id, email=user.email, name=user.name)

    def delete_entity(self, command: DeleteUserCommand) -> None:
        self.mediator.handle_command(command=command)
        return None

    def update_entity(self, command: UpdateUserCommand) -> UpdateUserResponse:
        return self.mediator.handle_command(command)

    def list_entities(self, query: ListUsersQuery) -> ListUsersResponse:
        return self.mediator.handle_query(query)
