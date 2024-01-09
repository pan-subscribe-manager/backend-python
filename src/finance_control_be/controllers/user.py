from typing import Annotated
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from finance_control_be.dependencies.user_information import get_user_information
from finance_control_be.models.user import User

router = APIRouter(prefix="/users", tags=["user"])


class UserInformationResponseDto(BaseModel):
    username: str
    full_name: str


@router.get("/me")
def user_info(user_information: Annotated[User, Depends(get_user_information)]) -> UserInformationResponseDto:
    return UserInformationResponseDto(username=user_information.username, full_name=user_information.full_name)
