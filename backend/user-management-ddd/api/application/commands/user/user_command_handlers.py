from uuid import UUID, uuid4

from ....domain.entities.user import User
from ....domain.events.base_event import EventDetail, EventMetaData
from ....domain.events.base_event_publisher import BaseEventPublisher
from ....domain.events.user_events import UserCreated, UserDeleted
from ....domain.repositories.user_repository import UserRepository
from ....exceptions.application import (DatabaseChangesPublishingError,
                                        EventPublicationError)
from ....infrastructure.caches.cache_base import CacheBase
from ...unit_of_work_base import UnitOfWorkBase
from ..base_command_handler import BaseCommandHandler
from ..database_queue_writer import BaseDataBaseQueueWriter
from .user_commands import (CreateUserCommand, DeleteUserCommand,
                            UpdateUserCommand)


def generate_id(prefix: str = "US") -> str:
    raw_id: UUID = uuid4()
    id: str = f"{prefix}-{str(raw_id)}"
    return id


class UnitOfWork(UnitOfWorkBase):
    def __init__(
        self,
        repository: UserRepository,
        publisher: BaseEventPublisher,
        database_writer: BaseDataBaseQueueWriter,
    ):
        super().__init__()
        self.repository = repository
        self.publisher = publisher
        self.database_writer = database_writer

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            if (
                exc_type is EventPublicationError
                or exc_type is DatabaseChangesPublishingError
            ):
                self.repository.rollback()


class UnitOfWorkDelete(UnitOfWorkBase):
    def __init__(
        self,
        cache: CacheBase,
        publisher: BaseEventPublisher,
        database_writer: BaseDataBaseQueueWriter,
    ):
        super().__init__()
        self.cache = cache
        self.publisher = publisher
        self.database_writer = database_writer

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            if (
                exc_type is EventPublicationError
                or exc_type is DatabaseChangesPublishingError
            ):
                self.repository.rollback()


class CreateUserCommandHandler(BaseCommandHandler):
    def __init__(
        self,
        user_repository: UserRepository,
        event_publisher: BaseEventPublisher,
        database_writer: BaseDataBaseQueueWriter,
    ):
        super().__init__()
        self.uow = UnitOfWork(
            repository=user_repository,
            publisher=event_publisher,
            database_writer=database_writer,
        )

    def handle(self, command: CreateUserCommand) -> User:
        user_id: str = generate_id()
        user: User = User(id=user_id, name=command.name, email=command.email)
        with self.uow as uow:
            uow.repository.create_entity(entity=user)
            metadata: EventMetaData = EventMetaData(
                idempotency_key=command.idempotency_key
            )
            event_data: dict = user.model_dump()
            event_detail: EventDetail = EventDetail(metadata=metadata, data=event_data)
            event: UserDeleted = UserDeleted(
                source="UserService", detail_type="UserDeleted", detail=event_detail
            )
            uow.publisher.publish(event=event)
            uow.database_writer.write(user, command="create")
        return user


class DeleteUserCommandHandler(BaseCommandHandler):
    def __init__(
        self,
        cache: CacheBase,
        event_publisher: BaseEventPublisher,
        database_writer: BaseDataBaseQueueWriter,
    ):
        super().__init__()
        self.uow = UnitOfWorkDelete(
            cache=cache,
            publisher=event_publisher,
            database_writer=database_writer,
        )

    def handle(self, command: DeleteUserCommand) -> None:
        with self.uow as uow:
            user: User = uow.cache.delete(key=command.id)
            metadata: EventMetaData = EventMetaData(
                idempotency_key=command.idempotency_key
            )
            event_data: dict = user.model_dump()
            event_detail: EventDetail = EventDetail(metadata=metadata, data=event_data)
            event: UserCreated = UserCreated(
                source="UserService", detail_type="UserDeleted", detail=event_detail
            )
            uow.publisher.publish(event=event)
            uow.database_writer.write(user, command="delete")


class UpdateUserCommandHandler(BaseCommandHandler):
    def __init__(
        self,
        cache: CacheBase,
        event_publisher: BaseEventPublisher,
        database_writer: BaseDataBaseQueueWriter,
    ):
        super().__init__()
        self.uow = UnitOfWorkDelete(
            cache=cache,
            publisher=event_publisher,
            database_writer=database_writer,
        )

    def handle(self, command: UpdateUserCommand) -> User:
        with self.uow as uow:
            user: User = uow.cache.repository.get_entity(id=command.id)
            event_data: dict = {}
            if command.email:
                user.email = command.email
                event_data["emai"] = command.email
            if command.name:
                user.name = command.name
                event_data["name"] = command.name
            uow.cache.repository.update_entity(user)
            if uow.cache.delete(command.id):
                uow.cache.set(command.id, user)
            if event_data:
                event_data["id"] = command.id
                metadata: EventMetaData = EventMetaData(
                    idempotency_key=command.idempotency_key
                )
                event_detail: EventDetail = EventDetail(
                    metadata=metadata, data=event_data
                )
                event: UserDeleted = UserDeleted(
                    source="UserService", detail_type="UserUpdated", detail=event_detail
                )
                uow.publisher.publish(event=event)
            uow.database_writer.write(user, command="update")
        return user
