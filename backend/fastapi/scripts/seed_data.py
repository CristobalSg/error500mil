"""
Script de seed para cargar datos base (asignaturas, docentes, secciones) desde CSV.

Uso:
    python backend/fastapi/scripts/seed_data.py \
        --asignaturas backend/fastapi/data/asignaturas.csv \
        --docentes backend/fastapi/data/docentes.csv \
        --secciones backend/fastapi/data/secciones.csv \
        --seccion-asignatura-id 1 \
        --seccion-semestre 1

Notas:
- El password de los docentes se toma de la variable de entorno DOCENTE_SEED_PASSWORD
  o usa el valor por defecto "SeedDocente#2025".
- Para secciones, se requiere un asignatura_id objetivo (por defecto 1) y un semestre
  (por defecto 1) porque el CSV de secciones no incluye el id de asignatura ni semestre.
"""

import argparse
import csv
import logging
import os
from pathlib import Path
from typing import Tuple

from pydantic import ValidationError

from config import settings
from domain.entities import AsignaturaCreate, DocenteCreate, UserCreate, UserUpdate, SeccionCreate
from infrastructure.auth import AuthService
from infrastructure.database.config import SessionLocal
from infrastructure.repositories.asignatura_repository import AsignaturaRepository
from infrastructure.repositories.docente_repository import DocenteRepository
from infrastructure.repositories.seccion_repository import SeccionRepository
from infrastructure.repositories.user_repository import SQLUserRepository

logger = logging.getLogger("seed_data")
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(asctime)s [%(name)s] %(message)s",
)


def _open_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def load_asignaturas(session, path: Path) -> Tuple[int, int]:
    created = updated = 0
    repo = AsignaturaRepository(session)
    with path.open(encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            payload = AsignaturaCreate(
                codigo=row["codigo"].strip(),
                nombre=row["nombre"].strip(),
                horas_presenciales=int(row["horas_presenciales"]),
                horas_mixtas=int(row["horas_mixtas"]),
                horas_autonomas=int(row["horas_autonomas"]),
                cantidad_creditos=int(row["cantidad_creditos"]),
                semestre=int(row["semestre"]),
            )
            existing = repo.get_by_codigo(payload.codigo)
            if existing:
                repo.update(
                    existing.id,
                    {
                        "nombre": payload.nombre,
                        "horas_presenciales": payload.horas_presenciales,
                        "horas_mixtas": payload.horas_mixtas,
                        "horas_autonomas": payload.horas_autonomas,
                        "cantidad_creditos": payload.cantidad_creditos,
                        "semestre": payload.semestre,
                    },
                )
                updated += 1
            else:
                repo.create(payload)
                created += 1
    return created, updated


def load_docentes(session, path: Path, default_password: str) -> Tuple[int, int]:
    created = updated = 0
    user_repo = SQLUserRepository(session)
    docente_repo = DocenteRepository(session)

    with path.open(encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            email = row["email"].strip()
            nombre = row["nombre"].strip()
            activo = str(row.get("activo", "true")).lower() in ("true", "1", "yes", "si")

            user = user_repo.get_by_email(email, include_deleted=True)
            if not user:
                try:
                    user = user_repo.create(
                        UserCreate(
                            nombre=nombre,
                            email=email,
                            rol="docente",
                            activo=activo,
                            contrasena=default_password,
                        )
                    )
                    created += 1
                except ValidationError as exc:
                    logger.error("Error creando docente %s: %s", email, exc)
                    continue
            else:
                needs_update = False
                update_payload = UserUpdate()
                if user.nombre != nombre:
                    update_payload.nombre = nombre
                    needs_update = True
                if user.rol != "docente":
                    update_payload.rol = "docente"
                    needs_update = True
                if user.activo != activo:
                    update_payload.activo = activo
                    needs_update = True
                if needs_update:
                    user_repo.update(user.id, update_payload)
                # Rotar contraseña si no coincide con el hash actual
                if not AuthService.verify_password(default_password, user.pass_hash):
                    user.pass_hash = AuthService.get_password_hash(default_password)
                    session.add(user)
                    session.commit()
                updated += 1

            # Asegurar registro en tabla docente
            if not docente_repo.get_by_user_id(user.id):
                docente_repo.create(DocenteCreate(user_id=user.id, departamento=None))
    return created, updated


def _infer_tipo_grupo(nombre: str) -> str:
    lower = nombre.lower()
    if "mención" in lower or "mencion" in lower:
        return "mencion"
    if "base" in lower:
        return "base"
    return "seccion"


def load_secciones(
    session,
    path: Path,
    asignatura_id: int,
    semestre: int,
) -> Tuple[int, int]:
    created = updated = 0
    repo = SeccionRepository(session)
    with path.open(encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            codigo = row["group_name"].strip()
            anio_academico = int(row["year_name"])
            numero_estudiantes = int(row["group_students"])
            tipo_grupo = _infer_tipo_grupo(codigo)

            payload = SeccionCreate(
                codigo=codigo,
                anio_academico=anio_academico,
                semestre=semestre,
                asignatura_id=asignatura_id,
                tipo_grupo=tipo_grupo,
                numero_estudiantes=numero_estudiantes,
                cupos=numero_estudiantes,
            )

            existing = repo.get_by_codigo(payload.codigo)
            if existing:
                repo.update(
                    existing.id,
                    {
                        "anio_academico": payload.anio_academico,
                        "semestre": payload.semestre,
                        "asignatura_id": payload.asignatura_id,
                        "tipo_grupo": payload.tipo_grupo,
                        "numero_estudiantes": payload.numero_estudiantes,
                        "cupos": payload.cupos,
                    },
                )
                updated += 1
            else:
                repo.create(payload)
                created += 1
    return created, updated


def parse_args():
    parser = argparse.ArgumentParser(description="Seed inicial de datos desde CSV.")
    parser.add_argument("--asignaturas", type=Path, default=Path("backend/fastapi/data/asignaturas.csv"))
    parser.add_argument("--docentes", type=Path, default=Path("backend/fastapi/data/docentes.csv"))
    parser.add_argument("--secciones", type=Path, default=Path("backend/fastapi/data/secciones.csv"))
    parser.add_argument(
        "--seccion-asignatura-id",
        type=int,
        default=1,
        help="ID de asignatura a usar para todas las secciones importadas (el CSV no lo incluye).",
    )
    parser.add_argument(
        "--seccion-semestre",
        type=int,
        default=1,
        choices=[1, 2],
        help="Semestre a asignar a las secciones importadas.",
    )
    parser.add_argument(
        "--docente-password",
        type=str,
        default=os.getenv("DOCENTE_SEED_PASSWORD", "SeedDocente#2025"),
        help="Password a asignar a los docentes importados.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    logger.info("Iniciando seed de datos...")
    # Validación mínima de password para cumplir política
    if len(args.docente_password) < 12:
        raise SystemExit("El password de docentes debe tener al menos 12 caracteres (política interna).")

    with next(_open_session()) as session:
        a_created, a_updated = load_asignaturas(session, args.asignaturas)
        d_created, d_updated = load_docentes(session, args.docentes, args.docente_password)
        s_created, s_updated = load_secciones(
            session,
            args.secciones,
            asignatura_id=args.seccion_asignatura_id,
            semestre=args.seccion_semestre,
        )

    logger.info(
        "Seed completado. Asignaturas created=%s updated=%s | Docentes created=%s updated=%s | Secciones created=%s updated=%s",
        a_created,
        a_updated,
        d_created,
        d_updated,
        s_created,
        s_updated,
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        logger.error("Seed falló: %s", exc)
        raise SystemExit(1) from exc
