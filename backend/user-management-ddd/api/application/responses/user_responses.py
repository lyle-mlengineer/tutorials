from .base_response import APIResponse


class UserCreatedResponse(APIResponse):
    id: str
    name: str
    email: str


class UserRetrievedResponse(APIResponse):
    pass


class UsersRetrievedResponse(APIResponse):
    users: UserRetrievedResponse
