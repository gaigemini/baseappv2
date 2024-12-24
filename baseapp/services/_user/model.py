from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional, Union, Literal, List
from baseapp.model.common import Status
from datetime import datetime, timezone

class User(BaseModel):
    username: str = Field(description="User name use for login.", error_msg_templates={"value_error.missing": "Username is required!"})
    email: str = Field(description="Email of the user.", error_msg_templates={"value_error.missing": "Email cannot be empty"})
    password: str = Field(description="Password of the user.")
    salt: Optional[str] = Field(default=None, description="Random string added to password for strengthening.")
    roles: List[str] = Field(description="Roles of the user")
    status: Optional[Status] = Field(default=None, description="Status of the user.")

class UpdateByAdmin(BaseModel):
    username: str = Field(description="User name use for login.", error_msg_templates={"value_error.missing": "Username is required!"})
    email: str = Field(description="Email of the user.", error_msg_templates={"value_error.missing": "Email cannot be empty"})
    roles: List[str] = Field(description="Roles of the user")
    status: Optional[Status] = Field(default=None, description="Status of the user.")

class UpdateUsername(BaseModel):
    """Representation of update username model."""
    id: str = Field(description="Id of the user.")
    username: str = Field(description="User name use for login.")

class UpdateEmail(BaseModel):
    """Representation of update email model."""
    id: str = Field(description="Id of the user.")
    email: str = Field(description="Email of the user.")

class UpdateRoles(BaseModel):
    """Representation of update roles model."""
    id: str = Field(description="Id of the user.")
    roles: List[str] = Field(description="Roles of the user")

class UpdateStatus(BaseModel):
    """Representation of update status model."""
    id: str = Field(description="Id of the user.")
    status: Status = Field(description="Status of the user.")

class ChangePassword(BaseModel):
    """Representation of change password model."""
    old_password: str = Field(description="Old password.", default=None)
    new_password: str = Field(description="New password.")
    verify_password: str = Field(description="Retype new password.")
