from typing import Optional

from pydantic import BaseModel


class BaseCommand(BaseModel):
    idempotency_key: Optional[str] = None
