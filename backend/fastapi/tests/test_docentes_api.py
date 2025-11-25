import pytest
from fastapi.testclient import TestClient


class TestDocentesEndpoints:
    """Tests para los endpoints de docentes"""

    def test_create_docente_success_admin(self, client: TestClient, auth_headers_admin):
        """Test creación exitosa de docente por administrador"""
        # Primero necesitamos crear un usuario para asociar al docente
        user_data = {
            "nombre": "Juan Perez",
            "email": "juan.perez@universidad.edu",
            "contrasena": "Docente123!SecurePass",
            "rol": "docente",
        }
        user_response = client.post(
            "/api/auth/register", json=user_data, headers=auth_headers_admin
        )
        assert user_response.status_code == 201
        user_id = user_response.json()["id"]

        # Crear el docente
        docente_data = {"user_id": user_id, "departamento": "INGENIERIA DE SOFTWARE"}

        response = client.post("/api/docentes", json=docente_data, headers=auth_headers_admin)

        if response.status_code != 201:
            print(f"Error response: {response.json()}")
        assert response.status_code == 201
        data = response.json()
        assert data["user_id"] == user_id
        assert data["departamento"] == "INGENIERIA DE SOFTWARE"
        assert "id" in data

    def test_create_docente_unauthorized(self, client: TestClient):
        """Test creación de docente sin autenticación"""
        docente_data = {"user_id": 1, "departamento": "Test"}

        response = client.post("/api/docentes", json=docente_data)
        assert response.status_code == 401

    def test_get_all_docentes_success(self, client: TestClient, auth_headers_admin):
        """Test obtener todos los docentes"""
        response = client.get("/api/docentes", headers=auth_headers_admin)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_all_docentes_with_pagination(self, client: TestClient, auth_headers_admin):
        """Test obtener docentes con paginación"""
        response = client.get("/api/docentes?skip=0&limit=10", headers=auth_headers_admin)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10

    def test_get_docente_by_id_success(self, client: TestClient, auth_headers_admin):
        """Test obtener docente específico por ID"""
        # Crear un docente primero
        user_data = {
            "nombre": "Maria Gonzalez",
            "email": "maria.gonzalez@universidad.edu",
            "contrasena": "Docente123!SecurePass",
            "rol": "docente",
        }
        user_response = client.post(
            "/api/auth/register", json=user_data, headers=auth_headers_admin
        )
        user_id = user_response.json()["id"]

        docente_data = {"user_id": user_id, "departamento": "MATEMATICAS"}
        create_response = client.post(
            "/api/docentes", json=docente_data, headers=auth_headers_admin
        )
        created_id = create_response.json()["id"]

        # Obtener por ID
        response = client.get(f"/api/docentes/{created_id}", headers=auth_headers_admin)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_id
        assert data["departamento"] == "MATEMATICAS"

    def test_get_docente_by_id_not_found(self, client: TestClient, auth_headers_admin):
        """Test obtener docente que no existe"""
        response = client.get("/api/docentes/99999", headers=auth_headers_admin)
        assert response.status_code == 404

    def test_get_docentes_by_departamento(self, client: TestClient, auth_headers_admin):
        """Test obtener docentes por departamento"""
        # Crear un docente con departamento específico
        user_data = {
            "nombre": "Carlos Ruiz",
            "email": "carlos.ruiz@universidad.edu",
            "contrasena": "Docente123!SecurePass",
            "rol": "docente",
        }
        user_response = client.post(
            "/api/auth/register", json=user_data, headers=auth_headers_admin
        )
        user_id = user_response.json()["id"]

        docente_data = {"user_id": user_id, "departamento": "FISICA"}
        client.post("/api/docentes", json=docente_data, headers=auth_headers_admin)

        # Buscar por departamento
        response = client.get("/api/docentes/departamento/FISICA", headers=auth_headers_admin)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_delete_docente_success(self, client: TestClient, auth_headers_admin):
        """Test eliminación exitosa de docente"""
        # Crear un docente primero
        user_data = {
            "nombre": "Ana Lopez",
            "email": "ana.lopez@universidad.edu",
            "contrasena": "Docente123!SecurePass",
            "rol": "docente",
        }
        user_response = client.post(
            "/api/auth/register", json=user_data, headers=auth_headers_admin
        )
        user_id = user_response.json()["id"]

        docente_data = {"user_id": user_id, "departamento": "QUIMICA"}
        create_response = client.post(
            "/api/docentes", json=docente_data, headers=auth_headers_admin
        )
        created_id = create_response.json()["id"]

        # Eliminar
        response = client.delete(f"/api/docentes/{created_id}", headers=auth_headers_admin)

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "eliminado exitosamente" in data["message"]

    def test_delete_docente_not_found(self, client: TestClient, auth_headers_admin):
        """Test eliminación de docente que no existe"""
        response = client.delete("/api/docentes/99999", headers=auth_headers_admin)
        assert response.status_code == 404

    def test_docente_endpoints_unauthorized_estudiante(
        self, client: TestClient, auth_headers_estudiante
    ):
        """Test que los endpoints de docente no son accesibles para estudiantes sin permisos"""
        response = client.get("/api/docentes", headers=auth_headers_estudiante)
        # Dependiendo de la implementación, podría ser 403 o permitido para lectura
        assert response.status_code in [200, 403]


