from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from application.use_cases.clase_uses_cases import ClaseUseCases
from domain.authorization import Permission
from domain.entities import Clase, User  # Response models
from domain.schemas import ClaseSecureCreate, ClaseSecurePatch  # ✅ SCHEMAS SEGUROS
from infrastructure.database.config import get_db
from infrastructure.dependencies import require_permission
from infrastructure.repositories.clase_repository import ClaseRepository

router = APIRouter()


def get_clase_use_cases(db: Session = Depends(get_db)) -> ClaseUseCases:
    clase_repo = ClaseRepository(db)
    return ClaseUseCases(clase_repo)


@router.get(
    "/",
    response_model=List[Clase],
    status_code=status.HTTP_200_OK,
    summary="Obtener clases",
    tags=["clases"],
)
async def get_clases(
    current_user: User = Depends(require_permission(Permission.CLASE_READ)),  # ✅ MIGRADO
    use_cases: ClaseUseCases = Depends(get_clase_use_cases),
):
    """Obtener todas las clases (requiere permiso CLASE:READ)"""
    try:
        clases = use_cases.get_all()
        return clases
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener las clases: {str(e)}",
        )


@router.get(
    "/{clase_id}",
    response_model=Clase,
    status_code=status.HTTP_200_OK,
    summary="Obtener clase por ID",
    tags=["clases"],
)
async def obtener_clase(
    clase_id: int = Path(..., gt=0, description="ID de la clase"),
    current_user: User = Depends(require_permission(Permission.CLASE_READ)),  # ✅ MIGRADO
    use_cases: ClaseUseCases = Depends(get_clase_use_cases),
):
    """Obtener una clase específica por ID (requiere permiso CLASE:READ)"""
    try:
        clase = use_cases.get_by_id(clase_id)
        if not clase:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Clase con ID {clase_id} no encontrada",
            )
        return clase
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener la clase: {str(e)}",
        )


@router.post(
    "/",
    response_model=Clase,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nueva clase",
    tags=["clases"],
)
async def create_clase(
    clase_data: ClaseSecureCreate,  # ✅ SCHEMA SEGURO
    use_cases: ClaseUseCases = Depends(get_clase_use_cases),
    current_user: User = Depends(require_permission(Permission.CLASE_WRITE)),
):
    """Crear una nueva clase con validaciones anti-inyección (requiere permiso CLASE:WRITE - solo administradores)"""
    try:
        nueva_clase = use_cases.create(clase_data)
        return nueva_clase
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error de validación: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear la clase: {str(e)}",
        )


@router.put(
    "/{clase_id}",
    response_model=Clase,
    status_code=status.HTTP_200_OK,
    summary="Actualizar clase completa",
    tags=["clases"],
)
async def update_clase(
    clase_data: ClaseSecurePatch,  # ✅ SCHEMA SEGURO (cambiado a Patch para flexibilidad)
    clase_id: int = Path(..., gt=0, description="ID de la clase"),
    current_user: User = Depends(require_permission(Permission.CLASE_WRITE)),
    use_cases: ClaseUseCases = Depends(get_clase_use_cases),
):
    """Actualizar completamente una clase con validaciones anti-inyección (requiere permiso CLASE:WRITE - solo administradores)"""
    try:
        clase_actualizada = use_cases.update(clase_id, clase_data)

        if not clase_actualizada:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Clase con ID {clase_id} no encontrada",
            )

        return clase_actualizada
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error de validación: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar la clase: {str(e)}",
        )


