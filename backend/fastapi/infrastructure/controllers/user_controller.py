from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from application.use_cases.user_management_use_cases import UserManagementUseCase
from domain.authorization import Permission  # ✅ Nuevo sistema
from domain.entities import User, UserUpdate
from infrastructure.dependencies import require_permission  # ✅ Nueva dependency
from infrastructure.dependencies import get_user_management_use_case

router = APIRouter()


@router.get("/", response_model=List[User], summary="Obtener todos los usuarios")
async def get_users(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a retornar"),
    user_use_case: UserManagementUseCase = Depends(get_user_management_use_case),
    current_user: User = Depends(require_permission(Permission.USER_READ_ALL)),
):
    """Obtener todos los usuarios con paginación (requiere permiso USER:READ:ALL)

    SEGURIDAD: Restringido a usuarios con permiso USER:READ:ALL (solo administradores).
    """
    try:
        users = user_use_case.get_all_users(skip=skip, limit=limit)
        return users
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor"
        )


@router.get("/{user_id}", response_model=User, summary="Obtener usuario por ID")
async def get_user_by_id(
    user_id: int = Path(..., gt=0, description="ID del usuario"),
    user_use_case: UserManagementUseCase = Depends(get_user_management_use_case),
    current_user: User = Depends(require_permission(Permission.USER_READ)),  # ✅ MIGRADO
):
    """Obtener un usuario por ID (requiere permiso USER:READ)

    SEGURIDAD:
    - Los usuarios pueden ver solo su propia información
    - Los administradores pueden ver cualquier usuario
    - La verificación de acceso horizontal se hace en el use case
    """
    try:
        # ✅ El use case verifica acceso horizontal
        user = user_use_case.get_user_by_id_with_authorization(current_user, user_id)
        return user
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor"
        )


@router.get("/email/{email}", response_model=User, summary="Obtener usuario por email")
async def get_user_by_email(
    email: str = Path(..., description="Email del usuario"),
    user_use_case: UserManagementUseCase = Depends(get_user_management_use_case),
    current_user: User = Depends(require_permission(Permission.USER_READ)),  # ✅ MIGRADO
):
    """Obtener un usuario por email (requiere permiso USER:READ)"""
    try:
        user = user_use_case.get_user_by_email(email)
        return user
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor"
        )


@router.get("/rol/{rol}", response_model=List[User], summary="Obtener usuarios por rol")
async def get_users_by_rol(
    rol: str = Path(..., description="Rol del usuario (administrador, docente, estudiante)"),
    user_use_case: UserManagementUseCase = Depends(get_user_management_use_case),
    current_user: User = Depends(require_permission(Permission.USER_READ_ALL)),
):
    """Obtener todos los usuarios con un rol específico (requiere permiso USER:READ:ALL)"""
    try:
        users = user_use_case.get_users_by_rol(rol)
        return users
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor"
        )


@router.get("/stats/count-by-role", summary="Contar usuarios por rol")
async def count_users_by_role(
    user_use_case: UserManagementUseCase = Depends(get_user_management_use_case),
    current_user: User = Depends(require_permission(Permission.USER_READ_ALL)),
):
    """
    Obtener el conteo total de usuarios agrupados por rol.
    
    Retorna un objeto con la cantidad de usuarios por cada rol:
    - docente: cantidad de docentes
    - estudiante: cantidad de estudiantes
    - administrador: cantidad de administradores
    
    Requiere permiso USER:READ:ALL (solo administradores).
    """
    try:
        counts = user_use_case.count_users_by_role()
        return {
            "total": sum(counts.values()),
            "by_role": counts
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Error interno del servidor"
        )


