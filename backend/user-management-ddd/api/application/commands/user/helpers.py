from uuid import UUID, uuid4


def generate_id(prefix: str = "US") -> str:
    raw_id: UUID = uuid4()
    id: str = f"{prefix}-{str(raw_id)}"
    return id


def hash_password(password: str) -> str:
    return password
