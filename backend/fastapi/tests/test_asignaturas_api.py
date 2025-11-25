import pytest
from fastapi.testclient import TestClient


DEFAULT_ASIGNATURA_PAYLOAD = {
    "codigo": "INFO1120",
    "nombre": "Programación I",
    "horas_presenciales": 3,
    "horas_mixtas": 2,
    "horas_autonomas": 5,
    "cantidad_creditos": 6,
    "semestre": 1,
}


def build_asignatura_payload(**overrides):
    payload = DEFAULT_ASIGNATURA_PAYLOAD.copy()
    payload.update(overrides)
    return payload


class TestAsignaturasEndpoints:
    """Tests para los endpoints de asignaturas"""

    def test_create_asignatura_success_admin(self, client: TestClient, auth_headers_admin):
        """Test creación exitosa de asignatura por administrador"""
        asignatura_data = build_asignatura_payload(
            codigo="ING101",
            nombre="Introducción a la Ingeniería",
            cantidad_creditos=3,
        )

        response = client.post(
            "/api/asignaturas/", json=asignatura_data, headers=auth_headers_admin
        )

        assert response.status_code == 201
        data = response.json()
        assert data["codigo"] == "ING101"
        assert data["nombre"] == "Introducción A La Ingeniería"  # El validador capitaliza
        assert data["cantidad_creditos"] == 3
        assert "id" in data

    def test_create_asignatura_unauthorized_docente(self, client: TestClient, auth_headers_docente):
        """Test que docentes no pueden crear asignaturas"""
        asignatura_data = build_asignatura_payload(
            codigo="MAT101", nombre="Matemáticas Básicas", cantidad_creditos=4
        )

        response = client.post(
            "/api/asignaturas/", json=asignatura_data, headers=auth_headers_docente
        )
        assert response.status_code == 403

    def test_create_asignatura_unauthorized(self, client: TestClient):
        """Test creación de asignatura sin autenticación"""
        asignatura_data = build_asignatura_payload(
            codigo="FIS101", nombre="Física Básica", cantidad_creditos=4
        )

        response = client.post("/api/asignaturas/", json=asignatura_data)
        assert response.status_code == 401

    def test_get_all_asignaturas_success(self, client: TestClient, auth_headers_admin):
        """Test obtener todas las asignaturas"""
        # Crear una asignatura primero
        asignatura_data = build_asignatura_payload(
            codigo="QUI101", nombre="Química General", cantidad_creditos=4
        )
        client.post("/api/asignaturas/", json=asignatura_data, headers=auth_headers_admin)

        # Obtener todas las asignaturas
        response = client.get("/api/asignaturas/", headers=auth_headers_admin)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_asignatura_by_id_success(self, client: TestClient, auth_headers_admin):
        """Test obtener asignatura específica por ID"""
        # Crear una asignatura primero
        asignatura_data = build_asignatura_payload(
            codigo="BIO101", nombre="Biología General", cantidad_creditos=3
        )
        create_response = client.post(
            "/api/asignaturas/", json=asignatura_data, headers=auth_headers_admin
        )
        created_id = create_response.json()["id"]

        # Obtener por ID
        response = client.get(f"/api/asignaturas/{created_id}", headers=auth_headers_admin)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_id
        assert data["codigo"] == "BIO101"

    def test_get_asignatura_by_id_not_found(self, client: TestClient, auth_headers_admin):
        """Test obtener asignatura que no existe"""
        response = client.get("/api/asignaturas/99999", headers=auth_headers_admin)
        assert response.status_code == 404

    def test_update_asignatura_put_success(self, client: TestClient, auth_headers_admin):
        """Test actualización completa de asignatura con PUT"""
        # Crear una asignatura primero
        asignatura_data = build_asignatura_payload(
            codigo="ART101",
            nombre="Arte Original",
            cantidad_creditos=2,
            horas_presenciales=2,
            horas_mixtas=1,
            horas_autonomas=3,
            semestre=2,
        )
        create_response = client.post(
            "/api/asignaturas/", json=asignatura_data, headers=auth_headers_admin
        )
        created_id = create_response.json()["id"]

        # Actualizar con PUT
        updated_data = build_asignatura_payload(
            codigo="ART101",
            nombre="Arte Actualizado",
            cantidad_creditos=3,
            horas_presenciales=4,
            horas_mixtas=2,
            horas_autonomas=5,
            semestre=3,
        )
        response = client.put(
            f"/api/asignaturas/{created_id}", json=updated_data, headers=auth_headers_admin
        )

        assert response.status_code == 200
        data = response.json()
        assert data["nombre"] == "Arte Actualizado"
        assert data["cantidad_creditos"] == 3
        assert data["horas_presenciales"] == 4

    def test_update_asignatura_patch_success(self, client: TestClient, auth_headers_admin):
        """Test actualización parcial de asignatura con PATCH"""
        # Crear una asignatura primero
        asignatura_data = build_asignatura_payload(
            codigo="LIT101", nombre="Literatura Clásica", cantidad_creditos=3
        )
        create_response = client.post(
            "/api/asignaturas/", json=asignatura_data, headers=auth_headers_admin
        )
        created_id = create_response.json()["id"]

        # Actualizar solo algunos campos con PATCH
        patch_data = {"cantidad_creditos": 4, "horas_autonomas": 6}
        response = client.patch(
            f"/api/asignaturas/{created_id}", json=patch_data, headers=auth_headers_admin
        )

        assert response.status_code == 200
        data = response.json()
        assert data["cantidad_creditos"] == 4
        assert data["horas_autonomas"] == 6
        assert data["codigo"] == "LIT101"  # Debe mantener el valor original

    def test_delete_asignatura_success(self, client: TestClient, auth_headers_admin):
        """Test eliminación exitosa de asignatura"""
        # Crear una asignatura primero
        asignatura_data = build_asignatura_payload(
            codigo="DEL101", nombre="Para Eliminar", cantidad_creditos=1
        )
        create_response = client.post(
            "/api/asignaturas/", json=asignatura_data, headers=auth_headers_admin
        )
        created_id = create_response.json()["id"]

        # Eliminar
        response = client.delete(f"/api/asignaturas/{created_id}", headers=auth_headers_admin)

        assert response.status_code == 204

        # Verificar que ya no existe
        get_response = client.get(f"/api/asignaturas/{created_id}", headers=auth_headers_admin)
        assert get_response.status_code == 404

    def test_delete_asignatura_not_found(self, client: TestClient, auth_headers_admin):
        """Test eliminación de asignatura que no existe"""
        response = client.delete("/api/asignaturas/99999", headers=auth_headers_admin)
        assert response.status_code == 404

    def test_asignaturas_read_access_docente(self, client: TestClient, auth_headers_docente):
        """Test que docentes pueden leer asignaturas"""
        response = client.get("/api/asignaturas/", headers=auth_headers_docente)
        assert response.status_code == 200

    def test_asignaturas_read_access_estudiante(self, client: TestClient, auth_headers_estudiante):
        """Test que estudiantes pueden leer asignaturas"""
        response = client.get("/api/asignaturas/", headers=auth_headers_estudiante)
        assert response.status_code == 200


