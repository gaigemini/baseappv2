from fastapi import APIRouter, Request
import logging

from baseapp.test_connection import crud as test
from baseapp.model.common import ApiResponse

from baseapp.config import setting
config = setting.get_settings()

from baseapp.utils.utility import get_response_based_on_env

logger = logging.getLogger()

router = APIRouter(prefix="/v1/test")

@router.get("/database", response_model=ApiResponse)
def test_connection_to_database(ctx: Request) -> ApiResponse:
    try:
        resp = test.test_connection_to_mongodb()
        response = ApiResponse(status=0, data=resp)
        return get_response_based_on_env(response, app_env=config.app_env)
    except Exception as err:
        error_message = f"test_connection_to_database {err=}, {type(err)=}"
        logger.error(err, stack_info=True)
        response = ApiResponse(status=4, message=error_message)
        return get_response_based_on_env(response, app_env=config.app_env)

@router.get("/redis")
def test_connection_to_redis(ctx: Request) -> ApiResponse:
    try:
        resp = test.test_connection_to_redis()
        response = ApiResponse(status=0, data=resp)
        return get_response_based_on_env(response, app_env=config.app_env)
    except Exception as err:
        error_message = f"test_connection_to_redis {err=}, {type(err)=}"
        logger.error(err, stack_info=True)
        response = ApiResponse(status=4, message=error_message)
        return get_response_based_on_env(response, app_env=config.app_env)
    
@router.get("/minio")
def test_connection_to_minio(ctx: Request) -> ApiResponse:
    try:
        resp = test.test_connection_to_minio()
        response = ApiResponse(status=0, data=resp)
        return get_response_based_on_env(response, app_env=config.app_env)
    except Exception as err:
        error_message = f"test_connection_to_minio {err=}, {type(err)=}"
        logger.error(err, stack_info=True)
        response = ApiResponse(status=4, message=error_message)
        return get_response_based_on_env(response, app_env=config.app_env)

@router.get("/rabbit")
def test_connection_to_rabbit(ctx: Request) -> ApiResponse:
    try:
        resp = test.test_connection_to_rabbit()
        response = ApiResponse(status=0, data=resp)
        return get_response_based_on_env(response, app_env=config.app_env)
    except Exception as err:
        error_message = f"test_connection_to_rabbit {err=}, {type(err)=}"
        logger.error(err, stack_info=True)
        response = ApiResponse(status=4, message=error_message)
        return get_response_based_on_env(response, app_env=config.app_env)
    
@router.get("/clickhouse")
def test_connection_to_clickhouse(ctx: Request) -> ApiResponse:
    try:
        resp = test.test_connection_to_clickhouse()
        response = ApiResponse(status=0, data=resp)
        return get_response_based_on_env(response, app_env=config.app_env)
    except Exception as err:
        error_message = f"test_connection_to_clickhouse {err=}, {type(err)=}"
        logger.error(err, stack_info=True)
        response = ApiResponse(status=4, message=error_message)
        return get_response_based_on_env(response, app_env=config.app_env)

