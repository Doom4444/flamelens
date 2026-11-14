from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import get_settings
from app.core.logging import setup_logging, logger
from app.core.exceptions import (
    FlameLensException,
    flamelens_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    global_exception_handler,
)
from app.api.router import api_router
from app.data_pipeline.metadata_repository import (
    DATASETS_FILE,
    FILES_FILE,
    INVESTIGATIONS_FILE,
    STORAGE_FILE,
    store as metadata_store,
)

settings = get_settings()

REQUIRED_METADATA_FILES = (
    INVESTIGATIONS_FILE,
    DATASETS_FILE,
    FILES_FILE,
    STORAGE_FILE,
)


def _validate_metadata_artifacts() -> None:
    """Verify the read-only metadata inventories shipped with the app.

    The API cannot serve real data without these four files, so a missing or
    unreadable inventory is treated as a hard startup failure instead of a
    runtime 500 later. Only file names (never absolute paths) are surfaced.
    """
    inventory_dir = metadata_store.metadata_dir
    missing = [
        filename
        for filename in REQUIRED_METADATA_FILES
        if not (inventory_dir / filename).is_file()
    ]
    if missing:
        raise RuntimeError(
            "Missing required metadata inventory file(s): "
            + ", ".join(missing)
            + ". Set FLAMELENS_METADATA_DIR to a directory containing the "
            "Stage 1 NASA PSI inventories."
        )

    # Load once so malformed JSON fails fast and the first request is warm.
    investigations = metadata_store.investigations_payload
    metadata_store.datasets_payload
    files = metadata_store.files_payload
    metadata_store.storage_payload

    logger.info(
        "Metadata inventories ready: %s investigations, %s files (dir=%s)",
        len(investigations.get("investigations", [])),
        len(files.get("files", [])),
        inventory_dir,
    )


def _log_cors_configuration() -> None:
    """Surface CORS misconfiguration (a common cause of blocked deployments)."""
    origins = settings.CORS_ORIGINS
    if settings.is_production:
        if origins == ["*"]:
            logger.warning(
                "CORS allows every origin. Set CORS_ORIGINS to the deployed "
                "frontend URL for a restricted production deployment."
            )
        elif not origins:
            logger.warning(
                "CORS_ORIGINS is empty; browser requests from the frontend "
                "will be rejected. Set it to the deployed frontend origin."
            )
        elif all(
            origin.startswith(("http://localhost", "http://127.0.0.1"))
            for origin in origins
        ):
            logger.warning(
                "CORS_ORIGINS only contains localhost origins in production. "
                "Set CORS_ORIGINS to the deployed frontend URL, e.g. "
                "https://<your-frontend>.vercel.app"
            )
    logger.info("CORS allowed origins: %s", ", ".join(origins) or "<none>")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for application startup and shutdown."""
    setup_logging(settings.LOG_LEVEL)
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION} [{settings.ENVIRONMENT}]")

    # Honour FLAMELENS_METADATA_DIR whether it comes from a real environment
    # variable (Docker/Render) or from a local .env file.
    configured_dir = settings.FLAMELENS_METADATA_DIR.strip()
    if configured_dir:
        resolved_dir = Path(configured_dir).expanduser().resolve()
        if resolved_dir != metadata_store.metadata_dir:
            metadata_store.metadata_dir = resolved_dir
            metadata_store.reload()

    _validate_metadata_artifacts()
    _log_cors_configuration()
    yield
    logger.info(f"Shutting down {settings.APP_NAME}")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="NASA Microgravity Combustion Research Explorer - Scientific Intelligence Platform",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Exception handlers
app.add_exception_handler(FlameLensException, flamelens_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# CORS configuration. Credentials are only enabled when origins are explicit;
# wildcard origins cannot be combined with credentialed requests.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials="*" not in settings.CORS_ORIGINS,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
    max_age=600,
)

# Metadata payloads are large JSON documents; gzip keeps responses small.
app.add_middleware(GZipMiddleware, minimum_size=1024)

# Central API Router
app.include_router(
    api_router,
    prefix=settings.API_PREFIX,
)


@app.get("/", summary="Root Endpoint")
async def root():
    """
    Root endpoint for FlameLens API service discovery.
    """
    return {
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online",
        "docs_url": "/docs",
        "api_v1": settings.API_PREFIX,
        "message": "Welcome to FlameLens API - NASA Microgravity Combustion Research Explorer",
    }
