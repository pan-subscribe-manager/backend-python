from uuid import uuid4

from enum import Enum
from sqlalchemy import ForeignKey, String, Text
from finance_control_be.models.base import Base
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.dialects.postgresql import UUID as SqlUUID
from uuid import UUID

from finance_control_be.models.subscription import Subscription


class Kind(Enum):
    bank_account = "bank_account"
    credit_card = "credit_card"
    debit_card = "debit_card"
    cash = "cash"  # ?
    other = "other"


class Method(Base):
    __tablename__ = "methods"

    id: Mapped[UUID] = mapped_column(
        SqlUUID(as_uuid=True), primary_key=True, default=uuid4()
    )
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    kind: Mapped[Kind] = mapped_column(SqlEnum(Kind), nullable=False)

    color: Mapped[str | None] = mapped_column(String(32), nullable=True)

    subscriptions: Mapped[list[Subscription]] = relationship()

    username: Mapped[str] = mapped_column(ForeignKey("users.username"))
