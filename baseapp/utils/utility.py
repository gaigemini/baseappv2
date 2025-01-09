import cbor2,bcrypt,string,secrets,logging
from fastapi.responses import Response, JSONResponse
from pymongo.errors import PyMongoError
from fastapi import Response, Request
from pydantic import BaseModel, ValidationError
from functools import wraps
from datetime import datetime, timezone

from baseapp.config.setting import get_settings
from baseapp.model.common import ApiResponse, PaginatedApiResponse, TokenResponse

config = get_settings()
logger = logging.getLogger()

# Custom CBOR response class
class CBORResponse(Response):
    def __init__(self, content, status_code: int = 200, **kwargs):
        # Periksa apakah konten adalah salah satu dari model yang didukung
        if isinstance(content, (ApiResponse, PaginatedApiResponse, TokenResponse)):
            content = process_mongodb_data(content.model_dump())
            cbor_content = cbor2.dumps(content)
        else:
            raise ValueError("Content must be an instance of ApiResponse or PaginatedApiResponse.")
        super().__init__(content=cbor_content, media_type="application/cbor", status_code=status_code, **kwargs)

def process_mongodb_data(data):
    logger.debug(f"ini bro: {type(data)}")
    if isinstance(data, dict):
        # Jika data adalah dictionary, proses semua nilai dalam dictionary
        if 'data' in data:
            # Jika ada key 'data', proses data dalam key tersebut
            data['data'] = process_mongodb_data(data['data'])
        return {k: process_mongodb_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        # Jika data adalah list, proses semua item dalam list
        return [process_mongodb_data(item) for item in data]
    elif isinstance(data, datetime):
        # Jika data adalah datetime, konversi ke string ISO 8601
        if data.tzinfo is None:
            data = data.replace(tzinfo=timezone.utc)
        return data.isoformat()  # Mengubah ke string ISO 8601
    return data

def get_response_based_on_env(response_model: BaseModel, status_code: int = 200):
    if config.app_env == "production":
        return CBORResponse(content=response_model, status_code=status_code)
    else:
        return JSONResponse(content=response_model.model_dump(), status_code=status_code)

def cbor_or_json(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Jalankan fungsi asli untuk mendapatkan hasil
        result = await func(*args, **kwargs)
        
        # Tentukan format respons
        return get_response_based_on_env(response_model=result)
    
    return wrapper

def cbor_or_json_req(model):
    def decorator(func):
        async def wrapper(req: Request, *args, **kwargs):
            content_type = req.headers.get("content-type", "")
            if content_type == "application/cbor":
                try:
                    body = cbor2.loads(await req.body())
                except Exception:
                    raise ValueError("Invalid CBOR format")

                # Validasi data menggunakan model Pydantic
                try:
                    validated_data = model(**body)
                except ValidationError as e:
                    raise ValueError(e.errors())

                kwargs["req"] = validated_data  # Berikan objek tervalidasi ke handler
            else:
                kwargs["req"] = await req.json()  # Untuk JSON, biarkan FastAPI memproses

            return await func(*args, **kwargs)

        return wrapper
    return decorator

async def parse_cbor_to_model(request: Request, model: BaseModel):
    try:
        if request.headers.get("content-type") == "application/cbor":
            body = await request.body()
            try:
                data = cbor2.loads(body)  # Parsing CBOR menjadi dictionary
            except cbor2.CBORDecodeError:
                raise ValueError("Invalid CBOR format")
        else:
            data = await request.json()  # Fallback ke JSON
        
        # Validasi menggunakan model Pydantic
        return model(**data)
    except Exception as e:
        raise ValueError(f"Invalid request format: {str(e)}")
    
def hash_password(password: str, salt=None) -> tuple:
    usalt = bcrypt.gensalt() if salt == None else salt
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), usalt)
    return usalt, hashed_password

def generate_password(length: int = 8):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password
 
def get_enum(mongo, enum_id):
    collection = mongo._db["_enum"]
    try:
        enum = collection.find_one({"_id": enum_id})
        return enum
    except PyMongoError as pme:
        raise ValueError("Database error occurred while find document.") from pme
    except Exception as e:
        raise

def is_none(variable, default_value):
    return default_value if variable is None else variable