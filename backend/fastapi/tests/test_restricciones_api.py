import pytest
from fastapi.testclient import TestClient


class TestRestriccionesEndpoints:
    """Tests para los endpoints de restricciones"""

    def test_create_restriccion_success_docente(
        self, client: TestClient, auth_headers_docente_completo, docente_completo
    ):
        """Test creación exitosa de restricción por docente"""
        restriccion_data = {
            "tipo": "horario",
            "valor": "no disponible mañanas",
            "prioridad": 5,
            "restriccion_blanda": True,
            "restriccion_dura": False,
            "activa": True,
            "docente_id": docente_completo["docente_id"],
        }

        response = client.post(
            "/api/restricciones/", json=restriccion_data, headers=auth_headers_docente_completo
        )

        assert response.status_code == 201
        data = response.json()
        assert data["tipo"] == "horario"
        assert data["valor"] == "no disponible mañanas"
        assert data["prioridad"] == 5
        assert data["restriccion_blanda"] is True
        assert data["restriccion_dura"] is False
        assert data["activa"] is True
        assert "id" in data
        assert "docente_id" in data

    def test_create_restriccion_success_admin(
        self, client: TestClient, auth_headers_admin, docente_completo
    ):
        """Test creación exitosa de restricción por administrador"""
        restriccion_data = {
            "tipo": "aula",
            "valor": "preferencia laboratorio",
            "prioridad": 8,
            "restriccion_blanda": False,
            "restriccion_dura": True,
            "activa": True,
            "docente_id": docente_completo["docente_id"],
        }

        response = client.post(
            "/api/restricciones/", json=restriccion_data, headers=auth_headers_admin
        )

        assert response.status_code == 201
        data = response.json()
        assert data["tipo"] == "aula"
        assert data["valor"] == "preferencia laboratorio"
        assert data["prioridad"] == 8

    def test_create_restriccion_unauthorized(self, client: TestClient, docente_completo):
        """Test creación de restricción sin autenticación"""
        restriccion_data = {
            "tipo": "horario",
            "valor": "test",
            "prioridad": 5,
            "restriccion_blanda": True,
            "restriccion_dura": False,
            "docente_id": docente_completo["docente_id"],
        }

        response = client.post("/api/restricciones/", json=restriccion_data)
        assert response.status_code == 401

    def test_create_restriccion_invalid_tipo(
        self, client: TestClient, auth_headers_docente_completo, docente_completo
    ):
        """Test creación de restricción con tipo inválido"""
        restriccion_data = {
            "tipo": "tipo_invalido",
            "valor": "test",
            "prioridad": 5,
            "restriccion_blanda": True,
            "restriccion_dura": False,
            "docente_id": docente_completo["docente_id"],
        }

        response = client.post(
            "/api/restricciones/", json=restriccion_data, headers=auth_headers_docente_completo
        )
        assert response.status_code == 422

    def test_create_restriccion_invalid_prioridad(
        self, client: TestClient, auth_headers_docente_completo, docente_completo
    ):
        """Test creación de restricción con prioridad inválida"""
        restriccion_data = {
            "tipo": "horario",
            "valor": "test",
            "prioridad": 15,  # Fuera del rango 1-10
            "restriccion_blanda": True,
            "restriccion_dura": False,
            "docente_id": docente_completo["docente_id"],
        }

        response = client.post(
            "/api/restricciones/", json=restriccion_data, headers=auth_headers_docente_completo
        )
        assert response.status_code == 422

    def test_get_restricciones_admin(
        self, client: TestClient, auth_headers_admin, docente_completo
    ):
        """Test obtener todas las restricciones como administrador"""
        # Crear una restricción primero
        restriccion_data = {
            "tipo": "horario",
            "valor": "test admin",
            "prioridad": 5,
            "restriccion_blanda": True,
            "restriccion_dura": False,
            "docente_id": docente_completo["docente_id"],
        }
        client.post("/api/restricciones/", json=restriccion_data, headers=auth_headers_admin)

        # Obtener restricciones
        response = client.get("/api/restricciones/", headers=auth_headers_admin)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert "id" in data[0]
            assert "tipo" in data[0]

    def test_get_restricciones_docente(
        self, client: TestClient, docente_completo, auth_headers_docente_completo
    ):
        """Test obtener restricciones propias como docente"""
        # Crear una restricción primero
        restriccion_data = {
            "tipo": "horario",
            "valor": "test docente",
            "prioridad": 5,
            "restriccion_blanda": True,
            "restriccion_dura": False,
            "docente_id": docente_completo["docente_id"],
        }
        client.post(
            "/api/restricciones/", json=restriccion_data, headers=auth_headers_docente_completo
        )

        # Obtener restricciones
        response = client.get("/api/restricciones/", headers=auth_headers_docente_completo)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_restricciones_unauthorized(self, client: TestClient):
        """Test obtener restricciones sin autenticación"""
        response = client.get("/api/restricciones/")
        assert response.status_code == 401

    def test_get_restriccion_by_id_success(
        self, client: TestClient, auth_headers_admin, docente_completo
    ):
        """Test obtener restricción específica por ID"""
        # Crear una restricción primero
        restriccion_data = {
            "tipo": "horario",
            "valor": "test get by id",
            "prioridad": 5,
            "restriccion_blanda": True,
            "restriccion_dura": False,
            "docente_id": docente_completo["docente_id"],
        }
        create_response = client.post(
            "/api/restricciones/", json=restriccion_data, headers=auth_headers_admin
        )
        created_id = create_response.json()["id"]

        # Obtener por ID
        response = client.get(f"/api/restricciones/{created_id}", headers=auth_headers_admin)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_id
        assert data["valor"] == "test get by id"

    def test_get_restriccion_by_id_not_found(self, client: TestClient, auth_headers_admin):
        """Test obtener restricción que no existe"""
        response = client.get("/api/restricciones/99999", headers=auth_headers_admin)
        assert response.status_code == 404

    def test_update_restriccion_put_success(
        self, client: TestClient, auth_headers_admin, docente_completo
    ):
        """Test actualización completa de restricción con PUT"""
        # Crear una restricción primero
        restriccion_data = {
            "tipo": "horario",
            "valor": "original",
            "prioridad": 5,
            "restriccion_blanda": True,
            "restriccion_dura": False,
            "docente_id": docente_completo["docente_id"],
        }
        create_response = client.post(
            "/api/restricciones/", json=restriccion_data, headers=auth_headers_admin
        )
        created_id = create_response.json()["id"]

        # Actualizar con PUT
        updated_data = {
            "tipo": "aula",
            "valor": "actualizado",
            "prioridad": 8,
            "restriccion_blanda": False,
            "restriccion_dura": True,
            "docente_id": docente_completo["docente_id"],
        }
        response = client.put(
            f"/api/restricciones/{created_id}", json=updated_data, headers=auth_headers_admin
        )

        assert response.status_code == 200
        data = response.json()
        assert data["tipo"] == "aula"
        assert data["valor"] == "actualizado"
        assert data["prioridad"] == 8

    def test_update_restriccion_patch_success(
        self, client: TestClient, auth_headers_admin, docente_completo
    ):
        """Test actualización parcial de restricción con PATCH"""
        # Crear una restricción primero
        restriccion_data = {
            "tipo": "horario",
            "valor": "original",
            "prioridad": 5,
            "restriccion_blanda": True,
            "restriccion_dura": False,
            "docente_id": docente_completo["docente_id"],
        }
        create_response = client.post(
            "/api/restricciones/", json=restriccion_data, headers=auth_headers_admin
        )
        created_id = create_response.json()["id"]

        # Actualizar solo algunos campos con PATCH
        patch_data = {"valor": "parcialmente actualizado", "prioridad": 9}
        response = client.patch(
            f"/api/restricciones/{created_id}", json=patch_data, headers=auth_headers_admin
        )

        assert response.status_code == 200
        data = response.json()
        assert data["valor"] == "parcialmente actualizado"
        assert data["prioridad"] == 9
        assert data["tipo"] == "horario"  # Debe mantener el valor original

    def test_update_restriccion_patch_empty_data(
        self, client: TestClient, auth_headers_admin, docente_completo
    ):
        """Test PATCH con datos vacíos"""
        # Crear una restricción primero
        restriccion_data = {
            "tipo": "horario",
            "valor": "original",
            "prioridad": 5,
            "restriccion_blanda": True,
            "restriccion_dura": False,
            "docente_id": docente_completo["docente_id"],
        }
        create_response = client.post(
            "/api/restricciones/", json=restriccion_data, headers=auth_headers_admin
        )
        created_id = create_response.json()["id"]

        # Intentar actualizar sin datos
        response = client.patch(
            f"/api/restricciones/{created_id}", json={}, headers=auth_headers_admin
        )
        assert response.status_code == 400  # El backend valida que no se envíen datos vacíos

    def test_delete_restriccion_success(
        self, client: TestClient, auth_headers_admin, docente_completo
    ):
        """Test eliminación exitosa de restricción"""
        # Crear una restricción primero
        restriccion_data = {
            "tipo": "horario",
            "valor": "para eliminar",
            "prioridad": 5,
            "restriccion_blanda": True,
            "restriccion_dura": False,
            "docente_id": docente_completo["docente_id"],
        }
        create_response = client.post(
            "/api/restricciones/", json=restriccion_data, headers=auth_headers_admin
        )
        created_id = create_response.json()["id"]

        # Eliminar
        response = client.delete(f"/api/restricciones/{created_id}", headers=auth_headers_admin)

        assert response.status_code == 204

        # Verificar que ya no existe
        get_response = client.get(f"/api/restricciones/{created_id}", headers=auth_headers_admin)
        assert get_response.status_code == 404

    def test_delete_restriccion_not_found(self, client: TestClient, auth_headers_admin):
        """Test eliminación de restricción que no existe"""
        response = client.delete("/api/restricciones/99999", headers=auth_headers_admin)
        assert response.status_code == 404


