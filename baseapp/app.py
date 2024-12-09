import os,uuid,time

from baseapp.config import setting, redis
config = setting.get_settings()

from json import dumps as jdumps, loads as jloads
from cbor2 import dumps as cdumps, loads as cloads

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

os.makedirs("log", exist_ok=True) # create log folder

import logging.config
logging.config.fileConfig('logging.conf')
from logging import getLogger
logger = getLogger()

from baseapp.test_connection.api import router as testconn_router # test connection
from baseapp.services.database.api import router as db_router # init database
from baseapp.services._enum.api import router as enum_router # enum
from baseapp.services._org.api import router as org_router # organization
from baseapp.services.auth.api import router as auth_router # auth

app = FastAPI(
    title="baseapp",
    description="Gateway for baseapp implementation.",
    version="0.0.1",
)

os.makedirs(config.file_location, exist_ok=True) # create folder data/files

app.include_router(testconn_router)
app.include_router(db_router)
app.include_router(enum_router)
app.include_router(org_router)
app.include_router(auth_router)

@app.middleware("http")
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

allowed_origins = [
    "https://gai.co.id",
    "https://baseapp.gai.co.id"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/v1/test")
def read_root():
    return "ok"