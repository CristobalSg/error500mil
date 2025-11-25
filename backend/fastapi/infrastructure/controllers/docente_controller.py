from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from application.use_cases.docente_use_cases import DocenteUseCases
from domain.authorization import Permission
from domain.entities import DocenteResponse  # ✅ Response model limpio
from domain.schemas import DocenteSecurePatch  # ✅ SCHEMA SEGURO (solo para update)
from infrastructure.database.config import get_db
from infrastructure.dependencies import require_permission
from infrastructure.repositories.docente_repository import DocenteRepository
from infrastructure.repositories.user_repository import SQLUserRepository

router = APIRouter()


def get_docente_use_case(db: Session = Depends(get_db)) -> DocenteUseCases:
    docente_repository = DocenteRepository(db)
    user_repository = SQLUserRepository(db)
    return DocenteUseCases(docente_repository, user_repository)


# ============================================================================
# NOTA IMPORTANTE: La creación de docentes se realiza a través de
# POST /api/auth/register con rol="docente" y departamento obligatorio.
# Esto garantiza consistencia y evita registros huérfanos.
# 
# Los IDs usados en estos endpoints son user_id (no docente_id interno).
# ============================================================================


@router.get("/", response_model=List[DocenteResponse])
async def get_all_docentes(
    skip: int = 0,
    limit: int = 100,
    docente_use_case: DocenteUseCases = Depends(get_docente_use_case),
    current_user=Depends(require_permission(Permission.DOCENTE_READ)),
):
    """
    Obtener todos los docentes (requiere permiso DOCENTE:READ).
    Retorna una lista simplificada usando user_id como ID principal.
    """
    try:
        docentes = docente_use_case.get_all(skip=skip, limit=limit)
        return [DocenteResponse.from_docente(d) for d in docentes]
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor"
        )


@router.get("/{user_id}", response_model=DocenteResponse)
async def get_docente_by_user_id(
    user_id: int,
    docente_use_case: DocenteUseCases = Depends(get_docente_use_case),
    current_user=Depends(require_permission(Permission.DOCENTE_READ)),
):
    """
    Obtener docente por user_id (requiere permiso DOCENTE:READ).
    Usa user_id como identificador principal.
    """
    try:
        docente = docente_use_case.get_by_user_id(user_id)
        return DocenteResponse.from_docente(docente)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor"
        )


@router.get("/departamento/{departamento}", response_model=List[DocenteResponse])
async def get_docentes_by_departamento(
    departamento: str,
    docente_use_case: DocenteUseCases = Depends(get_docente_use_case),
    current_user=Depends(require_permission(Permission.DOCENTE_READ)),
):
    """Obtener docentes por departamento (requiere permiso DOCENTE:READ)"""
    try:
        docentes = docente_use_case.get_by_departamento(departamento)
        return [DocenteResponse.from_docente(d) for d in docentes]
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor"
        )


@router.put(
    "/{user_id}",
    response_model=DocenteResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar docente completo",
    tags=["docentes"],
)
async def update_docente_complete(
    user_id: int,
    docente_data: DocenteSecurePatch,
    docente_use_case: DocenteUseCases = Depends(get_docente_use_case),
    current_user=Depends(require_permission(Permission.DOCENTE_WRITE)),
):
    """
    Actualizar completamente un docente con validaciones anti-inyección.
    Usa user_id como identificador (requiere permiso DOCENTE:WRITE).
    """
    try:
        docente = docente_use_case.update_by_user_id(user_id, docente_data)
        return DocenteResponse.from_docente(docente)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor"
        )


@router.patch(
    "/{user_id}",
    response_model=DocenteResponse,
    summary="Actualizar docente parcial",
    tags=["docentes"]
)
async def update_docente(
    user_id: int,
    docente_data: DocenteSecurePatch,
    docente_use_case: DocenteUseCases = Depends(get_docente_use_case),
    current_user=Depends(require_permission(Permission.DOCENTE_WRITE)),
):
    """
    Actualizar parcialmente un docente con validaciones anti-inyección.
    Usa user_id como identificador (requiere permiso DOCENTE:WRITE).
    """
    try:
        docente = docente_use_case.update_by_user_id(user_id, docente_data)
        return DocenteResponse.from_docente(docente)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor"
        )


@router.delete("/{user_id}")
async def delete_docente(
    user_id: int,
    docente_use_case: DocenteUseCases = Depends(get_docente_use_case),
    current_user=Depends(require_permission(Permission.DOCENTE_DELETE)),
):
    """
    Eliminar un docente usando user_id como identificador.
    (requiere permiso DOCENTE:DELETE)
    """
    try:
        success = docente_use_case.delete_by_user_id(user_id)
        return {"message": "Docente eliminado exitosamente"}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor"
        )
