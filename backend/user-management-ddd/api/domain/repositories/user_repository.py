from abc import abstractmethod
from typing import Optional

from ...domain.entities.user import User
from .base_repository import BaseRepository


class UserRepository(BaseRepository):
    @abstractmethod
    def get_user(self, email: str) -> Optional[User]:
        pass
