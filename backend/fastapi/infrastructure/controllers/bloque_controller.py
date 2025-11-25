from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from application.use_cases.bloque_use_cases import BloqueUseCases
from domain.authorization import Permission
from domain.entities import Bloque, User  # Response models
from domain.schemas import BloqueSecureCreate, BloqueSecurePatch  # ✅ SCHEMAS SEGUROS
from infrastructure.database.config import get_db
from infrastructure.dependencies import require_permission
from infrastructure.repositories.bloque_repository import BloqueRepository

router = APIRouter()


def get_bloque_use_cases(db: Session = Depends(get_db)) -> BloqueUseCases:
    repo = BloqueRepository(db)
    return BloqueUseCases(repo)


@router.get(
    "/",
    response_model=List[Bloque],
    status_code=status.HTTP_200_OK,
    summary="Obtener bloques",
    tags=["bloques"],
)
async def get_bloques(
    current_user: User = Depends(require_permission(Permission.BLOQUE_READ)),  # ✅ MIGRADO
    use_cases: BloqueUseCases = Depends(get_bloque_use_cases),
):
    """Obtener todos los bloques de horarios (requiere permiso BLOQUE:READ)"""
    try:
        bloques = use_cases.get_all()
        return bloques
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener los bloques: {str(e)}",
        )


@router.get(
    "/{bloque_id}",
    response_model=Bloque,
    status_code=status.HTTP_200_OK,
    summary="Obtener bloque por ID",
    tags=["bloques"],
)
async def obtener_bloque(
    bloque_id: int = Path(..., gt=0, description="ID del bloque"),
    current_user: User = Depends(require_permission(Permission.BLOQUE_READ)),  # ✅ MIGRADO
    use_cases: BloqueUseCases = Depends(get_bloque_use_cases),
):
    """Obtener un bloque específico por ID (requiere permiso BLOQUE:READ)"""
    try:
        bloque = use_cases.get_by_id(bloque_id)
        if not bloque:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Bloque con ID {bloque_id} no encontrado",
            )
        return bloque
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener el bloque: {str(e)}",
        )


@router.post(
    "/",
    response_model=Bloque,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nuevo bloque",
    tags=["bloques"],
)
async def create_bloque(
    bloque_data: BloqueSecureCreate,  # ✅ SCHEMA SEGURO
    use_cases: BloqueUseCases = Depends(get_bloque_use_cases),
    current_user: User = Depends(require_permission(Permission.BLOQUE_WRITE)),
):
    """Crear un nuevo bloque de horario con validaciones anti-inyección (requiere permiso BLOQUE:WRITE - solo administradores)"""
    try:
        nuevo_bloque = use_cases.create(bloque_data)
        return nuevo_bloque
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error de validación: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el bloque: {str(e)}",
        )


@router.put(
    "/{bloque_id}",
    response_model=Bloque,
    status_code=status.HTTP_200_OK,
    summary="Actualizar bloque completo",
    tags=["bloques"],
)
async def update_bloque(
    bloque_data: BloqueSecureCreate,  # ✅ SCHEMA SEGURO
    bloque_id: int = Path(..., gt=0, description="ID del bloque"),
    current_user: User = Depends(require_permission(Permission.BLOQUE_WRITE)),
    use_cases: BloqueUseCases = Depends(get_bloque_use_cases),
):
    """Actualizar completamente un bloque con validaciones anti-inyección (requiere permiso BLOQUE:WRITE - solo administradores)"""
    try:
        update_data = {
            "dia_semana": bloque_data.dia_semana,
            "hora_inicio": bloque_data.hora_inicio,
            "hora_fin": bloque_data.hora_fin,
        }

        bloque_actualizado = use_cases.update(bloque_id, **update_data)

        if not bloque_actualizado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Bloque con ID {bloque_id} no encontrado",
            )

        return bloque_actualizado
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error de validación: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar el bloque: {str(e)}",
        )


