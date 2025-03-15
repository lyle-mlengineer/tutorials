from uuid import UUID, uuid4

from pydantic import BaseModel


class EntityId:
    def __init__(self, id_prefix: str):
        self._id: str = f"{id_prefix}-{str(uuid4())}"

    @property
    def id(self) -> str:
        return self._id
