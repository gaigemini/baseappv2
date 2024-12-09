from fastapi import APIRouter, Query
from typing import Optional

from baseapp.model.common import ApiResponse, PaginatedApiResponse

from baseapp.config import setting
config = setting.get_settings()

from baseapp.utils.utility import get_response_based_on_env

from baseapp.services._enum import model

from baseapp.services._enum.crud import CRUD
_crud = CRUD()

import logging
logger = logging.getLogger()

router = APIRouter(prefix="/v1/_enum")

@router.post("/create", response_model=ApiResponse)
async def create(data: model.Enum) -> ApiResponse:
    try:
        response = _crud.create(data)
        if response["status"] == 0:
            return get_response_based_on_env(ApiResponse(status=response["status"], data=response["data"]), app_env=config.app_env)
        else:
            return get_response_based_on_env(ApiResponse(status=response["status"], message=response["message"]), app_env=config.app_env)
    except Exception as err:
        error_message = f"baseapp.services._enum.api {err=}, {type(err)=}"
        logger.error(err, stack_info=True)
        response = ApiResponse(status=4, message=error_message)
        return get_response_based_on_env(response, app_env=config.app_env)
    
@router.put("/update/{enum_id}", response_model=ApiResponse)
async def update_by_id(enum_id: str, data: model.EnumUpdate) -> ApiResponse:
    try:
        response = _crud.update_by_id(enum_id,data)
        if response["status"] == 0:
            return get_response_based_on_env(ApiResponse(status=response["status"], data=response["data"]), app_env=config.app_env)
        else:
            return get_response_based_on_env(ApiResponse(status=response["status"], message=response["message"]), app_env=config.app_env)
    except Exception as err:
        error_message = f"baseapp.services._enum.api {err=}, {type(err)=}"
        logger.error(err, stack_info=True)
        response = ApiResponse(status=4, message=error_message)
        return get_response_based_on_env(response, app_env=config.app_env)

@router.get("", response_model=PaginatedApiResponse)
async def get_all_data(
        page: int = Query(1, ge=1, description="Page number"),
        per_page: int = Query(10, ge=1, le=100, description="Items per page"),
        sort_field: str = Query("_id", description="Field to sort by"),
        sort_order: str = Query("asc", regex="^(asc|desc)$", description="Sort order: 'asc' or 'desc'"),
        module: Optional[str] = Query(None, description="Filter by module")
    ) -> PaginatedApiResponse:
    try:
        # Build filters dynamically
        filters = {}
        if module:
            filters["mod"] = module
        
        # Call CRUD function
        response = _crud.get_all(
            filters=filters,
            page=page,
            per_page=per_page,
            sort_field=sort_field,
            sort_order=sort_order,
        )

        if response["status"] == 0:
            return get_response_based_on_env(PaginatedApiResponse(status=response["status"], data=response["data"], pagination=response["pagination"]), app_env=config.app_env)
        else:
            return get_response_based_on_env(PaginatedApiResponse(status=response["status"], message=response["message"]), app_env=config.app_env)        
    except Exception as err:
        error_message = f"baseapp.services._enum.api {err=}, {type(err)=}"
        logger.error(err, stack_info=True)
        response = PaginatedApiResponse(status=4, message=error_message)
        return get_response_based_on_env(response, app_env=config.app_env)
        
@router.get("/find/{enum_id}", response_model=ApiResponse)
async def find_by_id(enum_id: str) -> ApiResponse:
    try:
        response = _crud.get_by_id(enum_id)
        if response["status"] == 0:
            return get_response_based_on_env(ApiResponse(status=response["status"], data=response["data"]), app_env=config.app_env)
        else:
            return get_response_based_on_env(ApiResponse(status=response["status"], message=response["message"]), app_env=config.app_env)        
    except Exception as err:
        error_message = f"baseapp.services._enum.api {err=}, {type(err)=}"
        logger.error(err, stack_info=True)
        response = ApiResponse(status=4, message=error_message)
        return get_response_based_on_env(response, app_env=config.app_env)
    
@router.delete("/delete/{enum_id}", response_model=ApiResponse)
async def delete_by_id(enum_id: str) -> ApiResponse:
    try:
        response = _crud.delete_by_id(enum_id)
        if response["status"] == 0:
            return get_response_based_on_env(ApiResponse(status=response["status"], data=response["data"]), app_env=config.app_env)
        else:
            return get_response_based_on_env(ApiResponse(status=response["status"], message=response["message"]), app_env=config.app_env)        
    except Exception as err:
        error_message = f"baseapp.services._enum.api {err=}, {type(err)=}"
        logger.error(err, stack_info=True)
        response = ApiResponse(status=4, message=error_message)
        return get_response_based_on_env(response, app_env=config.app_env)

