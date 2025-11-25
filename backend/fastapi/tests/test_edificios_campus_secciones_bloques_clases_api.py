import pytest
from fastapi.testclient import TestClient


class TestCampusEndpoints:
    """Tests para los endpoints de campus"""

    def test_create_campus_success(self, client: TestClient, auth_headers_admin):
        """Test crear campus exitoso"""
        campus_data = {"nombre": "Campus Central", "direccion": "Av. Universitaria 456"}

        response = client.post("/api/campus/", json=campus_data, headers=auth_headers_admin)

        assert response.status_code == 201
        data = response.json()
        assert data["nombre"] == "Campus Central"
        assert data["direccion"] == "Av. Universitaria 456"
        assert "id" in data

    def test_get_all_campus_success(self, client: TestClient, auth_headers_admin):
        """Test obtener todos los campus"""
        # Crear algunos campus
        campus_data = [
            {"nombre": "Campus Norte", "direccion": "Norte 123"},
            {"nombre": "Campus Sur", "direccion": "Sur 456"},
        ]

        for data in campus_data:
            client.post("/api/campus/", json=data, headers=auth_headers_admin)

        response = client.get("/api/campus/", headers=auth_headers_admin)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2


class TestEdificiosEndpoints:
    """Tests para los endpoints de edificios"""

    def test_create_edificio_success(self, client: TestClient, auth_headers_admin):
        """Test crear edificio exitoso"""
        # Primero crear un campus
        campus_data = {"nombre": "Campus Test", "direccion": "Test 123"}
        campus_response = client.post("/api/campus/", json=campus_data, headers=auth_headers_admin)
        campus_id = campus_response.json()["id"]

        edificio_data = {"nombre": "Edificio Principal", "pisos": 5, "campus_id": campus_id}

        response = client.post("/api/edificios/", json=edificio_data, headers=auth_headers_admin)

        assert response.status_code == 201
        data = response.json()
        assert data["nombre"] == "Edificio Principal"
        assert data["pisos"] == 5
        assert data["campus_id"] == campus_id
        assert "id" in data

    def test_create_edificio_unauthorized(self, client: TestClient):
        """Test crear edificio sin autenticación"""
        edificio_data = {"nombre": "Edificio Test", "pisos": 3, "campus_id": 1}

        response = client.post("/api/edificios/", json=edificio_data)
        assert response.status_code == 401

    def test_create_edificio_invalid_data(self, client: TestClient, auth_headers_admin):
        """Test crear edificio con datos inválidos"""
        edificio_data = {"nombre": "", "campus_id": 1}  # Nombre vacío

        response = client.post("/api/edificios/", json=edificio_data, headers=auth_headers_admin)
        assert response.status_code == 422

    def test_get_all_edificios_success(self, client: TestClient, auth_headers_admin):
        """Test obtener todos los edificios"""
        # Crear campus
        campus_data = {"nombre": "Campus Test", "direccion": "Test 123"}
        campus_response = client.post("/api/campus/", json=campus_data, headers=auth_headers_admin)
        campus_id = campus_response.json()["id"]

        # Crear algunos edificios
        edificios_data = [
            {"nombre": "Edificio A", "pisos": 3, "campus_id": campus_id},
            {"nombre": "Edificio B", "pisos": 4, "campus_id": campus_id},
        ]

        for edificio_data in edificios_data:
            client.post("/api/edificios/", json=edificio_data, headers=auth_headers_admin)

        response = client.get("/api/edificios/", headers=auth_headers_admin)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2

    def test_get_edificio_by_id_success(self, client: TestClient, auth_headers_admin):
        """Test obtener edificio por ID"""
        # Crear campus
        campus_data = {"nombre": "Campus Test", "direccion": "Test 123"}
        campus_response = client.post("/api/campus/", json=campus_data, headers=auth_headers_admin)
        campus_id = campus_response.json()["id"]

        # Crear edificio
        edificio_data = {"nombre": "Edificio Test ID", "pisos": 2, "campus_id": campus_id}

        create_response = client.post(
            "/api/edificios/", json=edificio_data, headers=auth_headers_admin
        )
        created_id = create_response.json()["id"]

        # Obtener por ID
        response = client.get(f"/api/edificios/{created_id}", headers=auth_headers_admin)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_id
        assert data["nombre"] == "Edificio Test ID"

    def test_get_edificio_by_id_not_found(self, client: TestClient, auth_headers_admin):
        """Test obtener edificio que no existe"""
        response = client.get("/api/edificios/99999", headers=auth_headers_admin)
        assert response.status_code == 404

    def test_update_edificio_success(self, client: TestClient, auth_headers_admin):
        """Test actualizar edificio"""
        # Crear campus
        campus_data = {"nombre": "Campus Test", "direccion": "Test 123"}
        campus_response = client.post("/api/campus/", json=campus_data, headers=auth_headers_admin)
        campus_id = campus_response.json()["id"]

        # Crear edificio
        edificio_data = {"nombre": "Edificio Original", "pisos": 3, "campus_id": campus_id}

        create_response = client.post(
            "/api/edificios/", json=edificio_data, headers=auth_headers_admin
        )
        created_id = create_response.json()["id"]

        # Actualizar
        update_data = {"nombre": "Edificio Actualizado", "pisos": 7, "campus_id": campus_id}

        response = client.put(
            f"/api/edificios/{created_id}", json=update_data, headers=auth_headers_admin
        )

        assert response.status_code == 200
        data = response.json()
        assert data["nombre"] == "Edificio Actualizado"
        assert data["pisos"] == 7

    def test_delete_edificio_success(self, client: TestClient, auth_headers_admin):
        """Test eliminar edificio"""
        # Crear campus
        campus_data = {"nombre": "Campus Test", "direccion": "Test 123"}
        campus_response = client.post("/api/campus/", json=campus_data, headers=auth_headers_admin)
        campus_id = campus_response.json()["id"]

        # Crear edificio
        edificio_data = {"nombre": "Edificio a Eliminar", "pisos": 2, "campus_id": campus_id}

        create_response = client.post(
            "/api/edificios/", json=edificio_data, headers=auth_headers_admin
        )
        created_id = create_response.json()["id"]

        # Eliminar
        response = client.delete(f"/api/edificios/{created_id}", headers=auth_headers_admin)
        # Puede retornar 200 o 204 dependiendo de la implementación
        assert response.status_code in [200, 204]

        # Verificar que no existe
        get_response = client.get(f"/api/edificios/{created_id}", headers=auth_headers_admin)
        assert get_response.status_code == 404

    def test_campus_edificios_relationship(self, client: TestClient, auth_headers_admin):
        """Test relación entre campus y edificios"""
        # Crear campus
        campus_data = {"nombre": "Campus Test", "direccion": "Test 123"}

        campus_response = client.post("/api/campus/", json=campus_data, headers=auth_headers_admin)
        campus_id = campus_response.json()["id"]

        # Crear edificio asociado al campus
        edificio_data = {"nombre": "Edificio Campus Test", "pisos": 4, "campus_id": campus_id}

        edificio_response = client.post(
            "/api/edificios/", json=edificio_data, headers=auth_headers_admin
        )
        assert edificio_response.status_code == 201

        edificio_data = edificio_response.json()
        assert edificio_data["campus_id"] == campus_id


