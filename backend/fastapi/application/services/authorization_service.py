"""
Servicio de Autorización - Application Layer
============================================

Implementa la lógica de verificación de permisos y autorización.
Usa las reglas definidas en la capa de dominio.

Arquitectura Hexagonal:
- Domain: Define reglas de negocio
- Application: Implementa casos de uso de autorización ← ESTE ARCHIVO
- Infrastructure: Aplica en endpoints y controllers
"""

from typing import List, Optional

from fastapi import HTTPException, status

from domain.authorization import (
    AuthorizationRules,
    InsufficientPermissionsError,
    OwnershipRequiredError,
    Permission,
    PermissionChecker,
    UserRole,
)
from domain.entities import User


class AuthorizationService:
    """
    Servicio de autorización del sistema.

    Proporciona métodos para verificar permisos y reglas de acceso.
    Centraliza toda la lógica de autorización para facilitar auditoría.
    """

    # ========================================================================
    # VERIFICACIÓN DE PERMISOS BÁSICOS
    # ========================================================================

    @staticmethod
    def verify_permission(user: User, permission: Permission) -> None:
        """
        Verificar que un usuario tenga un permiso específico.

        Args:
            user: Usuario a verificar
            permission: Permiso requerido

        Raises:
            HTTPException: Si el usuario no tiene el permiso
        """
        user_role = UserRole(user.rol)

        if not PermissionChecker.has_permission(user_role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permiso denegado: se requiere '{permission.value}'",
            )

    @staticmethod
    def verify_any_permission(user: User, permissions: List[Permission]) -> None:
        """
        Verificar que un usuario tenga al menos uno de los permisos.

        Args:
            user: Usuario a verificar
            permissions: Lista de permisos (requiere al menos uno)

        Raises:
            HTTPException: Si el usuario no tiene ninguno de los permisos
        """
        user_role = UserRole(user.rol)

        if not PermissionChecker.has_any_permission(user_role, permissions):
            perms_str = "', '".join([p.value for p in permissions])
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permiso denegado: se requiere uno de: '{perms_str}'",
            )

    @staticmethod
    def verify_all_permissions(user: User, permissions: List[Permission]) -> None:
        """
        Verificar que un usuario tenga todos los permisos.

        Args:
            user: Usuario a verificar
            permissions: Lista de permisos (requiere todos)

        Raises:
            HTTPException: Si el usuario no tiene todos los permisos
        """
        user_role = UserRole(user.rol)

        if not PermissionChecker.has_all_permissions(user_role, permissions):
            perms_str = "', '".join([p.value for p in permissions])
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permiso denegado: se requieren todos: '{perms_str}'",
            )

    # ========================================================================
    # VERIFICACIÓN DE ROLES
    # ========================================================================

    @staticmethod
    def verify_role(user: User, required_role: UserRole) -> None:
        """
        Verificar que un usuario tenga un rol específico.

        Args:
            user: Usuario a verificar
            required_role: Rol requerido

        Raises:
            HTTPException: Si el usuario no tiene el rol
        """
        if user.rol != required_role.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado: se requiere rol '{required_role.value}'",
            )

    @staticmethod
    def verify_any_role(user: User, required_roles: List[UserRole]) -> None:
        """
        Verificar que un usuario tenga uno de los roles especificados.

        Args:
            user: Usuario a verificar
            required_roles: Lista de roles válidos

        Raises:
            HTTPException: Si el usuario no tiene ninguno de los roles
        """
        if user.rol not in [role.value for role in required_roles]:
            roles_str = "', '".join([r.value for r in required_roles])
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado: se requiere uno de los roles: '{roles_str}'",
            )

    @staticmethod
    def is_admin(user: User) -> bool:
        """Verificar si el usuario es administrador"""
        return user.rol == UserRole.ADMINISTRADOR.value

    @staticmethod
    def is_docente(user: User) -> bool:
        """Verificar si el usuario es docente"""
        return user.rol == UserRole.DOCENTE.value

    @staticmethod
    def is_estudiante(user: User) -> bool:
        """Verificar si el usuario es estudiante"""
        return user.rol == UserRole.ESTUDIANTE.value

    # ========================================================================
    # VERIFICACIÓN DE ACCESO A USUARIOS
    # ========================================================================

    @staticmethod
    def verify_can_access_user(actor: User, target_user_id: int) -> None:
        """
        Verificar si un usuario puede acceder a datos de otro usuario.

        Regla: Los usuarios pueden ver solo sus propios datos,
               excepto administradores que pueden ver todos.

        Args:
            actor: Usuario que quiere acceder
            target_user_id: ID del usuario objetivo

        Raises:
            HTTPException: Si no tiene permiso
        """
        actor_role = UserRole(actor.rol)

        if not AuthorizationRules.can_access_user_data(actor_role, actor.id, target_user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos para acceder a este usuario",
            )

    @staticmethod
    def verify_can_list_all_users(user: User) -> None:
        """
        Verificar si un usuario puede listar todos los usuarios.

        Regla: Solo administradores

        Args:
            user: Usuario a verificar

        Raises:
            HTTPException: Si no es administrador
        """
        user_role = UserRole(user.rol)

        if not AuthorizationRules.can_list_all_users(user_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo administradores pueden listar todos los usuarios",
            )

    # ========================================================================
    # VERIFICACIÓN DE ACCESO A RESTRICCIONES
    # ========================================================================

    @staticmethod
    def verify_can_access_restriccion(
        actor: User, restriccion_docente_id: int, actor_docente_id: Optional[int] = None
    ) -> None:
        """
        Verificar si un usuario puede acceder a una restricción.

        Reglas:
        - Administradores: pueden acceder a cualquier restricción
        - Docentes: solo sus propias restricciones

        Args:
            actor: Usuario que quiere acceder
            restriccion_docente_id: ID del docente dueño de la restricción
            actor_docente_id: ID del docente del actor (si aplica)

        Raises:
            HTTPException: Si no tiene permiso
        """
        actor_role = UserRole(actor.rol)

        # Administradores tienen acceso total
        if actor_role == UserRole.ADMINISTRADOR:
            return

        # Docentes solo a sus propias restricciones
        if actor_role == UserRole.DOCENTE:
            if actor_docente_id is None:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="El docente no está correctamente configurado",
                )

            if actor_docente_id != restriccion_docente_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Solo puede acceder a sus propias restricciones",
                )
            return

        # Otros roles no tienen acceso
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para acceder a restricciones",
        )

    # ========================================================================
    # VERIFICACIÓN DE CREACIÓN DE RECURSOS
    # ========================================================================

    @staticmethod
    def verify_can_create_resource(user: User, resource_type: str) -> None:
        """
        Verificar si un usuario puede crear un tipo de recurso.

        Args:
            user: Usuario a verificar
            resource_type: Tipo de recurso (user, docente, sala, etc.)

        Raises:
            HTTPException: Si no tiene permiso
        """
        user_role = UserRole(user.rol)

        if not AuthorizationRules.can_create_resource(user_role, resource_type):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No tiene permisos para crear '{resource_type}'",
            )

    # ========================================================================
    # MÉTODOS DE CONVENIENCIA (Para mantener compatibilidad)
    # ========================================================================

    @staticmethod
    def require_admin(user: User) -> bool:
        """
        Verificar que el usuario sea administrador.

        DEPRECATED: Usar verify_role(user, UserRole.ADMINISTRADOR)
        Se mantiene por compatibilidad con código existente.
        """
        AuthorizationService.verify_role(user, UserRole.ADMINISTRADOR)
        return True

    @staticmethod
    def require_docente(user: User) -> bool:
        """
        Verificar que el usuario sea docente.

        DEPRECATED: Usar verify_role(user, UserRole.DOCENTE)
        Se mantiene por compatibilidad con código existente.
        """
        AuthorizationService.verify_role(user, UserRole.DOCENTE)
        return True

    @staticmethod
    def require_estudiante(user: User) -> bool:
        """
        Verificar que el usuario sea estudiante.

        DEPRECATED: Usar verify_role(user, UserRole.ESTUDIANTE)
        Se mantiene por compatibilidad con código existente.
        """
        AuthorizationService.verify_role(user, UserRole.ESTUDIANTE)
        return True

    @staticmethod
    def require_docente_or_admin(user: User) -> bool:
        """
        Verificar que el usuario sea docente o administrador.

        DEPRECATED: Usar verify_any_role(user, [UserRole.DOCENTE, UserRole.ADMINISTRADOR])
        Se mantiene por compatibilidad con código existente.
        """
        AuthorizationService.verify_any_role(user, [UserRole.DOCENTE, UserRole.ADMINISTRADOR])
        return True

    # ========================================================================
    # MÉTODOS DE INFORMACIÓN
    # ========================================================================

    @staticmethod
    def get_user_permissions(user: User) -> List[str]:
        """
        Obtener lista de permisos de un usuario.

        Args:
            user: Usuario

        Returns:
            Lista de strings con los permisos
        """
        user_role = UserRole(user.rol)
        permissions = PermissionChecker.get_user_permissions(user_role)
        return [perm.value for perm in permissions]

    @staticmethod
    def can_user_perform_action(user: User, resource_type: str, action: str) -> bool:
        """
        Verificar si un usuario puede realizar una acción sobre un recurso.

        Args:
            user: Usuario
            resource_type: Tipo de recurso
            action: Acción (read, write, delete)

        Returns:
            True si puede, False si no
        """
        user_role = UserRole(user.rol)

        # Construir el permiso
        permission_str = f"{resource_type}:{action}"

        # Verificar si el permiso existe
        try:
            permission = Permission(permission_str)
            return PermissionChecker.has_permission(user_role, permission)
        except ValueError:
            # El permiso no existe
            return False


