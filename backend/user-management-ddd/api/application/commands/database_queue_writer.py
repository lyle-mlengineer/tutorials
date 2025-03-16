from abc import ABC, abstractmethod
from typing import Literal

from ...domain.entities.base_entity import BaseEntity


class BaseDataBaseQueueWriter(ABC):
    @abstractmethod
    def write(
        self, entity: BaseEntity, command: Literal["create", "delete", "update"]
    ) -> None:
        pass
