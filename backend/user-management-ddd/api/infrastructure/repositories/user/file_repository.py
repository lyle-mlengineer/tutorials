import json
import os
from typing import Literal, Optional

from ....domain.entities.user import User, UserInDb
from ....domain.repositories.user_repository import UserRepository
from ....exceptions.application import (AccountAlreadyExistsError,
                                        AccountNotFoundError)


class FileRepository(UserRepository):
    def __init__(self):
        self._memory_path: str = "./db.json"

    def _load_file(self) -> list[dict]:
        if not os.path.exists(self._memory_path):
            with open(self._memory_path, "w") as f:
                json.dump([], f)
        else:
            try:
                with open(self._memory_path, "r") as f:
                    items = json.load(f)
            except json.JSONDecodeError:
                with open(self._memory_path, "w") as f:
                    json.dump([], f)
        with open(self._memory_path, "r") as f:
            items = json.load(f)
        return items

    def _save_file(self, contents: list[dict]) -> None:
        with open(self._memory_path, "w") as f:
            json.dump(contents, f, indent=4)

    def get_user(self, email: str) -> Optional[UserInDb]:
        items: list[dict] = self._load_file()
        for user in items:
            if user["email"] == email:
                return UserInDb(
                    id=user["id"],
                    name=user["name"],
                    email=user["email"],
                    password=user["password"],
                )
        raise AccountNotFoundError(f"The user with email '{email}' was not found!")

    def create_entity(self, entity: User) -> User:
        items: list[dict] = self._load_file()
        for user in items:
            if user["email"] == entity.email:
                raise AccountAlreadyExistsError(
                    f'A user with the email "{entity.email}" already exists!'
                )
        items.append(entity.model_dump())
        self._save_file(items)
        return entity

    def delete_entity(self, id) -> User:
        result: dict = None
        items: list[dict] = self._load_file()
        for user in items:
            if user["id"] == id:
                result = user
        if not result:
            raise AccountNotFoundError(f"The user with id '{id}' was not found!")
        items.remove(result)
        self._save_file(items)
        return User(id=result["id"], name=result["name"], email=result["email"])

    def get_entity(self, id: str) -> Optional[UserInDb]:
        items: list[dict] = self._load_file()
        for user in items:
            if user["id"] == id:
                return UserInDb(
                    id=user["id"],
                    name=user["name"],
                    email=user["email"],
                    password=user["password"],
                )
        raise AccountNotFoundError(f"The user with id '{id}' was not found!")

    def list_entities(
        self, skip: int = 0, limit: int = 10, sort: Literal["asc", "desc"] = "asc"
    ) -> list[User] | list:
        users: list[User] = []
        items: list[dict] = self._load_file()
        for user in items:
            users.append(User(id=user["id"], name=user["name"], email=user["email"]))
        return users

    def update_entity(self, entity: User) -> User:
        items: list[dict] = self._load_file()
        user_idx: int = -1
        for i, item in enumerate(items):
            if item["id"] == entity.id:
                user_idx = i
        if user_idx == -1:
            raise AccountNotFoundError(f"The user with id '{id}' was not found!")
        items[user_idx] = entity.model_dump()
        self._save_file(items)
        return entity

    def rollback(self) -> None:
        items: list[dict] = self._load_file()
        items.pop()
        self._save_file(items)
