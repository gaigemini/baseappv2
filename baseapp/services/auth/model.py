from uuid import UUID
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Union, Literal

class UserLoginModel(BaseModel):
    """Representation of a user login."""
    username: Optional[str] = Field(
        default=None, description="User name use for login.")
    password: Optional[str] = Field(
        default=None, description="Password of the user.")
    
class UserInfo(BaseModel):
    """Representation of a user information."""
    res_code: int = Field(description="Response code.")
    res_message: Optional[str] = Field(default=None, description="Error message.")
    id: Optional[str] = Field(default=None, description="Id of the user.")
    org_id: Optional[str] = Field(default=None, description="Organization associated with the user.")
    roles: Optional[str] = Field(default=None, description="Roles of the user.")
    authority: Optional[int] = Field(default=None, description="Authorization of the organization associated with the user, as owner or client.")