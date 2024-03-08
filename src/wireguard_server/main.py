from fastapi import FastAPI, Depends
from fastapi.openapi.models import APIKey

from auth import api_key_auth
from router import router
app = FastAPI()

app.include_router(router)

