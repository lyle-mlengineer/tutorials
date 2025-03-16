from typing import Literal

from ...application.commands.database_queue_writer import \
    BaseDataBaseQueueWriter
from ...domain.entities.base_entity import BaseEntity


class CMDQueueWriter(BaseDataBaseQueueWriter):
    def write(self, entity: BaseEntity, command: Literal["create", "delete", "update"]):
        print({"command": command, "data": entity.model_dump()})
