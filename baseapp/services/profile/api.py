from fastapi import APIRouter, Query, Depends
from typing import Optional

from baseapp.model.common import ApiResponse, PaginatedApiResponse, CurrentUser
from baseapp.utils.jwt import get_current_user

from baseapp.config import setting
config = setting.get_settings()

import logging

# from baseapp.services._enum import model
from baseapp.services.profile.crud import CRUD
_crud = CRUD()

router = APIRouter(prefix="/v1/profile")

# @router.post("/create", response_model=ApiResponse)
# async def create(data: model.Enum) -> ApiResponse:
#     response = _crud.create(data)
#     return ApiResponse(status=0, message="Data created", data=response)
    
# @router.put("/update/{enum_id}", response_model=ApiResponse)
# async def update_by_id(enum_id: str, data: model.EnumUpdate) -> ApiResponse:
#     response = _crud.update_by_id(enum_id,data)
#     return ApiResponse(status=0, message="Data updated", data=response)

# @router.get("", response_model=PaginatedApiResponse)
# async def get_all_data(
#         page: int = Query(1, ge=1, description="Page number"),
#         per_page: int = Query(10, ge=1, le=100, description="Items per page"),
#         sort_field: str = Query("_id", description="Field to sort by"),
#         sort_order: str = Query("asc", regex="^(asc|desc)$", description="Sort order: 'asc' or 'desc'"),
#         module: Optional[str] = Query(None, description="Filter by module")
#     ) -> PaginatedApiResponse:
    
#     # Build filters dynamically
#     filters = {}
#     if module:
#         filters["mod"] = module
#     # Call CRUD function
#     response = _crud.get_all(
#         filters=filters,
#         page=page,
#         per_page=per_page,
#         sort_field=sort_field,
#         sort_order=sort_order,
#     )
#     return PaginatedApiResponse(status=0, message="Data loaded", data=response["data"], pagination=response["pagination"])
    
@router.get("/user", response_model=ApiResponse)
async def get_profile(cu: CurrentUser = Depends(get_current_user)) -> ApiResponse:
    logging.debug(f"data cok {cu}")
    org_id = cu.org_id
    log_id = cu.log_id
    response = _crud.find_user_by_id(cu.id)
    return ApiResponse(status=0, data=response)
    
# @router.delete("/delete/{enum_id}", response_model=ApiResponse)
# async def delete_by_id(enum_id: str) -> ApiResponse:
#     response = _crud.delete_by_id(enum_id)
#     return ApiResponse(status=0, message="Document deleted", data=response)

