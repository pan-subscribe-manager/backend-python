from typing import TypedDict


class UserAuthenticationPayload(TypedDict):
    sub: str  # subject, username.
