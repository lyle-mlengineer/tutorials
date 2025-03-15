from abc import ABC, abstractmethod

from .base_event import BaseEvent


class BaseEventPublisher(ABC):
    @abstractmethod
    def publish(self, event: BaseEvent) -> None:
        pass
