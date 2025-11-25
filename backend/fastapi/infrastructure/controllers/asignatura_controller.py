from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from application.use_cases.asignatura_use_cases import AsignaturaUseCases
from domain.authorization import Permission
from domain.entities import Asignatura, User  # Response models
from domain.schemas import AsignaturaSecureCreate, AsignaturaSecurePatch  # ✅ SCHEMAS SEGUROS
from infrastructure.database.config import get_db
from infrastructure.dependencies import require_permission
from infrastructure.repositories.asignatura_repository import AsignaturaRepository

router = APIRouter()


def get_asignatura_use_cases(db: Session = Depends(get_db)) -> AsignaturaUseCases:
    repo = AsignaturaRepository(db)
    return AsignaturaUseCases(repo)


@router.get(
    "/",
    response_model=List[Asignatura],
    status_code=status.HTTP_200_OK,
    summary="Obtener asignaturas",
    tags=["asignaturas"],
)
async def get_asignaturas(
    current_user: User = Depends(require_permission(Permission.ASIGNATURA_READ)),  # ✅ MIGRADO
    use_cases: AsignaturaUseCases = Depends(get_asignatura_use_cases),
):
    """Obtener todas las asignaturas (requiere permiso ASIGNATURA:READ)"""
    try:
        asignaturas = use_cases.get_all()
        return asignaturas
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener las asignaturas: {str(e)}",
        )


@router.get(
    "/{asignatura_id}",
    response_model=Asignatura,
    status_code=status.HTTP_200_OK,
    summary="Obtener asignatura por ID",
    tags=["asignaturas"],
)
async def obtener_asignatura(
    asignatura_id: int = Path(..., gt=0, description="ID de la asignatura"),
    current_user: User = Depends(require_permission(Permission.ASIGNATURA_READ)),  # ✅ MIGRADO
    use_cases: AsignaturaUseCases = Depends(get_asignatura_use_cases),
):
    """Obtener una asignatura específica por ID (requiere permiso ASIGNATURA:READ)"""
    try:
        asignatura = use_cases.get_by_id(asignatura_id)
        if not asignatura:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Asignatura con ID {asignatura_id} no encontrada",
            )
        return asignatura
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener la asignatura: {str(e)}",
        )


@router.post(
    "/",
    response_model=Asignatura,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nueva asignatura",
    tags=["asignaturas"],
)
async def create_asignatura(
    asignatura_data: AsignaturaSecureCreate,  # ✅ SCHEMA SEGURO
    use_cases: AsignaturaUseCases = Depends(get_asignatura_use_cases),
    current_user: User = Depends(require_permission(Permission.ASIGNATURA_WRITE)),
):
    """Crear una nueva asignatura con validaciones anti-inyección (requiere permiso ASIGNATURA:WRITE - solo administradores)"""
    try:
        nueva_asignatura = use_cases.create(asignatura_data)
        return nueva_asignatura
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error de validación: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear la asignatura: {str(e)}",
        )


@router.put(
    "/{asignatura_id}",
    response_model=Asignatura,
    status_code=status.HTTP_200_OK,
    summary="Actualizar asignatura completa",
    tags=["asignaturas"],
)
async def update_asignatura(
    asignatura_data: AsignaturaSecureCreate,  # ✅ SCHEMA SEGURO
    asignatura_id: int = Path(..., gt=0, description="ID de la asignatura"),
    current_user: User = Depends(require_permission(Permission.ASIGNATURA_WRITE)),
    use_cases: AsignaturaUseCases = Depends(get_asignatura_use_cases),
):
    """Actualizar completamente una asignatura con validaciones anti-inyección (requiere permiso ASIGNATURA:WRITE - solo administradores)"""
    try:
        # Convertir AsignaturaSecureCreate a AsignaturaSecurePatch para el use case
        patch_data = AsignaturaSecurePatch(**asignatura_data.model_dump())

        asignatura_actualizada = use_cases.update(asignatura_id, patch_data)

        if not asignatura_actualizada:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Asignatura con ID {asignatura_id} no encontrada",
            )

        return asignatura_actualizada
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error de validación: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar la asignatura: {str(e)}",
        )


