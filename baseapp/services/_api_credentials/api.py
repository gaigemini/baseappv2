from fastapi import APIRouter, Query, Depends, Request

from baseapp.model.common import ApiResponse, CurrentUser, Status, UpdateStatus
from baseapp.utils.jwt import get_current_user
from baseapp.utils.utility import cbor_or_json, parse_request_body

from baseapp.config import setting
config = setting.get_settings()

from baseapp.services._api_credentials.model import ApiCredential, ApiCredentialCreate

from baseapp.services._api_credentials.crud import CRUD
_crud = CRUD()

from baseapp.services.permission_check_service import PermissionChecker
permission_checker = PermissionChecker()

router = APIRouter(prefix="/v1/api_credentials", tags=["API Credentials"])

@router.post("/create", response_model=ApiResponse)
@cbor_or_json
async def create(
    req: Request,
    cu: CurrentUser = Depends(get_current_user)
) -> ApiResponse:
    if not permission_checker.has_permission(cu.roles, "_api_credentials", 2):  # 2 untuk izin simpan baru
        raise PermissionError("Access denied")

    _crud.set_context(
        user_id=cu.id,
        org_id=cu.org_id,
        ip_address=cu.ip_address,  # Jika ada
        user_agent=cu.user_agent   # Jika ada
    )

    req = await parse_request_body(req, ApiCredential)
    response = _crud.create(req)

    return ApiResponse(status=0, message="Data created", data=response)

@router.post("/create-by-owner", response_model=ApiResponse)
@cbor_or_json
async def create_by_owner(
    req: Request,
    cu: CurrentUser = Depends(get_current_user)
) -> ApiResponse:
    if cu.authority != 1:
        raise PermissionError("Access denied")
    
    if not permission_checker.has_permission(cu.roles, "_api_credentials", 2):  # 2 untuk izin simpan baru
        raise PermissionError("Access denied")

    _crud.set_context(
        user_id=cu.id,
        org_id=cu.org_id,
        ip_address=cu.ip_address,  # Jika ada
        user_agent=cu.user_agent   # Jika ada
    )

    req = await parse_request_body(req, ApiCredentialCreate)
    response = _crud.create_by_owner(req)

    return ApiResponse(status=0, message="Data created", data=response)

@router.delete("/delete/{api_credential_id}", response_model=ApiResponse)
@cbor_or_json
async def delete_data(api_credential_id: str, cu: CurrentUser = Depends(get_current_user)) -> ApiResponse:
    if not permission_checker.has_permission(cu.roles, "_api_credentials", 4):  # 4 untuk izin simpan perubahan
        raise PermissionError("Access denied")
    
    _crud.set_context(
        user_id=cu.id,
        org_id=cu.org_id,
        ip_address=cu.ip_address,  # Jika ada
        user_agent=cu.user_agent   # Jika ada
    )
    
    # Buat instance model langsung
    manual_data = UpdateStatus(
        status=Status.DELETE  # nilai yang Anda tentukan
    )
    response = _crud.update_by_id(api_credential_id,manual_data)
    return ApiResponse(status=0, message="Data deleted", data=response)

@router.get("", response_model=ApiResponse)
@cbor_or_json
async def get_all_data(
        page: int = Query(1, ge=1, description="Page number"),
        per_page: int = Query(10, ge=1, le=100, description="Items per page"),
        sort_field: str = Query("_id", description="Field to sort by"),
        sort_order: str = Query("asc", regex="^(asc|desc)$", description="Sort order: 'asc' or 'desc'"),
        cu: CurrentUser = Depends(get_current_user),
        org_id: str = Query(None, description="Organization ID"),
        status: str = Query(None, description="Status data")
    ) -> ApiResponse:

    if not permission_checker.has_permission(cu.roles, "payment_method", 1):  # 1 untuk izin baca
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
    if org_id:
        if cu.authority == 1:
            filters["org_id"] = org_id
    else:
        filters["org_id"] = cu.org_id

    if status:
        filters["status"] = status

    # Call CRUD function
    response = _crud.get_all(
        filters=filters,
        page=page,
        per_page=per_page,
        sort_field=sort_field,
        sort_order=sort_order,
    )
    return ApiResponse(status=0, message="Data loaded", data=response["data"], pagination=response["pagination"])