class TestSeccionesEndpoints:
    """Tests para los endpoints de secciones"""

    def test_create_seccion_success(self, client: TestClient, auth_headers_admin):
        """Test crear sección exitosa"""
        # Crear asignatura primero
        asignatura_data = {
            "nombre": "Programación Avanzada",
            "codigo": "PROG-301",
            "horas_presenciales": 3,
            "horas_mixtas": 2,
            "horas_autonomas": 4,
            "cantidad_creditos": 4,
            "semestre": 5,
        }
        asignatura_response = client.post(
            "/api/asignaturas/", json=asignatura_data, headers=auth_headers_admin
        )
        asignatura_id = asignatura_response.json()["id"]

        seccion_data = {
            "codigo": "SEC-001",
            "anio": 2024,
            "semestre": 1,
            "cupos": 30,
            "asignatura_id": asignatura_id,
        }

        response = client.post("/api/secciones/", json=seccion_data, headers=auth_headers_admin)

        assert response.status_code == 201
        data = response.json()
        assert data["codigo"] == "SEC-001"
        assert data["anio"] == 2024
        assert data["semestre"] == 1
        assert data["cupos"] == 30
        assert "id" in data

    def test_get_secciones_by_docente(self, client: TestClient, auth_headers_docente):
        """Test obtener secciones por docente"""
        response = client.get("/api/secciones/", headers=auth_headers_docente)

        # Debería obtener solo las secciones del docente autenticado
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_create_seccion_capacity_validation(self, client: TestClient, auth_headers_admin):
        """Test validación de capacidad en secciones"""
        # Crear asignatura primero
        asignatura_data = {
            "nombre": "Test Asignatura",
            "codigo": "TEST-101",
            "horas_presenciales": 2,
            "horas_mixtas": 1,
            "horas_autonomas": 4,
            "cantidad_creditos": 3,
            "semestre": 2,
        }
        asignatura_response = client.post(
            "/api/asignaturas/", json=asignatura_data, headers=auth_headers_admin
        )
        asignatura_id = asignatura_response.json()["id"]

        seccion_data = {
            "codigo": "SEC-CAP",
            "anio": 2024,
            "semestre": 1,
            "cupos": -5,  # Capacidad inválida
            "asignatura_id": asignatura_id,
        }

        response = client.post("/api/secciones/", json=seccion_data, headers=auth_headers_admin)
        assert response.status_code == 422


