# /core/schemas.py
from pydantic import BaseModel, Field
from typing import TypeVar, Generic, List, Optional, Any

# This line was the source of the circular import and has been removed:
# from .schemas import SuccessResponse 

# This allows us to create a generic response model
T = TypeVar('T')

class SuccessResponse(BaseModel, Generic[T]):
    """
    Standard success response wrapper.
    """
    status: str = Field("success", description="The status of the response.")
    data: T = Field(..., description="The main data payload of the response.")

class ErrorDetail(BaseModel):
    """
    A detailed error message structure.
    """
    status: str
    title: str
    detail: str

class ErrorResponse(BaseModel):
    """
    Standard error response wrapper.
    """
    status: str = Field("error", description="The status of the response.")
    errors: List[ErrorDetail] = Field(..., description="A list of one or more error objects.")
