from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from finance_control_be.dependencies.db_session import get_session
from finance_control_be.dependencies.pagination import PaginationParameter

from finance_control_be.dependencies.user_information import get_user_information
from finance_control_be.models.method import Kind, Method
from finance_control_be.models.user import User

router = APIRouter(prefix="/methods", tags=["method"])


class MethodResponseDto(BaseModel):
    id: UUID
    name: str
    description: str | None
    kind: Kind
    color: str | None

    @classmethod
    def from_entity(cls, method: Method) -> "MethodResponseDto":
        return cls(
            id=method.id,
            name=method.name,
            description=method.description,
            kind=method.kind,
            color=method.color,
        )


class MethodPostDto(BaseModel):
    name: str
    description: str | None = None
    kind: Kind
    color: str | None = None

    def to_entity(self, username: str) -> Method:
        return Method(
            name=self.name,
            description=self.description,
            kind=self.kind,
            color=self.color,
            username=username,
        )


class MethodPatchDto(BaseModel):
    name: str | None = None
    description: str | None = None
    kind: Kind | None = None
    color: str | None = None


    def patch_entity(self, method: Method):
        method.name = self.name or method.name
        method.description = self.description or method.description
        method.kind = self.kind or method.kind
        method.color = self.color or method.color



@router.get("/")
def list_methods(
    user: Annotated[User, Depends(get_user_information)],
    pagination: Annotated[PaginationParameter, Depends()],
    session: Annotated[Session, Depends(get_session)],
) -> list[MethodResponseDto]:
    methods = (session.query(Method).filter(Method.username == user.username)
        .offset(pagination.offset)
        .limit(pagination.limit)
        .all())

    return [MethodResponseDto.from_entity(method) for method in methods]


@router.get("/{method_id}")
def get_method(
    user: Annotated[User, Depends(get_user_information)],
    method_id: UUID,
    session: Annotated[Session, Depends(get_session)],
) -> MethodResponseDto:
    method = session.query(Method).filter(Method.username == user.username, Method.id == method_id).first()
    if method is None:
        raise HTTPException(status_code=404)

    return MethodResponseDto.from_entity(method)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_method(
    user: Annotated[User, Depends(get_user_information)],
    method: MethodPostDto,
    session: Annotated[Session, Depends(get_session)],
) -> MethodResponseDto:
    method_entity = method.to_entity(user.username)
    session.add(method_entity)
    session.commit()

    return MethodResponseDto.from_entity(method_entity)


@router.patch("/{method_id}")
def update_method(
    user: Annotated[User, Depends(get_user_information)],
    method_id: UUID,
    method: MethodPatchDto,
    session: Annotated[Session, Depends(get_session)],
) -> MethodResponseDto:
    current_method = session.query(Method).filter(Method.username == user.username, Method.id == method_id).first()
    if current_method is None:
        raise HTTPException(status_code=404)

    method.patch_entity(current_method)
    session.merge(current_method)
    session.commit()

    return MethodResponseDto.from_entity(current_method)


@router.delete("/{method_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_method(
    user: Annotated[User, Depends(get_user_information)],
    method_id: UUID,
    session: Annotated[Session, Depends(get_session)],
) -> None:
    method = session.query(Method).filter(Method.username == user.username, Method.id == method_id).first()
    if method is None:
        raise HTTPException(status_code=404)

    session.delete(method)
    session.commit()
