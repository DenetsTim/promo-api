import os
import uvicorn

from app.app import app
from app.b2b.b2b_api import router as B2BRouter
from app.b2c.b2c_api import router as B2CRouter
from app.default_api import router as DefaultRouter


app.include_router(B2BRouter)
app.include_router(B2CRouter)
app.include_router(DefaultRouter)


if __name__ == "__main__":
    server_address = os.getenv("SERVER_ADDRESS", "0.0.0.0:8080")
    host, port = server_address.split(":")
    uvicorn.run(app, host=host, port=int(port))
