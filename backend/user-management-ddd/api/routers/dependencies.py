from fastapi import Depends

from ..application.commands.user.user_command_handlers import (
    CreateUserCommandHandler, DeleteUserCommandHandler,
    UpdateUserCommandHandler)
from ..application.commands.user.user_commands import (CreateUserCommand,
                                                       DeleteUserCommand,
                                                       UpdateUserCommand)
from ..application.queries.user.user_queries import (GetUserQuery,
                                                     ListUsersQuery)
from ..application.queries.user.user_query_handlers import (
    GetUserQueryHandler, ListUsersQueryHandler)
from ..application.services.base_service import BaseService
from ..application.services.user_service import UserService
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


def get_mediator() -> Mediator:
    mediator: Mediator = Mediator()
    mediator.register_command(CreateUserCommand, create_user_command_handler)
    mediator.register_query(GetUserQuery, get_user_handler)
    mediator.register_command(DeleteUserCommand, delete_user_handler)
    mediator.register_query(ListUsersQuery, list_users_handler)
    mediator.register_command(UpdateUserCommand, update_user)
    return mediator


def get_user_service(mediator: Mediator = Depends(get_mediator)) -> BaseService:
    return UserService(mediator=mediator)
