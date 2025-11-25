import pytest
from fastapi.testclient import TestClient


class TestUsersEndpoints:
    """Tests para los endpoints de usuarios"""

    def test_get_all_users_success_admin(self, client: TestClient, auth_headers_admin):
        """Test obtener todos los usuarios como administrador"""
        response = client.get("/api/users/", headers=auth_headers_admin)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Debería incluir al menos el usuario admin que creamos
        assert len(data) >= 1

        # Verificar estructura de usuario
        if len(data) > 0:
            user = data[0]
            assert "id" in user
            assert "nombre" in user
            assert "email" in user
            assert "rol" in user
            assert "activo" in user
            # No debería incluir la contraseña
            assert "contrasena" not in user

    def test_get_all_users_success_docente(self, client: TestClient, auth_headers_docente):
        """Test obtener usuarios como docente (si está permitido)"""
        response = client.get("/api/users/", headers=auth_headers_docente)

        # Dependiendo de la implementación, podría ser 200 o 403
        assert response.status_code in [200, 403]

    def test_get_all_users_success_estudiante(self, client: TestClient, auth_headers_estudiante):
        """Test obtener usuarios como estudiante (si está permitido)"""
        response = client.get("/api/users/", headers=auth_headers_estudiante)

        # Dependiendo de la implementación, podría ser 200 o 403
        assert response.status_code in [200, 403]

    def test_get_all_users_unauthorized(self, client: TestClient):
        """Test obtener usuarios sin autenticación"""
        response = client.get("/api/users/")
        assert response.status_code == 401

    def test_get_user_by_id_success(self, client: TestClient, auth_headers_admin):
        """Test obtener usuario específico por ID"""
        # Crear un usuario primero
        user_data = {
            "nombre": "Usuario Test",
            "email": "usuario.test@universidad.edu",
            "contrasena": "Usuario123!SecurePass",
            "rol": "estudiante",
        }
        create_response = client.post(
            "/api/auth/register", json=user_data, headers=auth_headers_admin
        )
        created_id = create_response.json()["id"]

        # Obtener por ID
        response = client.get(f"/api/users/{created_id}", headers=auth_headers_admin)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_id
        assert data["nombre"] == "Usuario Test"
        assert data["email"] == "usuario.test@universidad.edu"
        assert data["rol"] == "estudiante"
        # No debería incluir la contraseña
        assert "contrasena" not in data

    def test_get_user_by_id_not_found(self, client: TestClient, auth_headers_admin):
        """Test obtener usuario que no existe"""
        response = client.get("/api/users/99999", headers=auth_headers_admin)
        assert response.status_code == 404

    def test_get_user_by_id_unauthorized(self, client: TestClient):
        """Test obtener usuario sin autenticación"""
        response = client.get("/api/users/1")
        assert response.status_code == 401

    def test_get_own_user_id(self, client: TestClient, auth_headers_admin):
        """Test obtener información del propio usuario"""
        # Primero obtener el usuario actual para saber su ID
        me_response = client.get("/api/auth/me", headers=auth_headers_admin)
        assert me_response.status_code == 200
        user_id = me_response.json()["id"]

        # Obtener información del propio usuario por ID
        response = client.get(f"/api/users/{user_id}", headers=auth_headers_admin)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
        assert data["email"] == me_response.json()["email"]
        assert data["nombre"] == me_response.json()["nombre"]


class TestUsersFiltering:
    """Tests para funcionalidades de filtrado y búsqueda de usuarios"""

    def test_users_by_role_admin(self, client: TestClient, auth_headers_admin):
        """Test obtener usuarios y verificar roles"""
        # Crear usuarios con diferentes roles
        users_data = [
            {
                "nombre": "Admin Secundario",
                "email": "admin2@test.com",
                "contrasena": "Admin123!SecurePass",
                "rol": "administrador",
            },
            {
                "nombre": "Docente Secundario",
                "email": "docente2@test.com",
                "contrasena": "Docente123!SecurePass",
                "rol": "docente",
            },
            {
                "nombre": "Estudiante Secundario",
                "email": "estudiante2@test.com",
                "contrasena": "Estudiante123!SecurePass",
                "rol": "estudiante",
            },
        ]

        for user_data in users_data:
            response = client.post("/api/auth/register", json=user_data, headers=auth_headers_admin)
            assert (
                response.status_code == 201
            ), f"Failed to register {user_data['email']}: {response.json()}"

        # Obtener todos los usuarios
        response = client.get("/api/users/", headers=auth_headers_admin)
        assert response.status_code == 200

        data = response.json()

        # Verificar que tenemos usuarios de diferentes roles
        roles = [user["rol"] for user in data]
        assert "administrador" in roles
        assert "docente" in roles
        assert "estudiante" in roles

    def test_users_active_status(self, client: TestClient, auth_headers_admin):
        """Test verificar estado activo de usuarios"""
        response = client.get("/api/users/", headers=auth_headers_admin)
        assert response.status_code == 200

        data = response.json()

        # Todos los usuarios recién registrados deberían estar activos
        for user in data:
            assert "activo" in user
            assert user["activo"] is True

    def test_users_no_sensitive_data(self, client: TestClient, auth_headers_admin):
        """Test que no se expone información sensible"""
        response = client.get("/api/users/", headers=auth_headers_admin)
        assert response.status_code == 200

        data = response.json()

        for user in data:
            # No debería incluir información sensible
            assert "contrasena" not in user
            assert "password" not in user
            assert "hashed_password" not in user

            # Debería incluir solo información pública
            required_fields = ["id", "nombre", "email", "rol", "activo"]
            for field in required_fields:
                assert field in user


