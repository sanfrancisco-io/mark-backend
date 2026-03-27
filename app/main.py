from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.admin import router as admin_router
from app.routers.auth import router as auth_router
from app.routers.public import router as public_router
from app.s3 import ensure_bucket_exists


@asynccontextmanager
async def lifespan(app: FastAPI):
    await ensure_bucket_exists()
    yield


app = FastAPI(title="Marketplace API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(public_router, prefix="/v1/public")
app.include_router(auth_router, prefix="/v1/admin")
app.include_router(admin_router, prefix="/v1/admin")


@app.get("/health")
async def health():
    return {"status": "ok"}
