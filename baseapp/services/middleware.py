import logging,uuid,time
from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse

from baseapp.config import setting
from baseapp.model.common import ApiResponse

# from baseapp.utils.utility import get_response_based_on_env

config = setting.get_settings()
logger = logging.getLogger()

async def handle_exceptions(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except ValueError as ve:
        # Untuk kesalahan validasi user input
        return JSONResponse(
            content=ApiResponse(status=4, message=str(ve)).model_dump(),
            status_code=400,  # Bad Request
        )
    except ConnectionError as ce:
        # Untuk kesalahan koneksi ke layanan eksternal
        return JSONResponse(
            content=ApiResponse(status=4, message=str(ce)).model_dump(),
            status_code=500,  # Internal Server Error
        )
    except PermissionError as pe:
        # Untuk kesalahan otorisasi
        logger.warning(f"Access denied: {str(pe)}")
        return JSONResponse(
            content=ApiResponse(status=4, message="Access denied.").model_dump(),
            status_code=403,  # Forbidden
        )
    except Exception as e:
        # Untuk semua kesalahan lainnya
        logger.exception(f"Unhandled error: {str(e)}")
        return JSONResponse(
            content=ApiResponse(
                status=4, message="An unexpected error occurred. Please try again later."
            ).model_dump(),
            status_code=500,  # Internal Server Error
        )
    
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
