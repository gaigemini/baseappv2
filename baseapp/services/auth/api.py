from fastapi import APIRouter, Request, Response, Form
from datetime import datetime, timezone, timedelta
import logging

from baseapp.model.common import ApiResponse
from baseapp.config.setting import get_settings
from baseapp.config.redis import RedisConn
from baseapp.utils.jwt import create_access_token, create_refresh_token, decode_jwt_token
from baseapp.services.auth.model import TokenResponse, UserLoginModel
from baseapp.services.auth.crud import CRUD
# from baseapp.utils.utility import get_response_based_on_env

config = get_settings()
_crud = CRUD()
logger = logging.getLogger()
router = APIRouter(prefix="/v1/auth", tags=["Auth"])

@router.post("/login", response_model=ApiResponse)
async def login(response: Response, ctx: Request, req: UserLoginModel) -> ApiResponse:
    username = req.username
    password = req.password

    # Validasi user
    user_info = _crud.validate_user(username, password)
    logger.debug(f"User info: {user_info}")

    # Data token
    token_data = {
        "sub": username,
        "id": user_info.id,
        "roles": user_info.roles,
        "authority": user_info.authority,
        "org_id": user_info.org_id,
    }

    # Buat akses token dan refresh token
    access_token, expire_access_in = create_access_token(token_data)
    refresh_token, expire_refresh_in = create_refresh_token(token_data)

    # Simpan refresh token ke Redis
    with RedisConn() as redis_conn:
        redis_conn.set(
            username,
            refresh_token,
            ex=timedelta(days=expire_refresh_in),
        )

    # Hitung waktu kedaluwarsa akses token
    expired_at = datetime.now(timezone.utc) + timedelta(minutes=float(expire_access_in))
    data = {
        "access_token": access_token,
        "token_type": "bearer",
        "expired_at": expired_at.isoformat(),
    }

    # Atur cookie refresh token
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=config.app_env == "production",  # Gunakan secure hanya di production
        samesite="Strict",  # Prevent CSRF
    )

    # Return response berhasil
    return ApiResponse(status=0, data=data)
    # return get_response_based_on_env(ApiResponse(status=0, data=data), app_env=config.app_env)

@router.post("/token", response_model=TokenResponse)
async def token(
    response: Response,
    ctx: Request,
    username: str = Form(...),
    password: str = Form(...),
) -> TokenResponse:
    # Validasi user
    user_info = _crud.validate_user(username, password)
    logger.debug(f"User info: {user_info}")

    # Data token
    token_data = {
        "sub": username,
        "id": user_info.id,
        "roles": user_info.roles,
        "authority": user_info.authority,
        "org_id": user_info.org_id,
    }

    # Buat akses token dan refresh token
    access_token, expire_access_in = create_access_token(token_data)
    refresh_token, expire_refresh_in = create_refresh_token(token_data)

    # Simpan refresh token ke Redis
    with RedisConn() as redis_conn:
        redis_conn.set(
            username,
            refresh_token,
            ex=timedelta(days=expire_refresh_in),
        )

    # Hitung waktu kedaluwarsa akses token
    expired_at = datetime.now(timezone.utc) + timedelta(minutes=float(expire_access_in))
    data = {
        "access_token": access_token,
        "token_type": "bearer",
        "expired_at": expired_at.isoformat(),
    }

    # Atur cookie refresh token
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=config.app_env == "production",  # Gunakan secure hanya di production
        samesite="Strict",  # Prevent CSRF
    )

    # Return response berhasil
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expired_at=expired_at.isoformat()
    )

@router.post("/refresh", response_model=ApiResponse)
async def refresh_token(request: Request) -> ApiResponse:
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise ValueError("Refresh token missing")
        # return get_response_based_on_env(ApiResponse(status=4, message="Refresh token missing"), app_env=config.app_env)
    
    # Decode refresh token
    payload = decode_jwt_token(refresh_token)
    if not payload:
        raise ValueError("Invalid refresh token")
        # return get_response_based_on_env(ApiResponse(status=4, message="Invalid refresh token"), app_env=config.app_env)

    # Check token in Redis
    with RedisConn() as redis_conn:
        stored_token = redis_conn.get(payload["sub"])
        if stored_token != refresh_token:
            raise ValueError("Invalid refresh token")

    # Create new access token
    access_token, expire_access_in = create_access_token(payload)
    expired_at = datetime.now(timezone.utc) + timedelta(minutes=float(expire_access_in))
    data = {
        "access_token": access_token, 
        "token_type": "bearer",
        "expired_at": expired_at.isoformat()
    }
    return ApiResponse(status=0, data=data)
    
@router.post("/logout", response_model=ApiResponse)
async def logout(request: Request, response: Response) -> ApiResponse:
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise ValueError("Refresh token missing")
    
    # Decode refresh token
    payload = decode_jwt_token(refresh_token)
    if not payload:
        raise ValueError("Invalid refresh token")

    # Check token in Redis
    with RedisConn() as redis_conn:
        redis_conn.delete(payload["sub"])

    # Hapus cookie di klien
    response.delete_cookie("refresh_token")

    return ApiResponse(status=0, message="Logout")
