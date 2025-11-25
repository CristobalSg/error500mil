"""
Middleware de logging seguro para auditoría y monitoreo de seguridad.
"""

import logging
import time
from typing import Set

from fastapi import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


class SecurityLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware que registra eventos de seguridad relevantes.

    Características:
    - Logging de todas las requests con información de seguridad
    - Redacción automática de información sensible
    - Registro de eventos sospechosos
    - Métricas de rendimiento
    - Logs estructurados para facilitar análisis
    """

    # Campos sensibles que deben ser redactados en los logs
    SENSITIVE_FIELDS = {
        "password",
        "token",
        "secret",
        "api_key",
        "apikey",
        "access_token",
        "refresh_token",
        "authorization",
        "passwd",
        "pwd",
        "pass",
        "credential",
        "auth",
    }

    # Headers sensibles
    SENSITIVE_HEADERS = {"authorization", "cookie", "x-api-key", "x-auth-token"}

    # Endpoints que requieren logging especial por ser sensibles
    SENSITIVE_ENDPOINTS = {
        "/api/auth/login",
        "/api/auth/login-json",
        "/api/auth/register",
        "/api/auth/refresh",
        "/api/users",
        "/api/administradores",
    }

    def __init__(
        self,
        app,
        log_request_body: bool = False,  # Por defecto no loggear bodies (pueden tener datos sensibles)
        log_response_body: bool = False,
        enable_performance_logging: bool = True,
    ):
        super().__init__(app)
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
        self.enable_performance_logging = enable_performance_logging

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Procesa cada solicitud y registra eventos de seguridad.
        """
        start_time = time.time()

        # Información básica de la request
        client_ip = self._get_client_ip(request)
        method = request.method
        path = request.url.path
        user_agent = request.headers.get("user-agent", "unknown")

        # Identificar si es un endpoint sensible
        is_sensitive = any(sensitive in path for sensitive in self.SENSITIVE_ENDPOINTS)

        try:
            # Log de inicio de request
            log_data = {
                "event": "request_received",
                "method": method,
                "path": path,
                "client_ip": client_ip,
                "user_agent": user_agent,
                "is_sensitive": is_sensitive,
            }

            # Agregar query params (redactando sensibles)
            if request.query_params:
                log_data["query_params"] = self._redact_sensitive_data(dict(request.query_params))

            # Agregar headers relevantes (sin sensibles)
            log_data["headers"] = self._get_safe_headers(request)

            logger.info(f"Request: {log_data}")

            # Procesar la request
            response = await call_next(request)

            # Calcular tiempo de procesamiento
            process_time = time.time() - start_time

            # Log de respuesta
            response_log = {
                "event": "request_completed",
                "method": method,
                "path": path,
                "client_ip": client_ip,
                "status_code": response.status_code,
                "process_time_ms": round(process_time * 1000, 2),
                "is_sensitive": is_sensitive,
            }

            # Agregar el tiempo de procesamiento como header
            response.headers["X-Process-Time"] = str(process_time)

            # Determinar nivel de log según status code
            if response.status_code >= 500:
                logger.error(f"Server Error: {response_log}")
            elif response.status_code >= 400:
                logger.warning(f"Client Error: {response_log}")
            else:
                logger.info(f"Success: {response_log}")

            # Log especial para eventos de seguridad críticos
            self._log_security_events(request, response, client_ip, process_time)

            # Performance logging
            if self.enable_performance_logging and process_time > 1.0:
                logger.warning(
                    f"Slow request detected: {path} took {process_time:.2f}s from {client_ip}"
                )

            return response

        except Exception as e:
            process_time = time.time() - start_time

            # Log de error
            error_log = {
                "event": "request_failed",
                "method": method,
                "path": path,
                "client_ip": client_ip,
                "error": str(e),
                "error_type": type(e).__name__,
                "process_time_ms": round(process_time * 1000, 2),
            }
            logger.error(f"Request failed: {error_log}", exc_info=True)

            raise

    def _get_client_ip(self, request: Request) -> str:
        """
        Obtiene la IP del cliente, considerando proxies.
        """
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        return request.client.host if request.client else "unknown"

    def _get_safe_headers(self, request: Request) -> dict:
        """
        Obtiene headers seguros (sin información sensible).
        """
        safe_headers = {}
        for key, value in request.headers.items():
            if key.lower() not in self.SENSITIVE_HEADERS:
                safe_headers[key] = value
            else:
                safe_headers[key] = "[REDACTED]"
        return safe_headers

    def _redact_sensitive_data(self, data: dict) -> dict:
        """
        Redacta campos sensibles en un diccionario.
        """
        redacted = {}
        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in self.SENSITIVE_FIELDS):
                redacted[key] = "[REDACTED]"
            elif isinstance(value, dict):
                redacted[key] = self._redact_sensitive_data(value)
            else:
                redacted[key] = value
        return redacted

    def _log_security_events(
        self, request: Request, response: Response, client_ip: str, process_time: float
    ):
        """
        Registra eventos de seguridad específicos.
        """
        path = request.url.path
        status_code = response.status_code

        # Login exitoso
        if path in ["/api/auth/login", "/api/auth/login-json"] and status_code == 200:
            logger.info(
                f"SECURITY EVENT: Successful login from {client_ip} " f"(took {process_time:.2f}s)"
            )

        # Login fallido
        elif path in ["/api/auth/login", "/api/auth/login-json"] and status_code == 401:
            logger.warning(
                f"SECURITY EVENT: Failed login attempt from {client_ip} "
                f"(took {process_time:.2f}s)"
            )

        # Registro de nuevo usuario
        elif path == "/api/auth/register" and status_code == 201:
            logger.info(f"SECURITY EVENT: New user registration from {client_ip}")

        # Intentos de acceso no autorizado
        elif status_code == 403:
            logger.warning(f"SECURITY EVENT: Forbidden access attempt to {path} from {client_ip}")

        # Token inválido o expirado
        elif status_code == 401 and path not in ["/api/auth/login", "/api/auth/login-json"]:
            logger.warning(
                f"SECURITY EVENT: Unauthorized access attempt to {path} from {client_ip}"
            )

        # Múltiples errores 4xx (posible ataque)
        elif status_code >= 400 and status_code < 500:
            logger.info(f"SECURITY EVENT: Client error {status_code} on {path} from {client_ip}")
