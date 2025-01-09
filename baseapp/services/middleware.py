import logging,uuid,time,cbor2
from fastapi import Request, FastAPI, HTTPException
from fastapi.responses import JSONResponse, Response

from baseapp.config import setting
from baseapp.model.common import ApiResponse

from baseapp.utils.utility import get_response_based_on_env

config = setting.get_settings()
logger = logging.getLogger()

async def http_exception_handler(request: Request, exc: HTTPException):
    if config.app_env == "production":
        error_response = {
            "status": exc.status_code,
            "message": exc.detail
        }
        cbor_content = cbor2.dumps(error_response)
        return Response(content=cbor_content, media_type="application/cbor", status_code=exc.status_code)
    else:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )
    
async def handle_exceptions(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except ValueError as ve:
        # Untuk kesalahan validasi user input
        content = ApiResponse(status=4, message=str(ve))
        return get_response_based_on_env(content,status_code=400)
    except ConnectionError as ce:
        # Untuk kesalahan koneksi ke layanan eksternal
        content = ApiResponse(status=4, message=str(ce))
        return get_response_based_on_env(content, status_code=500)
    except PermissionError as pe:
        # Untuk kesalahan otorisasi
        logger.warning(f"Access denied: {str(pe)}")
        content = ApiResponse(status=4, message="Access denied.")
        return get_response_based_on_env(content, status_code=403)
    except Exception as e:
        # Untuk semua kesalahan lainnya
        logger.exception(f"Unhandled error: {str(e)}")
        content = ApiResponse(
            status=4,
            message="An unexpected error occurred. Please try again later."
        )
        return get_response_based_on_env(content, status_code=500)       
    
async def add_process_time_and_log(request: Request, call_next):
    if "log_id" in request.headers:
        log_id = request.headers.get("log_id")
    else:
        log_id = str(uuid.uuid4()).replace('-', '')
    request.state.log_id = log_id

    log_request = {
        "log_id": log_id,
        "method": request.method,
        "url": request.url.path
    }
    logging.info(f"request: {log_request}")

    start_time = time.time()
    response = await call_next(request)

    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    log_response = {
        "log_id": log_id,
        "process_time": str(process_time),
        "http_status_code": response.status_code
    }
    logging.info(f"response: {log_response}")
    return response

def setup_middleware(app: FastAPI):
    app.middleware("http")(handle_exceptions)
    app.middleware("http")(add_process_time_and_log)
    app.add_exception_handler(HTTPException, http_exception_handler)
