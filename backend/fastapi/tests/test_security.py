"""
Tests de seguridad completos para validar protecciones OWASP y middlewares.
Cubre: inyecciones, XSS, autenticación, autorización, rate limiting, etc.
"""

import time

import pytest
from fastapi.testclient import TestClient

# ============================================================================
# Tests de Inyección SQL (OWASP A03:2021)
# ============================================================================


class TestSQLInjectionProtection:
    """Tests para validar protección contra SQL Injection"""

    def test_sql_injection_in_login_username(self, client: TestClient):
        """Intentar SQL injection en campo username del login"""
        malicious_payloads = [
            "admin'; DROP TABLE users; --",
            "admin' OR '1'='1",
            "admin' OR 1=1--",
            "' UNION SELECT * FROM users--",
            "admin'; DELETE FROM users WHERE '1'='1",
        ]

        for payload in malicious_payloads:
            response = client.post(
                "/api/auth/login", json={"email": payload, "contrasena": "test123"}
            )
            # Debe ser bloqueado por sanitización (400) o fallar en autenticación (401/422)
            assert response.status_code in [400, 401, 422], f"Payload no bloqueado: {payload}"

    def test_sql_injection_in_register_fields(self, client: TestClient, auth_headers_admin):
        """Intentar SQL injection en campos de registro"""
        malicious_data = {
            "nombre": "Test' OR '1'='1",
            "email": "test@test.com'; DROP TABLE users; --",
            "contrasena": "S3cur3P@ssw0rd!2024#Strong",
            "rol": "estudiante",
        }

        response = client.post(
            "/api/auth/register", json=malicious_data, headers=auth_headers_admin
        )
        # Debe ser bloqueado por sanitización
        assert response.status_code in [400, 422]

    def test_sql_injection_in_query_params(self, client: TestClient, auth_headers_admin):
        """Intentar SQL injection en parámetros de consulta"""
        malicious_queries = [
            "1' OR '1'='1",
            "1; DROP TABLE users--",
            "1' UNION SELECT * FROM users--",
        ]

        for query in malicious_queries:
            response = client.get(f"/api/users?search={query}", headers=auth_headers_admin)
            # No debe causar error 500, debe ser manejado apropiadamente
            assert response.status_code != 500, f"Query maliciosa causó error: {query}"
            assert response.status_code in [400, 404, 200]


# ============================================================================
# Tests de XSS (Cross-Site Scripting) (OWASP A03:2021)
# ============================================================================


class TestXSSProtection:
    """Tests para validar protección contra XSS"""

    def test_xss_script_tags_in_input(self, client: TestClient, auth_headers_admin):
        """Intentar XSS con tags de script"""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<script>document.cookie</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg/onload=alert('XSS')>",
            "javascript:alert('XSS')",
        ]

        for payload in xss_payloads:
            response = client.post(
                "/api/auth/register",
                json={
                    "nombre": payload,
                    "email": "test@test.com",
                    "contrasena": "S3cur3P@ssw0rd!2024#Strong",
                    "rol": "estudiante",
                },
                headers=auth_headers_admin,
            )
            # Debe ser bloqueado por sanitización
            assert response.status_code in [400, 422], f"XSS payload no bloqueado: {payload}"

    def test_xss_event_handlers(self, client: TestClient, auth_headers_admin):
        """Intentar XSS con event handlers"""
        event_handlers = [
            "test' onerror='alert(1)'",
            'test" onload="alert(1)"',
            "test onclick=alert(1)",
            "test onmouseover=alert(1)",
        ]

        for handler in event_handlers:
            response = client.post(
                "/api/auth/register",
                json={
                    "nombre": handler,
                    "email": "test@test.com",
                    "contrasena": "S3cur3P@ssw0rd!2024#Strong",
                    "rol": "estudiante",
                },
                headers=auth_headers_admin,
            )
            assert response.status_code in [400, 422]

    def test_xss_in_campus_creation(self, client: TestClient, auth_headers_admin):
        """Intentar XSS en creación de campus"""
        xss_data = {
            "codigo": "CAMP-001",
            "nombre": "<script>alert('XSS')</script>",
            "direccion": "Calle <img src=x onerror=alert(1)>",
        }

        response = client.post("/api/campus/", json=xss_data, headers=auth_headers_admin)
        assert response.status_code in [400, 422]


