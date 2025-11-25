"""
Middleware de sanitización de entrada para prevenir inyecciones y ataques XSS.
"""

import json
import logging
import re
from typing import Any, Dict

from fastapi import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

logger = logging.getLogger(__name__)


class SanitizationMiddleware(BaseHTTPMiddleware):
    """
    Middleware que sanitiza los datos de entrada para prevenir ataques de inyección.

    Características:
    - Detecta patrones de SQL injection
    - Detecta patrones de XSS
    - Detecta path traversal
    - Valida tipos de contenido
    - Limita tamaño de payload
    """

    # Patrones sospechosos para SQL Injection
    SQL_INJECTION_PATTERNS = [
        r"(\bunion\b.*\bselect\b)",
        r"(\bselect\b.*\bfrom\b)",
        r"(\binsert\b.*\binto\b)",
        r"(\bupdate\b.*\bset\b)",
        r"(\bdelete\b.*\bfrom\b)",
        r"(\bdrop\b.*\btable\b)",
        r"(;.*--)",
        r"('.*or.*'.*=.*')",
        r"(\".*or.*\".*=.*\")",
        r"(\bexec\b.*\()",
        r"(\bexecute\b.*\()",
    ]

    # Patrones sospechosos para XSS
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"onerror\s*=",
        r"onload\s*=",
        r"onclick\s*=",
        r"<iframe[^>]*>",
        r"<object[^>]*>",
        r"<embed[^>]*>",
    ]

    # Patrones de path traversal
    PATH_TRAVERSAL_PATTERNS = [
        r"\.\./",
        r"\.\.",
        r"%2e%2e",
        r"%252e%252e",
    ]

    # Tamaño máximo de payload (5MB)
    MAX_PAYLOAD_SIZE = 5 * 1024 * 1024

    def __init__(
        self,
        app,
        enable_sql_check: bool = True,
        enable_xss_check: bool = True,
        enable_path_check: bool = True,
    ):
        super().__init__(app)
        self.enable_sql_check = enable_sql_check
        self.enable_xss_check = enable_xss_check
        self.enable_path_check = enable_path_check

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Procesa cada solicitud y aplica sanitización.
        """
        try:
            # 1. Validar Content-Type para requests con body
            if request.method in ["POST", "PUT", "PATCH"]:
                content_type = request.headers.get("content-type", "")
                if content_type and not self._is_valid_content_type(content_type):
                    logger.warning(
                        f"Content-Type inválido detectado: {content_type} desde {request.client.host}"
                    )
                    return JSONResponse(
                        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                        content={"detail": "Content-Type no soportado"},
                    )

            # 2. Validar tamaño del payload
            content_length = request.headers.get("content-length")
            if content_length and int(content_length) > self.MAX_PAYLOAD_SIZE:
                logger.warning(
                    f"Payload demasiado grande: {content_length} bytes desde {request.client.host}"
                )
                return JSONResponse(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    content={"detail": "Payload demasiado grande"},
                )

            # 3. Sanitizar query parameters
            if request.query_params:
                if not self._sanitize_dict(dict(request.query_params), request):
                    return JSONResponse(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        content={"detail": "Parámetros de consulta contienen datos sospechosos"},
                    )

            # 4. Sanitizar path parameters
            if not self._sanitize_string(request.url.path, request, "URL path"):
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"detail": "URL contiene patrones sospechosos"},
                )

            # 5. Sanitizar body (si existe)
            if request.method in ["POST", "PUT", "PATCH"]:
                content_type = request.headers.get("content-type", "")

                if "application/json" in content_type:
                    try:
                        body = await request.body()
                        if body:
                            body_str = body.decode("utf-8")
                            body_json = json.loads(body_str)

                            if not self._sanitize_dict(body_json, request):
                                return JSONResponse(
                                    status_code=status.HTTP_400_BAD_REQUEST,
                                    content={"detail": "Body contiene datos sospechosos"},
                                )

                            # Reconstruir el request con el body validado
                            async def receive():
                                return {"type": "http.request", "body": body}

                            request._receive = receive
                    except json.JSONDecodeError:
                        logger.warning(f"JSON inválido desde {request.client.host}")
                        return JSONResponse(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            content={"detail": "JSON inválido"},
                        )
                    except Exception as e:
                        logger.error(f"Error sanitizando body: {str(e)}")

            # Continuar con la solicitud
            response = await call_next(request)
            return response

        except Exception as e:
            logger.error(f"Error en SanitizationMiddleware: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Error interno del servidor"},
            )

    def _is_valid_content_type(self, content_type: str) -> bool:
        """Valida que el Content-Type sea permitido."""
        allowed_types = [
            "application/json",
            "application/x-www-form-urlencoded",
            "multipart/form-data",
        ]
        return any(allowed in content_type.lower() for allowed in allowed_types)

    def _sanitize_dict(self, data: Dict[str, Any], request: Request) -> bool:
        """
        Sanitiza recursivamente un diccionario.
        Retorna False si se detectan patrones sospechosos.
        """
        for key, value in data.items():
            if isinstance(value, str):
                if not self._sanitize_string(value, request, f"campo '{key}'"):
                    return False
            elif isinstance(value, dict):
                if not self._sanitize_dict(value, request):
                    return False
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        if not self._sanitize_string(item, request, f"campo '{key}' (lista)"):
                            return False
                    elif isinstance(item, dict):
                        if not self._sanitize_dict(item, request):
                            return False
        return True

    def _sanitize_string(self, value: str, request: Request, field_name: str = "campo") -> bool:
        """
        Verifica si una cadena contiene patrones sospechosos.
        Retorna False si se detectan patrones sospechosos.
        """
        value_lower = value.lower()

        # Check SQL Injection
        if self.enable_sql_check:
            for pattern in self.SQL_INJECTION_PATTERNS:
                if re.search(pattern, value_lower, re.IGNORECASE):
                    logger.warning(
                        f"Posible SQL Injection detectado en {field_name}: "
                        f"patrón '{pattern}' desde {request.client.host}"
                    )
                    return False

        # Check XSS
        if self.enable_xss_check:
            for pattern in self.XSS_PATTERNS:
                if re.search(pattern, value_lower, re.IGNORECASE):
                    logger.warning(
                        f"Posible XSS detectado en {field_name}: "
                        f"patrón '{pattern}' desde {request.client.host}"
                    )
                    return False

        # Check Path Traversal
        if self.enable_path_check:
            for pattern in self.PATH_TRAVERSAL_PATTERNS:
                if re.search(pattern, value_lower, re.IGNORECASE):
                    logger.warning(
                        f"Posible Path Traversal detectado en {field_name}: "
                        f"patrón '{pattern}' desde {request.client.host}"
                    )
                    return False

        return True