@router.patch(
    "/{asignatura_id}",
    response_model=Asignatura,
    status_code=status.HTTP_200_OK,
    summary="Actualizar asignatura parcial",
    tags=["asignaturas"],
)
async def patch_asignatura(
    asignatura_data: AsignaturaSecurePatch,  # ✅ SCHEMA SEGURO
    asignatura_id: int = Path(..., gt=0, description="ID de la asignatura"),
    current_user: User = Depends(require_permission(Permission.ASIGNATURA_WRITE)),
    use_cases: AsignaturaUseCases = Depends(get_asignatura_use_cases),
):
    """Actualizar parcialmente una asignatura con validaciones anti-inyección (requiere permiso ASIGNATURA:WRITE - solo administradores)"""
    try:
        # El use case maneja la validación de campos vacíos
        asignatura_actualizada = use_cases.update(asignatura_id, asignatura_data)

        if not asignatura_actualizada:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Asignatura con ID {asignatura_id} no encontrada",
            )

        return asignatura_actualizada
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error de validación: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar la asignatura: {str(e)}",
        )


@router.delete(
    "/{asignatura_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar asignatura",
    tags=["asignaturas"],
)
async def delete_asignatura(
    asignatura_id: int = Path(..., gt=0, description="ID de la asignatura"),
    current_user: User = Depends(require_permission(Permission.ASIGNATURA_DELETE)),  # ✅ MIGRADO
    use_cases: AsignaturaUseCases = Depends(get_asignatura_use_cases),
):
    """Eliminar una asignatura (requiere permiso ASIGNATURA:DELETE - solo administradores)"""
    try:
        eliminado = use_cases.delete(asignatura_id)

        if not eliminado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Asignatura con ID {asignatura_id} no encontrada",
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar la asignatura: {str(e)}",
        )


@router.get(
    "/codigo/{codigo}",
    response_model=Asignatura,
    status_code=status.HTTP_200_OK,
    summary="Obtener asignatura por código",
    tags=["asignaturas"],
)
async def get_asignatura_by_codigo(
    codigo: str = Path(..., description="Código de la asignatura"),
    current_user: User = Depends(require_permission(Permission.ASIGNATURA_READ)),  # ✅ MIGRADO
    use_cases: AsignaturaUseCases = Depends(get_asignatura_use_cases),
):
    """Obtener una asignatura específica por su código (requiere permiso ASIGNATURA:READ)"""
    try:
        asignatura = use_cases.get_by_codigo(codigo)
        if not asignatura:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Asignatura con código '{codigo}' no encontrada",
            )
        return asignatura
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener la asignatura: {str(e)}",
        )


@router.get(
    "/buscar/nombre",
    response_model=List[Asignatura],
    status_code=status.HTTP_200_OK,
    summary="Buscar asignaturas por nombre",
    tags=["asignaturas"],
)
async def search_asignaturas_by_nombre(
    nombre: str,
    current_user: User = Depends(require_permission(Permission.ASIGNATURA_READ)),  # ✅ MIGRADO
    use_cases: AsignaturaUseCases = Depends(get_asignatura_use_cases),
):
    """Buscar asignaturas por nombre (búsqueda parcial) - requiere permiso ASIGNATURA:READ"""
    try:
        asignaturas = use_cases.search_by_nombre(nombre)
        return asignaturas
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al buscar asignaturas: {str(e)}",
        )


@router.get(
    "/buscar/creditos",
    response_model=List[Asignatura],
    status_code=status.HTTP_200_OK,
    summary="Buscar asignaturas por cantidad de créditos",
    tags=["asignaturas"],
)
@router.get(
    "/buscar/cantidad-creditos",
    response_model=List[Asignatura],
    status_code=status.HTTP_200_OK,
    summary="Buscar asignaturas por cantidad de créditos",
    tags=["asignaturas"],
)
async def get_asignaturas_by_cantidad_creditos(
    creditos_min: Optional[int] = None,
    creditos_max: Optional[int] = None,
    current_user: User = Depends(require_permission(Permission.ASIGNATURA_READ)),  # ✅ MIGRADO
    use_cases: AsignaturaUseCases = Depends(get_asignatura_use_cases),
):
    """Buscar asignaturas por rango de cantidad de créditos (requiere permiso ASIGNATURA:READ)"""
    try:
        asignaturas = use_cases.get_by_cantidad_creditos(creditos_min, creditos_max)
        return asignaturas
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al buscar asignaturas: {str(e)}",
        )
