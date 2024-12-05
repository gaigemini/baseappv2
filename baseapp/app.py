import os

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

@app.get("/v1/test")
def read_root():
    return "ok"