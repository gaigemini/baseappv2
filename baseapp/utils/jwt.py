from datetime import datetime, timedelta, timezone
import logging
from typing import Dict, Any
from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt
from baseapp.model.common import CurrentUser
from baseapp.config.setting import get_settings
# from baseapp.util.utility import is_valid_user

config = get_settings()
jwt_secret_key = config.jwt_secret_key
jwt_algorithm = config.jwt_algorithm
jwt_access_expired_in = int(config.jwt_access_expired_in)
jwt_refresh_expired_in = int(config.jwt_refresh_expired_in)

def create_access_token(data: dict, expire_in: int = 1440) -> tuple:
    to_encode = data.copy()
    _expire_in = jwt_access_expired_in if expire_in else expire_in
    expire = datetime.now(timezone.utc) + timedelta(minutes=_expire_in)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, jwt_secret_key, algorithm=jwt_algorithm)
    return token, jwt_access_expired_in

def create_refresh_token(data: dict, expire_in: int = 7) -> tuple:
    to_encode = data.copy()
    _expire_in = jwt_refresh_expired_in if expire_in else expire_in
    expire = datetime.now(timezone.utc) + timedelta(days=_expire_in)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, jwt_secret_key, algorithm=jwt_algorithm)
    return token, jwt_refresh_expired_in

def decode_jwt_token(token: str) -> Dict[str, Any]:
    return jwt.decode(token, jwt_secret_key, algorithms=[jwt_algorithm])

def get_current_user(ctx: Request, token: str = Depends(OAuth2PasswordBearer(tokenUrl="token"))) -> CurrentUser:
    def credentials_exception(message: str):
        return HTTPException(
            status_code=401,
            detail=message,
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        credentials = decode_jwt_token(token)
    except ExpiredSignatureError as err:
        error_message = f"get_current_user - Log ID: , Error Code: 4, Error Message: {err=}, {type(err)=}"
        logging.error(error_message)
        raise credentials_exception("Token expired.")
    except JWTError as err:
        error_message = f"get_current_user - Log ID: , Error Code: 4, Error Message: {err=}, {type(err)=}"
        logging.error(error_message)
        raise credentials_exception("Could not validate credentials")
    
    # if not is_valid_user(credentials["sub"]):
    #     raise credentials_exception("Could not validate credentials")

    return CurrentUser(
        name=credentials["sub"],
        id=credentials["id"],
        roles=credentials["roles"],
        authority=credentials["authority"],
        org_id=credentials["org_id"],
        token=token,
        log_id=ctx.state.log_id
    )
