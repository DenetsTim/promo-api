from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError

from authx import AuthXConfig, AuthX
from datetime import timedelta
import os

from .database import init_tables


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    await init_tables()
    yield

app = FastAPI(title="Promo Code API", lifespan=lifespan)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(exc)
    raise HTTPException(400, {"status": "error"})

authXConfig = AuthXConfig()
authXConfig.JWT_SECRET_KEY = os.getenv("RANDOM_SECRET", "12345")
authXConfig.JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)

security = AuthX(config=authXConfig)
security.handle_errors(app)


@security.set_subject_getter
def get_account_id_from_uid(uid: str) -> str:
    return uid
