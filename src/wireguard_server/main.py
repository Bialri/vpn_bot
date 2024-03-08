from fastapi import FastAPI, Depends
from fastapi.openapi.models import APIKey

from auth import api_key_auth

app = FastAPI()


@app.get("/")
async def read_root(api_key: APIKey = Depends(api_key_auth)):
    return {"Hello": "World"}
