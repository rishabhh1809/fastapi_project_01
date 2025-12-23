from typing import Generic, TypeVar, Optional, List
from pydantic import BaseModel

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    code: int
    message: str
    status: str
    data: Optional[T] = None

    @classmethod
    def success(
        cls, message: str = "Success", data: Optional[T] = None, code: int = 200
    ):
        return cls(code=code, message=message, status="success", data=data)

    @classmethod
    def error(cls, message: str = "Something went wrong", code: int = 400):
        return cls(code=code, message=message, status="error", data=None)


class PaginatedData(BaseModel, Generic[T]):
    items: List[T]
    total: int
    skip: int
    limit: int

    class Config:
        from_attributes = True


class ErrorDetail(BaseModel):
    field: Optional[str] = None
    message: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int