@router.patch(
    "/{clase_id}",
    response_model=Clase,
    status_code=status.HTTP_200_OK,
    summary="Actualizar campos específicos de clase",
    tags=["clases"],
)
async def partial_update_clase(
    clase_data: ClaseSecurePatch,  # ✅ SCHEMA SEGURO
    clase_id: int = Path(..., gt=0, description="ID de la clase"),
    current_user: User = Depends(require_permission(Permission.CLASE_WRITE)),
    use_cases: ClaseUseCases = Depends(get_clase_use_cases),
):
    """Actualizar parcialmente una clase con validaciones anti-inyección (requiere permiso CLASE:WRITE - solo administradores)"""
    try:
        clase_actualizada = use_cases.update(clase_id, clase_data)

        if not clase_actualizada:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Clase con ID {clase_id} no encontrada",
            )

        return clase_actualizada
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error de validación: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar la clase: {str(e)}",
        )


@router.delete(
    "/{clase_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar clase", tags=["clases"]
)
async def delete_clase(
    clase_id: int = Path(..., gt=0, description="ID de la clase"),
    current_user: User = Depends(require_permission(Permission.CLASE_DELETE)),  # ✅ MIGRADO
    use_cases: ClaseUseCases = Depends(get_clase_use_cases),
):
    """Eliminar una clase (requiere permiso CLASE:DELETE - solo administradores)"""
    try:
        eliminado = use_cases.delete(clase_id)

        if not eliminado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Clase con ID {clase_id} no encontrada",
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar la clase: {str(e)}",
        )


@router.get(
    "/seccion/{seccion_id}",
    response_model=List[Clase],
    status_code=status.HTTP_200_OK,
    summary="Obtener clases por sección",
    tags=["clases"],
)
async def get_clases_by_seccion(
    seccion_id: int = Path(..., gt=0, description="ID de la sección"),
    current_user: User = Depends(require_permission(Permission.CLASE_READ)),  # ✅ MIGRADO
    use_cases: ClaseUseCases = Depends(get_clase_use_cases),
):
    """Obtener todas las clases de una sección (requiere permiso CLASE:READ)"""
    try:
        clases = use_cases.get_by_seccion(seccion_id)
        return clases
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener clases: {str(e)}",
        )


@router.get(
    "/docente/{docente_id}",
    response_model=List[Clase],
    status_code=status.HTTP_200_OK,
    summary="Obtener clases por docente",
    tags=["clases"],
)
async def get_clases_by_docente(
    docente_id: int = Path(..., gt=0, description="ID del docente"),
    current_user: User = Depends(require_permission(Permission.CLASE_READ)),  # ✅ MIGRADO
    use_cases: ClaseUseCases = Depends(get_clase_use_cases),
):
    """Obtener todas las clases de un docente (requiere permiso CLASE:READ)"""
    try:
        clases = use_cases.get_by_docente(docente_id)
        return clases
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener clases: {str(e)}",
        )


@router.get(
    "/sala/{sala_id}",
    response_model=List[Clase],
    status_code=status.HTTP_200_OK,
    summary="Obtener clases por sala",
    tags=["clases"],
)
async def get_clases_by_sala(
    sala_id: int = Path(..., gt=0, description="ID de la sala"),
    current_user: User = Depends(require_permission(Permission.CLASE_READ)),  # ✅ MIGRADO
    use_cases: ClaseUseCases = Depends(get_clase_use_cases),
):
    """Obtener todas las clases programadas en una sala (requiere permiso CLASE:READ)"""
    try:
        clases = use_cases.get_by_sala(sala_id)
        return clases
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener clases: {str(e)}",
        )


@router.get(
    "/bloque/{bloque_id}",
    response_model=List[Clase],
    status_code=status.HTTP_200_OK,
    summary="Obtener clases por bloque",
    tags=["clases"],
)
async def get_clases_by_bloque(
    bloque_id: int = Path(..., gt=0, description="ID del bloque"),
    current_user: User = Depends(require_permission(Permission.CLASE_READ)),  # ✅ MIGRADO
    use_cases: ClaseUseCases = Depends(get_clase_use_cases),
):
    """Obtener todas las clases programadas en un bloque horario (requiere permiso CLASE:READ)"""
    try:
        clases = use_cases.get_by_bloque(bloque_id)
        return clases
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener clases: {str(e)}",
        )
