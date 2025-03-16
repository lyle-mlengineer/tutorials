from typing import Optional

from ....domain.entities.user import User
from ....domain.repositories.user_repository import UserRepository
from ....exceptions.application import AccountNotFoundError


class UserInMemoryRepository(UserRepository):
    def __init__(self):
        self._users: list[User] = []

    def get_user(self, email: str) -> Optional[User]:
        for user in self._users:
            if user.email == email:
                return user
        return None

    def create_entity(self, entity: User) -> User:
        self._users.append(entity)
        return entity

    def delete_entity(self, id: str) -> User:
        user = None
        for user in self._users:
            if user.id == id:
                user = user
        if not user:
            raise AccountNotFoundError(f"The user with id '{id}' was not found!")
        self._users.remove(user)
        return user

    def get_entity(self, id: str) -> User:
        for user in self._users:
            if user.id == id:
                return user
        raise AccountNotFoundError(f"The user with id '{id}' was not found!")

    def list_entities(self, filters) -> Optional[list[User]]:
        return self._users

    def update_entity(self, entity):
        return super().update_entity(entity)
