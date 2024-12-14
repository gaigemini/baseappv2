from uuid import UUID
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Union, Dict, Literal
from datetime import datetime, timezone

class Role(BaseModel):
    color: Optional[str] = Field(default="black", description="Label color of role.")
    name: str = Field(description="Name of role.")
    rec_by: Optional[str] = Field(default=None, description="This role is created by.")
    rec_date: Optional[datetime] = Field(default=datetime.now(timezone.utc), description="This role is created at.")
    org_id: Optional[str] = Field(default=None, description="Organization associated with the role.")
    
class RoleUpdate(BaseModel):
    color: Optional[str] = Field(default="black", description="Label color of role.")
    name: str = Field(description="Name of role.")
    mod_by: Optional[str] = Field(default=None, description="This enum is modify by.")
    mod_date: Optional[datetime] = Field(default=datetime.now(timezone.utc), description="This enum is modify at.")