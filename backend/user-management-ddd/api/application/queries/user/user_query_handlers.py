from ....application.services.email_service import BaseEmailService
from ....domain.entities.email_entity import EmailEntity
from ....domain.entities.user import Token, User, UserInDb
from ....domain.events.base_event import EventDetail, EventMetaData
from ....domain.events.base_event_publisher import BaseEventPublisher
from ....domain.events.user_events import (PasswordResetRequested, UserFetched,
                                           UserLoggedIn)
from ....domain.repositories.base_repository import BaseRepository
from ....domain.repositories.user_repository import UserRepository
from ....exceptions.application import (AccountNotActiveError,
                                        InvalidCredentialsError)
from ....infrastructure.caches.cache_base import CacheBase
from ...queries.user.user_queries import (GetUserFromTokenQuery, GetUserQuery,
                                          ListUsersQuery, LoginUserQuery,
                                          RequestPasswordResetQuery)
from ...unit_of_work_base import UnitOfWorkBase
from ..base_query_handler import BaseQueryHandler
from .helpers import check_password, decode_token, generate_id


class UnitOfWork(UnitOfWorkBase):
    def __init__(self, cache: CacheBase, publisher: BaseEventPublisher):
        super().__init__()
        self.cache = cache
        self.publisher = publisher

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass


class UnitOfWorkList(UnitOfWorkBase):
    def __init__(self, repository: BaseRepository, publisher: BaseEventPublisher):
        super().__init__()
        self.repository = repository
        self.publisher = publisher

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass


class UnitOfWorkEmail(UnitOfWorkBase):
    def __init__(
        self,
        repository: BaseRepository,
        publisher: BaseEventPublisher,
        email_service: BaseEmailService,
    ):
        super().__init__()
        self.repository = repository
        self.publisher = publisher
        self.email_service = email_service

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass


class GetUserQueryHandler(BaseQueryHandler):
    def __init__(
        self,
        event_publisher: BaseEventPublisher,
        cache: CacheBase,
    ):
        self.uow = UnitOfWork(cache=cache, publisher=event_publisher)

    def handle(self, query: GetUserQuery) -> User | None:
        with self.uow:
            user: User = self.uow.cache.get(key=query.id)
            metadata: EventMetaData = EventMetaData(
                idempotency_key=query.idempotency_key
            )
            event_data: dict = user.model_dump()
            event_detail: EventDetail = EventDetail(metadata=metadata, data=event_data)
            event: UserFetched = UserFetched(
                source="UserService", detail_type="UsersListed", detail=event_detail
            )
            self.uow.publisher.publish(event)
            return user


class ListUsersQueryHandler(BaseQueryHandler):
    def __init__(
        self,
        event_publisher: BaseEventPublisher,
        repository: BaseRepository,
    ):
        self.uow = UnitOfWorkList(repository=repository, publisher=event_publisher)

    def handle(self, query: ListUsersQuery) -> list[User] | list:
        with self.uow:
            users: list[User] = self.uow.repository.list_entities()
            metadata: EventMetaData = EventMetaData(
                idempotency_key=query.idempotency_key
            )
            event_data: list[dict] = [user.model_dump() for user in users]
            event_detail: EventDetail = EventDetail(
                metadata=metadata, data={"users": event_data}
            )
            event: UserFetched = UserFetched(
                source="UserService", detail_type="UsersListed", detail=event_detail
            )
            self.uow.publisher.publish(event)
            return {"users": users}


class GetUserFromTokenQueryHandler(BaseQueryHandler):
    def __init__(
        self,
        event_publisher: BaseEventPublisher,
        repository: UserRepository,
    ):
        self.uow = UnitOfWorkList(repository=repository, publisher=event_publisher)

    def handle(self, query: GetUserFromTokenQuery) -> User:
        with self.uow:
            user_id: str = decode_token(token=query.token)
            user_id_db: UserInDb = self.uow.repository.get_entity(id=user_id)
            user: User = User(**user_id_db.model_dump())
            metadata: EventMetaData = EventMetaData(
                idempotency_key=query.idempotency_key
            )
            event_data: dict = user.model_dump()
            event_detail: EventDetail = EventDetail(metadata=metadata, data=event_data)
            event: UserLoggedIn = UserLoggedIn(
                source="UserService", detail_type="TokenDecoded", detail=event_detail
            )
            self.uow.publisher.publish(event)
            return user


class LoginUserQueryHandler(BaseQueryHandler):
    def __init__(
        self,
        event_publisher: BaseEventPublisher,
        repository: UserRepository,
    ):
        self.uow = UnitOfWorkList(repository=repository, publisher=event_publisher)

    def handle(self, query: LoginUserQuery) -> User:
        with self.uow:
            user: UserInDb = self.uow.repository.get_user(email=query.username)
            if not check_password(query.password, user.password):
                raise InvalidCredentialsError("Invalide username or password")
            if not user.is_active:
                raise AccountNotActiveError("Account not active")
            user.is_logged_in = True
            self.uow.repository.update_entity(user)
            token: Token = Token(access_token=user.id, token_type="bearer")
            metadata: EventMetaData = EventMetaData(
                idempotency_key=query.idempotency_key
            )
            event_data: dict = user.model_dump(exclude={"password"})
            event_detail: EventDetail = EventDetail(metadata=metadata, data=event_data)
            event: UserLoggedIn = UserLoggedIn(
                source="UserService", detail_type="UserLoggedIn", detail=event_detail
            )
            self.uow.publisher.publish(event)
            return token


class PasswordResetRequestQueryHandler(BaseQueryHandler):
    def __init__(
        self,
        event_publisher: BaseEventPublisher,
        repository: UserRepository,
        email_service: BaseEmailService,
    ):
        self.uow = UnitOfWorkEmail(
            repository=repository,
            publisher=event_publisher,
            email_service=email_service,
        )

    def handle(self, query: RequestPasswordResetQuery) -> None:
        with self.uow:
            user_id_db: UserInDb = self.uow.repository.get_entity(id=query.id)
            email: EmailEntity = EmailEntity(
                id=generate_id(prefix="EML"),
                recipients=[user_id_db.email],
                title="Password Reset",
                body="Please reset your password. Click the link below.",
                email_type="PasswordReset",
            )
            metadata: EventMetaData = EventMetaData(
                idempotency_key=query.idempotency_key
            )
            event_data: dict = user_id_db.model_dump(exclude={"password"})
            event_detail: EventDetail = EventDetail(metadata=metadata, data=event_data)
            event: PasswordResetRequested = PasswordResetRequested(
                source="UserService",
                detail_type="PasswordResetRequested",
                detail=event_detail,
            )
            self.uow.publisher.publish(event)
            self.uow.email_service.send_email(entity=email)
