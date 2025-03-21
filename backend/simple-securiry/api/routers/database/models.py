from sqlalchemy import Column
from sqlalchemy.orm import MappedColumn, mapped_column

from .database import Base


class UserInDb(Base):
    __tablename__ = "users"

    id: MappedColumn[str] = mapped_column(primary_key=True)
    name: MappedColumn[str] = mapped_column(nullable=False)
    email: MappedColumn[str] = mapped_column(nullable=False, index=True, unique=True)
    password: MappedColumn[str] = mapped_column(nullable=False)
    is_active: MappedColumn[bool] = mapped_column(default=False)
    is_logged_in: MappedColumn[bool] = mapped_column(default=False)