@router.put(
    "/{user_id}", response_model=User, status_code=status.HTTP_200_OK, summary="Actualizar usuario"
)
async def update_user(
    user_id: int = Path(..., gt=0, description="ID del usuario"),
    user_data: UserUpdate = None,
    user_use_case: UserManagementUseCase = Depends(get_user_management_use_case),
    current_user: User = Depends(require_permission(Permission.USER_WRITE)),  # ✅ MIGRADO
):
    """Actualizar información de un usuario (requiere permiso USER:WRITE)"""
    try:
        updated_user = user_use_case.update_user(user_id, user_data)
        return updated_user
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor"
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar usuario (soft delete)")
async def delete_user(
    user_id: int = Path(..., gt=0, description="ID del usuario"),
    user_use_case: UserManagementUseCase = Depends(get_user_management_use_case),
    current_user: User = Depends(require_permission(Permission.USER_DELETE)),  # ✅ MIGRADO
):
    """
    Soft delete de un usuario (requiere permiso USER:DELETE).
    
    El usuario NO se elimina físicamente, solo se marca con deleted_at timestamp.
    Se puede restaurar posteriormente con POST /users/{user_id}/restore.
    
    Para eliminación permanente (irreversible), usar DELETE /users/{user_id}/hard.
    """
    try:
        user_use_case.delete_user(user_id)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor"
        )


@router.patch(
    "/{user_id}/activate",
    response_model=User,
    status_code=status.HTTP_200_OK,
    summary="Activar usuario",
)
async def activate_user(
    user_id: int = Path(..., gt=0, description="ID del usuario"),
    user_use_case: UserManagementUseCase = Depends(get_user_management_use_case),
    current_user: User = Depends(require_permission(Permission.USER_ACTIVATE)),  # ✅ MIGRADO
):
    """Activar un usuario (requiere permiso USER:ACTIVATE)"""
    try:
        activated_user = user_use_case.activate_user(user_id)
        return activated_user
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor"
        )


@router.patch(
    "/{user_id}/deactivate",
    response_model=User,
    status_code=status.HTTP_200_OK,
    summary="Desactivar usuario",
)
async def deactivate_user(
    user_id: int = Path(..., gt=0, description="ID del usuario"),
    user_use_case: UserManagementUseCase = Depends(get_user_management_use_case),
    current_user: User = Depends(require_permission(Permission.USER_ACTIVATE)),  # ✅ MIGRADO
):
    """Desactivar un usuario (requiere permiso USER:ACTIVATE)"""
    try:
        deactivated_user = user_use_case.deactivate_user(user_id)
        return deactivated_user
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor"
        )


@router.post(
    "/{user_id}/restore",
    response_model=User,
    status_code=status.HTTP_200_OK,
    summary="Restaurar usuario eliminado",
)
async def restore_user(
    user_id: int = Path(..., gt=0, description="ID del usuario"),
    user_use_case: UserManagementUseCase = Depends(get_user_management_use_case),
    current_user: User = Depends(require_permission(Permission.USER_DELETE)),
):
    """
    Restaurar un usuario eliminado (soft delete).
    
    Requiere permiso USER:DELETE.
    Solo funciona con usuarios eliminados mediante soft delete.
    El usuario restaurado permanecerá inactivo hasta que se active explícitamente.
    """
    try:
        restored_user = user_use_case.restore_user(user_id)
        return restored_user
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor"
        )


@router.delete(
    "/{user_id}/hard",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar usuario permanentemente (hard delete)",
)
async def hard_delete_user(
    user_id: int = Path(..., gt=0, description="ID del usuario"),
    user_use_case: UserManagementUseCase = Depends(get_user_management_use_case),
    current_user: User = Depends(require_permission(Permission.USER_DELETE)),
):
    """
    Eliminación permanente de un usuario (hard delete).
    
    ⚠️ ADVERTENCIA: Esta operación es IRREVERSIBLE.
    Solo debe usarse en casos excepcionales (ej: cumplimiento GDPR, compliance legal).
    
    Requiere permiso USER:DELETE.
    Se recomienda usar soft delete (DELETE /users/{user_id}) en su lugar.
    """
    try:
        user_use_case.hard_delete_user(user_id)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor"
        )
