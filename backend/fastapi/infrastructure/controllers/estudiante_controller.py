"""
Controlador de estudiantes - Endpoints RESTful

ARQUITECTURA:
- NO existe POST /estudiantes/ - los estudiantes se crean vía POST /api/auth/register
- Los endpoints usan user_id como identificador (no el ID interno de la tabla estudiante)
- Response usa EstudianteResponse que expone solo user_id como 'id'
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from application.use_cases.estudiante_use_cases import EstudianteUseCase
from domain.authorization import Permission
from domain.entities import EstudianteResponse, User
from infrastructure.dependencies import get_db, require_permission
from infrastructure.repositories.estudiante_repository import SQLEstudianteRepository
from infrastructure.repositories.user_repository import SQLUserRepository

router = APIRouter()


def get_estudiante_use_case(db: Session = Depends(get_db)) -> EstudianteUseCase:
    """Dependency para obtener los casos de uso de estudiantes"""
    estudiante_repo = SQLEstudianteRepository(db)
    user_repo = SQLUserRepository(db)
    return EstudianteUseCase(estudiante_repo, user_repo)


@router.get(
    "/",
    response_model=List[EstudianteResponse],
    status_code=status.HTTP_200_OK,
    summary="Obtener todos los estudiantes",
)
async def get_estudiantes(
    skip: int = Query(0, ge=0, le=10000, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    use_case: EstudianteUseCase = Depends(get_estudiante_use_case),
    current_user: User = Depends(require_permission(Permission.USER_READ_ALL)),
):
    """
    Obtener todos los estudiantes con paginación.
    
    NOTA: Los estudiantes se crean mediante POST /api/auth/register con rol="estudiante"
    
    RESPUESTA: EstudianteResponse con estructura limpia:
    - id: user_id (identificador principal)
    - nombre, email, matricula, activo
    - NO expone el ID interno de la tabla estudiante
    
    SEGURIDAD: 
    - Requiere permiso USER:READ:ALL (solo administradores)
    - Validación de parámetros de paginación (skip: 0-10000, limit: 1-1000)
    - Protección contra inyección SQL mediante ORM
    """
    try:
        estudiantes = use_case.get_all_estudiantes(skip=skip, limit=limit)
        # Convertir a EstudianteResponse
        return [EstudianteResponse.from_estudiante(est) for est in estudiantes]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor",
        )


@router.get(
    "/{user_id}",
    response_model=EstudianteResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener estudiante por user_id",
)
async def get_estudiante(
    user_id: int = Path(..., gt=0, description="ID del usuario (user_id, debe ser positivo)"),
    use_case: EstudianteUseCase = Depends(get_estudiante_use_case),
    current_user: User = Depends(require_permission(Permission.USER_READ)),
):
    """
    Obtener un estudiante por su user_id.
    
    IMPORTANTE: Se usa user_id como identificador, no el ID interno de la tabla estudiante.
    
    SEGURIDAD:
    - Requiere permiso USER:READ
    - Control de acceso horizontal: usuarios normales solo pueden ver su propia información
    - Administradores pueden ver cualquier estudiante
    - Validación de ID positivo (gt=0) para prevenir inyección
    - NO expone datos sensibles (contraseña, tokens, etc.)
    """
    try:
        # 🔒 CONTROL DE ACCESO HORIZONTAL (IDOR Prevention)
        # Los usuarios normales solo pueden ver su propia información
        if current_user.rol != "administrador" and current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para ver este estudiante",
            )
        
        estudiante = use_case.get_estudiante_by_user_id(user_id)
        return EstudianteResponse.from_estudiante(estudiante)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor",
        )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar estudiante",
)
async def delete_estudiante(
    user_id: int = Path(..., gt=0, description="ID del usuario (user_id, debe ser positivo)"),
    use_case: EstudianteUseCase = Depends(get_estudiante_use_case),
    current_user: User = Depends(require_permission(Permission.USER_DELETE)),
):
    """
    Eliminar un estudiante por su user_id.
    
    IMPORTANTE: 
    - Esto solo elimina el registro de estudiante, no el usuario completo
    - Para eliminar el usuario completo, usar DELETE /api/users/{user_id}
    
    SEGURIDAD: 
    - Requiere permiso USER:DELETE (solo administradores)
    - Validación de ID positivo (gt=0) para prevenir inyección
    - No permite auto-eliminación para prevenir DoS accidental
    """
    try:
        # 🔒 PREVENCIÓN: No permitir auto-eliminación
        if current_user.id == user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No puedes eliminar tu propio registro de estudiante",
            )
        
        deleted = use_case.delete_estudiante_by_user_id(user_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Estudiante con user_id {user_id} no encontrado",
            )
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor",
        )
