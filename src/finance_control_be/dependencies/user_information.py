from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from finance_control_be.dependencies.db_session import get_session
from finance_control_be.auth.oauth import oauth2_scheme
from finance_control_be.auth.jwt import AccessTokenManager, create_access_token_manager
from finance_control_be.models.user import User


def get_user_information(
    session: Annotated[Session, Depends(get_session)],
    token: Annotated[str, Depends(oauth2_scheme)],
    access_token_manager: Annotated[AccessTokenManager, Depends(create_access_token_manager)],
) -> User:
    payload = access_token_manager.retrieve_info_from_token(token)

    # find the user according to the payload
    user = session.query(User).filter(User.username == payload['sub']).first()
    if user is None:
        raise HTTPException(status_code=401)

    return user