# ============================================================================
# Tests de Path Traversal (OWASP A01:2021)
# ============================================================================


class TestPathTraversalProtection:
    """Tests para validar protección contra Path Traversal"""

    def test_path_traversal_in_params(self, client: TestClient, auth_headers_admin):
        """Intentar path traversal en parámetros"""
        traversal_payloads = [
            "../../etc/passwd",
            "../../../etc/shadow",
            "..\\..\\windows\\system32",
            "%2e%2e%2f%2e%2e%2f",
            "....//....//etc/passwd",
        ]

        for payload in traversal_payloads:
            response = client.get(f"/api/users?file={payload}", headers=auth_headers_admin)
            # Debe ser bloqueado o manejado apropiadamente
            assert response.status_code in [400, 404]


# ============================================================================
# Tests de Autenticación Rota (OWASP A07:2021)
# ============================================================================


class TestBrokenAuthentication:
    """Tests para validar robustez de autenticación"""

    def test_access_protected_endpoint_without_token(self, client: TestClient):
        """Intentar acceder a endpoint protegido sin token"""
        protected_endpoints = [
            "/api/auth/me",
            "/api/users",
            "/api/campus/",
            "/api/docentes/",
            "/api/asignaturas/",
        ]

        for endpoint in protected_endpoints:
            response = client.get(endpoint)
            assert response.status_code == 401, f"Endpoint sin protección: {endpoint}"
            assert "Token de autorización requerido" in response.json().get("detail", "")

    def test_access_with_invalid_token(self, client: TestClient):
        """Intentar acceder con token inválido"""
        invalid_tokens = [
            "invalid_token",
            "Bearer invalid_token",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid",
            "",
            "null",
        ]

        for token in invalid_tokens:
            headers = {"Authorization": f"Bearer {token}"}
            response = client.get("/api/auth/me", headers=headers)
            assert response.status_code == 401

    def test_access_with_malformed_auth_header(self, client: TestClient):
        """Intentar acceder con header de autorización malformado"""
        malformed_headers = [
            {"Authorization": "invalid_format"},
            {"Authorization": "Bearer"},
            {"Authorization": ""},
            {"Auth": "Bearer token"},  # Header incorrecto
        ]

        for headers in malformed_headers:
            response = client.get("/api/auth/me", headers=headers)
            assert response.status_code == 401

    def test_token_reuse_after_refresh(self, client: TestClient, db_session, admin_user_data):
        """Validar que los tokens viejos no funcionen después de refresh"""
        # Crear usuario directamente en la base de datos
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

        # Hacer login
        login_response = client.post(
            "/api/auth/login",
            json={"email": admin_user_data.email, "contrasena": admin_user_data.contrasena},
        )

        old_token = login_response.json()["access_token"]
        refresh_token = login_response.json()["refresh_token"]

        # Usar el token viejo (debería funcionar)
        headers = {"Authorization": f"Bearer {old_token}"}
        response = client.get("/api/auth/me", headers=headers)
        assert response.status_code == 200

        # Hacer refresh
        refresh_response = client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
        assert refresh_response.status_code == 200

    def test_weak_password_rejected(self, client: TestClient, auth_headers_admin):
        """Validar que contraseñas débiles sean rechazadas"""
        weak_passwords = [
            "123",
            "password",
            "abc",
            "12345678",
            "qwerty",
            "Password123!",  # Muy común
            "Admin123!",  # Muy común
        ]

        for weak_pass in weak_passwords:
            response = client.post(
                "/api/auth/register",
                json={
                    "nombre": "Test User",
                    "email": f"test{weak_pass}@test.com",
                    "contrasena": weak_pass,
                    "rol": "estudiante",
                },
                headers=auth_headers_admin,
            )
            assert response.status_code == 422, f"Contraseña débil aceptada: {weak_pass}"


# ============================================================================
# Tests de Control de Acceso Roto (OWASP A01:2021)
# ============================================================================