# ============================================================================
# DOCUMENTACIÓN DE USO
# ============================================================================

"""
EJEMPLOS DE USO:

1. En Use Cases (Application Layer):

```python
from application.services.authorization_service import AuthorizationService
from domain.authorization import Permission

class UserManagementUseCase:
    def get_user_by_id(self, actor: User, user_id: int) -> User:
        # Verificar permiso básico
        AuthorizationService.verify_permission(actor, Permission.USER_READ)
        
        # Verificar acceso específico (regla de negocio)
        AuthorizationService.verify_can_access_user(actor, user_id)
        
        # Proceder con la lógica
        return self.repository.get_by_id(user_id)
    
    def list_all_users(self, actor: User) -> List[User]:
        # Verificar permiso
        AuthorizationService.verify_can_list_all_users(actor)
        
        # Proceder
        return self.repository.get_all()
```

2. En Controllers (Infrastructure Layer):

```python
@router.get("/{user_id}")
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    use_case: UserManagementUseCase = Depends(get_user_use_case)
):
    # La verificación se hace en el use case
    return use_case.get_user_by_id(current_user, user_id)
```

3. Usando Dependencies (Recomendado para endpoints):

```python
from infrastructure.dependencies import require_permission
from domain.authorization import Permission

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_permission(Permission.USER_DELETE)),
    use_case = Depends(get_user_use_case)
):
    return use_case.delete_user(user_id)
```

4. Verificación condicional:

```python
class RestriccionUseCase:
    def get_restricciones(self, actor: User) -> List[Restriccion]:
        # Admins ven todas, docentes solo las suyas
        if AuthorizationService.is_admin(actor):
            return self.repository.get_all()
        elif AuthorizationService.is_docente(actor):
            docente_id = self.get_docente_id(actor)
            return self.repository.get_by_docente(docente_id)
        else:
            raise HTTPException(403, "No autorizado")
```
"""