class TestBloquesEndpoints:
    """Tests para los endpoints de bloques horarios"""

    def test_create_bloque_success(self, client: TestClient, auth_headers_admin):
        """Test crear bloque horario exitoso"""
        bloque_data = {"dia_semana": 1, "hora_inicio": "08:00:00", "hora_fin": "09:30:00"}  # Lunes

        response = client.post("/api/bloques/", json=bloque_data, headers=auth_headers_admin)

        assert response.status_code == 201
        data = response.json()
        assert data["dia_semana"] == 1
        assert "08:00" in data["hora_inicio"]
        assert "09:30" in data["hora_fin"]
        assert "id" in data

    def test_create_bloque_invalid_time(self, client: TestClient, auth_headers_admin):
        """Test crear bloque con horario inválido"""
        bloque_data = {
            "dia_semana": 1,
            "hora_inicio": "10:00:00",
            "hora_fin": "09:00:00",  # Hora fin antes que hora inicio
        }

        response = client.post("/api/bloques/", json=bloque_data, headers=auth_headers_admin)
        assert response.status_code == 422

    def test_get_bloques_success(self, client: TestClient, auth_headers_admin):
        """Test obtener bloques"""
        # Crear bloques
        bloques_data = [
            {"dia_semana": 1, "hora_inicio": "08:00:00", "hora_fin": "09:30:00"},
            {"dia_semana": 2, "hora_inicio": "10:00:00", "hora_fin": "11:30:00"},
        ]

        for bloque_data in bloques_data:
            client.post("/api/bloques/", json=bloque_data, headers=auth_headers_admin)

        response = client.get("/api/bloques/", headers=auth_headers_admin)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2


