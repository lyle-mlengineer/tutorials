from pydantic import BaseModel


class User(BaseModel):
    name: str
    email: str
    is_active: bool
    is_logged_in: bool
