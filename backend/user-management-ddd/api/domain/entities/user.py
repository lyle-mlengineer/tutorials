from pydantic import BaseModel

from .base_entity import BaseEntity


class User(BaseEntity):
    name: str
    email: str
    is_logged_in: bool = False
    is_active: bool = False


class UserInDb(User):
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
