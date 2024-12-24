from fastapi import APIRouter, Depends

from baseapp.config import setting
from baseapp.model.common import ApiResponse, CurrentUser

from baseapp.config import setting
config = setting.get_settings()

from baseapp.utils.utility import get_response_based_on_env, is_none
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
async def create(org: model.Organization, user:model.User) -> ApiResponse:
    response = _crud.init_owner_org(org,user)
    return ApiResponse(status=0, message="Data created", data=response)

@router.post("/init_partner", response_model=ApiResponse)
async def create(org: model.Organization, user:model.User, cu: CurrentUser = Depends(get_current_user)) -> ApiResponse:
    if not permission_checker.has_permission(cu.roles, "_organization", 2):  # 2 untuk izin simpan baru
        raise PermissionError("Access denied")
    
    # check authority is not owner
    if cu.authority != 1:
        raise PermissionError("Access denied")
    
    org.rec_by = is_none(org.rec_by, cu.id)
    org.ref_id = cu.org_id

    response = _crud.init_partner_client_org(org,user)
    return ApiResponse(status=0, message="Data created", data=response)

@router.post("/init_client", response_model=ApiResponse)
async def create(org: model.Organization, user:model.User, cu: CurrentUser = Depends(get_current_user)) -> ApiResponse:
    if not permission_checker.has_permission(cu.roles, "_organization", 2):  # 2 untuk izin simpan baru
        raise PermissionError("Access denied")
    
    # check authority is not partner
    if cu.authority != 2:
        raise PermissionError("Access denied")
    
    org.rec_by = is_none(org.rec_by, cu.id)
    org.ref_id = cu.org_id

    response = _crud.init_partner_client_org(org,user)
    return ApiResponse(status=0, message="Data created", data=response)

