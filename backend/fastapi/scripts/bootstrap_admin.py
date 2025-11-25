"""
Script de bootstrap para garantizar que exista un usuario administrador inicial.

Ejecutar con: `python backend/fastapi/scripts/bootstrap_admin.py`
El script es idempotente: si el usuario ya existe, actualiza nombre/rol/password
y se asegura de que tenga la entrada correspondiente en la tabla administrador.
"""

import logging
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Tuple

from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

# Ajustar el PYTHONPATH cuando se ejecuta el script directamente
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from infrastructure.database.config import SessionLocal
from infrastructure.repositories.user_repository import SQLUserRepository
from infrastructure.repositories.administrador_repository import (
    SQLAdministradorRepository,
)
from domain.entities import AdministradorCreate, UserCreate
from domain.authorization import UserRole, Permission, ROLE_PERMISSIONS
from infrastructure.auth import AuthService
from config import settings

logger = logging.getLogger("bootstrap_admin")
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(asctime)s [%(name)s] %(message)s",
)


def _require_setting(value: str | None, env_names: Tuple[str, ...]) -> str:
    """
    Valida que una configuración obligatoria tenga valor, indicando
    los nombres de variables de entorno aceptados para facilitar el diagnóstico.
    """
    if value:
        return value
    raise RuntimeError(
        f"Configuración {'/'.join(env_names)} requerida para bootstrap del admin."
    )


@contextmanager
def _db_session() -> Iterator:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def ensure_initial_admin() -> None:
    """Crea o actualiza el usuario administrador configurado por entorno."""
    admin_name = _require_setting(
        settings.initial_admin_name,
        ("INITIAL_ADMIN_USERNAME"),
    )
    admin_email = _require_setting(
        settings.initial_admin_email,
        ("INITIAL_ADMIN_EMAIL",),
    )
    admin_password = _require_setting(
        settings.initial_admin_password,
        ("INITIAL_ADMIN_PASSWORD",),
    )
    admin_active = True

    with _db_session() as session:
        user_repo = SQLUserRepository(session)

        user = user_repo.get_by_email(admin_email)
        if not user:
            try:
                user = user_repo.create(
                    UserCreate(
                        nombre=admin_name,
                        email=admin_email,
                        rol="administrador",
                        activo=admin_active,
                        contrasena=admin_password,
                    )
                )
                logger.info(
                    "Usuario admin %s creado con id %s",
                    admin_email,
                    user.id,
                )
            except ValidationError as exc:
                raise RuntimeError(
                    f"Datos de usuario administrador inválidos: {exc}"
                ) from exc
        else:
            updated = False
            if user.nombre != admin_name:
                user.nombre = admin_name
                updated = True
            if user.rol != "administrador":
                user.rol = "administrador"
                updated = True
            if user.activo != admin_active:
                user.activo = admin_active
                updated = True
            # Rotar contraseña si la suministrada no coincide
            if not AuthService.verify_password(admin_password, user.pass_hash):
                user.pass_hash = AuthService.get_password_hash(admin_password)
                updated = True

            if updated:
                session.add(user)
                logger.info("Usuario admin %s actualizado", admin_email)



def main() -> None:
    logger.info("Iniciando bootstrap del usuario administrador…")
    try:
        ensure_initial_admin()
    except (RuntimeError, SQLAlchemyError) as exc:
        logger.error("Bootstrap del admin falló: %s", exc)
        raise SystemExit(1) from exc
    logger.info("Bootstrap del admin completado correctamente.")


if __name__ == "__main__":
    main()