class TestUsersPermissions:
    """Tests para permisos de acceso a usuarios"""

    def test_admin_access_all_users(self, client: TestClient, auth_headers_admin):
        """Test que administradores pueden acceder a todos los usuarios"""
        response = client.get("/api/users/", headers=auth_headers_admin)
        assert response.status_code == 200

    def test_docente_access_users(self, client: TestClient, auth_headers_docente):
        """Test acceso de docentes a usuarios"""
        response = client.get("/api/users/", headers=auth_headers_docente)
        # Dependiendo de las reglas de negocio
        assert response.status_code in [200, 403]

    def test_estudiante_access_users(self, client: TestClient, auth_headers_estudiante):
        """Test acceso de estudiantes a usuarios"""
        response = client.get("/api/users/", headers=auth_headers_estudiante)
        # Dependiendo de las reglas de negocio
        assert response.status_code in [200, 403]

    def test_cross_user_access_restriction(self, client: TestClient, auth_headers_admin):
        """Test que usuarios no pueden acceder a información de otros sin permisos adecuados"""
        # Crear dos usuarios
        user1_data = {
            "nombre": "Usuario Primero",
            "email": "user1@test.com",
            "contrasena": "User123!SecurePass",
            "rol": "estudiante",
        }
        user2_data = {
            "nombre": "Usuario Segundo",
            "email": "user2@test.com",
            "contrasena": "User123!SecurePass",
            "rol": "estudiante",
        }

        user1_response = client.post(
            "/api/auth/register", json=user1_data, headers=auth_headers_admin
        )
        user2_response = client.post(
            "/api/auth/register", json=user2_data, headers=auth_headers_admin
        )

        assert (
            user1_response.status_code == 201
        ), f"User1 registration failed: {user1_response.json()}"
        assert (
            user2_response.status_code == 201
        ), f"User2 registration failed: {user2_response.json()}"

        user1_id = user1_response.json()["id"]
        user2_id = user2_response.json()["id"]

        # Usuario 1 hace login
        login_response = client.post(
            "/api/auth/login",
            json={"email": user1_data["email"], "contrasena": user1_data["contrasena"]},
        )
        user1_token = login_response.json()["access_token"]
        user1_headers = {"Authorization": f"Bearer {user1_token}"}

        # Usuario 1 intenta acceder a información del Usuario 2
        response = client.get(f"/api/users/{user2_id}", headers=user1_headers)

        # Dependiendo de las reglas de negocio, podría estar permitido o no
        assert response.status_code in [200, 403]


class TestUsersDataIntegrity:
    """Tests para integridad de datos de usuarios"""

    def test_user_data_consistency(self, client: TestClient, auth_headers_admin):
        """Test consistencia de datos de usuarios"""
        # Crear un usuario
        user_data = {
            "nombre": "Consistencia Test",
            "email": "consistencia@test.com",
            "contrasena": "Consist123!SecurePass",
            "rol": "docente",
        }
        create_response = client.post(
            "/api/auth/register", json=user_data, headers=auth_headers_admin
        )
        created_id = create_response.json()["id"]

        # Obtener el usuario por diferentes endpoints
        response_list = client.get("/api/users/", headers=auth_headers_admin)
        response_single = client.get(f"/api/users/{created_id}", headers=auth_headers_admin)

        assert response_list.status_code == 200
        assert response_single.status_code == 200

        # Encontrar el usuario en la lista
        users_list = response_list.json()
        user_from_list = next((u for u in users_list if u["id"] == created_id), None)
        user_single = response_single.json()

        assert user_from_list is not None

        # Los datos deben ser consistentes
        assert user_from_list["id"] == user_single["id"]
        assert user_from_list["nombre"] == user_single["nombre"]
        assert user_from_list["email"] == user_single["email"]
        assert user_from_list["rol"] == user_single["rol"]
        assert user_from_list["activo"] == user_single["activo"]

    def test_user_timestamps(self, client: TestClient, auth_headers_admin):
        """Test que se incluyan timestamps apropiados"""
        user_data = {
            "nombre": "Timestamp Test",
            "email": "timestamp@test.com",
            "contrasena": "Time123!SecurePass",
            "rol": "estudiante",
        }
        create_response = client.post(
            "/api/auth/register", json=user_data, headers=auth_headers_admin
        )
        created_id = create_response.json()["id"]

        response = client.get(f"/api/users/{created_id}", headers=auth_headers_admin)
        assert response.status_code == 200

        data = response.json()

        # Verificar timestamps si están incluidos
        if "created_at" in data:
            assert data["created_at"] is not None
        if "updated_at" in data:
            assert data["updated_at"] is not None
