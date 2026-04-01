from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


def error_detail(code: str, message: str) -> dict:
    """Return a structured error detail dict for use with HTTPException.

    The custom exception handler in main.py converts this to the wire format:
        {"error": {"code": "...", "message": "..."}}
    """
    return {"code": code, "message": message}


class ListMeta(BaseModel):
    total: int
    limit: int
    offset: int


class ApiResponse(BaseModel, Generic[T]):
    data: T


class ListResponse(BaseModel, Generic[T]):
    data: list[T]
    meta: ListMeta


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: dict[str, str] = {}


class ErrorResponse(BaseModel):
    error: ErrorDetail
