from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
from finance_control_be.auth.exceptions import InvalidCredentialsException
from finance_control_be.auth.jwt import AccessTokenManager

from finance_control_be.dependencies.db_session import get_session

router = APIRouter(prefix="/token", tags=["user", "authentication"])


class Token(BaseModel):
    access_token: str
    token_type: str


@router.post("/", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    access_token_manager: Annotated[AccessTokenManager, Depends()],
    session: Annotated[Session, Depends(get_session)],
):
    try:
        token = access_token_manager.authenticate_and_create_access_token(
            form_data.username, form_data.password, session
        )
    except InvalidCredentialsException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    return {"access_token": token, "token_type": "bearer"}
