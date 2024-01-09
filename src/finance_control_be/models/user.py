from typing import Self
from sqlalchemy import String
from finance_control_be.models.base import Base
from sqlalchemy.orm import Mapped, mapped_column

from finance_control_be.dependencies.password_manager import PasswordManager

class User(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(64), primary_key=True)
    password: Mapped[str] = mapped_column(String(128), nullable=False)  # argon2
    full_name: Mapped[str] = mapped_column(String(128))  # fallback to username
    disabled: Mapped[bool] = mapped_column(default=False)
    email: Mapped[str] = mapped_column(String(256))  # optional


    @classmethod
    def new_hashed(cls, password: str, password_manager: PasswordManager) -> Self:
        user = cls()
        user.password = password_manager.hash_password(password=password)

        return user

    def verify_password(self, password: str, password_manager: PasswordManager) -> bool:
        return password_manager.verify_password(input_password=password, hash=self.password)


    def get_full_name(self) -> str:
        return self.full_name or self.username
