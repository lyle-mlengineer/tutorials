from typing import Annotated

import jwt
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session

from .database.database import get_session
from .database.repository import BaseRepository, SQLUserRepository
# from jose import jwt, JWTError
from .schemas import GetUserQuery, UserFetchedResponse
from .services.user import UserService

SECRET_KEY = "key"
ALGORITHM = "HS256"


def get_repository(session: Session = Depends(get_session)):
    repository: BaseRepository = SQLUserRepository(session=session)
    return repository


def get_user_service(
    repository: BaseRepository = Depends(get_repository),
) -> UserService:
    return UserService(repository=repository)


async def get_current_logged_in_user(
    security_scopes: SecurityScopes,
    authorization: Annotated[str | None, Header()],
    service: UserService = Depends(get_user_service),
) -> UserFetchedResponse:
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    if not authorization:
        HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization headers.",
            headers={"WWW-Authenticate": authenticate_value},
        )
    token: str = authorization.split()[-1]
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload: dict = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        scopes: list[str] = payload.get("scopes", [])
        for scope in security_scopes.scopes:
            if scope not in scopes:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not enough permissions",
                    headers={"WWW-Authenticate": authenticate_value},
                )
    except InvalidTokenError:
        raise credentials_exception
    return service.get_user(query=GetUserQuery(id=user_id))
