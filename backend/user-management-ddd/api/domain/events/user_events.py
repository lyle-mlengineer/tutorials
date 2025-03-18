from .base_event import BaseEvent


class UserCreated(BaseEvent):
    pass


class UserFetched(BaseEvent):
    pass


class UserDeleted(BaseEvent):
    pass


class UserLoggedIn(BaseEvent):
    pass
