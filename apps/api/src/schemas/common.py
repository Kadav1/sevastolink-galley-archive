from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


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
