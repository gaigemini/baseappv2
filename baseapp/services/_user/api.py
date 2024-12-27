from fastapi import APIRouter, Query, Depends
from typing import Optional

from baseapp.model.common import ApiResponse, PaginatedApiResponse, CurrentUser
from baseapp.utils.jwt import get_current_user
from baseapp.utils.utility import is_none

from baseapp.config import setting
config = setting.get_settings()

from baseapp.services._user import model

from baseapp.services._user.crud import CRUD
_crud = CRUD()

from baseapp.services.permission_check_service import PermissionChecker
permission_checker = PermissionChecker()

router = APIRouter(prefix="/v1/_user", tags=["User"])

@router.post("/create", response_model=ApiResponse)
async def create(req: model.User, cu: CurrentUser = Depends(get_current_user)) -> ApiResponse:
    if not permission_checker.has_permission(cu.roles, "_user", 2):  # 2 untuk izin simpan baru
        raise PermissionError("Access denied")

    _crud.set_context(
        user_id=cu.id,
        org_id=cu.org_id,
        ip_address=cu.ip_address,  # Jika ada
        user_agent=cu.user_agent   # Jika ada
    )

    response = _crud.create(req)
    return ApiResponse(status=0, message="Data created", data=response)
    
@router.put("/update/{user_id}", response_model=ApiResponse)
async def update_by_admin(user_id: str, req: model.UpdateByAdmin, cu: CurrentUser = Depends(get_current_user)) -> ApiResponse:
    if not permission_checker.has_permission(cu.roles, "_role", 4):  # 4 untuk izin simpan perubahan
        raise PermissionError("Access denied")
    
    _crud.set_context(
        user_id=cu.id,
        org_id=cu.org_id,
        ip_address=cu.ip_address,  # Jika ada
        user_agent=cu.user_agent   # Jika ada
    )
    response = _crud.update_all_by_admin(user_id,req)
    return ApiResponse(status=0, message="Data updated", data=response)

@router.put("/change_password", response_model=ApiResponse)
async def update_change_password(req: model.ChangePassword, cu: CurrentUser = Depends(get_current_user)) -> ApiResponse:
    if not permission_checker.has_permission(cu.roles, "_role", 4):  # 4 untuk izin simpan perubahan
        raise PermissionError("Access denied")
    
    _crud.set_context(
        user_id=cu.id,
        org_id=cu.org_id,
        ip_address=cu.ip_address,  # Jika ada
        user_agent=cu.user_agent   # Jika ada
    )

    response = _crud.change_password(req)
    return ApiResponse(status=0, message="Data updated", data=response)

@router.put("/reset_password/{user_id}", response_model=ApiResponse)
async def update_reset_passowrd(user_id: str, req: model.ChangePassword, cu: CurrentUser = Depends(get_current_user)) -> ApiResponse:
    if not permission_checker.has_permission(cu.roles, "_role", 4):  # 4 untuk izin simpan perubahan
        raise PermissionError("Access denied")
    
    _crud.set_context(
        user_id=cu.id,
        org_id=cu.org_id,
        ip_address=cu.ip_address,  # Jika ada
        user_agent=cu.user_agent   # Jika ada
    )

    response = _crud.reset_password(user_id,req)
    return ApiResponse(status=0, message="Data updated", data=response)

@router.get("", response_model=PaginatedApiResponse)
async def get_all_data(
        page: int = Query(1, ge=1, description="Page number"),
        per_page: int = Query(10, ge=1, le=100, description="Items per page"),
        sort_field: str = Query("_id", description="Field to sort by"),
        sort_order: str = Query("asc", regex="^(asc|desc)$", description="Sort order: 'asc' or 'desc'"),
        username: Optional[str] = Query(None, description="Filter by username"),
        email: Optional[str] = Query(None, description="Filter by email"),
        role: Optional[str] = Query(None, description="Filter by roles"),
        status: Optional[str] = Query(None, description="Filter by status"),
        cu: CurrentUser = Depends(get_current_user)
    ) -> PaginatedApiResponse:

    if not permission_checker.has_permission(cu.roles, "_user", 1):  # 1 untuk izin baca
        raise PermissionError("Access denied")

    _crud.set_context(
        user_id=cu.id,
        org_id=cu.org_id,
        ip_address=cu.ip_address,  # Jika ada
        user_agent=cu.user_agent   # Jika ada
    )
    
    # Build filters dynamically
    filters = {}
    
    # default filter by organization id
    if cu.org_id:
        filters["org_id"] = cu.org_id

    # addtional when filter running
    if username:
        filters["username"] = username
    if username:
        filters["email"] = email
    if status:
        filters["status"] = status
    if role:
        filters["roles"] = role

    # Call CRUD function
    response = _crud.get_all(
        filters=filters,
        page=page,
        per_page=per_page,
        sort_field=sort_field,
        sort_order=sort_order,
    )
    return PaginatedApiResponse(status=0, message="Data loaded", data=response["data"], pagination=response["pagination"])
    
@router.get("/find/{user_id}", response_model=ApiResponse)
async def find_by_id(user_id: str, cu: CurrentUser = Depends(get_current_user)) -> ApiResponse:
    if not permission_checker.has_permission(cu.roles, "_user", 1):  # 1 untuk izin baca
        raise PermissionError("Access denied")
    
    _crud.set_context(
        user_id=cu.id,
        org_id=cu.org_id,
        ip_address=cu.ip_address,  # Jika ada
        user_agent=cu.user_agent   # Jika ada
    )
    response = _crud.get_by_id(user_id)
    return ApiResponse(status=0, message="Data found", data=response)