from .base_response import APIResponse


class CreateUserResponse(APIResponse):
    id: str
    name: str
    email: str


class GetUserResponse(APIResponse):
    id: str
    name: str
    email: str


class ListUsersResponse(APIResponse):
    users: list[GetUserResponse] = []


class UpdateUserResponse(APIResponse):
    id: str
    name: str
    email: str
