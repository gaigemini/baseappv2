import cbor2
from fastapi.responses import Response
from baseapp.model.common import ApiResponse
import bcrypt
import string
import secrets

# Custom CBOR response class
class CBORResponse(Response):
    def __init__(self, content: ApiResponse, **kwargs):
        cbor_content = cbor2.dumps(content.model_dump())  # assuming ApiResponse is pydantic model
        super().__init__(content=cbor_content, media_type="application/cbor", **kwargs)

def get_response_based_on_env(response, app_env: str):
    if app_env == "production":
        return CBORResponse(content=response)
    return response

def hash_password(password: str, salt=None) -> tuple:
    usalt = bcrypt.gensalt() if salt == None else salt
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), usalt)
    return usalt, hashed_password

def generate_password(length: int = 8):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password