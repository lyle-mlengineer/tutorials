from abc import ABC, abstractmethod

from ...domain.entities.email_entity import EmailEntity


class BaseEmailService(ABC):
    @abstractmethod
    def send_email(self, entity: EmailEntity) -> None:
        pass

    @abstractmethod
    def publish_event(self) -> None:
        pass
