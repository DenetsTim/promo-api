from fastapi import APIRouter

from .database import init_tables, drop_tables

router = APIRouter(prefix="/api")


@router.get("/ping")
async def ping():
    return {"status": "PROOOOOOOOOOOOOOOOOD"}


@router.get("/init")
async def init_db():
    await init_tables()
    return {"status": "initted"}


@router.get("/drop")
async def drop_db():
    await drop_tables()
    return {"status": "dropped"}


@router.get("/restart")
async def restart_db():
    await drop_tables()
    await init_tables()
    return {"status": "restarted"}
