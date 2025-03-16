from ....domain.entities.user import User
from ....domain.events.base_event import EventDetail, EventMetaData
from ....domain.events.base_event_publisher import BaseEventPublisher
from ....domain.events.user_events import UserFetched
from ....domain.repositories.base_repository import BaseRepository
from ....infrastructure.caches.cache_base import CacheBase
from ...queries.user.user_queries import GetUserQuery, ListUsersQuery
from ...unit_of_work_base import UnitOfWorkBase
from ..base_query_handler import BaseQueryHandler


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
