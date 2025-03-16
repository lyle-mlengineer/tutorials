from abc import ABC, abstractmethod
from typing import Optional

from ...domain.entities.base_entity import BaseEntity
from ...domain.repositories.base_repository import BaseRepository


class CacheBase(ABC):
    def __init__(self, repository: Optional[BaseRepository] = None):
        super().__init__()
        self._repository = repository

    @property
    def repository(self) -> BaseRepository:
        return self._repository

    @repository.setter
    def repository(self, repository: BaseRepository) -> None:
        self._repository = repository

    @abstractmethod
    def set(self, key: str, value: BaseEntity):
        pass

    @abstractmethod
    def get(self, key: str) -> BaseEntity:
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        pass