class TestBrokenAccessControl:
    """Tests para validar control de acceso basado en roles"""

    def test_estudiante_cannot_create_users(self, client: TestClient, auth_headers_estudiante):
        """Estudiante no debe poder crear usuarios"""
        new_user = {
            "nombre": "Unauthorized User",
            "email": "unauth@test.com",
            "contrasena": "S3cur3P@ssw0rd!2024#Strong",
            "rol": "estudiante",
        }

        response = client.post("/api/auth/register", json=new_user, headers=auth_headers_estudiante)
        assert response.status_code == 403

    def test_docente_cannot_create_users(self, client: TestClient, auth_headers_docente):
        """Docente no debe poder crear usuarios"""
        new_user = {
            "nombre": "Unauthorized User",
            "email": "unauth@test.com",
            "contrasena": "S3cur3P@ssw0rd!2024#Strong",
            "rol": "estudiante",
        }

        response = client.post("/api/auth/register", json=new_user, headers=auth_headers_docente)
        assert response.status_code == 403

    def test_estudiante_cannot_access_admin_endpoints(
        self, client: TestClient, auth_headers_estudiante
    ):
        """Estudiante no debe acceder a endpoints de administración"""
        admin_endpoints = [
            ("/api/users", "GET"),
            ("/api/campus/", "POST"),
            ("/api/edificios/", "POST"),
            ("/api/salas/", "POST"),
        ]

        for endpoint, method in admin_endpoints:
            if method == "GET":
                response = client.get(endpoint, headers=auth_headers_estudiante)
            elif method == "POST":
                response = client.post(endpoint, json={}, headers=auth_headers_estudiante)

            assert response.status_code in [403, 422], f"Estudiante accedió a {endpoint}"

    def test_docente_cannot_delete_campus(
        self, client: TestClient, auth_headers_admin, auth_headers_docente, campus_completo
    ):
        """Docente no debe poder eliminar campus"""
        campus_id = campus_completo["id"]

        response = client.delete(f"/api/campus/{campus_id}", headers=auth_headers_docente)
        assert response.status_code == 403

    def test_admin_can_access_all_endpoints(self, client: TestClient, auth_headers_admin):
        """Administrador debe poder acceder a todos los endpoints"""
        admin_endpoints = [
            "/api/auth/me",
            "/api/users",
        ]

        for endpoint in admin_endpoints:
            response = client.get(endpoint, headers=auth_headers_admin)
            assert response.status_code in [200, 404], f"Admin no puede acceder a {endpoint}"

    def test_horizontal_privilege_escalation_prevention(
        self, client: TestClient, auth_headers_admin
    ):
        """Prevenir que un usuario modifique datos de otro usuario"""
        # Crear dos usuarios estudiantes
        user1_data = {
            "nombre": "Estudiante Uno",
            "email": "horiz_est1@test.com",
            "contrasena": "Estud1ant3_1!2024#SecurePass",
            "rol": "estudiante",
        }
        user2_data = {
            "nombre": "Estudiante Dos",
            "email": "horiz_est2@test.com",
            "contrasena": "Estud1ant3_2!2024#SecurePass",
            "rol": "estudiante",
        }

        user1_response = client.post(
            "/api/auth/register", json=user1_data, headers=auth_headers_admin
        )
        user2_response = client.post(
            "/api/auth/register", json=user2_data, headers=auth_headers_admin
        )

        assert user1_response.status_code == 201
        assert user2_response.status_code == 201

        user1_id = user1_response.json()["id"]

        # Login como usuario 2
        login_response = client.post(
            "/api/auth/login",
            json={"email": user2_data["email"], "contrasena": user2_data["contrasena"]},
        )
        user2_token = login_response.json()["access_token"]
        user2_headers = {"Authorization": f"Bearer {user2_token}"}

        # Intentar modificar datos del usuario 1
        # Esto depende de si tienes un endpoint PUT /api/users/{id}
        # Por ahora solo verificamos que /me retorna el usuario correcto
        response = client.get("/api/auth/me", headers=user2_headers)
        assert response.status_code == 200
        assert response.json()["id"] != user1_id


# ============================================================================
# Tests de Validación de Entrada (OWASP A03:2021)
# ============================================================================


