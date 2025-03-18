from typing import Literal

from ..base_query import BaseQuery


class GetUserQuery(BaseQuery):
    id: str


class ListUsersQuery(BaseQuery):
    skip: int = 0
    limit: int = 10
    sort: Literal["asc", "desc"] = "asc"


class LoginUserQuery(BaseQuery):
    username: str
    password: str


class GetUserFromTokenQuery(BaseQuery):
    token: str


class RequestPasswordResetQuery(BaseQuery):
    id: str