class TestClasesEndpoints:
    """Tests para los endpoints de clases"""

    def test_create_clase_success(self, client: TestClient, auth_headers_admin):
        """Test crear clase exitosa"""
        # Crear docente primero
        docente_data = {
            "nombres": "Carlos",
            "apellidos": "González",
            "email": "carlos.gonzalez.clase@universidad.edu",
            "password": "password123",
            "departamento": "Ingeniería",
        }
        docente_response = client.post(
            "/api/docentes/", json=docente_data, headers=auth_headers_admin
        )

        # Verificar si la creación fue exitosa y obtener el ID
        if docente_response.status_code != 201:
            # Si falla, puede ser porque el docente ya existe, usar ID existente
            # O buscar el docente por email
            docente_id = 2  # Usar un ID de docente existente del fixture
        else:
            docente_data_response = docente_response.json()
            # El endpoint de docentes puede retornar user_id en lugar de id
            docente_id = (
                docente_data_response.get("id") or docente_data_response.get("user_id") or 2
            )

        # Crear campus, edificio y sala
        campus_data = {"nombre": "Campus Test Clase", "direccion": "Test 123"}
        campus_response = client.post("/api/campus/", json=campus_data, headers=auth_headers_admin)
        campus_id = campus_response.json()["id"]

        edificio_data = {"nombre": "Edificio Test Clase", "pisos": 3, "campus_id": campus_id}
        edificio_response = client.post(
            "/api/edificios/", json=edificio_data, headers=auth_headers_admin
        )
        edificio_id = edificio_response.json()["id"]

        sala_data = {
            "codigo": "SALA-CLASE101",
            "capacidad": 30,
            "tipo": "aula",
            "disponible": True,
            "edificio_id": edificio_id,
        }
        sala_response = client.post("/api/salas/", json=sala_data, headers=auth_headers_admin)
        sala_id = sala_response.json()["id"]

        # Crear asignatura y sección
        asignatura_data = {
            "nombre": "Programación Clase",
            "codigo": "PROG-CLASE101",
            "horas_presenciales": 3,
            "horas_mixtas": 2,
            "horas_autonomas": 5,
            "cantidad_creditos": 4,
            "semestre": 3,
        }
        asignatura_response = client.post(
            "/api/asignaturas/", json=asignatura_data, headers=auth_headers_admin
        )
        asignatura_id = asignatura_response.json()["id"]

        seccion_data = {
            "codigo": "SEC-CLASE001",
            "anio": 2024,
            "semestre": 1,
            "cupos": 30,
            "asignatura_id": asignatura_id,
        }
        seccion_response = client.post(
            "/api/secciones/", json=seccion_data, headers=auth_headers_admin
        )
        seccion_id = seccion_response.json()["id"]

        # Crear bloque
        bloque_data = {"dia_semana": 1, "hora_inicio": "08:00:00", "hora_fin": "09:30:00"}
        bloque_response = client.post("/api/bloques/", json=bloque_data, headers=auth_headers_admin)
        bloque_id = bloque_response.json()["id"]

        # Crear clase
        clase_data = {
            "estado": "programada",
            "seccion_id": seccion_id,
            "docente_id": docente_id,
            "sala_id": sala_id,
            "bloque_id": bloque_id,
        }

        response = client.post("/api/clases/", json=clase_data, headers=auth_headers_admin)

        assert response.status_code == 201
        data = response.json()
        assert data["estado"] == "programada"
        assert "id" in data

    def test_get_clases_by_seccion(self, client: TestClient, auth_headers_docente):
        """Test obtener clases por sección"""
        response = client.get("/api/clases/?seccion_id=1", headers=auth_headers_docente)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_create_clase_invalid_estado(self, client: TestClient, auth_headers_admin):
        """Test crear clase con estado inválido"""
        clase_data = {
            "estado": "invalido",  # Estado no válido
            "seccion_id": 1,
            "docente_id": 1,
            "sala_id": 1,
            "bloque_id": 1,
        }

        response = client.post("/api/clases/", json=clase_data, headers=auth_headers_admin)
        assert response.status_code == 422
