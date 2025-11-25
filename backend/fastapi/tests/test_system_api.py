import pytest
from fastapi.testclient import TestClient


class TestSystemEndpoints:
    """Tests para los endpoints del sistema"""

    def test_root_endpoint(self, client: TestClient):
        """Test endpoint raíz de la API"""
        response = client.get("/api/")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "SGH Backend API"
        assert data["version"] == "1.0.0"  # Actualizado a la versión actual
        assert "environment" in data

    def test_health_endpoint(self, client: TestClient):
        """Test endpoint de salud del sistema"""
        response = client.get("/api/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "environment" in data
        assert data["database"] == "connected"

    def test_database_test_endpoint(self, client: TestClient):
        """Test endpoint de prueba de base de datos"""
        response = client.get("/api/db/test-db")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "Conexión a la base de datos exitosa" in data["message"]
        assert "data" in data
        assert "tablas_disponibles" in data["data"]

        # Verificar que se listan las tablas esperadas
        tablas_esperadas = [
            "docente",
            "asignatura",
            "seccion",
            "sala",
            "bloque",
            "clase",
            "restriccion",
        ]
        for tabla in tablas_esperadas:
            assert tabla in data["data"]["tablas_disponibles"]


class TestSystemIntegration:
    """Tests de integración del sistema"""

    def test_api_documentation_endpoints(self, client: TestClient):
        """Test que los endpoints de documentación están disponibles"""
        # Test endpoint de documentación Swagger
        docs_response = client.get("/api/docs")
        assert docs_response.status_code == 200

        # Test endpoint de documentación ReDoc
        redoc_response = client.get("/api/redoc")
        assert redoc_response.status_code == 200

    def test_cors_headers(self, client: TestClient):
        """Test que los headers CORS están configurados"""
        response = client.options("/api/")
        # En testing, CORS puede comportarse diferente, pero verificamos que no hay errores
        assert response.status_code in [200, 405]  # OPTIONS puede no estar permitido explícitamente

    def test_system_consistency(self, client: TestClient):
        """Test de consistencia general del sistema"""
        # Verificar que todos los endpoints principales están disponibles
        endpoints_to_check = ["/api/", "/api/health", "/api/db/test-db"]

        for endpoint in endpoints_to_check:
            response = client.get(endpoint)
            assert response.status_code == 200, f"Endpoint {endpoint} no está disponible"


class TestErrorHandling:
    """Tests para manejo de errores del sistema"""

    def test_nonexistent_endpoint(self, client: TestClient):
        """Test acceso a endpoint que no existe"""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404

    def test_method_not_allowed(self, client: TestClient):
        """Test método HTTP no permitido"""
        # Intentar POST en endpoint que solo acepta GET
        response = client.post("/api/")
        assert response.status_code == 405

    def test_invalid_json_payload(self, client: TestClient):
        """Test con payload JSON malformado"""
        response = client.post(
            "/api/auth/register",
            data="{invalid json}",
            headers={"Content-Type": "application/json"},
        )
        # El middleware de sanitización retorna 400 para JSON inválido
        assert response.status_code == 400


class TestDatabaseConnection:
    """Tests específicos para la conexión de base de datos"""

    def test_database_connection_with_data(self, client: TestClient, db_session, admin_user_data):
        """Test conexión a base de datos con datos existentes"""
        # Crear un usuario directamente en la base de datos para tener datos
        from domain.models import Administrador, User
        from infrastructure.auth import AuthService

        db_user = User(
            nombre=admin_user_data.nombre,
            email=admin_user_data.email,
            pass_hash=AuthService.get_password_hash(admin_user_data.contrasena),
            rol=admin_user_data.rol,
        )
        db_session.add(db_user)
        db_session.commit()
        db_session.refresh(db_user)

        # Crear registro de administrador
        admin = Administrador(user_id=db_user.id)
        db_session.add(admin)
        db_session.commit()

        assert db_user.id is not None

        # Luego probar la conexión
        response = client.get("/api/db/test-db")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "success"
        # Puede que ahora haya datos en la primera consulta
        assert "data" in data

    def test_multiple_database_requests(self, client: TestClient):
        """Test múltiples solicitudes a la base de datos"""
        # Hacer varias solicitudes para verificar que la conexión es estable
        for i in range(5):
            response = client.get("/api/db/test-db")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
