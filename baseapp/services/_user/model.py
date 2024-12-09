from uuid import UUID
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Union, Literal
from baseapp.model.common import Status

class User(BaseModel):
    username: str = Field(description="User name use for login.", error_msg_templates={"value_error.missing": "Username is required!"})
    email: str = Field(description="Email of the user.", error_msg_templates={"value_error.missing": "Email cannot be empty"})
    password: str = Field(description="Password of the user.")
    salt: Optional[str] = Field(default=None, description="Random string added to password for strengthening.")
    roles: Optional[str] = Field(default=None, description="Roles of the user")
    status: Optional[Status] = Field(default=None, description="Status of the user.")
    org_id: Optional[str] = Field(default=None, description="Organization associated with the user.")

class UserLoginModel(BaseModel):
    """Representation of a user login."""
    username: Optional[str] = Field(
        default=None, description="User name use for login.")
    password: Optional[str] = Field(
        default=None, description="Password of the user.")