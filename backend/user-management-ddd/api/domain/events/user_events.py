from .base_event import BaseEvent


class UserCreated(BaseEvent):
    pass


class UserFetched(BaseEvent):
    pass


class UserDeleted(BaseEvent):
    pass


class UserLoggedIn(BaseEvent):
    pass


class UserLoggedOut(BaseEvent):
    pass


class UserAccountActivated(BaseEvent):
    pass


class PasswordResetRequested(BaseEvent):
    pass


class PasswordResetConfirmed(BaseEvent):
    pass
