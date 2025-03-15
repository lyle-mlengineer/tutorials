from ...domain.events.base_event import BaseEvent
from ...domain.events.base_event_publisher import BaseEventPublisher


class CommandLineEventPublisher(BaseEventPublisher):
    def publish(self, event: BaseEvent) -> None:
        print(event.model_dump())
