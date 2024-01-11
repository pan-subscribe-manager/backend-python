from datetime import datetime, timedelta
from typing import cast

from jose import jwt, JWTError
from finance_control_be.auth.const import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    SECRET_KEY,
)
from sqlalchemy.orm import Session
from finance_control_be.auth.exceptions import (
    InactiveUserException,
    InvalidCredentialsException,
    InvalidTokenException,
)

from finance_control_be.auth.payload import UserAuthenticationPayload
from finance_control_be.auth.password import PasswordManager
from finance_control_be.models.user import User


class AccessTokenManager:
    def __init__(
        self,
        password_manager: PasswordManager | None = None,
        secret_key: str | None = None,
        algorithm: str | None = None,
        access_token_expire_minutes: int | None = None,
    ):
        self.password_manager = password_manager or PasswordManager()
        self.secret_key = secret_key or SECRET_KEY
        self.algorithm = algorithm or ALGORITHM
        self.access_token_expire_minutes = (
            access_token_expire_minutes or ACCESS_TOKEN_EXPIRE_MINUTES
        )

    def get_password_manager(self) -> PasswordManager:
        return self.password_manager

    def authenticate_and_create_access_token(
        self, username: str, password: str, session: Session
    ) -> str:
        user = self._get_user_info(
            username=username, password=password, session=session
        )
        return self._create_access_token(data={"sub": user.username})

    def retrieve_info_from_token(self, token: str) -> UserAuthenticationPayload:
        try:
            return cast(
                UserAuthenticationPayload,
                jwt.decode(token, self.secret_key, algorithms=[self.algorithm]),
            )
        except JWTError:
            raise InvalidTokenException()

    def _get_user_info(self, username: str, password: str, session: Session) -> User:
        user = session.query(User).filter(User.username == username).first()
        if not user:
            raise InvalidCredentialsException()

        if user.disabled:
            raise InactiveUserException()

        if not user.verify_password(
            password=password, password_manager=PasswordManager()
        ):
            raise InvalidCredentialsException()

        return user

    def _create_access_token(
        self, data: UserAuthenticationPayload, expires_delta: timedelta | None = None
    ) -> str:
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=self.access_token_expire_minutes
            )

        to_encode = {**data, "exp": expire}
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt


def create_access_token_manager() -> AccessTokenManager:
    return AccessTokenManager()