class TestAsignaturasValidation:
    """Tests para validación de datos de asignaturas"""

    def test_codigo_validation_format(self, client: TestClient, auth_headers_admin):
        """Test validación de formato de código"""
        codigos_validos = ["ING101", "MAT-202", "FIS300", "CS-401"]
        nombres_validos = ["Ingenieria Uno", "Matematicas Dos", "Fisica Tres", "Ciencias Cuatro"]

        for i, codigo in enumerate(codigos_validos):
            asignatura_data = build_asignatura_payload(
                codigo=codigo, nombre=nombres_validos[i], semestre=i + 1
            )

            response = client.post(
                "/api/asignaturas/", json=asignatura_data, headers=auth_headers_admin
            )
            if response.status_code != 201:
                print(f"Error para {codigo}: {response.json()}")
            assert response.status_code == 201, f"Falló para código: {codigo}"
            # El validador convierte a mayúsculas
            assert response.json()["codigo"] == codigo.upper()

    def test_codigo_validation_invalid(self, client: TestClient, auth_headers_admin):
        """Test códigos inválidos"""
        # Códigos que realmente son inválidos según el validador
        # El validador acepta letras, números y guiones, pero no espacios ni caracteres especiales
        codigos_invalidos = ["MAT 202", "FIS@300", ""]

        for codigo in codigos_invalidos:
            asignatura_data = build_asignatura_payload(codigo=codigo, nombre="Test Asignatura")

            response = client.post(
                "/api/asignaturas/", json=asignatura_data, headers=auth_headers_admin
            )
            assert (
                response.status_code == 422
            ), f"Debería fallar para código: {codigo}, pero obtuvo {response.status_code}"

    def test_cantidad_creditos_validation_range(self, client: TestClient, auth_headers_admin):
        """Test validación de rango de cantidad de créditos"""
        # Créditos válidos (1-30)
        nombres_creditos = ["Uno", "Cinco", "Diez", "Quince", "Veinte"]
        for idx, creditos in enumerate([1, 5, 10, 15, 20]):
            asignatura_data = build_asignatura_payload(
                codigo=f"TEST{creditos}",
                nombre=f"Test {nombres_creditos[idx]} creditos",
                cantidad_creditos=creditos,
            )

            response = client.post(
                "/api/asignaturas/", json=asignatura_data, headers=auth_headers_admin
            )
            assert response.status_code == 201, f"Falló para créditos: {creditos}"

    def test_cantidad_creditos_validation_invalid(self, client: TestClient, auth_headers_admin):
        """Test cantidad de créditos inválida"""
        creditos_invalidos = [0, -1, 31, 100]

        for creditos in creditos_invalidos:
            asignatura_data = build_asignatura_payload(
                codigo=f"FAIL{abs(creditos)}",
                nombre="Test Asignatura",
                cantidad_creditos=creditos,
            )

            response = client.post(
                "/api/asignaturas/", json=asignatura_data, headers=auth_headers_admin
            )
            assert response.status_code == 422, f"Debería fallar para créditos: {creditos}"

    def test_nombre_validation(self, client: TestClient, auth_headers_admin):
        """Test validación de nombre"""
        # Nombre válido
        asignatura_data = build_asignatura_payload(
            codigo="VALID1", nombre="Nombre Válido de Asignatura"
        )
        response = client.post(
            "/api/asignaturas/", json=asignatura_data, headers=auth_headers_admin
        )
        assert response.status_code == 201

        # Nombre vacío (inválido)
        asignatura_data_invalid = build_asignatura_payload(codigo="INVALID1", nombre="")
        response = client.post(
            "/api/asignaturas/", json=asignatura_data_invalid, headers=auth_headers_admin
        )
        assert response.status_code == 422

    def test_codigo_unique_constraint(self, client: TestClient, auth_headers_admin):
        """Test que no se pueden crear asignaturas con códigos duplicados"""
        # Crear primera asignatura
        asignatura_data = build_asignatura_payload(
            codigo="UNIQUE1", nombre="Primera Asignatura", cantidad_creditos=3
        )
        response1 = client.post(
            "/api/asignaturas/", json=asignatura_data, headers=auth_headers_admin
        )
        assert response1.status_code == 201

        # Intentar crear segunda con mismo código
        asignatura_data_duplicate = build_asignatura_payload(
            codigo="UNIQUE1", nombre="Segunda Asignatura", cantidad_creditos=4
        )
        response2 = client.post(
            "/api/asignaturas/", json=asignatura_data_duplicate, headers=auth_headers_admin
        )
        assert response2.status_code == 400  # Conflicto por duplicado


