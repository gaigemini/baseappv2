from pydantic import BaseModel, Field
from typing import Optional, Any, Literal, List
from enum import Enum
from datetime import datetime, timezone

REDIS_QUEUE_BASE_KEY: str = "otp_tasks"

class Status(str, Enum):
    """Status of a user and client"""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPEND = "SUSPENDED"
    DELETE = "DELETED"

class CurrentUser(BaseModel):
    """current user"""
    id: str
    name: str = Field(description="Content would be username or email or phonenumber")
    roles: List
    org_id: str
    token: str
    authority: int
    features: Optional[dict] = None
    bitws: Optional[dict] = None
    log_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent : Optional[str] = None

class CurrentClient(BaseModel):
    """current client"""
    id: str
    client_id: str = Field(description="Client ID")
    org_id: str
    log_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent : Optional[str] = None

class Pagination(BaseModel):
    """Pagination details."""
    total_items: int = Field(description="Total number of items.")
    total_pages: int = Field(description="Total number of pages.")
    current_page: int = Field(description="Current page.")
    items_per_page: int = Field(description="Number of items per page.")
class ApiResponse(BaseModel):
    """Representation of API response."""
    status: int = Field(description="Status of response, 0 is successfully.")
    message: Optional[str] = Field(
        default=None, description="Explaination of the error.")
    data: Optional[Any] = Field(
        default=None, description="Content of result from API call.")
    pagination: Optional[Pagination] = Field(
        default=None, description="Pagination details if applicable.")
    
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
    
class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class UpdateStatus(BaseModel):
    """Representation of update status model."""
    status: Status = Field(description="Status of the data.")

class DMSOperationType(str, Enum):
    TO_TRASH = "to_trash"
    RESTORE = "restore"