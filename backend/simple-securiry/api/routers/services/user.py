from ..database.models import UserInDb
from ..database.repository import BaseRepository
from ..exceptions import InvalidCredentialsError
from ..schemas import (CreateUserCommand, DeleteUserCommand, GetUserQuery,
                       ListUsersResponse, LoginUserCommand, LogoutUserCommand,
                       UpdateUserCommand, UserCreatedResponse,
                       UserFetchedResponse, UserLoggedInResponse,
                       UserUpdatedResponse)
from .helpers import (create_access_token, generate_user_id, hash_password,
                      verify_password)


class UserService:
    def __init__(self, repository: BaseRepository):
        self.repository = repository

    def create_user(self, command: CreateUserCommand) -> UserCreatedResponse:
        id: str = generate_user_id()
        hashed_password: str = hash_password(command.password)
        user: UserInDb = UserInDb(
            id=id, name=command.name, email=command.email, password=hashed_password
        )
        user = self.repository.save(user)
        return UserCreatedResponse(name=user.name, email=user.email, id=user.id)

    def login_user(self, command: LoginUserCommand) -> UserLoggedInResponse:
        user: UserInDb = self.repository.get_by_email(command.email)
        if not verify_password(command.password, user.password):
            raise InvalidCredentialsError("Invalid username or password")
        data: dict = {
            "sub": user.id,
            "scopes": ["own:read", "own:delete", "own:update", "users:list"],
        }
        access_token = create_access_token(data=data)
        return UserLoggedInResponse(token=access_token, token_type="bearer")

    def logout_user(self, id: str, command: LogoutUserCommand) -> None:
        pass

    def get_user(self, query: GetUserQuery) -> UserFetchedResponse:
        user: UserInDb = self.repository.get(id=query.id)
        return UserFetchedResponse(name=user.name, email=user.email, id=user.id)

    def update_user(self, id: str, command: UpdateUserCommand) -> UserUpdatedResponse:
        user: UserInDb = self.repository.get(id=id)
        if command.name:
            user.name = command.name
        if command.email:
            user.email = command.email
        user = self.repository.update(user)
        return UserUpdatedResponse(name=user.name, email=user.email, id=user.id)

    def delete_user(self, command: DeleteUserCommand) -> None:
        user: UserInDb = self.repository.delete(id=command.id)
        return

    def list_users(
        self, offset: int, limit: int, sort: str, sort_col: str
    ) -> ListUsersResponse:
        users: list[UserInDb] = self.repository.list_users(
            offset, limit, sort, sort_col
        )
        users: list[UserFetchedResponse] = [
            UserFetchedResponse(name=user.name, email=user.email, id=user.id)
            for user in users
        ]
        return ListUsersResponse(users=users)
