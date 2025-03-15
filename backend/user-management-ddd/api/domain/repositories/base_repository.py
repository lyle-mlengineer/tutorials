from abc import ABC, abstractmethod
from typing import Optional

from ..entities.base_entity import BaseEntity


class BaseRepository(ABC):
    @abstractmethod
    def create_entity(self, entity: BaseEntity) -> BaseEntity:
        pass

    @abstractmethod
    def get_entity(self, id: int) -> Optional[BaseEntity]:
        pass

    @abstractmethod
    def list_entities(self, filters: dict) -> Optional[BaseEntity]:
        pass

    @abstractmethod
    def update_entity(self, entity: BaseEntity) -> None:
        pass

    @abstractmethod
    def delete_entity(self, id: int) -> None:
        pass