class TestAsignaturasSearch:
    """Tests para funcionalidades de búsqueda de asignaturas"""

    def test_search_by_codigo(self, client: TestClient, auth_headers_admin):
        """Test búsqueda de asignatura por código"""
        # Crear varias asignaturas
        asignaturas = [
            build_asignatura_payload(codigo="SEARCH1", nombre="Busqueda Uno"),
            build_asignatura_payload(codigo="SEARCH2", nombre="Busqueda Dos"),
            build_asignatura_payload(codigo="OTHER1", nombre="Otra Uno"),
        ]

        for asignatura in asignaturas:
            client.post("/api/asignaturas/", json=asignatura, headers=auth_headers_admin)

        # Si existe endpoint de búsqueda por código (por implementar)
        # response = client.get("/api/asignaturas/search?codigo=SEARCH", headers=auth_headers_admin)
        # assert response.status_code == 200
        # data = response.json()
        # assert len(data) == 2  # Debería encontrar SEARCH1 y SEARCH2

    def test_filter_by_cantidad_creditos(self, client: TestClient, auth_headers_admin):
        """Test filtrado de asignaturas por cantidad de créditos"""
        # Crear asignaturas con diferentes créditos
        asignaturas = [
            build_asignatura_payload(
                codigo="CRED3A", nombre="Tres Creditos A", cantidad_creditos=3
            ),
            build_asignatura_payload(
                codigo="CRED3B", nombre="Tres Creditos B", cantidad_creditos=3
            ),
            build_asignatura_payload(
                codigo="CRED4", nombre="Cuatro Creditos", cantidad_creditos=4
            ),
        ]

        for asignatura in asignaturas:
            client.post("/api/asignaturas/", json=asignatura, headers=auth_headers_admin)

        # Si existe endpoint de filtrado por créditos (por implementar)
        # response = client.get("/api/asignaturas?creditos=3", headers=auth_headers_admin)
        # assert response.status_code == 200
        # data = response.json()
        # assert len(data) == 2  # Debería encontrar las dos asignaturas de 3 créditos
