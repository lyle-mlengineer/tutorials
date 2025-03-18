from ...application.services.email_service import BaseEmailService
from ...domain.entities.email_entity import EmailEntity


class CMDEmailService(BaseEmailService):
    def __init__(self):
        super().__init__()

    def send_email(self, entity: EmailEntity) -> None:
        print(entity.model_dump())

    def publish_event(self) -> None:
        pass
