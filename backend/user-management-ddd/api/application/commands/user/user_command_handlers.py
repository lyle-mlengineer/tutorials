from uuid import UUID, uuid4

from ....domain.entities.user import User
from ....domain.events.base_event_publisher import BaseEventPublisher
from ....domain.events.user_events import UserCreated
from ....domain.repositories.user_repository import UserRepository
from ..base_command_handler import BaseCommandHandler
from .user_commands import CreateUserCommand


def generate_id(prefix: str = "US") -> str:
    raw_id: UUID = uuid4()
    id: str = f"{prefix}-{str(raw_id)}"
    return id


class CreateUserCommandHandler(BaseCommandHandler):
    def __init__(
        self, user_repository: UserRepository, event_publisher: BaseEventPublisher
    ):
        super().__init__()
        self.user_repository = user_repository
        self.event_publisher = event_publisher

    def handle(self, command: CreateUserCommand) -> User:
        user_id: str = generate_id()
        user: User = User(id=user_id, name=command.name, email=command.email)
        self.user_repository.create_entity(entity=user)
        self.event_publisher.publish(
            event=UserCreated(name=command.name, email=command.email, id=user_id)
        )
        return user
