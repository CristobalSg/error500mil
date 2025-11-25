from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from application.use_cases.campus_use_cases import CampusUseCase
from domain.authorization import Permission
from domain.entities import Campus  # Response models
from domain.schemas import CampusSecureCreate, CampusSecurePatch  # ✅ SCHEMAS SEGUROS
from infrastructure.database.config import get_db
from infrastructure.dependencies import require_permission
from infrastructure.repositories.campus_repository import SQLCampusRepository

router = APIRouter()


def get_campus_use_case(db: Session = Depends(get_db)) -> CampusUseCase:
    campus_repository = SQLCampusRepository(db)
    return CampusUseCase(campus_repository)


@router.post("/", response_model=Campus, status_code=status.HTTP_201_CREATED)
async def create_campus(
    campus_data: CampusSecureCreate,  # ✅ SCHEMA SEGURO
    campus_use_case: CampusUseCase = Depends(get_campus_use_case),
    current_user=Depends(require_permission(Permission.CAMPUS_WRITE)),
):
    """Crear un nuevo campus con validaciones anti-inyección (requiere permiso CAMPUS:WRITE)"""
    try:
        campus = campus_use_case.create_campus(campus_data)
        return campus
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor"
        )


@router.get("/", response_model=List[Campus])
async def get_all_campus(
    campus_use_case: CampusUseCase = Depends(get_campus_use_case),
    current_user=Depends(require_permission(Permission.CAMPUS_READ)),  # ✅ MIGRADO
):
    """Obtener todos los campus (requiere permiso CAMPUS:READ)"""
    try:
        campus = campus_use_case.get_all_campus()
        return campus
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor"
        )


@router.get("/{campus_id}", response_model=Campus)
async def get_campus_by_id(
    campus_id: int,
    campus_use_case: CampusUseCase = Depends(get_campus_use_case),
    current_user=Depends(require_permission(Permission.CAMPUS_READ)),  # ✅ MIGRADO
):
    """Obtener campus por ID (requiere permiso CAMPUS:READ)"""
    try:
        campus = campus_use_case.get_campus_by_id(campus_id)
        return campus
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor"
        )


@router.put(
    "/{campus_id}",
    response_model=Campus,
    status_code=status.HTTP_200_OK,
    summary="Actualizar campus completo",
    tags=["campus"],
)
async def update_campus_complete(
    campus_id: int,
    campus_data: CampusSecurePatch,  # ✅ SCHEMA SEGURO PATCH
    campus_use_case: CampusUseCase = Depends(get_campus_use_case),
    current_user=Depends(require_permission(Permission.CAMPUS_WRITE)),
):
    """Actualizar completamente un campus con validaciones anti-inyección (requiere permiso CAMPUS:WRITE)"""
    try:
        campus = campus_use_case.update_campus(campus_id, campus_data)
        return campus
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor"
        )


@router.patch(
    "/{campus_id}", response_model=Campus, summary="Actualizar campus parcial", tags=["campus"]
)
async def update_campus(
    campus_id: int,
    campus_data: CampusSecurePatch,  # ✅ SCHEMA SEGURO
    campus_use_case: CampusUseCase = Depends(get_campus_use_case),
    current_user=Depends(require_permission(Permission.CAMPUS_WRITE)),
):
    """Actualizar parcialmente un campus con validaciones anti-inyección (requiere permiso CAMPUS:WRITE)"""
    try:
        campus = campus_use_case.update_campus(campus_id, campus_data)
        return campus
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor"
        )


@router.delete("/{campus_id}")
async def delete_campus(
    campus_id: int,
    campus_use_case: CampusUseCase = Depends(get_campus_use_case),
    current_user=Depends(require_permission(Permission.CAMPUS_DELETE)),  # ✅ MIGRADO
):
    """Eliminar un campus (requiere permiso CAMPUS:DELETE)"""
    try:
        success = campus_use_case.delete_campus(campus_id)
        return {"message": "Campus eliminado exitosamente"}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor"
        )
