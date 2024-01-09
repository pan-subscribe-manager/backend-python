from pydantic import BaseModel


class PaginationParameter(BaseModel):
    """Pagination parameters.

    FIXME: Performance concerns."""

    limit: int = 10
    offset: int = 0
