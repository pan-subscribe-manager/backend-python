from datetime import date, datetime
from decimal import Decimal
from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session
from finance_control_be.dependencies.db_session import get_session
from finance_control_be.dependencies.pagination import PaginationParameter

from finance_control_be.dependencies.user_information import get_user_information
from finance_control_be.models.method import Method
from finance_control_be.models.subscription import PeriodUnit, Subscription
from finance_control_be.models.user import User


def verify_method_access(
    method_id: UUID,
    user: Annotated[User, Depends(get_user_information)],
    session: Annotated[Session, Depends(get_session)],
):
    # verify if the user has access to the method
    method = (
        session.query(Method)
        .filter(Method.username == user.username, Method.id == method_id)
        .count()
    )
    if method == 0:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


router = APIRouter(
    prefix="/methods/{method_id}/subscriptions",
    tags=["subscription"],
    dependencies=[Depends(verify_method_access)],
)


class SubscriptionResponseDto(BaseModel):
    id: UUID
    name: str
    description: str | None

    price: Decimal
    currency: str

    period: int
    period_unit: PeriodUnit
    purchased_at: date

    is_active: bool

    @classmethod
    def from_entity(cls, subscription: Subscription) -> "SubscriptionResponseDto":
        return cls(
            id=subscription.id,
            name=subscription.name,
            description=subscription.description,
            price=subscription.price,
            currency=subscription.currency,
            period=subscription.period,
            period_unit=subscription.period_unit,
            purchased_at=subscription.purchased_at,
            is_active=subscription.is_active,
        )


class SubscriptionPostDto(BaseModel):
    name: str
    description: str | None = None

    price: Decimal
    currency: str

    period: int
    period_unit: PeriodUnit
    purchased_at: date = datetime.now().date()

    is_active: bool | None = None

    def to_entity(self, method_id: UUID) -> Subscription:
        return Subscription(
            name=self.name,
            description=self.description,
            price=self.price,
            currency=self.currency,
            period=self.period,
            period_unit=self.period_unit,
            purchased_at=self.purchased_at,
            is_active=self.is_active,
            method_id=method_id,
        )


class SubscriptionPatchDto(BaseModel):
    name: str | None = None
    description: str | None = None

    price: Decimal | None = None
    currency: str | None = None

    period: int | None = None
    period_unit: PeriodUnit | None = None
    purchased_at: date | None = None

    is_active: bool | None = None

    def patch_entity(self, subscription: Subscription):
        subscription.name = self.name or subscription.name
        subscription.description = self.description or subscription.description
        subscription.price = self.price or subscription.price
        subscription.currency = self.currency or subscription.currency
        subscription.period = self.period or subscription.period
        subscription.period_unit = self.period_unit or subscription.period_unit
        subscription.purchased_at = self.purchased_at or subscription.purchased_at
        subscription.is_active = self.is_active or subscription.is_active


class SubscriptionNextPaidDate(BaseModel):
    """The next date of the subscription payment."""

    model_config = ConfigDict(ser_json_timedelta="iso8601")

    last_purchased_at: date
    next_date_of_payment: date


@router.get("/")
def list_subscriptions(
    method_id: UUID,
    pagination: Annotated[PaginationParameter, Depends()],
    session: Annotated[Session, Depends(get_session)],
):
    subscriptions = (
        session.query(Subscription)
        .filter(Subscription.method_id == method_id)
        .offset(pagination.offset)
        .limit(pagination.limit)
        .all()
    )

    return [
        SubscriptionResponseDto.from_entity(subscription)
        for subscription in subscriptions
    ]


@router.get("/{subscription_id}")
def get_subscription(
    subscription_id: UUID,
    session: Annotated[Session, Depends(get_session)],
):
    subscription = (
        session.query(Subscription).filter(Subscription.id == subscription_id).first()
    )

    if subscription is None:
        raise HTTPException(status_code=404)

    return SubscriptionResponseDto.from_entity(subscription)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_subscription(
    method_id: UUID,
    subscription: SubscriptionPostDto,
    session: Annotated[Session, Depends(get_session)],
):
    subscription_entity = subscription.to_entity(method_id=method_id)
    session.add(subscription_entity)
    session.commit()

    return SubscriptionResponseDto.from_entity(subscription_entity)


@router.patch("/{subscription_id}")
def update_subscription(
    subscription_id: UUID,
    subscription: SubscriptionPatchDto,
    session: Annotated[Session, Depends(get_session)],
):
    current_subscription = (
        session.query(Subscription).filter(Subscription.id == subscription_id).first()
    )
    if current_subscription is None:
        raise HTTPException(status_code=404)

    subscription.patch_entity(current_subscription)
    session.merge(current_subscription)
    session.commit()

    return SubscriptionResponseDto.from_entity(current_subscription)


@router.delete("/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subscription(
    subscription_id: UUID,
    session: Annotated[Session, Depends(get_session)],
):
    subscription = (
        session.query(Subscription).filter(Subscription.id == subscription_id).first()
    )
    if subscription is None:
        raise HTTPException(status_code=404)

    session.delete(subscription)
    session.commit()


@router.get(
    "/{subscription_id}/next-payment-date",
    description="Get the estimated date of the next payment.",
)
def get_estimated_next_paid_date(
    subscription_id: UUID,
    session: Annotated[Session, Depends(get_session)],
) -> SubscriptionNextPaidDate:
    subscription = (
        session.query(Subscription).filter(Subscription.id == subscription_id).first()
    )
    if subscription is None:
        raise HTTPException(status_code=404)

    today = datetime.now().date()
    td = subscription.period_to_timedelta()

    # calculate the next date of payment
    # FIXME: performance?
    next_date_of_payment = subscription.purchased_at
    while next_date_of_payment <= today:
        next_date_of_payment += td

    return SubscriptionNextPaidDate(
        last_purchased_at=subscription.purchased_at,
        next_date_of_payment=next_date_of_payment,
    )


@router.post(
    "/{subscription_id}/mark-purchased",
    status_code=status.HTTP_204_NO_CONTENT,
)
def mark_subscription_as_purchased(
    subscription_id: UUID,
    session: Annotated[Session, Depends(get_session)],
):
    subscription = (
        session.query(Subscription).filter(Subscription.id == subscription_id).first()
    )
    if subscription is None:
        raise HTTPException(status_code=404)

    subscription.purchased_at = datetime.now().date()
    session.merge(subscription)
    session.commit()
