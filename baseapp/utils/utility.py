import cbor2
from fastapi.responses import Response
from baseapp.model.common import ApiResponse

# Custom CBOR response class
class CBORResponse(Response):
    def __init__(self, content: ApiResponse, **kwargs):
        cbor_content = cbor2.dumps(content.model_dump())  # assuming ApiResponse is pydantic model
        super().__init__(content=cbor_content, media_type="application/cbor", **kwargs)

def get_response_based_on_env(response, app_env: str):
    if app_env == "production":
        return CBORResponse(content=response)
    return response