from ..application.commands.user.user_command_handlers import \
    CreateUserCommandHandler
from ..application.commands.user.user_commands import CreateUserCommand
from ..application.services.user_service import UserService
from ..infrastructure.event_publishers.cmd_publisher import \
    CommandLineEventPublisher
from ..infrastructure.mediators.mediator import Mediator
from ..infrastructure.repositories.user.in_memory_repository import \
    UserInMemoryRepository

repository: UserInMemoryRepository = UserInMemoryRepository()
publisher: CommandLineEventPublisher = CommandLineEventPublisher()
create_user_command_handler: CreateUserCommandHandler = CreateUserCommandHandler(
    user_repository=repository, event_publisher=publisher
)
mediator: Mediator = Mediator()
mediator.register_command(CreateUserCommand, create_user_command_handler)

user_service = UserService(mediator=mediator)
