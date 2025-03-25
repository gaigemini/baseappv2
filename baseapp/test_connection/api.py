from fastapi import APIRouter, Request, Depends
import logging, httpx, json, time, cbor2

from baseapp.test_connection import crud as test
from baseapp.model.common import ApiResponse, CurrentUser

from baseapp.config import setting
config = setting.get_settings()

from baseapp.utils.utility import cbor_or_json
from baseapp.utils.jwt import get_current_user

logger = logging.getLogger()

router = APIRouter(prefix="/v1/test", tags=["Test Connection"])

@router.get("/database", response_model=ApiResponse)
@cbor_or_json
async def test_connection_to_database(ctx: Request) -> ApiResponse:
    resp = test.test_connection_to_mongodb()
    return ApiResponse(status=0, message=resp)

@router.get("/redis")
@cbor_or_json
async def test_connection_to_redis(ctx: Request) -> ApiResponse:
    resp = test.test_connection_to_redis()
    return ApiResponse(status=0, message=resp)
    
@router.get("/minio")
@cbor_or_json
async def test_connection_to_minio(ctx: Request) -> ApiResponse:
    resp = test.test_connection_to_minio()
    return ApiResponse(status=0, message=resp)

@router.get("/rabbit")
@cbor_or_json
async def test_connection_to_rabbit(ctx: Request) -> ApiResponse:
    resp = test.test_connection_to_rabbit()
    return ApiResponse(status=0, message=resp)
    
@router.get("/clickhouse")
@cbor_or_json
async def test_connection_to_clickhouse(ctx: Request) -> ApiResponse:
    resp = test.test_connection_to_clickhouse()
    return ApiResponse(status=0, message=resp)

@router.api_route("/forward/cbor/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"], response_model=ApiResponse)
async def test_api_cbor(ctx: Request, path: str, cu: CurrentUser = Depends(get_current_user)) -> ApiResponse:
    # Extract incoming request details
    method = ctx.method.upper()
    headers = dict(ctx.headers)
    
    # content_type = headers.get("content-type", "").lower()
    # api_key = ctx.headers.get("x-api-key")
    # api_secret = ctx.headers.get("x-api-secret")
    forwarded_url = f"{config.host}/{path}"
    logger.debug(f"Target URL: {forwarded_url}")

    body = await ctx.body()
    encoded_body = {}
    if body:
        logger.debug(f"Payload body: {len(body)} type: {type(body)}")

        # Generate `x-signature`
        minified_body = json.loads(body.decode("utf-8"))
        # Encode body ke CBOR
        encoded_body = cbor2.dumps(minified_body)

    logger.debug(f"Informasi header: {headers}")
    
    async with httpx.AsyncClient() as client:
        try:
            logger.debug("awal client")
            obj_headers = {"Content-Type": "application/cbor"}
            if "authorization" in headers:
                obj_headers["authorization"] = headers["authorization"]
            response = await client.request(
                method=method,
                url=forwarded_url,
                headers=obj_headers,
                data=encoded_body,
                timeout=30
            )
            logger.debug("akhir client")
            logger.debug(f"respon status: {response.raise_for_status()}")
            logger.debug(f"ini dia responsenya: {cbor2.loads(response.content)}")
            response.raise_for_status()
            return cbor2.loads(response.content)
        except httpx.RequestError as exc:
            logger.error(f"An error occurred while requesting {exc.request.url}: {exc}")
            raise ValueError(str(exc))
        except httpx.HTTPStatusError as exc:
            logger.error(f"HTTP error occurred: {exc.response.status_code}")
            error_detail = cbor2.loads(exc.response.content)  # Decode CBOR jika response CBOR
            return error_detail
        except Exception as e:
            logger.error(f"errornya disini ya bro: {e}")
            raise ValueError(e)

