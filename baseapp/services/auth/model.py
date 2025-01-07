from pydantic import BaseModel, Field
from typing import Optional, List

class UserLoginModel(BaseModel):
    """Representation of a user login."""
    username: Optional[str] = Field(
        default=None, description="User name use for login.")
    password: Optional[str] = Field(
        default=None, description="Password of the user.")
    
class UserInfo(BaseModel):
    """Representation of a user information."""
    id: Optional[str] = Field(default=None, description="Id of the user.")
    org_id: Optional[str] = Field(default=None, description="Organization associated with the user.")
    roles: List[str] = Field(description="Roles of the user")
    authority: Optional[int] = Field(default=None, description="Authorization of the organization associated with the user, as owner or client.")

class VerifyOTPRequest(BaseModel):
    username: str = Field(description="Email")
    otp: str = Field(description="OTP Code.")