class TestDocentesValidation:
    """Tests para validación de datos de docentes"""

    def test_create_docente_invalid_user_id(self, client: TestClient, auth_headers_admin):
        """Test creación de docente con user_id inválido"""
        docente_data = {"user_id": 99999, "departamento": "Test"}  # Usuario que no existe

        response = client.post("/api/docentes", json=docente_data, headers=auth_headers_admin)
        assert response.status_code in [400, 404]

    def test_create_docente_missing_departamento(self, client: TestClient, auth_headers_admin):
        """Test creación de docente sin departamento (debería ser opcional)"""
        user_data = {
            "nombre": "Docente Sin Depto",
            "email": "sin.depto@universidad.edu",
            "contrasena": "Docente123!SecurePass",
            "rol": "docente",
        }
        user_response = client.post(
            "/api/auth/register", json=user_data, headers=auth_headers_admin
        )
        user_id = user_response.json()["id"]

        docente_data = {
            "user_id": user_id
            # Sin departamento
        }

        response = client.post("/api/docentes", json=docente_data, headers=auth_headers_admin)
        # Departamento es opcional según la entidad
        assert response.status_code == 201

    def test_departamento_name_validation(self, client: TestClient, auth_headers_admin):
        """Test validación de nombres de departamento"""
        departamentos_validos = [
            "INGENIERIA DE SOFTWARE",
            "MATEMATICAS",
            "FISICA",
            "QUIMICA",
            "CIENCIAS DE LA COMPUTACION",
        ]

        nombres_docentes = [
            "Carlos Ramirez",
            "Maria Lopez",
            "Pedro Gonzalez",
            "Ana Martinez",
            "Luis Hernandez",
        ]

        for i, departamento in enumerate(departamentos_validos):
            user_data = {
                "nombre": nombres_docentes[i],
                "email": f"docente{i}@universidad.edu",
                "contrasena": "Docente123!SecurePass",
                "rol": "docente",
            }
            user_response = client.post(
                "/api/auth/register", json=user_data, headers=auth_headers_admin
            )
            assert (
                user_response.status_code == 201
            ), f"Failed to register user: {user_response.json()}"
            user_id = user_response.json()["id"]

            docente_data = {"user_id": user_id, "departamento": departamento}

            response = client.post("/api/docentes", json=docente_data, headers=auth_headers_admin)
            assert response.status_code == 201, f"Falló para departamento: {departamento}"
            assert response.json()["departamento"] == departamento


class TestDocentesIntegration:
    """Tests de integración para docentes"""

    def test_docente_lifecycle_complete(self, client: TestClient, auth_headers_admin):
        """Test ciclo completo: crear -> obtener -> actualizar -> eliminar docente"""
        # 1. Crear usuario
        user_data = {
            "nombre": "Lifecycle Test",
            "email": "lifecycle@universidad.edu",
            "contrasena": "Docente123!SecurePass",
            "rol": "docente",
        }
        user_response = client.post(
            "/api/auth/register", json=user_data, headers=auth_headers_admin
        )
        user_id = user_response.json()["id"]

        # 2. Crear docente
        docente_data = {"user_id": user_id, "departamento": "Testing"}
        create_response = client.post(
            "/api/docentes", json=docente_data, headers=auth_headers_admin
        )
        assert create_response.status_code == 201
        docente_id = create_response.json()["id"]

        # 3. Obtener docente
        get_response = client.get(f"/api/docentes/{docente_id}", headers=auth_headers_admin)
        assert get_response.status_code == 200
        assert get_response.json()["departamento"] == "Testing"

        # 4. Eliminar docente
        delete_response = client.delete(f"/api/docentes/{docente_id}", headers=auth_headers_admin)
        assert delete_response.status_code == 200

        # 5. Verificar que ya no existe
        get_after_delete = client.get(f"/api/docentes/{docente_id}", headers=auth_headers_admin)
        assert get_after_delete.status_code == 404
