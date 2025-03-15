from ...application.commands.base_command import BaseCommand
from ...application.commands.base_command_handler import BaseCommandHandler
from ...application.queries.base_query import BaseQuery
from ...application.queries.base_query_handler import BaseQueryHandler
from .base_mediator import BaseMediator


class Mediator(BaseMediator):
    def __init__(self):
        super().__init__()
        self._command_handlers = {}
        self._query_handlers = {}

    def register_command(self, command: BaseCommand, handler: BaseCommandHandler):
        self._command_handlers[command] = handler

    def handle_command(self, command: BaseCommand):
        handler: BaseCommandHandler = self._command_handlers[command.__class__]
        return handler.handle(command)

    def handle_query(self, query):
        return super().handle_query(query)

    def register_query(self, query, handler):
        return super().register_query(query, handler)
