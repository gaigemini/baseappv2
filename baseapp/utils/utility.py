import cbor2,bcrypt,string,secrets,requests
from fastapi.responses import Response

from baseapp.config import setting
from baseapp.model.common import ApiResponse

from baseapp.services._enum.crud import CRUD

config = setting.get_settings()

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

def get_enum(enum_id,use_api = False):
    if use_api:
        try:
            response = requests.get(f"{config.host}/enum/{enum_id}")
            response.raise_for_status()  # Raise error jika HTTP status bukan 200
            response = response.json()
            return response["data"]
        except requests.RequestException as e:
            return {"error": f"API call failed: {str(e)}"}
    else:
        _crud = CRUD()
        response = _crud.get_by_id(enum_id)
        return response["data"]