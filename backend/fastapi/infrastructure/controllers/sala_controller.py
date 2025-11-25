from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from application.use_cases.sala_use_cases import SalaUseCases
from domain.authorization import Permission
from domain.entities import Sala, User  # Response models
from domain.schemas import SalaSecureCreate, SalaSecurePatch  # ✅ SCHEMAS SEGUROS
from infrastructure.database.config import get_db
from infrastructure.dependencies import require_permission
from infrastructure.repositories.edificio_repository import SQLEdificioRepository
from infrastructure.repositories.sala_repository import SalaRepository

router = APIRouter()


def get_sala_use_case(db: Session = Depends(get_db)) -> SalaUseCases:
    sala_repository = SalaRepository(db)
    edificio_repository = SQLEdificioRepository(db)
    return SalaUseCases(sala_repository, edificio_repository)


@router.post(
    "/",
    response_model=Sala,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nueva sala",
    tags=["salas"],
)
async def create_sala(
    sala_data: SalaSecureCreate,  # ✅ SCHEMA SEGURO
    sala_use_case: SalaUseCases = Depends(get_sala_use_case),
    current_user: User = Depends(require_permission(Permission.SALA_WRITE)),
):
    """Crear una nueva sala con validaciones anti-inyección (requiere permiso SALA:WRITE - solo administradores)"""
    try:
        sala = sala_use_case.create(sala_data)
        return sala
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor"
        )


@router.get("/", response_model=List[Sala])
async def get_all_salas(
    skip: int = 0,
    limit: int = 100,
    sala_use_case: SalaUseCases = Depends(get_sala_use_case),
    current_user=Depends(require_permission(Permission.SALA_READ)),  # ✅ MIGRADO
):
    """Obtener todas las salas (requiere permiso SALA:READ)"""
    try:
        salas = sala_use_case.get_all(skip=skip, limit=limit)
        return salas
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor"
        )


@router.get("/{sala_id}", response_model=Sala)
async def get_sala_by_id(
    sala_id: int,
    sala_use_case: SalaUseCases = Depends(get_sala_use_case),
    current_user=Depends(require_permission(Permission.SALA_READ)),  # ✅ MIGRADO
):
    """Obtener sala por ID (requiere permiso SALA:READ)"""
    try:
        sala = sala_use_case.get_by_id(sala_id)
        return sala
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor"
        )


@router.get("/codigo/{codigo}", response_model=Sala)
async def get_sala_by_codigo(
    codigo: str,
    sala_use_case: SalaUseCases = Depends(get_sala_use_case),
    current_user=Depends(require_permission(Permission.SALA_READ)),  # ✅ MIGRADO
):
    """Obtener sala por código (requiere permiso SALA:READ)"""
    try:
        sala = sala_use_case.get_by_codigo(codigo)
        return sala
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor"
        )


# Esta ruta debe estar en edificio_controller, pero la dejamos aquí por compatibilidad
@router.get("/edificio/{edificio_id}", response_model=List[Sala])
async def get_salas_by_edificio(
    edificio_id: int,
    sala_use_case: SalaUseCases = Depends(get_sala_use_case),
    current_user=Depends(require_permission(Permission.SALA_READ)),  # ✅ MIGRADO
):
    """Obtener salas por edificio (requiere permiso SALA:READ)"""
    try:
        salas = sala_use_case.get_by_edificio(edificio_id)
        return salas
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor"
        )


@router.put(
    "/{sala_id}",
    response_model=Sala,
    status_code=status.HTTP_200_OK,
    summary="Actualizar sala completa",
    tags=["salas"],
)
async def update_sala_complete(
    sala_id: int,
    sala_data: SalaSecurePatch,  # ✅ SCHEMA SEGURO PATCH
    sala_use_case: SalaUseCases = Depends(get_sala_use_case),
    current_user=Depends(require_permission(Permission.SALA_WRITE)),
):
    """Actualizar una sala completamente con validaciones anti-inyección (requiere permiso SALA:WRITE)"""
    try:
        sala = sala_use_case.update(sala_id, sala_data)
        return sala
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor"
        )


@router.patch(
    "/{sala_id}",
    response_model=Sala,
    status_code=status.HTTP_200_OK,
    summary="Actualizar campos específicos de sala",
    tags=["salas"],
)
async def update_sala_partial(
    sala_id: int,
    sala_data: SalaSecurePatch,  # ✅ SCHEMA SEGURO PATCH
    sala_use_case: SalaUseCases = Depends(get_sala_use_case),
    current_user=Depends(require_permission(Permission.SALA_WRITE)),
):
    """Actualizar parcialmente una sala con validaciones anti-inyección (requiere permiso SALA:WRITE)"""
    try:
        sala = sala_use_case.update(sala_id, sala_data)
        return sala
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor"
        )


@router.delete("/{sala_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sala(
    sala_id: int,
    sala_use_case: SalaUseCases = Depends(get_sala_use_case),
    current_user=Depends(require_permission(Permission.SALA_DELETE)),  # ✅ MIGRADO
):
    """Eliminar una sala (requiere permiso SALA:DELETE)"""
    try:
        sala_use_case.delete(sala_id)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor"
        )


@router.get("/buscar/tipo/{tipo}", response_model=List[Sala])
async def get_salas_by_tipo(
    tipo: str,
    sala_use_case: SalaUseCases = Depends(get_sala_use_case),
    current_user=Depends(require_permission(Permission.SALA_READ)),  # ✅ MIGRADO
):
    """Obtener salas por tipo (requiere permiso SALA:READ)"""
    try:
        salas = sala_use_case.get_by_tipo(tipo)
        return salas
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor"
        )


@router.get("/buscar/capacidad", response_model=List[Sala])
async def get_salas_by_capacidad(
    capacidad_min: int = None,
    capacidad_max: int = None,
    sala_use_case: SalaUseCases = Depends(get_sala_use_case),
    current_user=Depends(require_permission(Permission.SALA_READ)),  # ✅ MIGRADO
):
    """Obtener salas por rango de capacidad (requiere permiso SALA:READ)"""
    try:
        salas = sala_use_case.get_by_capacidad(capacidad_min, capacidad_max)
        return salas
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor"
        )


@router.get("/disponibles", response_model=List[Sala])
async def get_salas_disponibles(
    bloque_id: int = None,
    sala_use_case: SalaUseCases = Depends(get_sala_use_case),
    current_user=Depends(require_permission(Permission.SALA_READ)),  # ✅ MIGRADO
):
    """Obtener salas disponibles (requiere permiso SALA:READ)"""
    try:
        salas = sala_use_case.get_salas_disponibles(bloque_id)
        return salas
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor"
        )