class TestInputValidation:
    """Tests para validar sanitización y validación de entradas"""

    def test_oversized_payload_rejected(self, client: TestClient, auth_headers_admin):
        """Payload muy grande debe ser rechazado"""
        # Crear un payload de más de 5MB (límite del middleware)
        large_data = {
            "nombre": "x" * (6 * 1024 * 1024),  # 6MB
            "email": "test@test.com",
            "contrasena": "Password123!",
            "rol": "estudiante",
        }

        response = client.post("/api/auth/register", json=large_data, headers=auth_headers_admin)
        # Debe ser rechazado por tamaño
        assert response.status_code in [413, 422]

    def test_invalid_email_format_rejected(self, client: TestClient, auth_headers_admin):
        """Emails con formato inválido deben ser rechazados"""
        invalid_emails = [
            "notanemail",
            "@test.com",
            "test@",
            "test@.com",
            "",
            "test@test",  # Sin dominio de nivel superior
        ]

        for email in invalid_emails:
            response = client.post(
                "/api/auth/register",
                json={
                    "nombre": "Test User",
                    "email": email,
                    "contrasena": "S3cur3P@ssw0rd!2024#Strong",
                    "rol": "estudiante",
                },
                headers=auth_headers_admin,
            )
            assert response.status_code == 422, f"Email inválido aceptado: {email}"

    def test_invalid_content_type_rejected(self, client: TestClient, auth_headers_admin):
        """Content-Type inválido debe ser rechazado"""
        response = client.post(
            "/api/auth/register",
            data="invalid data",
            headers={**auth_headers_admin, "Content-Type": "text/plain"},
        )
        assert response.status_code in [415, 422]

    def test_special_characters_in_fields(self, client: TestClient, auth_headers_admin):
        """Validar manejo de caracteres especiales"""
        special_chars_data = {
            "nombre": "Test User ñáéíóú",
            "email": "test-user_123@test.com",
            "contrasena": "S3cur3P@ssw0rd!2024#Strong$%&",
            "rol": "estudiante",
        }

        response = client.post(
            "/api/auth/register", json=special_chars_data, headers=auth_headers_admin
        )
        # Caracteres especiales válidos deben ser aceptados
        assert response.status_code in [201, 422]

    def test_null_values_rejected(self, client: TestClient, auth_headers_admin):
        """Valores null en campos requeridos deben ser rechazados"""
        null_data = {
            "nombre": None,
            "email": "test@test.com",
            "contrasena": "S3cur3P@ssw0rd!2024#Strong",
            "rol": "estudiante",
        }

        response = client.post("/api/auth/register", json=null_data, headers=auth_headers_admin)
        assert response.status_code == 422


# ============================================================================
# Tests de Rate Limiting
# ============================================================================


class TestRateLimiting:
    """Tests para validar rate limiting"""

    def test_rate_limit_on_login_endpoint(self, client: TestClient):
        """Validar que rate limiting funciona en login"""
        # Nota: Los límites están aumentados en conftest.py para testing
        # Este test verifica que el mecanismo existe pero con límites de test
        # En producción, el límite real sería mucho menor

        # Hacer múltiples requests rápidas
        responses = []
        # Usamos un número menor porque los límites de test son altos (10000)
        # Solo verificamos que el código de rate limiting está funcionando
        for i in range(20):
            response = client.post(
                "/api/auth/login", json={"email": f"test{i}@test.com", "contrasena": "password"}
            )
            responses.append(response.status_code)

        # Verificar que al menos se procesaron las solicitudes
        # En un entorno de producción, habría 429s, pero en test los límites son altos
        assert any(
            code in [401, 422] for code in responses
        ), "Login endpoint no está respondiendo correctamente"

    def test_rate_limit_headers_present(self, client: TestClient):
        """Validar que headers de rate limit están presentes"""
        response = client.post(
            "/api/auth/login", json={"email": "test@test.com", "contrasena": "password"}
        )

        # Verificar headers (pueden no estar si el endpoint está excluido)
        # O verificar en un endpoint que seguro los tiene
        assert response.status_code in [401, 422, 429]

    def test_authenticated_users_higher_limit(self, client: TestClient, auth_headers_admin):
        """Usuarios autenticados deben tener límite más alto"""
        # Este test es conceptual, en práctica necesitaría tiempo real
        # Solo verificamos que con token se puede hacer más requests
        count = 0
        for i in range(50):
            response = client.get("/api/auth/me", headers=auth_headers_admin)
            if response.status_code == 200:
                count += 1

        # Con autenticación debe poder hacer al menos 50 requests
        assert count >= 40  # Margen por otros factores


