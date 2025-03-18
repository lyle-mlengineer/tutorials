from typing import Literal

from .base_entity import BaseEntity


class EmailEntity(BaseEntity):
    title: str
    body: str
    recipients: list[str]
    email_type: Literal["AccountActivation", "PasswordReset"]
