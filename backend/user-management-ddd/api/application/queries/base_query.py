from typing import Optional

from pydantic import BaseModel


class BaseQuery(BaseModel):
    idempotency_key: Optional[str] = None