class TestRestriccionesAdminEndpoints:
    """Tests para endpoints específicos de administradores"""

    def test_admin_get_restricciones_by_docente(self, client: TestClient, auth_headers_admin):
        """Test obtener restricciones de un docente específico como admin"""
        # Crear una restricción para un docente específico
        restriccion_data = {
            "tipo": "horario",
            "valor": "test admin endpoint",
            "prioridad": 5,
            "restriccion_blanda": True,
            "restriccion_dura": False,
            "docente_id": 2,
        }
        client.post("/api/restricciones/", json=restriccion_data, headers=auth_headers_admin)

        # Obtener restricciones del docente 2
        response = client.get("/api/restricciones/admin/docente/2", headers=auth_headers_admin)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_admin_create_restriccion_for_docente(self, client: TestClient, auth_headers_admin):
        """Test crear restricción para docente específico como admin"""
        restriccion_data = {
            "tipo": "aula",
            "valor": "admin creates for docente",
            "prioridad": 7,
            "restriccion_blanda": False,
            "restriccion_dura": True,
            "docente_id": 3,  # Este se sobrescribirá por el parámetro de la URL
        }

        response = client.post(
            "/api/restricciones/admin/docente/5", json=restriccion_data, headers=auth_headers_admin
        )

        assert response.status_code == 201
        data = response.json()
        assert data["docente_id"] == 5  # Debe usar el ID de la URL
        assert data["valor"] == "admin creates for docente"

    def test_admin_endpoints_unauthorized_docente(self, client: TestClient, auth_headers_docente):
        """Test que los endpoints de admin no son accesibles para docentes"""
        response = client.get("/api/restricciones/admin/docente/1", headers=auth_headers_docente)
        assert response.status_code == 403

    def test_admin_endpoints_unauthorized_estudiante(
        self, client: TestClient, auth_headers_estudiante
    ):
        """Test que los endpoints de admin no son accesibles para estudiantes"""
        response = client.get("/api/restricciones/admin/docente/1", headers=auth_headers_estudiante)
        assert response.status_code == 403


