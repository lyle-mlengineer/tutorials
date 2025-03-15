from abc import ABC, abstractmethod

from .base_query import BaseQuery


class BaseQueryHandler(ABC):
    @abstractmethod
    def handle(self, query: BaseQuery):
        pass
