from typing import Annotated

from fastapi import Depends, Header
from fastapi.security import OAuth2PasswordBearer

from ..application.commands.user.user_command_handlers import (
    CreateUserCommandHandler, DeleteUserCommandHandler,
    UpdateUserCommandHandler)
from ..application.commands.user.user_commands import (CreateUserCommand,
                                                       DeleteUserCommand,
                                                       UpdateUserCommand)
from ..application.queries.user.user_queries import (GetUserFromTokenQuery,
                                                     GetUserQuery,
                                                     ListUsersQuery,
                                                     LoginUserQuery)
from ..application.queries.user.user_query_handlers import (
    GetUserFromTokenQueryHandler, GetUserQueryHandler, ListUsersQueryHandler,
    LoginUserQueryHandler)
from ..application.services.base_service import BaseService
from ..application.services.user_service import UserService
from ..domain.entities.user import User
from ..infrastructure.caches.file_cache import FileCache
from ..infrastructure.database_queue_writers.cmd_writer import CMDQueueWriter
from ..infrastructure.database_queue_writers.redis_writer import \
    RedisQueueWriter
from ..infrastructure.event_publishers.cmd_publisher import \
    CommandLineEventPublisher
from ..infrastructure.event_publishers.redis_publisher import \
    RedisEventPublisher
from ..infrastructure.mediators.mediator import Mediator
from ..infrastructure.repositories.user.file_repository import FileRepository
from ..infrastructure.repositories.user.in_memory_repository import \
    UserInMemoryRepository

file_repo = FileRepository()
memory_repo = UserInMemoryRepository()
db_writer = CMDQueueWriter()
cache = FileCache(repository=file_repo)
publisher: CommandLineEventPublisher = CommandLineEventPublisher()
redis_pub = RedisEventPublisher()
rq_writer = RedisQueueWriter()

create_user_command_handler: CreateUserCommandHandler = CreateUserCommandHandler(
    user_repository=file_repo, event_publisher=publisher, database_writer=db_writer
)
get_user_handler = GetUserQueryHandler(event_publisher=publisher, cache=cache)
delete_user_handler = DeleteUserCommandHandler(
    cache=cache, event_publisher=publisher, database_writer=db_writer
)
list_users_handler = ListUsersQueryHandler(
    event_publisher=publisher, repository=file_repo
)
update_user = UpdateUserCommandHandler(
    cache=cache, event_publisher=publisher, database_writer=db_writer
)
login_user = LoginUserQueryHandler(event_publisher=publisher, repository=file_repo)
user_from_token = GetUserFromTokenQueryHandler(
    event_publisher=publisher, repository=file_repo
)


def get_mediator() -> Mediator:
    mediator: Mediator = Mediator()
    mediator.register_command(CreateUserCommand, create_user_command_handler)
    mediator.register_query(GetUserQuery, get_user_handler)
    mediator.register_command(DeleteUserCommand, delete_user_handler)
    mediator.register_query(ListUsersQuery, list_users_handler)
    mediator.register_command(UpdateUserCommand, update_user)
    mediator.register_query(LoginUserQuery, login_user)
    mediator.register_query(GetUserFromTokenQuery, user_from_token)
    return mediator


def get_user_service(mediator: Mediator = Depends(get_mediator)) -> BaseService:
    return UserService(mediator=mediator)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    service: UserService = Depends(get_user_service),
    x_idmp_key: Annotated[str | None, Header()] = None,
) -> User:
    user: User = service.get_user_from_token(
        query=GetUserFromTokenQuery(token=token, idempotency_key=x_idmp_key)
    )
    return user