@router.patch(
    "/{bloque_id}",
    response_model=Bloque,
    status_code=status.HTTP_200_OK,
    summary="Actualizar campos específicos de bloque",
    tags=["bloques"],
)
async def partial_update_bloque(
    bloque_data: BloqueSecurePatch,  # ✅ SCHEMA SEGURO
    bloque_id: int = Path(..., gt=0, description="ID del bloque"),
    current_user: User = Depends(require_permission(Permission.BLOQUE_WRITE)),
    use_cases: BloqueUseCases = Depends(get_bloque_use_cases),
):
    """Actualizar parcialmente un bloque con validaciones anti-inyección (requiere permiso BLOQUE:WRITE - solo administradores)"""
    try:
        # Filtrar solo los campos que no son None
        update_data = {k: v for k, v in bloque_data.model_dump().items() if v is not None}

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se proporcionaron campos para actualizar",
            )

        bloque_actualizado = use_cases.update(bloque_id, **update_data)

        if not bloque_actualizado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Bloque con ID {bloque_id} no encontrado",
            )

        return bloque_actualizado
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error de validación: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar el bloque: {str(e)}",
        )


@router.delete(
    "/{bloque_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar bloque",
    tags=["bloques"],
)
async def delete_bloque(
    bloque_id: int = Path(..., gt=0, description="ID del bloque"),
    current_user: User = Depends(require_permission(Permission.BLOQUE_DELETE)),  # ✅ MIGRADO
    use_cases: BloqueUseCases = Depends(get_bloque_use_cases),
):
    """Eliminar un bloque (requiere permiso BLOQUE:DELETE - solo administradores)"""
    try:
        eliminado = use_cases.delete(bloque_id)

        if not eliminado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Bloque con ID {bloque_id} no encontrado",
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar el bloque: {str(e)}",
        )


@router.get(
    "/dia/{dia_semana}",
    response_model=List[Bloque],
    status_code=status.HTTP_200_OK,
    summary="Obtener bloques por día de la semana",
    tags=["bloques"],
)
async def get_bloques_by_dia_semana(
    dia_semana: int = Path(..., ge=1, le=7, description="Día de la semana (1=Lunes, 7=Domingo)"),
    current_user: User = Depends(require_permission(Permission.BLOQUE_READ)),  # ✅ MIGRADO
    use_cases: BloqueUseCases = Depends(get_bloque_use_cases),
):
    """Obtener bloques por día de la semana (requiere permiso BLOQUE:READ)"""
    try:
        bloques = use_cases.get_by_dia_semana(dia_semana)
        return bloques
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener bloques: {str(e)}",
        )


@router.get(
    "/buscar/horario",
    response_model=List[Bloque],
    status_code=status.HTTP_200_OK,
    summary="Buscar bloques por horario",
    tags=["bloques"],
)
async def get_bloques_by_horario(
    hora_inicio: Optional[str] = None,
    hora_fin: Optional[str] = None,
    current_user: User = Depends(require_permission(Permission.BLOQUE_READ)),  # ✅ MIGRADO
    use_cases: BloqueUseCases = Depends(get_bloque_use_cases),
):
    """Buscar bloques por rango de horario (requiere permiso BLOQUE:READ)"""
    try:
        bloques = use_cases.get_by_horario(hora_inicio, hora_fin)
        return bloques
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al buscar bloques: {str(e)}",
        )


@router.get(
    "/libres",
    response_model=List[Bloque],
    status_code=status.HTTP_200_OK,
    summary="Obtener bloques libres",
    tags=["bloques"],
)
async def get_bloques_libres(
    dia_semana: Optional[int] = None,
    current_user: User = Depends(require_permission(Permission.BLOQUE_READ)),  # ✅ MIGRADO
    use_cases: BloqueUseCases = Depends(get_bloque_use_cases),
):
    """Obtener bloques libres, opcionalmente filtrados por día de la semana (requiere permiso BLOQUE:READ)"""
    try:
        bloques = use_cases.get_bloques_libres(dia_semana)
        return bloques
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener bloques libres: {str(e)}",
        )
