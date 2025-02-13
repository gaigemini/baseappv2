from fastapi import APIRouter
from baseapp.model.common import ApiResponse
from baseapp.utils.utility import cbor_or_json
from baseapp.config.setting import get_settings
config = get_settings()

from baseapp.services.database.crud import CRUD
_crud = CRUD()

import logging
logger = logging.getLogger()

router = APIRouter(prefix="/v1/init", tags=["Init"])

@router.post("/database", response_model=ApiResponse)
@cbor_or_json
async def init_database() -> ApiResponse:
    response = _crud.create()
    return ApiResponse(status=0, message="Database created", data=not response)

