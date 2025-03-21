from abc import ABC, abstractmethod

from sqlalchemy import asc, desc
from sqlalchemy.exc import IntegrityError, NoResultFound

from ..exceptions import AccountAlreadyExistsError, AccountNotFoundError
from .models import UserInDb


class BaseRepository(ABC):
    @abstractmethod
    def save(self, user: UserInDb) -> UserInDb:
        pass

    @abstractmethod
    def get(self, id: str) -> UserInDb:
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> UserInDb:
        pass

    @abstractmethod
    def update(self, id: str, user: UserInDb) -> UserInDb:
        pass

    @abstractmethod
    def delete(self, id: str) -> UserInDb:
        pass

    @abstractmethod
    def list_users(self, offset: int, limit: int, sort: str) -> list[UserInDb] | list:
        pass


class SQLUserRepository(BaseRepository):
    def __init__(self, session):
        super().__init__()
        self.session = session

    def save(self, user: UserInDb) -> UserInDb:
        try:
            self.session.add(user)
            self.session.commit()
            self.session.refresh(user)
        except IntegrityError:
            raise AccountAlreadyExistsError(
                f"The user with email '{user.email}' already exists!"
            )
        return user

    def get(self, id: str) -> UserInDb:
        try:
            user: UserInDb = (
                self.session.query(UserInDb).filter(UserInDb.id == id).scalar()
            )
        except NoResultFound:
            raise AccountNotFoundError("Account with id address '{id}' not found!")
        return user

    def get_by_email(self, email: str) -> UserInDb:
        try:
            user: UserInDb = (
                self.session.query(UserInDb).filter(UserInDb.email == email).one()
            )
        except NoResultFound:
            print("account not found")
            raise AccountNotFoundError(
                "Account with email address '{email}' not found!"
            )
        return user

    def update(self, user: UserInDb) -> UserInDb:
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def delete(self, id: str) -> UserInDb:
        user: UserInDb = self.get(id=id)
        self.session.delete(user)
        self.session.commit()
        return user

    def list_users(
        self, offset: int, limit: int, sort: str, sort_col: str
    ) -> list[UserInDb] | list:
        order = {"asc": asc, "desc": desc}
        col = {"id": UserInDb.id, "email": UserInDb.email, "name": UserInDb.name}
        users: list[UserInDb] = (
            self.session.query(UserInDb)
            .order_by(order[sort](col[sort_col]))
            .offset(offset)
            .limit(limit)
            .all()
        )
        return users
