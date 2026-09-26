from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import Settings, get_settings
from app.core.logging import configure_logging


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings.log_level)

    is_prod = settings.app_env == "production"
    app = FastAPI(
        title="AuditReady API",
        version="0.1.0",
        # OpenAPI stays on: the frontend client is generated from it. Docs UI hidden in prod.
        docs_url=None if is_prod else "/docs",
        redoc_url=None,
        openapi_url=f"{settings.api_prefix}/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,  # only frontend origins, never "*" (Section 12.2)
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
    )

    app.include_router(api_router, prefix=settings.api_prefix)
    return app


app = create_app()
