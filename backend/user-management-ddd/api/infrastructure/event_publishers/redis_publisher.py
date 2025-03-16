import json

import redis
from redis.exceptions import ConnectionError

from ...domain.events.base_event import BaseEvent
from ...domain.events.base_event_publisher import BaseEventPublisher
from ...exceptions.application import EventPublicationError


class RedisEventPublisher(BaseEventPublisher):
    def publish(self, event: BaseEvent) -> None:
        try:
            redis_client = redis.StrictRedis(host="localhost", port=6379, db=0)
            event: dict = event.model_dump()
            event_str: str = json.dumps(event)
            channel: str = "events"
            redis_client.publish(channel, event_str)
        except ConnectionError:
            raise EventPublicationError(
                "We have an internal error. Please try again in a few minutes."
            )
