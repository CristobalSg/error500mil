from config import settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from api.api import api_router
from application.middlewares import (
    SanitizationMiddleware,
    RateLimitMiddleware,
    SecurityLoggingMiddleware
)
from application.logging_config import configure_logging
import logging

# Configurar logging
configure_logging(level="INFO" if settings.environment == "production" else "DEBUG")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SGH - Sistema de Gestión de Horarios", 
    version="1.0.0",
    description="API REST para la gestión de horarios académicos",
    docs_url="/api/docs", 
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

logger.info(f"Iniciando aplicación en modo {settings.environment}")

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            if method in ["get", "post", "put", "delete", "patch"]:
                endpoint_info = openapi_schema["paths"][path][method]
                # Endpoints públicos (sin autenticación requerida)
                public_endpoints = [
                    "/api/auth/login", 
                    "/api/auth/login-json",
                    "/api/auth/refresh",
                    "/api/",
                    "/api/health"
                ]
                # NOTA: /api/auth/register NO es público - requiere admin (USER:CREATE)
                if path not in public_endpoints:
                    if "security" not in endpoint_info:
                        endpoint_info["security"] = [{"BearerAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Middlewares de seguridad (orden importante: de más específico a más general)
# 1. Security Logging - debe ser el primero para capturar todo
app.add_middleware(
    SecurityLoggingMiddleware,
    log_request_body=False,  # No loggear bodies por seguridad
    log_response_body=False,
    enable_performance_logging=True
)

# 2. Rate Limiting - controlar abuso
app.add_middleware(
    RateLimitMiddleware,
    requests_limit=100,  # 100 requests por minuto para no autenticados
    window_seconds=60,
    auth_requests_limit=200  # 200 requests por minuto para autenticados
)

# 3. Sanitization - validar y sanitizar entrada
app.add_middleware(
    SanitizationMiddleware,
    enable_sql_check=True,
    enable_xss_check=True,
    enable_path_check=True
)

# 4. CORS - debe ser uno de los últimos
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.get("/api/")
def root():
    return {
        "message": "SGH Backend API",
        "version": "1.0.0",
        "environment": settings.environment,
        "docs": "/api/docs"
    }

@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "environment": settings.environment,
        "database": "connected"
    }
