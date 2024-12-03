from fastapi import APIRouter
import logging

from baseapp.config import setting
from baseapp.model.common import ApiResponse

from baseapp.config import setting
config = setting.get_settings()

from baseapp.utils.utility import get_response_based_on_env

from baseapp.services._enum import crud, model

logger = logging.getLogger()

router = APIRouter(prefix="/v1/_enum")

@router.post("/create", response_model=ApiResponse)
async def create(data: model.EnumCreate) -> ApiResponse:
    try:
        createdEnum = crud.create_enum(data)
        response = ApiResponse(status=0, data=createdEnum)
        return get_response_based_on_env(response, app_env=config.app_env)
    except Exception as err:
        error_message = f"baseapp.services.database.api {err=}, {type(err)=}"
        logger.error(err, stack_info=True)
        response = ApiResponse(status=4, message=error_message)
        return get_response_based_on_env(response, app_env=config.app_env)

