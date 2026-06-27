"""MamaCare AI FastAPI application entry point."""

import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from app.api import advice, dashboard, health, reminders, sms, users, ussd
from app.core.config import get_settings
from app.core.database import Base, engine
from app.schemas.common import ErrorResponse


def configure_logging() -> None:
    """Configure loguru for structured application logging."""
    settings = get_settings()
    logger.remove()
    logger.add(
        sys.stdout,
        level=settings.log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    configure_logging()
    settings = get_settings()
    logger.info("Starting {} v{}", settings.app_name, settings.app_version)

    # Create tables for development/SQLite; production should use Alembic migrations.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    logger.info("Shutting down {}", settings.app_name)
    await engine.dispose()


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered women's health companion for Africa's Talking USSD and Deepseek AI advice.",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(_request: Request, exc: HTTPException) -> JSONResponse:
    """Return consistent JSON error responses for HTTP exceptions."""
    message = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(message=message).model_dump(),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    _request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Return consistent JSON error responses for validation failures."""
    errors = exc.errors()
    first_error = errors[0] if errors else {}
    field = ".".join(str(part) for part in first_error.get("loc", []))
    message = first_error.get("msg", "Validation error")
    if field:
        message = f"{field}: {message}"

    return JSONResponse(
        status_code=422,
        content=ErrorResponse(message=message).model_dump(),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler for unexpected server errors."""
    logger.exception("Unhandled exception: {}", exc)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(message="Internal server error").model_dump(),
    )


app.include_router(health.router)
app.include_router(users.router)
app.include_router(advice.router)
app.include_router(ussd.router)
app.include_router(reminders.router)
from app.api import sms, dashboard

app.include_router(sms.router)
app.include_router(dashboard.router)
app.include_router(sms.router)
app.include_router(dashboard.router)
