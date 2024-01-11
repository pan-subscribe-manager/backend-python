from tkinter import E
from turtle import st
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from loguru import logger
import psycopg2
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from finance_control_be.auth.exceptions import InvalidCredentialsException
from finance_control_be.auth.jwt import AccessTokenManager, create_access_token_manager

from finance_control_be.dependencies.db_session import get_session
from finance_control_be.models.user import User

router = APIRouter(tags=["user", "authentication"])


class Token(BaseModel):
    access_token: str
    token_type: str


class UserRegisterRequest(BaseModel):
    username: str
    password: str
    full_name: str | None = None
    email: str | None = None


class UserResponse(BaseModel):
    username: str
    full_name: str | None
    email: str | None


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    access_token_manager: Annotated[AccessTokenManager, Depends(create_access_token_manager)],
    session: Annotated[Session, Depends(get_session)],
) -> Token:
    try:
        token = access_token_manager.authenticate_and_create_access_token(
            form_data.username, form_data.password, session
        )
    except InvalidCredentialsException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    return Token(access_token=token, token_type="bearer")


@router.post("/register", response_model=UserResponse)
async def register(
    user: UserRegisterRequest,
    session: Annotated[Session, Depends(get_session)],
    access_token_manager: Annotated[AccessTokenManager, Depends(create_access_token_manager)],
) -> UserResponse:
    new_user = User.new_hashed(password=user.password, password_manager=access_token_manager.get_password_manager())
    new_user.username = user.username
    new_user.full_name = user.full_name
    new_user.email = user.email

    try:
        session.add(new_user)
        session.commit()
    except Exception as e:
        session.rollback()

        if isinstance(e, IntegrityError):
            logger.error("{} -> ({}) {}", type(e), type(e.orig), e.orig)
            if isinstance(e.orig, psycopg2.errors.UniqueViolation):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Username already exists",
                )

        logger.error("{} {}", type(e), e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )

    return UserResponse(username=user.username, full_name=user.full_name, email=user.email)
