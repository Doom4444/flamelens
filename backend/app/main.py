from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import (
    APP_NAME,
    APP_VERSION,
    API_PREFIX,
    CORS_ORIGINS,
)
from app.api.router import api_router

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="NASA Microgravity Combustion Research Explorer",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    api_router,
    prefix=API_PREFIX,
)


@app.get("/")
async def root():
    return {
        "application": APP_NAME,
        "version": APP_VERSION,
        "message": "Welcome to FlameLens API",
    }