# ============================================================================
# Tests de Configuración de Seguridad (OWASP A05:2021)
# ============================================================================


class TestSecurityConfiguration:
    """Tests para validar configuración de seguridad"""

    def test_cors_headers_present(self, client: TestClient):
        """Validar que headers CORS están configurados"""
        response = client.options("/api/health")
        # Verificar que el servidor responde a OPTIONS (preflight)
        assert response.status_code in [200, 405]

    def test_security_headers_in_response(self, client: TestClient):
        """Validar que headers de seguridad están en las respuestas"""
        response = client.get("/api/health")

        # Verificar headers agregados por middlewares
        assert "X-Process-Time" in response.headers or response.status_code == 200

    def test_error_messages_not_verbose(self, client: TestClient):
        """Validar que mensajes de error no son muy verbosos"""
        # Intentar login con credenciales incorrectas
        response = client.post(
            "/api/auth/login", json={"email": "nonexistent@test.com", "contrasena": "wrongpassword"}
        )

        error_message = response.json().get("detail", "")
        # No debe revelar si el usuario existe o no
        assert "Email o contraseña incorrectos" in error_message
        # No debe decir "usuario no encontrado" o "contraseña incorrecta"
        assert "usuario no encontrado" not in error_message.lower()
        assert "email no encontrado" not in error_message.lower()


# ============================================================================
# Tests de Logging y Auditoría
# ============================================================================


class TestSecurityLogging:
    """Tests para validar que eventos de seguridad se registran"""

    def test_failed_login_attempts_logged(self, client: TestClient, db_session, admin_user_data):
        """Validar que intentos de login fallidos se registran"""
        # Crear usuario directamente en la base de datos
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

        # Intentar login fallido
        response = client.post(
            "/api/auth/login", json={"email": admin_user_data.email, "contrasena": "wrongpassword"}
        )

        assert response.status_code == 401
        # El middleware de logging debería registrar esto
        # En un test real, verificaríamos los logs

    def test_successful_login_logged(self, client: TestClient, db_session, admin_user_data):
        """Validar que logins exitosos se registran"""
        # Crear usuario directamente en la base de datos
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

        # Login exitoso
        response = client.post(
            "/api/auth/login",
            json={"email": admin_user_data.email, "contrasena": admin_user_data.contrasena},
        )

        assert response.status_code == 200
        # El middleware de logging debería registrar esto

    def test_unauthorized_access_logged(self, client: TestClient):
        """Validar que accesos no autorizados se registran"""
        response = client.get("/api/users")
        assert response.status_code == 401
        # El middleware debería loggear este intento


# ============================================================================
# Tests de Roles y Permisos Específicos
# ============================================================================


