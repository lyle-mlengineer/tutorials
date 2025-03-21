from typing import Literal

from pydantic import BaseModel


class CreateUserCommand(BaseModel):
    name: str
    email: str
    password: str


class LoginUserCommand(BaseModel):
    email: str
    password: str


class LogoutUserCommand(BaseModel):
    id: str


class GetUserQuery(BaseModel):
    id: str


class UpdateUserCommand(BaseModel):
    name: str
    email: str


class DeleteUserCommand(BaseModel):
    id: str


class ListUsersQuery(BaseModel):
    offset: int = 0
    limit: int = 10
    order: Literal["asc", "desc"] = "asc"


# ---------------------- Responses -----------------------


class UserCreatedResponse(BaseModel):
    name: str
    email: str
    id: str


class UserLoggedInResponse(BaseModel):
    token: str
    token_type: str


class UserFetchedResponse(BaseModel):
    name: str
    email: str
    id: str


class UserUpdatedResponse(BaseModel):
    name: str
    email: str
    id: str


class ListUsersResponse(BaseModel):
    users: list[UserFetchedResponse] = []
