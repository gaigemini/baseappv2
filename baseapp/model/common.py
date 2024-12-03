from pydantic import BaseModel, Field
from typing import Optional, Any

class CurrentUser(BaseModel):
    """current user"""
    id: str
    username: str
    r_id: str
    org_id: str
    org_name: str
    org_initial: str
    org_code: str
    org_ref_id: str
    org_reg_domain: Optional[str]
    org_private_db: Optional[int]
    org_private_bucket: Optional[int]
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
