from fastapi import APIRouter, Request, Response, Depends
from fastapi.security import OAuth2PasswordRequestForm
import logging

from baseapp.config import setting
from baseapp.model.common import ApiResponse

from baseapp.config import setting, redis
config = setting.get_settings()

from baseapp.utils.utility import get_response_based_on_env
from baseapp.utils.jwt import create_access_token, create_refresh_token, decode_jwt_token

from baseapp.services.auth import model

from datetime import datetime, timezone, timedelta

from baseapp.services.auth.crud import CRUD
_crud = CRUD()

logger = logging.getLogger()

router = APIRouter(prefix="/v1/auth")

@router.post("/login", response_model=ApiResponse)
async def login(response: Response, ctx: Request, req: model.UserLoginModel) -> ApiResponse:
    try:
        log_id = ctx.state.log_id
        username = req.username
        password = req.password
        user_info = _crud.validate_user(username,password)
        logger.debug(f"User info: {user_info}")
        if user_info.res_code == 0:
            token_data = {
                "sub": username, 
                "id": user_info.id,
                "roles": user_info.roles, 
                "authority": user_info.authority,
                "org_id": user_info.org_id
            }
            
            access_token, expire_access_in = create_access_token(token_data)
            refresh_token, expire_refresh_in = create_refresh_token(token_data)

            # save refresh token to redis
            client = redis.RedisConn()
            redis_conn = client.get_connection()
            redis_conn.set(username, refresh_token, timedelta(days=expire_refresh_in))
            redis_conn.close()
        
            expired_at = datetime.now(timezone.utc) + timedelta(minutes=float(expire_access_in))
            data = {
                "access_token": access_token, 
                "token_type": "bearer",
                "expired_at": expired_at.isoformat()
            }
            response.set_cookie(
                "refresh_token",
                refresh_token,
                httponly=True,  # Prevent access via JavaScript
                secure=True,    # Send only over HTTPS
                samesite="Strict"  # Prevent cross-site requests
            )
            return get_response_based_on_env(ApiResponse(status=user_info.res_code, data=data), app_env=config.app_env)
        
        return get_response_based_on_env(ApiResponse(status=user_info.res_code, message=user_info.res_message), app_env=config.app_env)
    except Exception as err:
        error_message = f"baseapp.services.auth.api {err=}, {type(err)=}"
        logger.error(err, stack_info=True)
        response = ApiResponse(status=4, message=error_message)
        return get_response_based_on_env(response, app_env=config.app_env)

@router.post("/refresh", response_model=ApiResponse)
async def refresh_token(request: Request) -> ApiResponse:
    try:
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            return get_response_based_on_env(ApiResponse(status=4, message="Refresh token missing"), app_env=config.app_env)
        
        # Decode refresh token
        payload = decode_jwt_token(refresh_token)
        if not payload:
            return get_response_based_on_env(ApiResponse(status=4, message="Invalid refresh token"), app_env=config.app_env)

        # Check token in Redis
        client = redis.RedisConn()
        redis_conn = client.get_connection()
        stored_token = redis_conn.get(payload["sub"])
        if stored_token != refresh_token:
            return get_response_based_on_env(ApiResponse(status=4, message="Invalid refresh token"), app_env=config.app_env)

        # Create new access token
        access_token, expire_access_in = create_access_token(payload)
        expired_at = datetime.now(timezone.utc) + timedelta(minutes=float(expire_access_in))
        data = {
            "access_token": access_token, 
            "token_type": "bearer",
            "expired_at": expired_at.isoformat()
        }
        return get_response_based_on_env(ApiResponse(status=0, data=data), app_env=config.app_env)
    except Exception as err:
        error_message = f"baseapp.services.auth.api {err=}, {type(err)=}"
        logger.error(err, stack_info=True)
        response = ApiResponse(status=4, message=error_message)
        return get_response_based_on_env(response, app_env=config.app_env)
    
@router.post("/logout", response_model=ApiResponse)
async def logout(request: Request, response: Response) -> ApiResponse:
    try:
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            return get_response_based_on_env(ApiResponse(status=4, message="Refresh token missing"), app_env=config.app_env)
        
        # Decode refresh token
        payload = decode_jwt_token(refresh_token)
        if not payload:
            return get_response_based_on_env(ApiResponse(status=4, message="Invalid refresh token"), app_env=config.app_env)

        # Check token in Redis
        client = redis.RedisConn()
        redis_conn = client.get_connection()
        redis_conn.delete(payload["sub"])

        # Hapus cookie di klien
        response.delete_cookie("refresh_token")

        return get_response_based_on_env(ApiResponse(status=0, message="Logout"), app_env=config.app_env)
    except Exception as err:
        error_message = f"baseapp.services.auth.api {err=}, {type(err)=}"
        logger.error(err, stack_info=True)
        response = ApiResponse(status=4, message=error_message)
        return get_response_based_on_env(response, app_env=config.app_env)
