from pydantic import BaseModel, Field
from typing import Optional, Any, Literal
from enum import Enum
from datetime import datetime, timezone

class Status(str, Enum):
    """Status of a user and client"""
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    DELETED = "DELETED"

class CurrentUser(BaseModel):
    """current user"""
    id: str
    username: str
    roles: str
    org_id: str
    org_name: str
    org_initial: str
    org_ref_id: str
    authority: int

class ApiResponse(BaseModel):
    """Representation of API response."""
    status: int = Field(description="Status of response, 0 is successfully.")
    message: Optional[str] = Field(
        default=None, description="Explaination of the error.")
    data: Optional[Any] = Field(
        default=None, description="Content of result from API call.")
    
class LogInfo(BaseModel):
    """Representation of Logging for information."""
    log_id: Optional[str] = Field(
        default=None, description="Logging id of process flow.")
    info: Optional[Any] = Field(
        default=None, description="Content of logging information.")

class LogError(BaseModel):
    """Representation of Logging for information."""
    log_id: str = Field(description="Logging id of process flow.")
    error_id: int = Field(description="Error id.")
    error: Any = Field(description="Error description.")
class Pagination(BaseModel):
    """Pagination details."""
    total_items: int = Field(description="Total number of items.")
    total_pages: int = Field(description="Total number of pages.")
    current_page: int = Field(description="Current page.")
    items_per_page: int = Field(description="Number of items per page.")

class PaginatedApiResponse(ApiResponse):
    """API response with paginated data."""
    pagination: Optional[Pagination] = Field(
        default=None, description="Pagination details if applicable.")