class TestRestriccionesValidation:
    """Tests para validación de datos de restricciones"""

    def test_tipos_restriccion_validos(
        self, client: TestClient, auth_headers_admin, docente_completo
    ):
        """Test todos los tipos de restricción válidos"""
        tipos_validos = ["horario", "aula", "materia", "periodo", "disponibilidad"]

        for tipo in tipos_validos:
            restriccion_data = {
                "tipo": tipo,
                "valor": f"test {tipo}",
                "prioridad": 5,
                "restriccion_blanda": True,
                "restriccion_dura": False,
                "docente_id": docente_completo["docente_id"],
            }

            response = client.post(
                "/api/restricciones/", json=restriccion_data, headers=auth_headers_admin
            )
            assert response.status_code == 201, f"Falló para tipo: {tipo}"
            assert response.json()["tipo"] == tipo

    def test_prioridad_limite_inferior(
        self, client: TestClient, auth_headers_admin, docente_completo
    ):
        """Test prioridad mínima válida"""
        restriccion_data = {
            "tipo": "horario",
            "valor": "prioridad minima",
            "prioridad": 1,
            "restriccion_blanda": True,
            "restriccion_dura": False,
            "docente_id": docente_completo["docente_id"],
        }

        response = client.post(
            "/api/restricciones/", json=restriccion_data, headers=auth_headers_admin
        )
        assert response.status_code == 201

    def test_prioridad_limite_superior(
        self, client: TestClient, auth_headers_admin, docente_completo
    ):
        """Test prioridad máxima válida"""
        restriccion_data = {
            "tipo": "horario",
            "valor": "prioridad maxima",
            "prioridad": 10,
            "restriccion_blanda": True,
            "restriccion_dura": False,
            "docente_id": docente_completo["docente_id"],
        }

        response = client.post(
            "/api/restricciones/", json=restriccion_data, headers=auth_headers_admin
        )
        assert response.status_code == 201

    def test_valor_vacio_invalido(self, client: TestClient, auth_headers_admin, docente_completo):
        """Test valor vacío es inválido"""
        restriccion_data = {
            "tipo": "horario",
            "valor": "",
            "prioridad": 5,
            "restriccion_blanda": True,
            "restriccion_dura": False,
            "docente_id": docente_completo["docente_id"],
        }

        response = client.post(
            "/api/restricciones/", json=restriccion_data, headers=auth_headers_admin
        )
        assert response.status_code == 422
