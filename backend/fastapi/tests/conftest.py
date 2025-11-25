import os
import sys
from pathlib import Path

# Configurar variables de entorno para testing
os.environ.setdefault("NODE_ENV", "testing")
os.environ.setdefault("DB_URL", "sqlite:///:memory:")
os.environ.setdefault("JWT_SECRET_KEY", "test_secret_key_for_testing")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("JWT_EXPIRE_MINUTES", "30")

# Añadir el directorio raíz del proyecto al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
from fastapi.testclient import TestClient

# Importar main ANTES de modificar los middlewares
from main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from domain.entities import UserCreate
from domain.models import Base
from infrastructure.database.config import get_db

# Modificar límites de rate limiting para tests
# Esto debe hacerse después de importar app pero antes de crear el cliente
for middleware in app.user_middleware:
    if hasattr(middleware, "kwargs"):
        # Aumentar los límites para testing
        if "requests_limit" in middleware.kwargs:
            middleware.kwargs["requests_limit"] = 10000
        if "auth_requests_limit" in middleware.kwargs:
            middleware.kwargs["auth_requests_limit"] = 20000

# Base de datos en memoria
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def db_engine():
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # Importar todos los modelos para asegurar que estén registrados
    from domain.models import (
        Administrador,
        Asignatura,
        Base,
        Bloque,
        Campus,
        Clase,
        Docente,
        Edificio,
        Estudiante,
        Restriccion,
        RestriccionHorario,
        Sala,
        Seccion,
        User,
    )

    # Crear todas las tablas con la estructura actual
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    # Asegurar que todas las tablas estén creadas
    from domain.models import Base

    Base.metadata.create_all(bind=db_session.bind)

    # Crear un nuevo TestClient que inicializará nuevas instancias de middlewares
    test_client = TestClient(app)

    yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def admin_user_data():
    return UserCreate(
        nombre="Admin Test",
        email="admin@test.com",
        contrasena="AdminT3st!2024#Secure",
        rol="administrador",
    )


@pytest.fixture
def docente_user_data():
    return UserCreate(
        nombre="Docente Test",
        email="docente@test.com",
        contrasena="Doc3nteT3st!2024#Strong",
        rol="docente",
    )


@pytest.fixture
def estudiante_user_data():
    return UserCreate(
        nombre="Estudiante Test",
        email="estudiante@test.com",
        contrasena="Estud1ant3T3st!2024#Pass",
        rol="estudiante",
    )


@pytest.fixture
def admin_token(client, db_session, admin_user_data):
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
    return login_response.json()["access_token"]


@pytest.fixture
def docente_token(client, db_session, docente_user_data):
    # Crear usuario directamente en la base de datos
    from domain.models import Docente, User
    from infrastructure.auth import AuthService

    db_user = User(
        nombre=docente_user_data.nombre,
        email=docente_user_data.email,
        pass_hash=AuthService.get_password_hash(docente_user_data.contrasena),
        rol=docente_user_data.rol,
    )
    db_session.add(db_user)
    db_session.commit()
    db_session.refresh(db_user)

    # Crear registro de docente
    docente = Docente(user_id=db_user.id)
    db_session.add(docente)
    db_session.commit()

    # Hacer login
    login_response = client.post(
        "/api/auth/login",
        json={"email": docente_user_data.email, "contrasena": docente_user_data.contrasena},
    )
    return login_response.json()["access_token"]


@pytest.fixture
def estudiante_token(client, db_session, estudiante_user_data):
    # Crear usuario directamente en la base de datos
    from domain.models import Estudiante, User
    from infrastructure.auth import AuthService

    db_user = User(
        nombre=estudiante_user_data.nombre,
        email=estudiante_user_data.email,
        pass_hash=AuthService.get_password_hash(estudiante_user_data.contrasena),
        rol=estudiante_user_data.rol,
    )
    db_session.add(db_user)
    db_session.commit()
    db_session.refresh(db_user)

    # Crear registro de estudiante
    estudiante = Estudiante(user_id=db_user.id)
    db_session.add(estudiante)
    db_session.commit()

    # Hacer login
    login_response = client.post(
        "/api/auth/login",
        json={"email": estudiante_user_data.email, "contrasena": estudiante_user_data.contrasena},
    )
    return login_response.json()["access_token"]


@pytest.fixture
def auth_headers_admin(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def auth_headers_docente(docente_token):
    return {"Authorization": f"Bearer {docente_token}"}


@pytest.fixture
def auth_headers_estudiante(estudiante_token):
    return {"Authorization": f"Bearer {estudiante_token}"}


@pytest.fixture
def docente_completo(client, db_session, auth_headers_admin):
    """Crea un usuario docente y su registro en la tabla Docente"""
    from domain.models import Docente, User
    from infrastructure.auth import AuthService

    # Crear usuario docente directamente en la base de datos
    password = "D0c3nt3C0mpl3t0!2024#Secure"
    db_user = User(
        nombre="Carlos Ramírez Docente",
        email="docente.completo@test.com",
        pass_hash=AuthService.get_password_hash(password),
        rol="docente",
    )
    db_session.add(db_user)
    db_session.commit()
    db_session.refresh(db_user)

    # Crear el perfil de docente asociado al usuario
    docente = Docente(user_id=db_user.id, departamento="Ingeniería")
    db_session.add(docente)
    db_session.commit()
    db_session.refresh(docente)

    # Retornar tanto el user_id como el id del docente
    return {
        "user_id": db_user.id,
        "docente_id": docente.id,
        "email": db_user.email,
        "password": password,
    }


@pytest.fixture
def auth_headers_docente_completo(client, docente_completo):
    """Headers de autenticación para el docente completo"""
    login_response = client.post(
        "/api/auth/login",
        json={"email": docente_completo["email"], "contrasena": docente_completo["password"]},
    )
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_user(client, db_session, auth_headers_admin, admin_user_data):
    """Usuario administrador creado y registrado en la base de datos"""
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

    return {"id": db_user.id, "nombre": db_user.nombre, "email": db_user.email, "rol": db_user.rol}


@pytest.fixture
def campus_completo(client, auth_headers_admin):
    """Crea un campus completo para usar en tests"""
    campus_data = {"codigo": "CAMPUS-TEST", "nombre": "Campus Test", "direccion": "Calle Test 123"}

    response = client.post("/api/campus/", json=campus_data, headers=auth_headers_admin)
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def edificio_completo(client, auth_headers_admin, campus_completo):
    """Crea un edificio completo para usar en tests"""
    edificio_data = {
        "codigo": "EDIF-TEST",
        "nombre": "Edificio Test",
        "campus_id": campus_completo["id"],
    }

    response = client.post("/api/edificios/", json=edificio_data, headers=auth_headers_admin)
    assert response.status_code == 201
    return response.json()
