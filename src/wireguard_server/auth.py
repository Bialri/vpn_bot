from fastapi.security.api_key import APIKeyHeader
from fastapi import Security, HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED
import hashlib
import json
import base64

api_key_header = APIKeyHeader(name="X-API-Key")


async def api_key_auth(api_key_header: str = Security(api_key_header)):
    with open("api_keys.json", "r") as file:
        api_keys = json.load(file)
    key_hashed = hashlib.pbkdf2_hmac("sha256",
                                     api_key_header.encode('utf8'),
                                     b'salt',
                                     100000)
    key_hashed_decoded = base64.b64encode(key_hashed).decode('utf8')

    if key_hashed_decoded not in api_keys:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )
