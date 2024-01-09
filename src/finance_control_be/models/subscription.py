from datetime import date
from decimal import Decimal
from enum import Enum
from uuid import UUID, uuid4

from dateutil.relativedelta import relativedelta
from sqlalchemy import ForeignKey, String, Date as SqlDate
from finance_control_be.models.base import Base
from sqlalchemy import DECIMAL as SqlDecimal, Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as SqlUUID


class PeriodUnit(Enum):
    day = "day"
    week = "week"
    month = "month"
    year = "year"


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[UUID] = mapped_column(
        SqlUUID(as_uuid=True), primary_key=True, default=uuid4()
    )

    name: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str | None] = mapped_column(String(256), nullable=True)

    price: Mapped[Decimal] = mapped_column(SqlDecimal(), nullable=False)
    currency: Mapped[str] = mapped_column(String(8), nullable=False)

    period: Mapped[int] = mapped_column(default=1)
    period_unit: Mapped[PeriodUnit] = mapped_column(SqlEnum(PeriodUnit), nullable=False)
    purchased_at: Mapped[date] = mapped_column(SqlDate(), nullable=False)  # we don't need to store time

    is_active: Mapped[bool] = mapped_column(default=True)

    method_id: Mapped[UUID] = mapped_column(ForeignKey("methods.id"))


    def period_to_timedelta(self) -> relativedelta:
        match self.period_unit:
            case PeriodUnit.day:
                return relativedelta(days=self.period)
            case PeriodUnit.week:
                return relativedelta(weeks=self.period)
            case PeriodUnit.month:
                return relativedelta(months=self.period)
            case PeriodUnit.year:
                return relativedelta(years=self.period)
            case _:
                raise ValueError(f"Invalid period unit: {self.period_unit}")
