from fastapi import APIRouter, Query, Depends

from baseapp.model.common import ApiResponse, CurrentUser
from baseapp.utils.jwt import get_current_user
from baseapp.utils.utility import cbor_or_json

from baseapp.config import setting
config = setting.get_settings()

from baseapp.services._dms.browse.crud import CRUD
_crud = CRUD()

from baseapp.services.permission_check_service import PermissionChecker
permission_checker = PermissionChecker()

router = APIRouter(prefix="/v1/_dms/browse", tags=["DMS - Browse"])

@router.get("/key/{refkey_table}/{refkey_id}", response_model=ApiResponse)
@cbor_or_json
async def browse_by_key(
        refkey_table: str, refkey_id: str,
        cu: CurrentUser = Depends(get_current_user)
    ) -> ApiResponse:

    if not permission_checker.has_permission(cu.roles, "_dmsbrowse", 1):  # 1 untuk izin baca
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

    if refkey_table:
        filters["refkey_table"] = refkey_table

    if refkey_id:
        filters["refkey_id"] = refkey_id

    # Call CRUD function
    response = _crud.browse_by_key(
        filters=filters
    )
    return ApiResponse(status=0, message="Data loaded", data=response["data"])

@router.get("/folder/{pid}", response_model=ApiResponse)
@cbor_or_json
async def list_folder(
        pid: str,
        cu: CurrentUser = Depends(get_current_user)
    ) -> ApiResponse:

    if not permission_checker.has_permission(cu.roles, "_dmsbrowse", 1):  # 1 untuk izin baca
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

    if pid != "root":
        filters["pid"] = pid
    else:
        filters["level"] = 1

    # Call CRUD function
    response = _crud.list_folder(
        filters=filters
    )
    return ApiResponse(status=0, message="Data loaded", data=response["data"])

@router.get("/explore/{folder_id}", response_model=ApiResponse)
@cbor_or_json
async def list_file_by_folder_id(
        folder_id: str, 
        page: int = Query(1, ge=1, description="Page number"),
        per_page: int = Query(10, ge=1, le=100, description="Items per page"),
        sort_field: str = Query("_id", description="Field to sort by"),
        sort_order: str = Query("asc", regex="^(asc|desc)$", description="Sort order: 'asc' or 'desc'"),
        cu: CurrentUser = Depends(get_current_user)
    ) -> ApiResponse:

    if not permission_checker.has_permission(cu.roles, "_dmsbrowse", 1):  # 1 untuk izin baca
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

    if folder_id:
        filters["folder_id"] = folder_id

    # Call CRUD function
    response = _crud.list_file(
        filters=filters,
        page=page,
        per_page=per_page,
        sort_field=sort_field,
        sort_order=sort_order,
    )
    return ApiResponse(status=0, message="Data loaded", data=response["data"], pagination=response["pagination"])

@router.get("/storage", response_model=ApiResponse)
@cbor_or_json
async def storage(
        cu: CurrentUser = Depends(get_current_user)
    ) -> ApiResponse:

    if not permission_checker.has_permission(cu.roles, "_dmsbrowse", 1):  # 1 untuk izin baca
        raise PermissionError("Access denied")

    _crud.set_context(
        user_id=cu.id,
        org_id=cu.org_id,
        ip_address=cu.ip_address,  # Jika ada
        user_agent=cu.user_agent   # Jika ada
    )

    # Call CRUD function
    response = _crud.check_storage()
    return ApiResponse(status=0, message="Data loaded", data=response)