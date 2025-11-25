import pytest
from fastapi.testclient import TestClient


class TestAuthEndpoints:
    """Tests para los endpoints de autenticación"""

    def test_register_admin_success(self, client: TestClient, admin_user_data, auth_headers_admin):
        """Test registro exitoso de administrador"""
        # Usar un email diferente al del admin que ya existe
        new_admin_data = admin_user_data.model_copy(update={"email": "newadmin@test.com"})
        response = client.post(
            "/api/auth/register", json=new_admin_data.model_dump(), headers=auth_headers_admin
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == new_admin_data.email
        assert data["nombre"] == new_admin_data.nombre
        assert data["rol"] == "administrador"
        assert data["activo"] is True
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
        # La contraseña no debe estar en la respuesta
        assert "contrasena" not in data

    def test_register_docente_success(
        self, client: TestClient, docente_user_data, auth_headers_admin
    ):
        """Test registro exitoso de docente"""
        response = client.post(
            "/api/auth/register", json=docente_user_data.model_dump(), headers=auth_headers_admin
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == docente_user_data.email
        assert data["nombre"] == docente_user_data.nombre
        assert data["rol"] == "docente"
        assert data["activo"] is True

    def test_register_estudiante_success(
        self, client: TestClient, estudiante_user_data, auth_headers_admin
    ):
        """Test registro exitoso de estudiante"""
        response = client.post(
            "/api/auth/register",
            json=estudiante_user_data.model_dump(),
            headers=auth_headers_admin,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == estudiante_user_data.email
        assert data["nombre"] == estudiante_user_data.nombre
        assert data["rol"] == "estudiante"
        assert data["activo"] is True

    def test_register_duplicate_email(
        self, client: TestClient, admin_user_data, auth_headers_admin
    ):
        """Test registro con email duplicado"""
        # Registrar primera vez
        client.post(
            "/api/auth/register", json=admin_user_data.model_dump(), headers=auth_headers_admin
        )

        # Intentar registrar con el mismo email
        response = client.post(
            "/api/auth/register", json=admin_user_data.model_dump(), headers=auth_headers_admin
        )

        assert response.status_code == 400
        assert "email ya está registrado" in response.json()["detail"]

    def test_register_invalid_email(self, client: TestClient, auth_headers_admin):
        """Test registro con email inválido"""
        invalid_data = {
            "nombre": "Test User",
            "email": "invalid-email",
            "contrasena": "Password123!",
            "rol": "estudiante",
        }

        response = client.post("/api/auth/register", json=invalid_data, headers=auth_headers_admin)
        assert response.status_code == 422

    def test_register_weak_password(self, client: TestClient, auth_headers_admin):
        """Test registro con contraseña débil"""
        weak_password_data = {
            "nombre": "Test User",
            "email": "test@example.com",
            "contrasena": "weak",
            "rol": "estudiante",
        }

        response = client.post(
            "/api/auth/register", json=weak_password_data, headers=auth_headers_admin
        )
        assert response.status_code == 422

    def test_register_invalid_role(self, client: TestClient, auth_headers_admin):
        """Test registro con rol inválido"""
        invalid_role_data = {
            "nombre": "Test User",
            "email": "test@example.com",
            "contrasena": "Password123!",
            "rol": "invalid_role",
        }

        response = client.post(
            "/api/auth/register", json=invalid_role_data, headers=auth_headers_admin
        )
        assert response.status_code == 422

    def test_login_success(self, client: TestClient, auth_headers_admin):
        """Test login exitoso"""
        # Crear usuario de prueba para login
        user_data = {
            "nombre": "Login Test User",
            "email": "login.test@test.com",
            "contrasena": "LoginTest123!Secure",
            "rol": "docente",
        }
        client.post("/api/auth/register", json=user_data, headers=auth_headers_admin)

        # Hacer login
        login_data = {"email": user_data["email"], "contrasena": user_data["contrasena"]}
        response = client.post("/api/auth/login", json=login_data)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert data["expires_in"] > 0

    def test_login_json_success(self, client: TestClient, auth_headers_admin):
        """Test login con endpoint JSON exitoso"""
        # Crear usuario de prueba para login
        user_data = {
            "nombre": "Login JSON Test",
            "email": "login.json@test.com",
            "contrasena": "LoginJson123!Secure",
            "rol": "estudiante",
        }
        client.post("/api/auth/register", json=user_data, headers=auth_headers_admin)

        # Hacer login con endpoint JSON
        login_data = {"email": user_data["email"], "contrasena": user_data["contrasena"]}
        response = client.post("/api/auth/login-json", json=login_data)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data

    def test_login_wrong_password(self, client: TestClient, auth_headers_admin):
        """Test login con contraseña incorrecta"""
        # Crear usuario de prueba
        user_data = {
            "nombre": "Wrong Password Test",
            "email": "wrong.password@test.com",
            "contrasena": "CorrectPass123!",
            "rol": "estudiante",
        }
        client.post("/api/auth/register", json=user_data, headers=auth_headers_admin)

        # Intentar login con contraseña incorrecta
        login_data = {"email": user_data["email"], "contrasena": "wrong_password"}
        response = client.post("/api/auth/login", json=login_data)

        assert response.status_code == 401
        assert "Email o contraseña incorrectos" in response.json()["detail"]

    def test_login_nonexistent_user(self, client: TestClient):
        """Test login con usuario que no existe"""
        login_data = {"email": "nonexistent@test.com", "contrasena": "Password123!"}
        response = client.post("/api/auth/login", json=login_data)

        assert response.status_code == 401
        assert "Email o contraseña incorrectos" in response.json()["detail"]

    def test_get_current_user_success(
        self, client: TestClient, auth_headers_admin, admin_user_data
    ):
        """Test obtener información del usuario actual"""
        response = client.get("/api/auth/me", headers=auth_headers_admin)

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == admin_user_data.email
        assert data["nombre"] == admin_user_data.nombre
        assert data["rol"] == "administrador"
        assert "id" in data

    def test_get_current_user_without_token(self, client: TestClient):
        """Test obtener usuario actual sin token"""
        response = client.get("/api/auth/me")

        assert response.status_code == 401
        assert "Token de autorización requerido" in response.json()["detail"]

    def test_get_current_user_invalid_token(self, client: TestClient):
        """Test obtener usuario actual con token inválido"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/auth/me", headers=headers)

        assert response.status_code == 401

    def test_get_current_user_detailed_success(self, client: TestClient, auth_headers_admin):
        """Test obtener información detallada del usuario actual"""
        response = client.get("/api/auth/me/detailed", headers=auth_headers_admin)

        assert response.status_code == 200
        # Este endpoint puede retornar información adicional específica del rol

    def test_refresh_token_success(self, client: TestClient, auth_headers_admin):
        """Test refresh token exitoso"""
        # Crear usuario y hacer login
        user_data = {
            "nombre": "Refresh Token Test",
            "email": "refresh.token@test.com",
            "contrasena": "RefreshToken123!",
            "rol": "docente",
        }
        client.post("/api/auth/register", json=user_data, headers=auth_headers_admin)

        login_response = client.post(
            "/api/auth/login",
            json={"email": user_data["email"], "contrasena": user_data["contrasena"]},
        )

        refresh_token = login_response.json()["refresh_token"]

        # Usar refresh token
        refresh_data = {"refresh_token": refresh_token}
        response = client.post("/api/auth/refresh", json=refresh_data)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_refresh_token_invalid(self, client: TestClient):
        """Test refresh token con token inválido"""
        refresh_data = {"refresh_token": "invalid_refresh_token"}
        response = client.post("/api/auth/refresh", json=refresh_data)

        assert response.status_code == 401

    # TODO: Implementar endpoint validate-role
    # def test_validate_role_admin_success(self, client: TestClient, auth_headers_admin):
    #     """Test validación de rol administrador"""
    #     response = client.get("/api/auth/validate-role/administrador", headers=auth_headers_admin)
    #
    #     assert response.status_code == 200
    #     data = response.json()
    #     assert data["valid"] is True
    #     assert data["user_rol"] == "administrador"
    #     assert data["required_role"] == "administrador"
    #
    # def test_validate_role_insufficient_permissions(
    #     self, client: TestClient, auth_headers_estudiante
    # ):
    #     """Test validación de rol con permisos insuficientes"""
    #     response = client.get(
    #         "/api/auth/validate-role/administrador", headers=auth_headers_estudiante
    #     )
    #
    #     assert response.status_code == 200
    #     data = response.json()
    #     assert data["valid"] is False
    #     assert data["user_rol"] == "estudiante"
    #     assert data["required_role"] == "administrador"
    #
    # def test_validate_role_without_token(self, client: TestClient):
    #     """Test validación de rol sin token"""
    #     response = client.get("/api/auth/validate-role/administrador")
    #
    #     assert response.status_code == 401


class TestAuthenticationFlow:
    """Tests para flujos completos de autenticación"""

    def test_complete_auth_flow(self, client: TestClient, auth_headers_admin):
        """Test de flujo completo: registro -> login -> acceso a endpoint protegido"""
        # 1. Registro
        user_data = {
            "nombre": "Flujo Test",
            "email": "flujo@test.com",
            "contrasena": "Flujo123!SecurePass",
            "rol": "administrador",
        }
        register_response = client.post(
            "/api/auth/register", json=user_data, headers=auth_headers_admin
        )
        if register_response.status_code != 201:
            print(f"Error en registro: {register_response.json()}")
        assert register_response.status_code == 201

        # 2. Login
        login_response = client.post(
            "/api/auth/login",
            json={"email": user_data["email"], "contrasena": user_data["contrasena"]},
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # 3. Acceso a endpoint protegido
        headers = {"Authorization": f"Bearer {token}"}
        me_response = client.get("/api/auth/me", headers=headers)
        assert me_response.status_code == 200
        assert me_response.json()["email"] == user_data["email"]

    def test_token_expiration_handling(self, client: TestClient, auth_headers_admin):
        """Test para manejo de tokens (este test es básico, en producción necesitaría más lógica)"""
        # Crear usuario y hacer login
        user_data = {
            "nombre": "Token Expiration Test",
            "email": "token.expiration@test.com",
            "contrasena": "TokenExp123!Secure",
            "rol": "docente",
        }
        client.post("/api/auth/register", json=user_data, headers=auth_headers_admin)

        login_response = client.post(
            "/api/auth/login",
            json={"email": user_data["email"], "contrasena": user_data["contrasena"]},
        )

        token_data = login_response.json()
        assert "expires_in" in token_data
        assert token_data["expires_in"] > 0

        # Verificar que el token funciona inmediatamente
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        response = client.get("/api/auth/me", headers=headers)
        assert response.status_code == 200
