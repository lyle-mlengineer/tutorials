from abc import ABC, abstractmethod
from typing import Literal, Optional

from ..entities.base_entity import BaseEntity


class BaseRepository(ABC):
    @abstractmethod
    def create_entity(self, entity: BaseEntity) -> BaseEntity:
        pass

    @abstractmethod
    def get_entity(self, id: str) -> Optional[BaseEntity]:
        pass

    @abstractmethod
    def list_entities(
        self, skip: int = 0, limit: int = 10, sort: Literal["asc", "desc"] = "asc"
    ) -> list[BaseEntity] | list:
        pass

    @abstractmethod
    def update_entity(self, entity: BaseEntity) -> BaseEntity:
        pass

    @abstractmethod
    def delete_entity(self, id: str) -> BaseEntity:
        pass
