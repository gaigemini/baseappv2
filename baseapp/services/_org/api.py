from fastapi import APIRouter, Depends, Request

from baseapp.config import setting
from baseapp.model.common import ApiResponse, CurrentUser
from baseapp.utils.utility import cbor_or_json, parse_request_body

from baseapp.config import setting
config = setting.get_settings()

from baseapp.utils.jwt import get_current_user
from baseapp.services._org import model

from baseapp.services._org.crud import CRUD
_crud = CRUD()

from baseapp.services.permission_check_service import PermissionChecker
permission_checker = PermissionChecker()

import logging
logger = logging.getLogger()

router = APIRouter(prefix="/v1/_organization", tags=["Organization"])

@router.post("/init_owner", response_model=ApiResponse)
@cbor_or_json
# async def create(org: model.Organization, user:model.User) -> ApiResponse:
async def create(req: Request) -> ApiResponse:
    request_body = await parse_request_body(req, model.InitRequest)

    response = _crud.init_owner_org(request_body.org, request_body.user)
    # response = _crud.init_owner_org(org,user)
    return ApiResponse(status=0, message="Data created", data=response)

@router.post("/init_partner", response_model=ApiResponse)
@cbor_or_json
# async def create(org: model.Organization, user:model.User, cu: CurrentUser = Depends(get_current_user)) -> ApiResponse:
async def create(req: Request, cu: CurrentUser = Depends(get_current_user)) -> ApiResponse:
    if not permission_checker.has_permission(cu.roles, "_organization", 2):  # 2 untuk izin simpan baru
        raise PermissionError("Access denied")
    
    # check authority is not owner
    if cu.authority != 1:
        raise PermissionError("Access denied")
    
    _crud.set_context(
        user_id=cu.id,
        org_id=cu.org_id,
        ip_address=cu.ip_address,  # Jika ada
        user_agent=cu.user_agent   # Jika ada
    )

    request_body = await parse_request_body(req, model.InitRequest)
    request_body.org.authority = 2
    # org.authority = 2

    response = _crud.init_partner_client_org(request_body.org, request_body.user)
    # response = _crud.init_partner_client_org(org,user)
    return ApiResponse(status=0, message="Data created", data=response)

@router.post("/init_client", response_model=ApiResponse)
@cbor_or_json
# async def create(org: model.Organization, user:model.User, cu: CurrentUser = Depends(get_current_user)) -> ApiResponse:
async def create(req: Request, cu: CurrentUser = Depends(get_current_user)) -> ApiResponse:
    if not permission_checker.has_permission(cu.roles, "_organization", 2):  # 2 untuk izin simpan baru
        raise PermissionError("Access denied")
    
    # check authority is not partner
    if cu.authority != 2:
        raise PermissionError("Access denied")
    
    _crud.set_context(
        user_id=cu.id,
        org_id=cu.org_id,
        ip_address=cu.ip_address,  # Jika ada
        user_agent=cu.user_agent   # Jika ada
    )
    
    request_body = await parse_request_body(req, model.InitRequest)
    request_body.org.authority = 4

    # org.authority = 4

    response = _crud.init_partner_client_org(request_body.org, request_body.user)
    # response = _crud.init_partner_client_org(org,user)
    return ApiResponse(status=0, message="Data created", data=response)

@router.get("/find/{org_id}", response_model=ApiResponse)
@cbor_or_json
async def find_by_id(org_id: str, cu: CurrentUser = Depends(get_current_user)) -> ApiResponse:
    if not permission_checker.has_permission(cu.roles, "_organization", 1):  # 1 untuk izin baca
        raise PermissionError("Access denied")
    
    _crud.set_context(
        user_id=cu.id,
        org_id=cu.org_id,
        ip_address=cu.ip_address,  # Jika ada
        user_agent=cu.user_agent   # Jika ada
    )
    
    response = _crud.get_by_id(org_id)
    return ApiResponse(status=0, message="Data found", data=response)

@router.put("/update/{org_id}", response_model=ApiResponse)
@cbor_or_json
async def update_by_id(org_id: str, req: model.OrganizationUpdate, cu: CurrentUser = Depends(get_current_user)) -> ApiResponse:
    if not permission_checker.has_permission(cu.roles, "_organization", 4):  # 4 untuk izin simpan perubahan
        raise PermissionError("Access denied")
    
    _crud.set_context(
        user_id=cu.id,
        org_id=cu.org_id,
        ip_address=cu.ip_address,  # Jika ada
        user_agent=cu.user_agent   # Jika ada
    )

    response = _crud.update_by_id(org_id,req)
    return ApiResponse(status=0, message="Data updated", data=response)