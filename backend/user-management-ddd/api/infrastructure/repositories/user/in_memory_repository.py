from typing import Optional

from ....domain.entities.user import User
from ....domain.repositories.user_repository import UserRepository


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

    def delete_entity(self, id):
        return super().delete_entity(id)

    def get_entity(self, id):
        return super().get_entity(id)

    def list_entities(self, filters):
        return super().list_entities(filters)

    def update_entity(self, entity):
        return super().update_entity(entity)
