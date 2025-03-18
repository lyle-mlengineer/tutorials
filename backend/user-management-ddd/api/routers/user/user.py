from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from ...application.commands.user.user_commands import (
    ActivateUserAccountCommand, CreateUserCommand, DeleteUserCommand,
    LogoutUserCommand, ResetPasswordCommand, UpdateUserCommand)
from ...application.queries.user.user_queries import (
    GetUserQuery, ListUsersQuery, LoginUserQuery, RequestPasswordResetQuery)
from ...application.responses.user_responses import (CreateUserResponse,
                                                     GetUserResponse,
                                                     ListUsersResponse,
                                                     LoginUserResponse,
                                                     UpdateUserResponse)
from ...application.services.user_service import UserService
from ...exceptions.application import (AccountAlreadyExistsError,
                                       AccountNotActiveError,
                                       AccountNotFoundError,
                                       DatabaseChangesPublishingError,
                                       EventPublicationError,
                                       InvalidCredentialsError)
from ..dependencies import BaseService, get_current_user, get_user_service

router = APIRouter(tags=["User"], prefix="/users")


@router.post(
    "/oauth/register",
    status_code=status.HTTP_201_CREATED,
    response_model=CreateUserResponse,
)
async def register_user(
    command: CreateUserCommand,
    service: BaseService = Depends(get_user_service),
    x_idmp_key: Annotated[str | None, Header()] = None,
):
    try:
        command.idempotency_key = x_idmp_key
        response = service.create_entity(command=command)
    except AccountAlreadyExistsError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except (EventPublicationError, DatabaseChangesPublishingError) as e:
        raise HTTPException(status_code=502, detail=str(e))
    else:
        return response


@router.get("/oauth/me", status_code=status.HTTP_200_OK)
async def me(current_user: Annotated[dict, Depends(get_current_user)]):
    return current_user


@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=GetUserResponse)
async def get_user(
    id: str,
    service: BaseService = Depends(get_user_service),
    x_idmp_key: Annotated[str | None, Header()] = None,
):
    try:
        response = service.get_entity(
            query=GetUserQuery(id=id, idempotency_key=x_idmp_key)
        )
    except AccountNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    else:
        return response


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    id: str,
    service: BaseService = Depends(get_user_service),
    x_idmp_key: Annotated[str | None, Header()] = None,
):
    try:
        response = service.delete_entity(
            command=DeleteUserCommand(id=id, idempotency_key=x_idmp_key)
        )
    except AccountNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    # Permission denied
    else:
        return response


@router.get("/", status_code=status.HTTP_200_OK, response_model=ListUsersResponse)
async def list_users(
    skip: int = 0,
    limit: int = 10,
    sort: Literal["asc", "desc"] = "asc",
    service: BaseService = Depends(get_user_service),
    x_idmp_key: Annotated[str | None, Header()] = None,
):
    try:
        response = service.list_entities(
            query=ListUsersQuery(
                skip=skip, limit=limit, sort=sort, idempotency_key=x_idmp_key
            )
        )
    except AccountNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    else:
        return response


@router.put("/{id}", status_code=status.HTTP_200_OK, response_model=UpdateUserResponse)
async def update_user(
    id: str,
    command: UpdateUserCommand,
    service: BaseService = Depends(get_user_service),
    x_idmp_key: Annotated[str | None, Header()] = None,
):
    try:
        command.id = id
        command.idempotency_key = x_idmp_key
        response = service.update_entity(command=command)
    except AccountNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except (EventPublicationError, DatabaseChangesPublishingError) as e:
        raise HTTPException(status_code=502, detail=str(e))
    else:
        return response


@router.post(
    "/oauth/login", status_code=status.HTTP_200_OK, response_model=LoginUserResponse
)
async def login_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    x_idmp_key: Annotated[str | None, Header()] = None,
    service: UserService = Depends(get_user_service),
):
    try:
        query: LoginUserQuery = LoginUserQuery(
            username=form_data.username,
            password=form_data.password,
            idempotency_key=x_idmp_key,
        )
        response = service.login_user(query=query)
    except (InvalidCredentialsError, AccountNotFoundError):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    except AccountNotActiveError:
        raise HTTPException(status_code=401, detail="Account not active")
    else:
        return response


@router.get("/oauth/logout", status_code=status.HTTP_200_OK)
async def logout_user(
    current_user: Annotated[dict, Depends(get_current_user)],
    x_idmp_key: Annotated[str | None, Header()] = None,
    service: UserService = Depends(get_user_service),
):
    service.logout(
        command=LogoutUserCommand(idempotency_key=x_idmp_key), id=current_user.id
    )
    return current_user


@router.get("/oauth/reset_password_request", status_code=status.HTTP_204_NO_CONTENT)
async def reset_password_request(
    id: str,
    idmp_key: Annotated[str | None, Header()] = None,
    service: UserService = Depends(get_user_service),
):
    service.request_password_reset(
        query=RequestPasswordResetQuery(idempotency_key=idmp_key, id=id)
    )
    return


@router.post("/oauth/reset_password", status_code=status.HTTP_204_NO_CONTENT)
async def reset_password(
    id: str,
    idmp_key: Annotated[str | None, Header()] = None,
    service: UserService = Depends(get_user_service),
):
    service.reset_password(
        command=ResetPasswordCommand(idempotency_key=idmp_key, id=id)
    )
    return


@router.get("/oauth/activate_account/{token}", status_code=status.HTTP_204_NO_CONTENT)
async def activate_account(
    token: str,
    x_idmp_key: Annotated[str | None, Header()] = None,
    service: UserService = Depends(get_user_service),
):
    service.activate_user_account(
        command=ActivateUserAccountCommand(token=token, idempotency_key=x_idmp_key)
    )
