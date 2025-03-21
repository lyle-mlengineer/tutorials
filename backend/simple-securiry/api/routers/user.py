from typing import Annotated, Literal

from fastapi import (APIRouter, Depends, Header, HTTPException, Response,
                     Security, status)
from fastapi.security import OAuth2PasswordRequestForm

from .dependencies import (UserService, get_current_logged_in_user, check_authorization,
                           get_user_service)
from .exceptions import (AccountAlreadyExistsError, AccountNotFoundError,
                         InvalidCredentialsError)
from .schemas import (CreateUserCommand, DeleteUserCommand, GetUserQuery,
                      ListUsersResponse, LoginUserCommand, UpdateUserCommand,
                      UserCreatedResponse, UserFetchedResponse,
                      UserLoggedInResponse, UserUpdatedResponse)

user_router = APIRouter(prefix="/users", tags=["User"])


@user_router.post(
    "/register", status_code=status.HTTP_201_CREATED, response_model=UserCreatedResponse
)
def register(
    command: CreateUserCommand, service: UserService = Depends(get_user_service)
):
    try:
        response = service.create_user(command=command)
    except AccountAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return response


@user_router.post(
    "/login", status_code=status.HTTP_200_OK, response_model=UserLoggedInResponse
)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: UserService = Depends(get_user_service),
):
    try:
        reponse = service.login_user(
            command=LoginUserCommand(
                email=form_data.username, password=form_data.password
            )
        )
    except (InvalidCredentialsError, AccountNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return reponse

@user_router.get("/authority")
def test(_ : Annotated[None, Security(check_authorization, scopes=["own:read"])]):
    return {'hello': 'auth passed'}


@user_router.get(
    "/me", status_code=status.HTTP_200_OK, response_model=UserFetchedResponse
)
def get_logged_in_user(
    user: Annotated[
        UserFetchedResponse, Security(get_current_logged_in_user, scopes=["users:delete"])
    ],
):
    return user


@user_router.get(
    "/{id}", status_code=status.HTTP_200_OK, response_model=UserFetchedResponse
)
def get_user(id: str, service: UserService = Depends(get_user_service)):
    return service.get_user(query=GetUserQuery(id=id))


@user_router.get("/", status_code=status.HTTP_200_OK, response_model=ListUsersResponse)
def list_users(
    offset: int = 0,
    limit: int = 10,
    sort: Literal["asc", "desc"] = "asc",
    sort_col: Literal["id", "name", "email"] = "name",
    service: UserService = Depends(get_user_service),
):
    return service.list_users(offset, limit, sort, sort_col)


@user_router.put(
    "/{id}", status_code=status.HTTP_200_OK, response_model=UserUpdatedResponse
)
def update(
    id: str,
    command: UpdateUserCommand,
    service: UserService = Depends(get_user_service),
):
    return service.update_user(id=id, command=command)


@user_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(id: str, service: UserService = Depends(get_user_service)):
    return service.delete_user(command=DeleteUserCommand(id=id))
