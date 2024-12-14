from fastapi import APIRouter
import logging

from baseapp.config import setting
from baseapp.model.common import ApiResponse

from baseapp.config import setting
config = setting.get_settings()

from baseapp.utils.utility import get_response_based_on_env

from baseapp.services._org import model

from baseapp.services._org.crud import CRUD
_crud = CRUD()

logger = logging.getLogger()

router = APIRouter(prefix="/v1/_organization", tags=["Organization"])

@router.post("/init_owner", response_model=ApiResponse)
async def create(org: model.Organization, user:model.User) -> ApiResponse:
    response = _crud.init_owner_org(org,user)
    return ApiResponse(status=0, message="Data created", data=response)

