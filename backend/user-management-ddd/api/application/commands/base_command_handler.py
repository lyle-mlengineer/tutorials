from abc import ABC, abstractmethod

from .base_command import BaseCommand


class BaseCommandHandler(ABC):
    @abstractmethod
    def handle(self, command: BaseCommand):
        pass
