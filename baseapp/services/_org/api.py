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

router = APIRouter(prefix="/v1/_organization")

@router.post("/init_owner", response_model=ApiResponse)
async def create(org: model.Organization, user:model.User) -> ApiResponse:
    try:
        response = _crud.init_owner_org(org,user)
        if response["status"] == 0:
            return get_response_based_on_env(ApiResponse(status=response["status"], data=response["data"]), app_env=config.app_env)
        else:
            return get_response_based_on_env(ApiResponse(status=response["status"], message=response["message"]), app_env=config.app_env)
    except Exception as err:
        error_message = f"baseapp.services._org.api {err=}, {type(err)=}"
        logger.error(err, stack_info=True)
        response = ApiResponse(status=4, message=error_message)
        return get_response_based_on_env(response, app_env=config.app_env)

