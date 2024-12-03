from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional, Union, Dict, Literal

class CustomDataModel(BaseModel):
    key: str
    value: Union[str, int, Dict[str, str]]

class Enum(BaseModel):
    id: Optional[UUID]  # UUID sebagai _id
    app: str = Field(description="App of the enum data.")
    mod: str = Field(description="Module of the enum data.")
    code: str = Field(description="App of the enum data.")
    type: Literal["hardcoded","user"] = Field(description="Type of the enum data is hardcoded or user")
    value: Union[str,int,CustomDataModel]

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

class EnumInDB(Enum):
    id: UUID

    class Config:
        orm_mode = True

class EnumCreate(BaseModel):
    app: str = Field(description="App of the enum data.")
    mod: str = Field(description="Module of the enum data.")
    code: str = Field(description="App of the enum data.")
    type: Literal["hardcoded","user"] = Field(description="Type of the enum data is hardcoded or user")
    value: Union[str,int,CustomDataModel]
