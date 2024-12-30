from fastapi import APIRouter, Depends

from baseapp.model.common import ApiResponse, CurrentUser
from baseapp.utils.jwt import get_current_user

from baseapp.config import setting
config = setting.get_settings()

import logging, httpx
logger = logging.getLogger()

router = APIRouter(prefix="/v1/profile", tags=["Profile"])
    
@router.get("/organization", response_model=ApiResponse)
async def get_profile(cu: CurrentUser = Depends(get_current_user)) -> ApiResponse:
    token: str = cu.token
    org_id: str = cu.org_id
    api_url = config.host + f"/v1/_organization/find/{org_id}"
    headers = {'Content-Type': 'application/json', 'Authorization': "Bearer "+ token}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(api_url, headers=headers, timeout=10)
            response.raise_for_status()
            return ApiResponse.model_validate_json(response.text)
        except httpx.RequestError as exc:
            logger.error(f"An error occurred while requesting {exc.request.url}: {exc}")
            raise ValueError(str(exc))
        except httpx.HTTPStatusError as exc:
            logger.error(f"HTTP error occurred: {exc.response.status_code}")
            raise ValueError(exc.response.text)

@router.get("/user", response_model=ApiResponse)
async def get_profile(cu: CurrentUser = Depends(get_current_user)) -> ApiResponse:
    token: str = cu.token
    user_id: str = cu.id
    api_url = config.host + f"/v1/_user/find/{user_id}"
    headers = {'Content-Type': 'application/json', 'Authorization': "Bearer "+ token}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(api_url, headers=headers, timeout=10)
            response.raise_for_status()
            return ApiResponse.model_validate_json(response.text)
        except httpx.RequestError as exc:
            logger.error(f"An error occurred while requesting {exc.request.url}: {exc}")
            raise ValueError(str(exc))
        except httpx.HTTPStatusError as exc:
            logger.error(f"HTTP error occurred: {exc.response.status_code}")
            raise ValueError(exc.response.text)
    
