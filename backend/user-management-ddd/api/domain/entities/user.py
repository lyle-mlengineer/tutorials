from pydantic import BaseModel

from .base_entity import BaseEntity


class User(BaseEntity):
    name: str
    email: str


class UserInDb(User):
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
