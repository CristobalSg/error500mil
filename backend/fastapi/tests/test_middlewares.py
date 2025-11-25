"""
Tests para los middlewares de seguridad.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from application.middlewares import (
    RateLimitMiddleware,
    SanitizationMiddleware,
    SecurityLoggingMiddleware,
)


# Fixture: App básica con middlewares
@pytest.fixture
def app_with_sanitization():
    app = FastAPI()
    app.add_middleware(
        SanitizationMiddleware, enable_sql_check=True, enable_xss_check=True, enable_path_check=True
    )

    @app.post("/test")
    async def test_endpoint(data: dict):
        return {"message": "success", "data": data}

    @app.get("/test/{item_id}")
    async def test_path_endpoint(item_id: str):
        return {"item_id": item_id}

    return app


@pytest.fixture
def app_with_rate_limit():
    app = FastAPI()
    app.add_middleware(
        RateLimitMiddleware,
        requests_limit=5,  # Límite bajo para testing
        window_seconds=60,
        auth_requests_limit=10,
    )

    @app.get("/test")
    async def test_endpoint():
        return {"message": "success"}

    @app.get("/api/health")
    async def health_endpoint():
        return {"status": "ok"}

    return app


@pytest.fixture
def app_with_logging():
    app = FastAPI()
    app.add_middleware(
        SecurityLoggingMiddleware,
        log_request_body=False,
        log_response_body=False,
        enable_performance_logging=True,
    )

    @app.post("/api/auth/login")
    async def login_endpoint():
        return {"token": "test_token"}

    @app.get("/test")
    async def test_endpoint():
        return {"message": "success"}

    return app


# ============================================================================
# Tests para SanitizationMiddleware
# ============================================================================


class TestSanitizationMiddleware:
    """Tests para el middleware de sanitización."""

    def test_valid_request(self, app_with_sanitization):
        """Request válida debe pasar sin problemas."""
        client = TestClient(app_with_sanitization)
        response = client.post("/test", json={"username": "john_doe", "email": "john@example.com"})
        assert response.status_code == 200
        assert response.json()["message"] == "success"

    def test_sql_injection_in_body(self, app_with_sanitization):
        """Detectar SQL injection en el body."""
        client = TestClient(app_with_sanitization)
        response = client.post("/test", json={"username": "admin'; DROP TABLE users; --"})
        assert response.status_code == 400
        assert "sospechosos" in response.json()["detail"].lower()

    def test_sql_injection_union_select(self, app_with_sanitization):
        """Detectar UNION SELECT."""
        client = TestClient(app_with_sanitization)
        response = client.post("/test", json={"search": "test' UNION SELECT * FROM users --"})
        assert response.status_code == 400

    def test_xss_script_tag(self, app_with_sanitization):
        """Detectar XSS con script tag."""
        client = TestClient(app_with_sanitization)
        response = client.post("/test", json={"name": "<script>alert('XSS')</script>"})
        assert response.status_code == 400

    def test_xss_javascript_protocol(self, app_with_sanitization):
        """Detectar XSS con javascript: protocol."""
        client = TestClient(app_with_sanitization)
        response = client.post("/test", json={"url": "javascript:alert(1)"})
        assert response.status_code == 400

    def test_xss_event_handler(self, app_with_sanitization):
        """Detectar XSS con event handlers."""
        client = TestClient(app_with_sanitization)
        response = client.post("/test", json={"html": "<img src=x onerror=alert(1)>"})
        assert response.status_code == 400

    def test_path_traversal_in_query(self, app_with_sanitization):
        """Detectar path traversal en query params."""
        client = TestClient(app_with_sanitization)
        response = client.post("/test?file=../../etc/passwd", json={"data": "test"})
        assert response.status_code == 400

    def test_path_traversal_encoded(self, app_with_sanitization):
        """Detectar path traversal codificado."""
        client = TestClient(app_with_sanitization)
        response = client.post("/test?path=%2e%2e%2f", json={"data": "test"})
        assert response.status_code == 400

    def test_nested_json_sanitization(self, app_with_sanitization):
        """Sanitizar JSON anidado."""
        client = TestClient(app_with_sanitization)
        response = client.post(
            "/test", json={"user": {"name": "John", "query": "SELECT * FROM users"}}
        )
        assert response.status_code == 400

    def test_array_sanitization(self, app_with_sanitization):
        """Sanitizar arrays."""
        client = TestClient(app_with_sanitization)
        response = client.post(
            "/test", json={"items": ["item1", "<script>alert(1)</script>", "item3"]}
        )
        assert response.status_code == 400

    def test_invalid_content_type(self, app_with_sanitization):
        """Rechazar Content-Type inválido."""
        client = TestClient(app_with_sanitization)
        response = client.post("/test", data="test data", headers={"Content-Type": "text/plain"})
        assert response.status_code == 415

    def test_payload_too_large(self, app_with_sanitization):
        """Rechazar payload muy grande."""
        client = TestClient(app_with_sanitization)
        large_data = {"data": "x" * (6 * 1024 * 1024)}  # 6MB
        response = client.post(
            "/test", json=large_data, headers={"Content-Length": str(6 * 1024 * 1024)}
        )
        assert response.status_code == 413


# ============================================================================
# Tests para RateLimitMiddleware
# ============================================================================


class TestRateLimitMiddleware:
    """Tests para el middleware de rate limiting."""

    def test_within_rate_limit(self, app_with_rate_limit):
        """Requests dentro del límite deben funcionar."""
        client = TestClient(app_with_rate_limit)

        for _ in range(5):
            response = client.get("/test")
            assert response.status_code == 200

    def test_exceed_rate_limit(self, app_with_rate_limit):
        """Exceder el límite debe retornar 429."""
        client = TestClient(app_with_rate_limit)

        # Hacer 5 requests (el límite)
        for _ in range(5):
            response = client.get("/test")
            assert response.status_code == 200

        # La sexta debe fallar
        response = client.get("/test")
        assert response.status_code == 429
        assert "retry_after" in response.json()

    def test_rate_limit_headers(self, app_with_rate_limit):
        """Verificar headers de rate limit."""
        client = TestClient(app_with_rate_limit)

        response = client.get("/test")
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Reset" in response.headers

    def test_excluded_endpoints(self, app_with_rate_limit):
        """Endpoints excluidos no deben tener rate limit."""
        client = TestClient(app_with_rate_limit)

        # Hacer muchas requests al endpoint de health
        for _ in range(20):
            response = client.get("/api/health")
            assert response.status_code == 200

    def test_authenticated_higher_limit(self, app_with_rate_limit):
        """Usuarios autenticados tienen límite mayor."""
        client = TestClient(app_with_rate_limit)

        # Con token (autenticado) - límite es 10
        for _ in range(10):
            response = client.get("/test", headers={"Authorization": "Bearer test_token"})
            assert response.status_code == 200

        # La 11 debe fallar
        response = client.get("/test", headers={"Authorization": "Bearer test_token"})
        assert response.status_code == 429


# ============================================================================
# Tests para SecurityLoggingMiddleware
# ============================================================================


class TestSecurityLoggingMiddleware:
    """Tests para el middleware de logging de seguridad."""

    def test_request_logging(self, app_with_logging, caplog):
        """Verificar que las requests se loggean."""
        client = TestClient(app_with_logging)

        response = client.get("/test")
        assert response.status_code == 200

        # Verificar que se loggeó
        assert "request_received" in caplog.text or "request_completed" in caplog.text

    def test_process_time_header(self, app_with_logging):
        """Verificar header de tiempo de procesamiento."""
        client = TestClient(app_with_logging)

        response = client.get("/test")
        assert "X-Process-Time" in response.headers
        assert float(response.headers["X-Process-Time"]) >= 0

    def test_login_event_logging(self, app_with_logging, caplog):
        """Verificar logging de eventos de login."""
        client = TestClient(app_with_logging)

        response = client.post("/api/auth/login")
        assert response.status_code == 200

        # Debería loggear evento de login
        # (El log específico depende del código de respuesta)

    def test_error_logging(self, app_with_logging, caplog):
        """Verificar logging de errores."""
        app = app_with_logging

        @app.get("/error")
        async def error_endpoint():
            raise ValueError("Test error")

        client = TestClient(app)

        try:
            client.get("/error")
        except:
            pass

        # Debería haber loggeado el error


# ============================================================================
# Tests de Integración
# ============================================================================


class TestMiddlewaresIntegration:
    """Tests de integración con múltiples middlewares."""

    @pytest.fixture
    def app_with_all_middlewares(self):
        app = FastAPI()

        # Agregar todos los middlewares
        app.add_middleware(SecurityLoggingMiddleware)
        app.add_middleware(RateLimitMiddleware, requests_limit=10)
        app.add_middleware(SanitizationMiddleware)

        @app.post("/test")
        async def test_endpoint(data: dict):
            return {"message": "success"}

        return app

    def test_all_middlewares_working(self, app_with_all_middlewares):
        """Todos los middlewares deben funcionar juntos."""
        client = TestClient(app_with_all_middlewares)

        # Request válida
        response = client.post("/test", json={"name": "John"})
        assert response.status_code == 200
        assert "X-Process-Time" in response.headers
        assert "X-RateLimit-Limit" in response.headers

    def test_sanitization_blocks_before_rate_limit(self, app_with_all_middlewares):
        """Sanitización debe bloquear antes que rate limit."""
        client = TestClient(app_with_all_middlewares)

        # Request maliciosa
        response = client.post("/test", json={"query": "SELECT * FROM users"})
        assert response.status_code == 400

        # No debería contar para rate limit
        for _ in range(10):
            response = client.post("/test", json={"name": "John"})
            assert response.status_code == 200
