from ....domain.entities.email_entity import EmailEntity
from ....domain.entities.user import User, UserInDb
from ....domain.events.base_event import EventDetail, EventMetaData
from ....domain.events.base_event_publisher import BaseEventPublisher
from ....domain.events.user_events import (PasswordResetConfirmed,
                                           UserAccountActivated, UserCreated,
                                           UserDeleted, UserLoggedOut)
from ....domain.repositories.user_repository import UserRepository
from ....exceptions.application import (DatabaseChangesPublishingError,
                                        EventPublicationError)
from ....infrastructure.caches.cache_base import CacheBase
from ...services.email_service import BaseEmailService
from ...unit_of_work_base import UnitOfWorkBase
from ..base_command_handler import BaseCommandHandler
from ..database_queue_writer import BaseDataBaseQueueWriter
from .helpers import generate_id, hash_password
from .user_commands import (ActivateUserAccountCommand, CreateUserCommand,
                            DeleteUserCommand, LogoutUserCommand,
                            ResetPasswordCommand, UpdateUserCommand)


class UnitOfWork(UnitOfWorkBase):
    def __init__(
        self,
        repository: UserRepository,
        publisher: BaseEventPublisher,
        database_writer: BaseDataBaseQueueWriter,
        email_service: BaseEmailService = None,
    ):
        super().__init__()
        self.repository = repository
        self.publisher = publisher
        self.database_writer = database_writer
        self.email_service = email_service

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
        email_service: BaseEmailService = None,
    ):
        super().__init__()
        self.uow = UnitOfWork(
            repository=user_repository,
            publisher=event_publisher,
            database_writer=database_writer,
            email_service=email_service,
        )

    def handle(self, command: CreateUserCommand) -> User:
        user_id: str = generate_id()
        hashed_password: str = hash_password(password=command.password)
        user_id_db: UserInDb = UserInDb(
            id=user_id, name=command.name, email=command.email, password=hashed_password
        )
        with self.uow as uow:
            user: User = uow.repository.create_entity(entity=user_id_db)
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
            if uow.email_service:
                email: EmailEntity = EmailEntity(
                    id=generate_id(prefix="EML"),
                    recipients=[command.email],
                    title="Account Activation",
                    body="Please activate your account. Click the link below.",
                    email_type="AccountActivation",
                )
                uow.email_service.send_email(entity=email)

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


class ActivateUserAccountCommandHandler(BaseCommandHandler):
    def __init__(
        self,
        event_publisher: BaseEventPublisher,
        database_writer: BaseDataBaseQueueWriter,
        repository: UserRepository,
    ):
        super().__init__()
        self.uow = UnitOfWork(
            repository=repository,
            publisher=event_publisher,
            database_writer=database_writer,
        )

    def handle(self, command: ActivateUserAccountCommand) -> None:
        with self.uow as uow:
            user: User = uow.repository.get_entity(id=command.id)
            user.is_active = True
            uow.repository.update_entity(user)
            event_data: dict = {}
            event_data["id"] = command.id
            event_data["is_active"] = user.is_active
            metadata: EventMetaData = EventMetaData(
                idempotency_key=command.idempotency_key
            )
            event_detail: EventDetail = EventDetail(metadata=metadata, data=event_data)
            event: UserAccountActivated = UserAccountActivated(
                source="UserService",
                detail_type="UserAccountActivated",
                detail=event_detail,
            )
            uow.publisher.publish(event=event)
            uow.database_writer.write(user, command="update")
        return user


class LogoutUserCommandHandler(BaseCommandHandler):
    def __init__(
        self,
        event_publisher: BaseEventPublisher,
        cache: CacheBase,
        database_writer: BaseDataBaseQueueWriter,
    ):
        self.uow = UnitOfWorkDelete(
            cache=cache, publisher=event_publisher, database_writer=database_writer
        )

    def handle(self, command: LogoutUserCommand) -> None:
        with self.uow:
            user: User = self.uow.cache.get(key=command.id)
            if not user.is_logged_in:
                return
            user.is_logged_in = False
            self.uow.cache.delete(key=command.id)
            self.uow.cache.repository.update_entity(user)
            metadata: EventMetaData = EventMetaData(
                idempotency_key=command.idempotency_key
            )
            event_data: dict = {}
            event_data["id"] = command.id
            event_data["is_logged_in"] = user.is_logged_in
            event_detail: EventDetail = EventDetail(metadata=metadata, data=event_data)
            event: UserLoggedOut = UserLoggedOut(
                source="UserService", detail_type="UserLoggedOut", detail=event_detail
            )
            self.uow.publisher.publish(event)
            self.uow.database_writer.write(user, command="update")


class ResetPasswordCommandHandler(BaseCommandHandler):
    def __init__(
        self,
        event_publisher: BaseEventPublisher,
        database_writer: BaseDataBaseQueueWriter,
        repository: UserRepository,
    ):
        super().__init__()
        self.uow = UnitOfWork(
            repository=repository,
            publisher=event_publisher,
            database_writer=database_writer,
        )

    def handle(self, command: ResetPasswordCommand) -> None:
        with self.uow as uow:
            user: UserInDb = uow.repository.get_entity(id=command.id)
            hashed_password: str = hash_password(password=command.password)
            user.password = hashed_password
            uow.repository.update_entity(user)
            event_data: dict = {}
            event_data["id"] = command.id
            event_data["password"] = user.password
            metadata: EventMetaData = EventMetaData(
                idempotency_key=command.idempotency_key
            )
            event_detail: EventDetail = EventDetail(metadata=metadata, data=event_data)
            event: PasswordResetConfirmed = PasswordResetConfirmed(
                source="UserService",
                detail_type="PasswordResetConfirmed",
                detail=event_detail,
            )
            uow.publisher.publish(event=event)
            uow.database_writer.write(user, command="update")
        return user
