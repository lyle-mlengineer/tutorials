from abc import ABC, abstractmethod

from ...application.commands.base_command import BaseCommand
from ...application.commands.base_command_handler import BaseCommandHandler
from ...application.queries.base_query import BaseQuery
from ...application.queries.base_query_handler import BaseQueryHandler


class BaseMediator(ABC):
    @abstractmethod
    def register_command(self, command: BaseCommand, handler: BaseCommandHandler):
        pass

    @abstractmethod
    def handle_command(self, command: BaseCommand):
        pass

    @abstractmethod
    def register_query(self, query: BaseQuery, handler: BaseQueryHandler):
        pass

    @abstractmethod
    def handle_query(self, query: BaseQuery):
        pass
