from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from application.use_cases.restriccion_use_cases import RestriccionUseCases
from domain.authorization import Permission
from domain.entities import Restriccion, User  # Response models
from domain.schemas import RestriccionSecureCreate, RestriccionSecurePatch  # ✅ SCHEMAS SEGUROS
from infrastructure.database.config import get_db
from infrastructure.dependencies import require_any_permission, require_permission
from infrastructure.repositories.docente_repository import DocenteRepository
from infrastructure.repositories.restriccion_repository import RestriccionRepository

router = APIRouter()


def get_restriccion_use_cases(db: Session = Depends(get_db)) -> RestriccionUseCases:
    repo = RestriccionRepository(db)
    docente_repo = DocenteRepository(db)
    return RestriccionUseCases(repo, docente_repo)


@router.get(
    "/",
    response_model=List[Restriccion],
    status_code=status.HTTP_200_OK,
    summary="Obtener restricciones",
    tags=["restricciones"],
)
async def get_restricciones(
    current_user: User = Depends(
        require_any_permission(
            Permission.RESTRICCION_READ_ALL,  # Admin: todas las restricciones
            Permission.RESTRICCION_READ_OWN,  # Docente: solo las propias
        )
    ),
    use_cases: RestriccionUseCases = Depends(get_restriccion_use_cases),
):
    """Obtener restricciones (docentes: sus propias / administradores: todas) - requiere RESTRICCION:READ:ALL o RESTRICCION:READ:OWN"""
    try:
        if current_user.rol == "administrador":
            restricciones = use_cases.get_all()
        else:  # docente
            restricciones = use_cases.get_by_docente_user(current_user)
        return restricciones
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener las restricciones: {str(e)}",
        )


@router.get(
    "/{restriccion_id}",
    response_model=Restriccion,
    status_code=status.HTTP_200_OK,
    summary="Obtener restricción por ID",
    tags=["restricciones"],
)
async def obtener_restriccion(
    restriccion_id: int,
    current_user: User = Depends(
        require_any_permission(
            Permission.RESTRICCION_READ_ALL,  # Admin: cualquier restricción
            Permission.RESTRICCION_READ_OWN,  # Docente: solo las propias
        )
    ),
    use_cases: RestriccionUseCases = Depends(get_restriccion_use_cases),
):
    """Obtener restricción por ID (con verificación de propiedad) - requiere RESTRICCION:READ:ALL o RESTRICCION:READ:OWN"""
    try:
        restriccion = use_cases.get_by_id_and_docente_user(restriccion_id, current_user)
        return restriccion
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener la restricción: {str(e)}",
        )


@router.post(
    "/",
    response_model=Restriccion,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nueva restricción",
    tags=["restricciones"],
)
async def create_restriccion(
    restriccion_data: RestriccionSecureCreate,  # ✅ SCHEMA SEGURO
    use_cases: RestriccionUseCases = Depends(get_restriccion_use_cases),
    current_user: User = Depends(
        require_any_permission(
            Permission.RESTRICCION_WRITE,  # Admin: crear para cualquiera
            Permission.RESTRICCION_WRITE_OWN,  # Docente: crear para sí mismo
        )
    ),
):
    """Crear restricción con validaciones anti-inyección (docentes: para sí mismos / admin: para cualquiera) - requiere RESTRICCION:WRITE o RESTRICCION:WRITE:OWN"""
    try:
        nueva_restriccion = use_cases.create_for_docente_user(restriccion_data, current_user)
        return nueva_restriccion
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error de validación: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear la restricción: {str(e)}",
        )


@router.put(
    "/{restriccion_id}",
    response_model=Restriccion,
    status_code=status.HTTP_200_OK,
    summary="Actualizar restricción completa",
    tags=["restricciones"],
)
async def update_restriccion(
    restriccion_data: RestriccionSecureCreate,  # ✅ SCHEMA SEGURO
    restriccion_id: int,
    use_cases: RestriccionUseCases = Depends(get_restriccion_use_cases),
    current_user: User = Depends(
        require_any_permission(
            Permission.RESTRICCION_WRITE,  # Admin: actualizar cualquiera
            Permission.RESTRICCION_WRITE_OWN,  # Docente: actualizar solo las propias
        )
    ),
):
    """Actualizar restricción completa con validaciones anti-inyección (con verificación de propiedad) - requiere RESTRICCION:WRITE o RESTRICCION:WRITE:OWN"""
    try:
        # Convertir RestriccionSecureCreate a RestriccionSecurePatch para el use case
        patch_data = RestriccionSecurePatch(
            tipo=restriccion_data.tipo,
            valor=restriccion_data.valor,
            prioridad=restriccion_data.prioridad,
            restriccion_blanda=restriccion_data.restriccion_blanda,
            restriccion_dura=restriccion_data.restriccion_dura,
        )

        restriccion_actualizada = use_cases.update_for_docente_user(
            restriccion_id, current_user, patch_data
        )

        if not restriccion_actualizada:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Restricción con ID {restriccion_id} no encontrada",
            )

        return restriccion_actualizada
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error de validación: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar la restricción: {str(e)}",
        )


