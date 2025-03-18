from uuid import UUID, uuid4

from ....domain.entities.user import User


def generate_id(prefix: str = "US") -> str:
    raw_id: UUID = uuid4()
    id: str = f"{prefix}-{str(raw_id)}"
    return id


def decode_token(token: str) -> str:
    return "US-e2005f88-b45c-43c4-ba2e-30cf4dc0f417"


def check_password(password: str, hashed_password: str) -> bool:
    return password == hashed_password
