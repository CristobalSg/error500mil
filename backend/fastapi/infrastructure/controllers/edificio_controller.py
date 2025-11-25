from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from application.use_cases.edificio_use_cases import EdificioUseCase
from domain.authorization import Permission
from domain.entities import Edificio  # Response models
from domain.schemas import EdificioSecureCreate, EdificioSecurePatch  # ✅ SCHEMAS SEGUROS
from infrastructure.database.config import get_db
from infrastructure.dependencies import require_permission
from infrastructure.repositories.campus_repository import SQLCampusRepository
from infrastructure.repositories.edificio_repository import SQLEdificioRepository

router = APIRouter()


def get_edificio_use_case(db: Session = Depends(get_db)) -> EdificioUseCase:
    edificio_repository = SQLEdificioRepository(db)
    campus_repository = SQLCampusRepository(db)
    return EdificioUseCase(edificio_repository, campus_repository)


@router.post("/", response_model=Edificio, status_code=status.HTTP_201_CREATED)
async def create_edificio(
    edificio_data: EdificioSecureCreate,  # ✅ SCHEMA SEGURO
    edificio_use_case: EdificioUseCase = Depends(get_edificio_use_case),
    current_user=Depends(require_permission(Permission.EDIFICIO_WRITE)),
):
    """Crear un nuevo edificio con validaciones anti-inyección (requiere permiso EDIFICIO:WRITE)"""
    try:
        edificio = edificio_use_case.create_edificio(edificio_data)
        return edificio
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor"
        )


@router.get("/", response_model=List[Edificio])
async def get_all_edificios(
    edificio_use_case: EdificioUseCase = Depends(get_edificio_use_case),
    current_user=Depends(require_permission(Permission.EDIFICIO_READ)),  # ✅ MIGRADO
):
    """Obtener todos los edificios (requiere permiso EDIFICIO:READ)"""
    try:
        edificios = edificio_use_case.get_all_edificios()
        return edificios
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor"
        )


@router.get("/{edificio_id}", response_model=Edificio)
async def get_edificio_by_id(
    edificio_id: int,
    edificio_use_case: EdificioUseCase = Depends(get_edificio_use_case),
    current_user=Depends(require_permission(Permission.EDIFICIO_READ)),  # ✅ MIGRADO
):
    """Obtener edificio por ID (requiere permiso EDIFICIO:READ)"""
    try:
        edificio = edificio_use_case.get_edificio_by_id(edificio_id)
        return edificio
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor"
        )


@router.get("/campus/{campus_id}", response_model=List[Edificio])
async def get_edificios_by_campus(
    campus_id: int,
    edificio_use_case: EdificioUseCase = Depends(get_edificio_use_case),
    current_user=Depends(require_permission(Permission.EDIFICIO_READ)),  # ✅ MIGRADO
):
    """Obtener edificios por campus (requiere permiso EDIFICIO:READ)"""
    try:
        edificios = edificio_use_case.get_edificios_by_campus(campus_id)
        return edificios
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor"
        )


@router.put(
    "/{edificio_id}",
    response_model=Edificio,
    status_code=status.HTTP_200_OK,
    summary="Actualizar edificio completo",
    tags=["edificios"],
)
async def update_edificio_complete(
    edificio_id: int,
    edificio_data: EdificioSecurePatch,  # ✅ SCHEMA SEGURO PATCH
    edificio_use_case: EdificioUseCase = Depends(get_edificio_use_case),
    current_user=Depends(require_permission(Permission.EDIFICIO_WRITE)),
):
    """Actualizar un edificio completamente con validaciones anti-inyección (requiere permiso EDIFICIO:WRITE)"""
    try:
        edificio = edificio_use_case.update_edificio(edificio_id, edificio_data)
        return edificio
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor"
        )


@router.patch(
    "/{edificio_id}",
    response_model=Edificio,
    status_code=status.HTTP_200_OK,
    summary="Actualizar campos específicos de edificio",
    tags=["edificios"],
)
async def update_edificio_partial(
    edificio_id: int,
    edificio_data: EdificioSecurePatch,  # ✅ SCHEMA SEGURO PATCH
    edificio_use_case: EdificioUseCase = Depends(get_edificio_use_case),
    current_user=Depends(require_permission(Permission.EDIFICIO_WRITE)),
):
    """Actualizar parcialmente un edificio con validaciones anti-inyección (requiere permiso EDIFICIO:WRITE)"""
    try:
        edificio = edificio_use_case.update_edificio(edificio_id, edificio_data)
        return edificio
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor"
        )


@router.delete("/{edificio_id}", summary="Eliminar edificio", tags=["edificios"])
async def delete_edificio(
    edificio_id: int,
    edificio_use_case: EdificioUseCase = Depends(get_edificio_use_case),
    current_user=Depends(require_permission(Permission.EDIFICIO_DELETE)),  # ✅ MIGRADO
):
    """Eliminar un edificio (requiere permiso EDIFICIO:DELETE)"""
    try:
        success = edificio_use_case.delete_edificio(edificio_id)
        return {"message": "Edificio eliminado exitosamente"}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor"
        )