@router.patch(
    "/{restriccion_id}",
    response_model=Restriccion,
    summary="Actualizar restricción parcial",
    tags=["restricciones"],
)
async def patch_restriccion(
    patch_data: RestriccionSecurePatch,  # ✅ SCHEMA SEGURO
    restriccion_id: int,
    current_user: User = Depends(
        require_any_permission(
            Permission.RESTRICCION_WRITE,  # Admin: modificar cualquiera
            Permission.RESTRICCION_WRITE_OWN,  # Docente: modificar solo las propias
        )
    ),
    use_cases: RestriccionUseCases = Depends(get_restriccion_use_cases),
):
    """Actualizar parcialmente restricción con validaciones anti-inyección (con verificación de propiedad) - requiere RESTRICCION:WRITE o RESTRICCION:WRITE:OWN"""
    try:
        # El use case maneja la validación de campos vacíos
        restriccion_actualizada = use_cases.update_for_docente_user(
            restriccion_id, current_user, patch_data
        )

        if not restriccion_actualizada:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Restricción con ID {restriccion_id} no encontrada",
            )

        return restriccion_actualizada
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error de validación: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar la restricción: {str(e)}",
        )


@router.delete(
    "/{restriccion_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar restricción",
    tags=["restricciones"],
)
async def delete_restriccion(
    restriccion_id: int,
    current_user: User = Depends(
        require_any_permission(
            Permission.RESTRICCION_DELETE,  # Admin: eliminar cualquiera
            Permission.RESTRICCION_DELETE_OWN,  # Docente: eliminar solo las propias
        )
    ),
    use_cases: RestriccionUseCases = Depends(get_restriccion_use_cases),
):
    """Eliminar restricción (con verificación de propiedad) - requiere RESTRICCION:DELETE o RESTRICCION:DELETE:OWN"""
    try:
        deleted = use_cases.delete_for_docente_user(restriccion_id, current_user)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Restricción con ID {restriccion_id} no encontrada",
            )
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar la restricción: {str(e)}",
        )


# =====================================
# ENDPOINTS ÚNICOS PARA ADMINISTRADORES
# =====================================


@router.get(
    "/admin/docente/{user_id}",
    response_model=List[Restriccion],
    status_code=status.HTTP_200_OK,
    summary="[ADMIN] Obtener restricciones de un docente específico",
    tags=["admin-restricciones"],
)
async def admin_get_restricciones_by_docente(
    user_id: int,
    current_user: User = Depends(require_permission(Permission.RESTRICCION_READ_ALL)),
    use_cases: RestriccionUseCases = Depends(get_restriccion_use_cases),
):
    """Obtener todas las restricciones de un docente específico usando user_id - requiere RESTRICCION:READ:ALL (solo administradores)"""
    try:
        restricciones = use_cases.get_by_user_id(user_id)
        return restricciones
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener las restricciones del docente: {str(e)}",
        )


@router.post(
    "/admin/docente/{user_id}",
    response_model=Restriccion,
    status_code=status.HTTP_201_CREATED,
    summary="[ADMIN] Crear restricción para un docente específico",
    tags=["admin-restricciones"],
)
async def create_restriccion_for_docente(
    restriccion_data: RestriccionSecureCreate,  # ✅ SCHEMA SEGURO
    user_id: int,
    use_cases: RestriccionUseCases = Depends(get_restriccion_use_cases),
    current_user: User = Depends(require_permission(Permission.RESTRICCION_WRITE)),
):
    """[ADMIN] Crear restricción para docente específico usando user_id con validaciones anti-inyección (solo administradores) - requiere RESTRICCION:WRITE"""
    try:
        # Forzar el user_id al valor del parámetro de ruta
        restriccion_data.user_id = user_id
        nueva_restriccion = use_cases.create(restriccion_data)
        return nueva_restriccion
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error de validación: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear la restricción: {str(e)}",
        )
