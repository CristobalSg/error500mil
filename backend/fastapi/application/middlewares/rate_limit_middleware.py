"""
Middleware de rate limiting básico para prevenir abuso de la API.
"""

import logging
import time
from collections import defaultdict
from typing import Dict, Tuple

from fastapi import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware que implementa rate limiting básico por IP.

    Características:
    - Límite de requests por ventana de tiempo
    - Tracking por IP
    - Diferentes límites para endpoints públicos y autenticados
    - Limpieza automática de registros antiguos
    """

    def __init__(
        self,
        app,
        requests_limit: int = 100,  # Requests por ventana
        window_seconds: int = 60,  # Ventana de tiempo en segundos
        auth_requests_limit: int = 200,  # Límite mayor para usuarios autenticados
        cleanup_interval: int = 300,  # Limpiar cache cada 5 minutos
    ):
        super().__init__(app)
        self.requests_limit = requests_limit
        self.window_seconds = window_seconds
        self.auth_requests_limit = auth_requests_limit
        self.cleanup_interval = cleanup_interval

        # Storage: {ip: [(timestamp, is_authenticated), ...]}
        self.request_counts: Dict[str, list] = defaultdict(list)
        self.last_cleanup = time.time()

        # Endpoints que no requieren rate limiting estricto
        self.excluded_paths = ["/api/health", "/api/", "/api/docs", "/api/openapi.json"]

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Procesa cada solicitud y aplica rate limiting.
        """
        try:
            # Excluir ciertos endpoints del rate limiting
            if request.url.path in self.excluded_paths:
                return await call_next(request)

            # Obtener IP del cliente
            client_ip = self._get_client_ip(request)

            # Limpiar registros antiguos periódicamente
            current_time = time.time()
            if current_time - self.last_cleanup > self.cleanup_interval:
                self._cleanup_old_records(current_time)
                self.last_cleanup = current_time

            # Verificar si está autenticado (buscar token en headers)
            is_authenticated = self._is_authenticated(request)

            # Verificar rate limit
            if not self._check_rate_limit(client_ip, current_time, is_authenticated):
                logger.warning(
                    f"Rate limit excedido para IP {client_ip} " f"(autenticado: {is_authenticated})"
                )
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "detail": "Demasiadas solicitudes. Por favor, intenta más tarde.",
                        "retry_after": self.window_seconds,
                    },
                    headers={
                        "Retry-After": str(self.window_seconds),
                        "X-RateLimit-Limit": str(
                            self.auth_requests_limit if is_authenticated else self.requests_limit
                        ),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(int(current_time + self.window_seconds)),
                    },
                )

            # Registrar la solicitud
            self.request_counts[client_ip].append((current_time, is_authenticated))

            # Procesar la solicitud
            response = await call_next(request)

            # Agregar headers de rate limit a la respuesta
            response = self._add_rate_limit_headers(
                response, client_ip, current_time, is_authenticated
            )

            return response

        except Exception as e:
            logger.error(f"Error en RateLimitMiddleware: {str(e)}")
            # En caso de error, permitir la solicitud para no bloquear el servicio
            return await call_next(request)

    def _get_client_ip(self, request: Request) -> str:
        """
        Obtiene la IP del cliente, considerando proxies.
        """
        # Verificar headers de proxy
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            # Tomar la primera IP (cliente original)
            return forwarded.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fallback a la IP directa
        return request.client.host if request.client else "unknown"

    def _is_authenticated(self, request: Request) -> bool:
        """
        Verifica si la solicitud incluye un token de autenticación.
        """
        auth_header = request.headers.get("Authorization")
        return bool(auth_header and auth_header.startswith("Bearer "))

    def _check_rate_limit(self, ip: str, current_time: float, is_authenticated: bool) -> bool:
        """
        Verifica si la IP ha excedido el rate limit.
        Retorna True si está dentro del límite, False si lo excedió.
        """
        # Obtener límite según autenticación
        limit = self.auth_requests_limit if is_authenticated else self.requests_limit

        # Filtrar requests dentro de la ventana de tiempo
        window_start = current_time - self.window_seconds
        recent_requests = [(ts, auth) for ts, auth in self.request_counts[ip] if ts > window_start]

        # Actualizar el storage con solo requests recientes
        self.request_counts[ip] = recent_requests

        # Verificar si excede el límite
        return len(recent_requests) < limit

    def _add_rate_limit_headers(
        self, response: Response, ip: str, current_time: float, is_authenticated: bool
    ) -> Response:
        """
        Agrega headers informativos sobre el rate limit a la respuesta.
        """
        limit = self.auth_requests_limit if is_authenticated else self.requests_limit
        window_start = current_time - self.window_seconds

        recent_count = sum(1 for ts, _ in self.request_counts[ip] if ts > window_start)

        remaining = max(0, limit - recent_count)

        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(current_time + self.window_seconds))

        return response

    def _cleanup_old_records(self, current_time: float):
        """
        Limpia registros antiguos para evitar crecimiento ilimitado de memoria.
        """
        window_start = current_time - self.window_seconds

        # Crear una nueva estructura solo con datos recientes
        cleaned_counts = defaultdict(list)
        for ip, timestamps in self.request_counts.items():
            recent = [(ts, auth) for ts, auth in timestamps if ts > window_start]
            if recent:  # Solo mantener IPs con requests recientes
                cleaned_counts[ip] = recent

        self.request_counts = cleaned_counts
        logger.info(f"Rate limit cache limpiado. IPs activas: {len(self.request_counts)}")
