from .base_event import BaseEvent


class UserCreated(BaseEvent):
    id: str
    name: str
    email: str


class UserFetched(BaseEvent):
    id: str
    name: str
    email: str
