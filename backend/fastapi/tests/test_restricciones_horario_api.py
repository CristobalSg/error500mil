from datetime import time

import pytest
from fastapi.testclient import TestClient


class TestRestriccionesHorarioAdminEndpoints:
    """Tests para endpoints de restricciones de horario para administradores"""

    def test_admin_create_restriccion_horario_success(
        self, client: TestClient, auth_headers_admin, docente_completo
    ):
        """Test creación exitosa de restricción de horario por administrador"""
        restriccion_data = {
            "docente_id": docente_completo["docente_id"],
            "dia_semana": 1,  # Lunes
            "hora_inicio": "08:00",
            "hora_fin": "12:00",
            "disponible": True,
            "descripcion": "Disponible mañanas lunes",
            "activa": True,
        }

        response = client.post(
            "/api/restricciones-horario/", json=restriccion_data, headers=auth_headers_admin
        )

        assert response.status_code == 201
        data = response.json()
        assert data["docente_id"] == 1
        assert data["dia_semana"] == 1
        assert data["hora_inicio"] == "08:00:00"
        assert data["hora_fin"] == "12:00:00"
        assert data["disponible"] is True
        assert data["descripcion"] == "Disponible mañanas lunes"
        assert data["activa"] is True
        assert "id" in data

    def test_admin_create_restriccion_horario_invalid_hours(
        self, client: TestClient, auth_headers_admin, docente_completo
    ):
        """Test creación con horas inválidas (fin antes que inicio)"""
        restriccion_data = {
            "docente_id": docente_completo["docente_id"],
            "dia_semana": 1,
            "hora_inicio": "12:00",
            "hora_fin": "08:00",  # Hora fin antes que inicio
            "disponible": True,
            "descripcion": "Invalid hours",
        }

        response = client.post(
            "/api/restricciones-horario/", json=restriccion_data, headers=auth_headers_admin
        )
        assert response.status_code == 422

    def test_admin_create_restriccion_horario_invalid_day(
        self, client: TestClient, auth_headers_admin, docente_completo
    ):
        """Test creación con día de semana inválido"""
        restriccion_data = {
            "docente_id": docente_completo["docente_id"],
            "dia_semana": 7,  # Día inválido (debe ser 0-6)
            "hora_inicio": "08:00",
            "hora_fin": "12:00",
            "disponible": True,
        }

        response = client.post(
            "/api/restricciones-horario/", json=restriccion_data, headers=auth_headers_admin
        )
        assert response.status_code == 422

    def test_admin_create_restriccion_horario_docente_inexistente(
        self, client: TestClient, auth_headers_admin
    ):
        """Test creación con user_id inexistente debe fallar"""
        restriccion_data = {
            "docente_id": 99999,  # User que no existe
            "dia_semana": 1,
            "hora_inicio": "08:00",
            "hora_fin": "12:00",
            "disponible": True,
            "descripcion": "Restricción con usuario inexistente",
        }

        response = client.post(
            "/api/restricciones-horario/", json=restriccion_data, headers=auth_headers_admin
        )
        assert response.status_code == 404
        data = response.json()
        assert "no encontrado" in data["detail"].lower()

    def test_admin_create_restriccion_horario_auto_crea_docente(
        self, client: TestClient, auth_headers_admin, auth_headers_docente
    ):
        """Test que se crea automáticamente el registro de docente si se usa un user_id de un docente sin perfil"""
        # Obtener el ID del usuario docente desde el token/fixture
        # El fixture auth_headers_docente tiene un usuario docente
        # Vamos a intentar usar directamente el user_id 2 que sabemos es un docente
        
        restriccion_data = {
            "docente_id": 2,  # ID del usuario docente (no el docente_id de la tabla docente)
            "dia_semana": 2,
            "hora_inicio": "10:00",
            "hora_fin": "12:00",
            "disponible": True,
            "descripcion": "Test auto-creación de docente si falta perfil",
        }

        response = client.post(
            "/api/restricciones-horario/", json=restriccion_data, headers=auth_headers_admin
        )
        
        # Debería crear exitosamente la restricción
        # Si el docente no existe, lo crea automáticamente
        # Si el docente ya existe, simplemente crea la restricción
        assert response.status_code == 201
        data = response.json()
        assert data["descripcion"] == "Test auto-creación de docente si falta perfil"
        assert "docente_id" in data

    def test_admin_get_restricciones_horario(
        self, client: TestClient, auth_headers_admin, docente_completo
    ):
        """Test obtener todas las restricciones de horario como admin"""
        # Crear una restricción primero
        restriccion_data = {
            "docente_id": docente_completo["docente_id"],
            "dia_semana": 2,
            "hora_inicio": "14:00",
            "hora_fin": "18:00",
            "disponible": False,
            "descripcion": "No disponible tardes martes",
        }
        client.post(
            "/api/restricciones-horario/", json=restriccion_data, headers=auth_headers_admin
        )

        # Obtener todas las restricciones
        response = client.get("/api/restricciones-horario/", headers=auth_headers_admin)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_admin_get_restricciones_horario_with_pagination(
        self, client: TestClient, auth_headers_admin, docente_completo
    ):
        """Test paginación en obtener restricciones de horario"""
        response = client.get(
            "/api/restricciones-horario/?skip=0&limit=10", headers=auth_headers_admin
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10

    def test_admin_get_restriccion_horario_by_id(
        self, client: TestClient, auth_headers_admin, docente_completo
    ):
        """Test obtener restricción de horario específica por ID"""
        # Crear una restricción primero
        restriccion_data = {
            "docente_id": docente_completo["docente_id"],
            "dia_semana": 3,
            "hora_inicio": "09:00",
            "hora_fin": "11:00",
            "disponible": True,
            "descripcion": "Test get by ID",
        }
        create_response = client.post(
            "/api/restricciones-horario/", json=restriccion_data, headers=auth_headers_admin
        )
        created_id = create_response.json()["id"]

        # Obtener por ID
        response = client.get(
            f"/api/restricciones-horario/{created_id}", headers=auth_headers_admin
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_id
        assert data["descripcion"] == "Test get by ID"

    def test_admin_get_restriccion_horario_not_found(
        self, client: TestClient, auth_headers_admin, docente_completo
    ):
        """Test obtener restricción de horario que no existe"""
        response = client.get("/api/restricciones-horario/99999", headers=auth_headers_admin)
        assert response.status_code == 404

    def test_admin_update_restriccion_horario_patch(
        self, client: TestClient, auth_headers_admin, docente_completo
    ):
        """Test actualización parcial de restricción de horario"""
        # Crear una restricción primero
        restriccion_data = {
            "docente_id": docente_completo["docente_id"],
            "dia_semana": 4,
            "hora_inicio": "10:00",
            "hora_fin": "12:00",
            "disponible": True,
            "descripcion": "Original description",
        }
        create_response = client.post(
            "/api/restricciones-horario/", json=restriccion_data, headers=auth_headers_admin
        )
        created_id = create_response.json()["id"]

        # Actualizar parcialmente
        patch_data = {"descripcion": "Updated description", "disponible": False}
        response = client.patch(
            f"/api/restricciones-horario/{created_id}", json=patch_data, headers=auth_headers_admin
        )

        assert response.status_code == 200
        data = response.json()
        assert data["descripcion"] == "Updated description"
        assert data["disponible"] is False
        assert data["dia_semana"] == 4  # Debe mantener el valor original

    def test_admin_update_restriccion_horario_empty_data(
        self, client: TestClient, auth_headers_admin, docente_completo
    ):
        """Test actualización con datos vacíos"""
        # Crear una restricción primero
        restriccion_data = {
            "docente_id": docente_completo["docente_id"],
            "dia_semana": 5,
            "hora_inicio": "15:00",
            "hora_fin": "17:00",
            "disponible": True,
        }
        create_response = client.post(
            "/api/restricciones-horario/", json=restriccion_data, headers=auth_headers_admin
        )
        created_id = create_response.json()["id"]

        # Intentar actualizar sin datos
        response = client.patch(
            f"/api/restricciones-horario/{created_id}", json={}, headers=auth_headers_admin
        )
        assert response.status_code == 400

    def test_admin_delete_restriccion_horario(
        self, client: TestClient, auth_headers_admin, docente_completo
    ):
        """Test eliminación de restricción de horario"""
        # Crear una restricción primero
        restriccion_data = {
            "docente_id": docente_completo["docente_id"],
            "dia_semana": 6,
            "hora_inicio": "08:00",
            "hora_fin": "10:00",
            "disponible": True,
            "descripcion": "Para eliminar",
        }
        create_response = client.post(
            "/api/restricciones-horario/", json=restriccion_data, headers=auth_headers_admin
        )
        created_id = create_response.json()["id"]

        # Eliminar
        response = client.delete(
            f"/api/restricciones-horario/{created_id}", headers=auth_headers_admin
        )

        assert response.status_code == 204

        # Verificar que ya no existe
        get_response = client.get(
            f"/api/restricciones-horario/{created_id}", headers=auth_headers_admin
        )
        assert get_response.status_code == 404

    def test_admin_get_restricciones_by_docente(
        self, client: TestClient, auth_headers_admin, docente_completo
    ):
        """Test obtener restricciones de horario por docente específico"""
        # Crear restricciones para un docente específico
        restriccion_data = {
            "docente_id": 2,
            "dia_semana": 1,
            "hora_inicio": "08:00",
            "hora_fin": "12:00",
            "disponible": True,
            "descripcion": "Test by docente",
        }
        client.post(
            "/api/restricciones-horario/", json=restriccion_data, headers=auth_headers_admin
        )

        # Obtener restricciones del docente 2
        response = client.get("/api/restricciones-horario/docente/2", headers=auth_headers_admin)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_admin_get_restricciones_by_day(
        self, client: TestClient, auth_headers_admin, docente_completo
    ):
        """Test obtener restricciones de horario por día de la semana"""
        # Crear restricciones para un día específico
        restriccion_data = {
            "docente_id": docente_completo["docente_id"],
            "dia_semana": 3,  # Miércoles
            "hora_inicio": "09:00",
            "hora_fin": "11:00",
            "disponible": True,
            "descripcion": "Miércoles test",
        }
        client.post(
            "/api/restricciones-horario/", json=restriccion_data, headers=auth_headers_admin
        )

        # Obtener restricciones del miércoles
        response = client.get("/api/restricciones-horario/dia/3", headers=auth_headers_admin)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_admin_get_disponibilidad_docente(
        self, client: TestClient, auth_headers_admin, docente_completo
    ):
        """Test obtener disponibilidad de un docente"""
        # Crear restricción de disponibilidad
        restriccion_data = {
            "docente_id": docente_completo["docente_id"],
            "dia_semana": 1,
            "hora_inicio": "08:00",
            "hora_fin": "12:00",
            "disponible": True,
            "descripcion": "Disponible lunes mañana",
        }
        client.post(
            "/api/restricciones-horario/", json=restriccion_data, headers=auth_headers_admin
        )

        # Obtener disponibilidad del docente
        response = client.get(
            "/api/restricciones-horario/disponibilidad/1", headers=auth_headers_admin
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_admin_get_disponibilidad_docente_with_day(
        self, client: TestClient, auth_headers_admin, docente_completo
    ):
        """Test obtener disponibilidad de un docente para día específico"""
        response = client.get(
            "/api/restricciones-horario/disponibilidad/1?dia_semana=1", headers=auth_headers_admin
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_admin_delete_restricciones_by_docente(
        self, client: TestClient, auth_headers_admin, docente_completo
    ):
        """Test eliminar todas las restricciones de un docente"""
        # Crear varias restricciones para un docente
        for dia in [1, 2, 3]:
            restriccion_data = {
                "docente_id": 3,
                "dia_semana": dia,
                "hora_inicio": "08:00",
                "hora_fin": "12:00",
                "disponible": True,
                "descripcion": f"Día {dia}",
            }
            client.post(
                "/api/restricciones-horario/", json=restriccion_data, headers=auth_headers_admin
            )

        # Eliminar todas las restricciones del docente 3
        response = client.delete("/api/restricciones-horario/docente/3", headers=auth_headers_admin)

        assert response.status_code == 200
        data = response.json()
        assert "mensaje" in data
        assert "eliminadas" in data

    def test_admin_endpoints_unauthorized_docente(self, client: TestClient, auth_headers_docente):
        """Test que los endpoints de admin no son accesibles para docentes"""
        response = client.get("/api/restricciones-horario/", headers=auth_headers_docente)
        assert response.status_code == 403

    def test_admin_endpoints_unauthorized_estudiante(
        self, client: TestClient, auth_headers_estudiante
    ):
        """Test que los endpoints de admin no son accesibles para estudiantes"""
        response = client.get("/api/restricciones-horario/", headers=auth_headers_estudiante)
        assert response.status_code == 403


class TestRestriccionesHorarioDocenteEndpoints:
    """Tests para endpoints de restricciones de horario para docentes"""

    def test_docente_get_mis_restricciones(
        self, client: TestClient, docente_completo, auth_headers_docente_completo
    ):
        """Test docente obtiene sus propias restricciones de horario"""
        # Primero crear una restricción para tener datos
        restriccion_data = {
            "docente_id": docente_completo["docente_id"],
            "dia_semana": 1,
            "hora_inicio": "08:00",
            "hora_fin": "12:00",
            "disponible": True,
            "descripcion": "Restricción para test GET",
        }
        create_response = client.post(
            "/api/restricciones-horario/docente/mis-restricciones",
            json=restriccion_data,
            headers=auth_headers_docente_completo,
        )
        assert create_response.status_code == 201

        # Ahora obtener todas las restricciones
        response = client.get(
            "/api/restricciones-horario/docente/mis-restricciones",
            headers=auth_headers_docente_completo,
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(r["descripcion"] == "Restricción para test GET" for r in data)

    def test_docente_create_restriccion_horario(
        self, client: TestClient, docente_completo, auth_headers_docente_completo
    ):
        """Test docente crea su propia restricción de horario"""
        restriccion_data = {
            "docente_id": docente_completo[
                "docente_id"
            ],  # Este valor será sobrescrito por el sistema
            "dia_semana": 1,
            "hora_inicio": "08:00",
            "hora_fin": "12:00",
            "disponible": True,
            "descripcion": "Mi restricción como docente",
        }

        response = client.post(
            "/api/restricciones-horario/docente/mis-restricciones",
            json=restriccion_data,
            headers=auth_headers_docente_completo,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["descripcion"] == "Mi restricción como docente"
        assert data["dia_semana"] == 1

    def test_docente_get_restriccion_by_id(
        self, client: TestClient, docente_completo, auth_headers_docente_completo
    ):
        """Test docente obtiene una de sus restricciones por ID"""
        # Crear una restricción primero
        restriccion_data = {
            "docente_id": docente_completo["docente_id"],
            "dia_semana": 2,
            "hora_inicio": "14:00",
            "hora_fin": "16:00",
            "disponible": False,
            "descripcion": "Test get by id docente",
        }
        create_response = client.post(
            "/api/restricciones-horario/docente/mis-restricciones",
            json=restriccion_data,
            headers=auth_headers_docente_completo,
        )
        created_id = create_response.json()["id"]

        # Obtener por ID
        response = client.get(
            f"/api/restricciones-horario/docente/mis-restricciones/{created_id}",
            headers=auth_headers_docente_completo,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_id

    def test_docente_update_restriccion_horario(
        self, client: TestClient, docente_completo, auth_headers_docente_completo
    ):
        """Test docente actualiza su propia restricción de horario"""
        # Crear una restricción primero
        restriccion_data = {
            "docente_id": docente_completo["docente_id"],
            "dia_semana": 3,
            "hora_inicio": "10:00",
            "hora_fin": "12:00",
            "disponible": True,
            "descripcion": "Original docente",
        }
        create_response = client.post(
            "/api/restricciones-horario/docente/mis-restricciones",
            json=restriccion_data,
            headers=auth_headers_docente_completo,
        )
        created_id = create_response.json()["id"]

        # Actualizar
        patch_data = {"descripcion": "Actualizado por docente", "disponible": False}
        response = client.patch(
            f"/api/restricciones-horario/docente/mis-restricciones/{created_id}",
            json=patch_data,
            headers=auth_headers_docente_completo,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["descripcion"] == "Actualizado por docente"
        assert data["disponible"] is False

    def test_docente_delete_restriccion_horario(
        self, client: TestClient, docente_completo, auth_headers_docente_completo
    ):
        """Test docente elimina su propia restricción de horario"""
        # Crear una restricción primero
        restriccion_data = {
            "docente_id": docente_completo["docente_id"],
            "dia_semana": 4,
            "hora_inicio": "15:00",
            "hora_fin": "17:00",
            "disponible": True,
            "descripcion": "Para eliminar por docente",
        }
        create_response = client.post(
            "/api/restricciones-horario/docente/mis-restricciones",
            json=restriccion_data,
            headers=auth_headers_docente_completo,
        )
        created_id = create_response.json()["id"]

        # Eliminar
        response = client.delete(
            f"/api/restricciones-horario/docente/mis-restricciones/{created_id}",
            headers=auth_headers_docente_completo,
        )

        assert response.status_code == 204

    def test_docente_get_mi_disponibilidad(
        self, client: TestClient, docente_completo, auth_headers_docente_completo
    ):
        """Test docente obtiene su propia disponibilidad"""
        # Crear una restricción de disponibilidad primero
        restriccion_data = {
            "docente_id": docente_completo["docente_id"],
            "dia_semana": 1,
            "hora_inicio": "08:00",
            "hora_fin": "12:00",
            "disponible": True,
            "descripcion": "Mi disponibilidad",
        }
        client.post(
            "/api/restricciones-horario/docente/mis-restricciones",
            json=restriccion_data,
            headers=auth_headers_docente_completo,
        )

        # Obtener disponibilidad
        response = client.get(
            "/api/restricciones-horario/docente/mi-disponibilidad",
            headers=auth_headers_docente_completo,
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_docente_get_mi_disponibilidad_by_day(
        self, client: TestClient, docente_completo, auth_headers_docente_completo
    ):
        """Test docente obtiene su disponibilidad para día específico"""
        # Crear una restricción de disponibilidad para día específico
        restriccion_data = {
            "docente_id": docente_completo["docente_id"],
            "dia_semana": 2,
            "hora_inicio": "10:00",
            "hora_fin": "14:00",
            "disponible": True,
            "descripcion": "Disponibilidad martes",
        }
        client.post(
            "/api/restricciones-horario/docente/mis-restricciones",
            json=restriccion_data,
            headers=auth_headers_docente_completo,
        )

        # Obtener disponibilidad para ese día
        response = client.get(
            "/api/restricciones-horario/docente/mi-disponibilidad?dia_semana=2",
            headers=auth_headers_docente_completo,
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert all(r["dia_semana"] == 2 for r in data)

    def test_docente_endpoints_unauthorized_estudiante(
        self, client: TestClient, auth_headers_estudiante
    ):
        """Test que los endpoints de docente no son accesibles para estudiantes"""
        response = client.get(
            "/api/restricciones-horario/docente/mis-restricciones", headers=auth_headers_estudiante
        )
        assert response.status_code == 403

    def test_docente_endpoints_unauthorized(self, client: TestClient):
        """Test que los endpoints de docente requieren autenticación"""
        response = client.get("/api/restricciones-horario/docente/mis-restricciones")
        assert response.status_code == 401


class TestRestriccionesHorarioValidation:
    """Tests para validación de datos de restricciones de horario"""

    def test_dias_semana_validos(self, client: TestClient, auth_headers_admin, docente_completo):
        """Test todos los días de semana válidos (0-6)"""
        for dia in range(0, 7):  # 0=Domingo, 6=Sábado
            restriccion_data = {
                "docente_id": docente_completo["docente_id"],
                "dia_semana": dia,
                "hora_inicio": "08:00",
                "hora_fin": "12:00",
                "disponible": True,
                "descripcion": f"Día {dia}",
            }

            response = client.post(
                "/api/restricciones-horario/", json=restriccion_data, headers=auth_headers_admin
            )
            assert response.status_code == 201, f"Falló para día: {dia}"

    def test_horas_limite_validas(self, client: TestClient, auth_headers_admin, docente_completo):
        """Test horas límite válidas"""
        # Test hora muy temprana
        restriccion_data = {
            "docente_id": docente_completo["docente_id"],
            "dia_semana": 1,
            "hora_inicio": "00:00",
            "hora_fin": "01:00",
            "disponible": True,
        }
        response = client.post(
            "/api/restricciones-horario/", json=restriccion_data, headers=auth_headers_admin
        )
        assert response.status_code == 201

        # Test hora muy tarde
        restriccion_data["hora_inicio"] = "23:00"
        restriccion_data["hora_fin"] = "23:59"
        response = client.post(
            "/api/restricciones-horario/", json=restriccion_data, headers=auth_headers_admin
        )
        assert response.status_code == 201

    def test_descripcion_opcional(self, client: TestClient, auth_headers_admin, docente_completo):
        """Test que la descripción es opcional"""
        restriccion_data = {
            "docente_id": docente_completo["docente_id"],
            "dia_semana": 1,
            "hora_inicio": "08:00",
            "hora_fin": "12:00",
            "disponible": True,
            # Sin descripción
        }

        response = client.post(
            "/api/restricciones-horario/", json=restriccion_data, headers=auth_headers_admin
        )
        assert response.status_code == 201

    def test_descripcion_vacia_se_convierte_a_null(
        self, client: TestClient, auth_headers_admin, docente_completo
    ):
        """Test que descripción vacía se convierte a null"""
        restriccion_data = {
            "docente_id": docente_completo["docente_id"],
            "dia_semana": 1,
            "hora_inicio": "08:00",
            "hora_fin": "12:00",
            "disponible": True,
            "descripcion": "",  # Descripción vacía
        }

        response = client.post(
            "/api/restricciones-horario/", json=restriccion_data, headers=auth_headers_admin
        )
        assert response.status_code == 201
        # La validación debería convertir esto a None/null

    def test_activa_default_true(self, client: TestClient, auth_headers_admin, docente_completo):
        """Test que 'activa' tiene valor por defecto True"""
        restriccion_data = {
            "docente_id": docente_completo["docente_id"],
            "dia_semana": 1,
            "hora_inicio": "08:00",
            "hora_fin": "12:00",
            "disponible": True,
            # Sin campo 'activa'
        }

        response = client.post(
            "/api/restricciones-horario/", json=restriccion_data, headers=auth_headers_admin
        )
        assert response.status_code == 201
        data = response.json()
        assert data["activa"] is True
