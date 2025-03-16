import json
from typing import Literal

import redis
from redis.exceptions import ConnectionError

from ...application.commands.database_queue_writer import \
    BaseDataBaseQueueWriter
from ...domain.entities.base_entity import BaseEntity
from ...exceptions.application import DatabaseChangesPublishingError


class RedisQueueWriter(BaseDataBaseQueueWriter):
    def write(self, entity: BaseEntity, command: Literal["create", "delete", "update"]):
        try:
            r = redis.Redis(host="localhost", port=6379, db=0)
            message: dict = {"command": command, "data": entity.model_dump()}
            r.lpush("alarm_queue", json.dumps(message))
        except ConnectionError:
            raise DatabaseChangesPublishingError(
                "We have an internal error. Please try again in a few minutes."
            )
