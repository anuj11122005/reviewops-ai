"""FastAPI application entrypoint for ReviewOps AI.

Creates the app, registers routers, sets up middleware, and defines the
global exception handler per rules.md §5.
"""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import UTC, datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import pull_requests, repositories, webhooks
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.db.session import init_engine

logger = logging.getLogger(__name__)


# ── Lifespan ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Startup / shutdown lifecycle hook."""
    settings = get_settings()
    setup_logging(level=logging.DEBUG if settings.debug else logging.INFO)
    init_engine()

    if not settings.debug and not settings.github_webhook_secret:
        logger.warning(
            "GITHUB_WEBHOOK_SECRET is empty in production. "
            "Webhook signature verification is silently disabled!"
        )

    logger.info("ReviewOps AI backend started")
    yield
    logger.info("ReviewOps AI backend shutting down")


# ── App factory ──────────────────────────────────────────
def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # ── CORS ─────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Global exception handler (rules.md §5) ──────────
    @app.exception_handler(Exception)
    async def _global_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """Convert unhandled exceptions into the standard error shape.

        Never leaks raw stack traces to API responses.
        """
        logger.exception(
            "Unhandled exception",
            extra={"path": request.url.path, "method": request.method},
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                    "details": None,
                }
            },
        )

    # ── Health check ─────────────────────────────────────
    @app.get("/health", tags=["system"])
    def health_check() -> dict[str, str]:
        """Basic liveness probe."""
        return {
            "status": "healthy",
            "timestamp": datetime.now(tz=UTC).isoformat(),
            "version": settings.app_version,
        }

    # ── Routers ──────────────────────────────────────────
    from app.api.routes import pull_requests, repositories, webhooks, feedback
    app.include_router(webhooks.router, prefix="/api")
    app.include_router(repositories.router, prefix="/api")
    app.include_router(pull_requests.router, prefix="/api")
    app.include_router(feedback.router, prefix="/api")

    return app


app = create_app()
