from fastapi import APIRouter
from baseapp.model.common import ApiResponse

from baseapp.config import setting
config = setting.get_settings()

from baseapp.utils.utility import get_response_based_on_env

from baseapp.services.database import crud

import logging
logger = logging.getLogger()

router = APIRouter(prefix="/v1/init")

@router.post("/database", response_model=ApiResponse)
async def init_database() -> ApiResponse:
    try:
        initDB = crud.init_database()
        response = ApiResponse(status=0, data=not initDB)
        return get_response_based_on_env(response, app_env=config.app_env)
    except Exception as err:
        error_message = f"baseapp.services.database.api {err=}, {type(err)=}"
        logger.error(err, stack_info=True)
        response = ApiResponse(status=4, message=error_message)
        return get_response_based_on_env(response, app_env=config.app_env)

