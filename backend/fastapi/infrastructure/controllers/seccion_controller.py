from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from application.use_cases.seccion_use_cases import SeccionUseCases
from domain.authorization import Permission
from domain.entities import Seccion, User, StudentYearsResponse  # Response models
from domain.schemas import SeccionSecureCreate, SeccionSecurePatch  # ✅ SCHEMAS SEGUROS
from infrastructure.database.config import get_db
from infrastructure.dependencies import require_permission
from infrastructure.repositories.seccion_repository import SeccionRepository

router = APIRouter()


def get_seccion_use_cases(db: Session = Depends(get_db)) -> SeccionUseCases:
    repo = SeccionRepository(db)
    return SeccionUseCases(repo)


@router.get(
    "/",
    response_model=StudentYearsResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener secciones agrupadas por año académico",
    tags=["secciones"],
)
async def get_secciones(
    current_user: User = Depends(require_permission(Permission.SECCION_READ)),
    use_cases: SeccionUseCases = Depends(get_seccion_use_cases),
):
    """
    Obtener secciones agrupadas por año académico en formato FET.
    
    Retorna:
    ```json
    {
      "student_years": [
        {
          "id": "year-1",
          "name": "1",
          "total_students": 90,
          "groups": [
            {"id": "g-1-seccion-1", "name": "1 sección 1", "students": 30}
          ]
        }
      ]
    }
    ```
    """
    try:
        student_years = use_cases.get_student_years_format()
        return {"student_years": student_years}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener las secciones: {str(e)}",
        )


@router.get(
    "/{seccion_id}",
    response_model=Seccion,
    status_code=status.HTTP_200_OK,
    summary="Obtener sección por ID",
    tags=["secciones"],
)
async def obtener_seccion(
    seccion_id: int = Path(..., gt=0, description="ID de la sección"),
    current_user: User = Depends(require_permission(Permission.SECCION_READ)),  # ✅ MIGRADO
    use_cases: SeccionUseCases = Depends(get_seccion_use_cases),
):
    """Obtener una sección específica por ID (requiere permiso SECCION:READ)"""
    try:
        seccion = use_cases.get_by_id(seccion_id)
        if not seccion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sección con ID {seccion_id} no encontrada",
            )
        return seccion
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener la sección: {str(e)}",
        )


@router.post(
    "/",
    response_model=Seccion,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nueva sección",
    tags=["secciones"],
)
async def create_seccion(
    seccion_data: SeccionSecureCreate,  # ✅ SCHEMA SEGURO
    use_cases: SeccionUseCases = Depends(get_seccion_use_cases),
    current_user: User = Depends(require_permission(Permission.SECCION_WRITE)),
):
    """Crear una nueva sección con validaciones anti-inyección (requiere permiso SECCION:WRITE - solo administradores)"""
    try:
        nueva_seccion = use_cases.create(seccion_data)
        return nueva_seccion
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error de validación: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear la sección: {str(e)}",
        )


@router.put(
    "/{seccion_id}",
    response_model=Seccion,
    status_code=status.HTTP_200_OK,
    summary="Actualizar sección completa",
    tags=["secciones"],
)
async def update_seccion(
    seccion_data: SeccionSecureCreate,
    seccion_id: int = Path(..., gt=0, description="ID de la sección"),
    current_user: User = Depends(require_permission(Permission.SECCION_WRITE)),
    use_cases: SeccionUseCases = Depends(get_seccion_use_cases),
):
    """Actualizar completamente una sección con validaciones anti-inyección (requiere permiso SECCION:WRITE - solo administradores)"""
    try:
        seccion_actualizada = use_cases.update(seccion_id, seccion_data)

        if not seccion_actualizada:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sección con ID {seccion_id} no encontrada",
            )

        return seccion_actualizada
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error de validación: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar la sección: {str(e)}",
        )


@router.patch(
    "/{seccion_id}",
    response_model=Seccion,
    status_code=status.HTTP_200_OK,
    summary="Actualizar campos específicos de sección",
    tags=["secciones"],
)
async def partial_update_seccion(
    seccion_data: SeccionSecurePatch,
    seccion_id: int = Path(..., gt=0, description="ID de la sección"),
    current_user: User = Depends(require_permission(Permission.SECCION_WRITE)),
    use_cases: SeccionUseCases = Depends(get_seccion_use_cases),
):
    """Actualizar parcialmente una sección con validaciones anti-inyección (requiere permiso SECCION:WRITE - solo administradores)"""
    try:
        seccion_actualizada = use_cases.update(seccion_id, seccion_data)

        if not seccion_actualizada:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sección con ID {seccion_id} no encontrada",
            )

        return seccion_actualizada
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error de validación: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar la sección: {str(e)}",
        )


@router.delete(
    "/{seccion_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar sección",
    tags=["secciones"],
)
async def delete_seccion(
    seccion_id: int = Path(..., gt=0, description="ID de la sección"),
    current_user: User = Depends(require_permission(Permission.SECCION_DELETE)),  # ✅ MIGRADO
    use_cases: SeccionUseCases = Depends(get_seccion_use_cases),
):
    """Eliminar una sección (requiere permiso SECCION:DELETE - solo administradores)"""
    try:
        eliminado = use_cases.delete(seccion_id)

        if not eliminado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sección con ID {seccion_id} no encontrada",
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar la sección: {str(e)}",
        )


@router.get(
    "/asignatura/{asignatura_id}",
    response_model=List[Seccion],
    status_code=status.HTTP_200_OK,
    summary="Obtener secciones por asignatura",
    tags=["secciones"],
)
async def get_secciones_by_asignatura(
    asignatura_id: int = Path(..., gt=0, description="ID de la asignatura"),
    current_user: User = Depends(require_permission(Permission.SECCION_READ)),  # ✅ MIGRADO
    use_cases: SeccionUseCases = Depends(get_seccion_use_cases),
):
    """Obtener todas las secciones de una asignatura (requiere permiso SECCION:READ)"""
    try:
        secciones = use_cases.get_by_asignatura(asignatura_id)
        return secciones
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener secciones: {str(e)}",
        )


@router.get(
    "/periodo/{anio}/{semestre}",
    response_model=List[Seccion],
    status_code=status.HTTP_200_OK,
    summary="Obtener secciones por periodo",
    tags=["secciones"],
)
async def get_secciones_by_periodo(
    anio: int = Path(..., gt=2000, description="Año del periodo"),
    semestre: int = Path(..., ge=1, le=2, description="Semestre (1 o 2)"),
    current_user: User = Depends(require_permission(Permission.SECCION_READ)),  # ✅ MIGRADO
    use_cases: SeccionUseCases = Depends(get_seccion_use_cases),
):
    """Obtener secciones por año y semestre (requiere permiso SECCION:READ)"""
    try:
        secciones = use_cases.get_by_periodo(anio, semestre)
        return secciones
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener secciones: {str(e)}",
        )


@router.get(
    "/activas",
    response_model=List[Seccion],
    status_code=status.HTTP_200_OK,
    summary="Obtener secciones activas",
    tags=["secciones"],
)
async def get_secciones_activas(
    current_user: User = Depends(require_permission(Permission.SECCION_READ)),  # ✅ MIGRADO
    use_cases: SeccionUseCases = Depends(get_seccion_use_cases),
):
    """Obtener todas las secciones activas (requiere permiso SECCION:READ)"""
    try:
        secciones = use_cases.get_secciones_activas()
        return secciones
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener secciones activas: {str(e)}",
        )
