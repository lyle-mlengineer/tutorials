from abc import ABC, abstractmethod
from typing import Optional

from ..commands.base_command import BaseCommand
from ..queries.base_query import BaseQuery
from ..responses.base_response import APIResponse


class BaseService(ABC):
    @abstractmethod
    def create_entity(self, command: BaseCommand) -> APIResponse:
        pass

    @abstractmethod
    def get_entity(self, query: BaseQuery) -> Optional[APIResponse]:
        pass

    @abstractmethod
    def list_entities(self, query: BaseQuery) -> Optional[APIResponse]:
        pass

    @abstractmethod
    def update_entity(self, command: BaseCommand) -> None:
        pass

    @abstractmethod
    def delete_entity(self, command: BaseCommand) -> None:
        pass
