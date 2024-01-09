from typing import Generator
from sqlalchemy.orm import Session

from finance_control_be.database import SessionLocal


def get_session() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session