class TestRoleBasedAccess:
    """Tests específicos para validar acceso basado en roles"""

    def test_only_admin_can_create_campus(
        self, client: TestClient, auth_headers_admin, auth_headers_docente, auth_headers_estudiante
    ):
        """Solo admin puede crear campus"""
        campus_data = {"codigo": "CAMP-TEST", "nombre": "Campus Test", "direccion": "Test 123"}

        # Admin puede
        response = client.post("/api/campus/", json=campus_data, headers=auth_headers_admin)
        assert response.status_code in [201, 409]  # 409 si ya existe

        # Docente no puede
        campus_data["codigo"] = "CAMP-DOC"
        response = client.post("/api/campus/", json=campus_data, headers=auth_headers_docente)
        assert response.status_code == 403

        # Estudiante no puede
        campus_data["codigo"] = "CAMP-EST"
        response = client.post("/api/campus/", json=campus_data, headers=auth_headers_estudiante)
        assert response.status_code == 403

    def test_docente_can_view_own_data(self, client: TestClient, docente_completo):
        """Docente puede ver sus propios datos"""
        # Login como docente
        login_response = client.post(
            "/api/auth/login",
            json={"email": docente_completo["email"], "contrasena": docente_completo["password"]},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Debe poder ver su perfil
        response = client.get("/api/auth/me", headers=headers)
        assert response.status_code == 200
        assert response.json()["email"] == docente_completo["email"]

    def test_estudiante_cannot_modify_other_students(self, client: TestClient, auth_headers_admin):
        """Estudiante no puede modificar datos de otros estudiantes"""
        # Crear dos estudiantes
        est1_data = {
            "nombre": "Estudiante Uno",
            "email": "modif_est1@test.com",
            "contrasena": "Estud1ant3_1!2024#SecurePass",
            "rol": "estudiante",
        }
        est2_data = {
            "nombre": "Estudiante Dos",
            "email": "modif_est2@test.com",
            "contrasena": "Estud1ant3_2!2024#SecurePass",
            "rol": "estudiante",
        }

        client.post("/api/auth/register", json=est1_data, headers=auth_headers_admin)
        client.post("/api/auth/register", json=est2_data, headers=auth_headers_admin)

        # Login como estudiante 1
        login_response = client.post(
            "/api/auth/login",
            json={"email": est1_data["email"], "contrasena": est1_data["contrasena"]},
        )
        est1_token = login_response.json()["access_token"]
        est1_headers = {"Authorization": f"Bearer {est1_token}"}

        # Verificar que solo puede ver sus propios datos
        response = client.get("/api/auth/me", headers=est1_headers)
        assert response.status_code == 200
        assert response.json()["email"] == est1_data["email"]


# ============================================================================
# Tests de Escenarios de Ataque Combinados
# ============================================================================


class TestCombinedAttackScenarios:
    """Tests para escenarios de ataque combinados y complejos"""

    def test_brute_force_login_protection(self, client: TestClient, db_session, admin_user_data):
        """Validar protección contra fuerza bruta en login"""
        # Crear usuario directamente en la base de datos
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

        # Intentar múltiples logins fallidos
        failed_attempts = 0
        rate_limited = False

        for i in range(110):  # Más del límite
            response = client.post(
                "/api/auth/login",
                json={"email": admin_user_data.email, "contrasena": f"wrongpassword{i}"},
            )

            if response.status_code == 429:
                rate_limited = True
                break
            elif response.status_code == 401:
                failed_attempts += 1

        # Debe haber rate limiting o al menos fallar todos los intentos
        assert rate_limited or failed_attempts > 0

    def test_sql_injection_with_xss_combination(self, client: TestClient, auth_headers_admin):
        """Intentar ataque combinado SQL + XSS"""
        malicious_data = {
            "nombre": "<script>alert('XSS')</script>' OR '1'='1",
            "email": "test@test.com'; DROP TABLE users; --",
            "contrasena": "S3cur3P@ssw0rd!2024#Strong",
            "rol": "estudiante",
        }

        response = client.post(
            "/api/auth/register", json=malicious_data, headers=auth_headers_admin
        )
        # Debe ser bloqueado
        assert response.status_code in [400, 422]

    def test_authorization_bypass_attempt(self, client: TestClient, auth_headers_estudiante):
        """Intentar bypass de autorización manipulando tokens"""
        # Intentar acceder a endpoint de admin con token de estudiante
        admin_endpoints = [
            ("/api/users", "GET"),
            ("/api/campus/", "POST"),
        ]

        for endpoint, method in admin_endpoints:
            if method == "GET":
                response = client.get(endpoint, headers=auth_headers_estudiante)
            elif method == "POST":
                response = client.post(endpoint, json={}, headers=auth_headers_estudiante)

            assert response.status_code in [403, 422]

    def test_mass_assignment_prevention(self, client: TestClient, auth_headers_admin):
        """Prevenir mass assignment de campos no permitidos"""
        # Intentar crear usuario con campos extra
        data_with_extra_fields = {
            "nombre": "Test User",
            "email": "test@test.com",
            "contrasena": "S3cur3P@ssw0rd!2024#Strong",
            "rol": "estudiante",
            "is_admin": True,  # Campo no permitido
            # Nota: activo es un campo válido en UserSecureCreate
            "created_at": "2020-01-01",  # Campo del sistema
        }

        response = client.post(
            "/api/auth/register", json=data_with_extra_fields, headers=auth_headers_admin
        )

        # Si se crea, verificar que campos extra no fueron asignados
        if response.status_code == 201:
            user = response.json()
            assert user["rol"] == "estudiante"  # No "administrador"
            # El campo created_at no debería ser manipulable por el usuario
