from fastapi import FastAPI

from app.routes import api_router
from app.settings import get_settings


def create_app() -> FastAPI:
    """
    Build the FastAPI application with a single entry-point.

    The service only exposes /api/v1/fet/run which orchestrates:
    1. Validación y normalización del payload recibido.
    2. Generación del archivo .fet esperado por FET.
    3. Ejecución del binario de FET y entrega de un resumen.
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.title,
        version=settings.version,
        description=settings.description,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        debug=settings.debug,
    )

    app.include_router(api_router, prefix="/api")
    return app


__all__ = ["create_app"]
