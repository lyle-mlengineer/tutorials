from typing import Literal

from pydantic import BaseModel


class EventMetaData(BaseModel):
    idempotency_key: str


class EventDetail(BaseModel):
    metadata: EventMetaData
    data: dict


class BaseEvent(BaseModel):
    source: Literal["UserService"]
    detail_type: Literal[
        "UserCreated",
        "UserFetched",
        "UserDeleted",
        "UserUpdated",
        "UsersListed",
        "UserLoggedIn",
        "TokenDecoded",
        "UserAccountActivated",
        "PasswordResetRequested",
        "PasswordResetConfirmed",
    ]
    detail: EventDetail
