import json
import os
from typing import Optional

from ...domain.entities.base_entity import BaseEntity
from ...domain.entities.user import User
from ...domain.repositories.base_repository import BaseRepository
from ...exceptions.application import AccountNotFoundError
from .cache_base import CacheBase


class FileCache(CacheBase):
    def __init__(self, repository: Optional[BaseRepository] = None):
        super().__init__(repository)
        self._cache_path: str = "./cache.json"

    @property
    def repository(self) -> BaseRepository:
        return self._repository

    def _load_file(self) -> list[dict]:
        if not os.path.exists(self._cache_path):
            with open(self._cache_path, "w") as f:
                json.dump({}, f)
        with open(self._cache_path, "r") as f:
            items = json.load(f)
        return items

    def _save_file(self, contents: list[dict]) -> None:
        with open(self._cache_path, "w") as f:
            json.dump(contents, f, indent=4)

    @repository.setter
    def repository(self, repository: BaseRepository) -> None:
        self._repository = repository

    def set(self, key: str, value: BaseEntity):
        cache: dict[str, dict] = self._load_file()
        cache[key] = value.model_dump()
        self._save_file(cache)

    def get(self, key: str) -> BaseEntity:
        cache: dict[str, dict] = self._load_file()
        result: dict = cache.get(key)
        if result:
            user = User(name=result["name"], email=result["email"], id=result["id"])
            return user
        result: User = self.repository.get_entity(key)
        self.set(key, result)
        return result

    def delete(self, key: str) -> User | None:
        cache: dict[str, dict] = self._load_file()
        result: dict = cache.get(key)
        if result:
            del cache[key]
            self._save_file(cache)
            result: User = self.repository.delete_entity(key)
            return result
        return None
