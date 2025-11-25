from typing import Callable, Optional

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from application.services.authorization_service import AuthorizationService
from application.use_cases.user_auth_use_cases import UserAuthUseCase
from application.use_cases.user_management_use_cases import UserManagementUseCase
from application.use_cases.password_reset_use_case import PasswordResetUseCase
from domain.authorization import Permission, UserRole
from domain.entities import User
from infrastructure.database.config import get_db
from infrastructure.repositories.administrador_repository import SQLAdministradorRepository
from infrastructure.repositories.docente_repository import DocenteRepository
from infrastructure.repositories.estudiante_repository import SQLEstudianteRepository
from infrastructure.repositories.user_repository import SQLUserRepository


def get_user_repository(db: Session = Depends(get_db)) -> SQLUserRepository:
    """Dependency para obtener el repositorio de usuarios"""
    return SQLUserRepository(db)


def get_docente_repository(db: Session = Depends(get_db)) -> DocenteRepository:
    """Dependency para obtener el repositorio de docentes"""
    return DocenteRepository(db)


def get_estudiante_repository(db: Session = Depends(get_db)) -> SQLEstudianteRepository:
    """Dependency para obtener el repositorio de estudiantes"""
    return SQLEstudianteRepository(db)


def get_administrador_repository(db: Session = Depends(get_db)) -> SQLAdministradorRepository:
    """Dependency para obtener el repositorio de administradores"""
    return SQLAdministradorRepository(db)


def get_user_auth_use_case(session: Session = Depends(get_db)) -> UserAuthUseCase:
    """Dependencia para obtener el caso de uso de autenticación de usuarios"""
    from infrastructure.repositories.docente_repository import DocenteRepository
    from infrastructure.repositories.estudiante_repository import SQLEstudianteRepository
    from infrastructure.repositories.administrador_repository import SQLAdministradorRepository
    
    user_repository = SQLUserRepository(session)
    docente_repository = DocenteRepository(session)
    estudiante_repository = SQLEstudianteRepository(session)
    administrador_repository = SQLAdministradorRepository(session)
    
    return UserAuthUseCase(
        user_repository,
        docente_repository,
        estudiante_repository,
        administrador_repository
    )


def get_password_reset_use_case(session: Session = Depends(get_db)) -> PasswordResetUseCase:
    """Dependencia para obtener el caso de uso de recuperación de contraseñas"""
    user_repository = SQLUserRepository(session)
    return PasswordResetUseCase(user_repository)


def get_token_from_header(authorization: Optional[str] = Header(None)) -> str:
    """Extraer token del header Authorization"""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autorización requerido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token debe ser de tipo Bearer",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return token
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Esquema de autorización inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(
    token: str = Depends(get_token_from_header),
    auth_use_case: UserAuthUseCase = Depends(get_user_auth_use_case),
) -> User:
    """Dependency para obtener el usuario actual desde el token"""
    return auth_use_case.get_current_active_user(token)


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Dependency para obtener el usuario actual activo"""
    if not current_user.activo:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario inactivo")
    return current_user


def get_current_admin_user(
    current_user: User = Depends(get_current_active_user),
    auth_use_case: UserAuthUseCase = Depends(get_user_auth_use_case),
) -> User:
    """Dependency para obtener el usuario actual que debe ser administrador"""
    auth_use_case.require_admin(current_user)
    return current_user


def get_current_docente_user(
    current_user: User = Depends(get_current_active_user),
    auth_use_case: UserAuthUseCase = Depends(get_user_auth_use_case),
) -> User:
    """Dependency para obtener el usuario actual que debe ser docente"""
    auth_use_case.require_docente(current_user)
    return current_user


def get_current_estudiante_user(
    current_user: User = Depends(get_current_active_user),
    auth_use_case: UserAuthUseCase = Depends(get_user_auth_use_case),
) -> User:
    """Dependency para obtener el usuario actual que debe ser estudiante"""
    auth_use_case.require_estudiante(current_user)
    return current_user


def get_current_docente_or_admin_user(
    current_user: User = Depends(get_current_active_user),
    auth_use_case: UserAuthUseCase = Depends(get_user_auth_use_case),
) -> User:
    """Dependency para obtener el usuario actual que debe ser docente o administrador"""
    auth_use_case.require_docente_or_admin(current_user)
    return current_user


def get_user_management_use_case(
    user_repository: SQLUserRepository = Depends(get_user_repository),
) -> UserManagementUseCase:
    return UserManagementUseCase(user_repository)


def get_password_reset_use_case(
    user_repository: SQLUserRepository = Depends(get_user_repository),
) -> PasswordResetUseCase:
    """Dependency para obtener el caso de uso de recuperación de contraseñas"""
    return PasswordResetUseCase(user_repository)


# ============================================================================
# NUEVAS DEPENDENCIES BASADAS EN PERMISOS
# ============================================================================


def require_permission(permission: Permission) -> Callable:
    """
    Factory de dependency para requerir un permiso específico.

    Uso:
        @router.delete("/users/{user_id}")
        async def delete_user(
            user_id: int,
            current_user: User = Depends(require_permission(Permission.USER_DELETE))
        ):
            ...

    Args:
        permission: Permiso requerido

    Returns:
        Dependency function que verifica el permiso
    """

    def permission_dependency(current_user: User = Depends(get_current_active_user)) -> User:
        AuthorizationService.verify_permission(current_user, permission)
        return current_user

    return permission_dependency


def require_any_permission(*permissions: Permission) -> Callable:
    """
    Factory de dependency para requerir al menos uno de varios permisos.

    Uso:
        @router.get("/restricciones")
        async def get_restricciones(
            user: User = Depends(require_any_permission(
                Permission.RESTRICCION_READ,
                Permission.RESTRICCION_READ_OWN
            ))
        ):
            ...

    Args:
        *permissions: Permisos (requiere al menos uno)

    Returns:
        Dependency function que verifica los permisos
    """

    def permission_dependency(current_user: User = Depends(get_current_active_user)) -> User:
        AuthorizationService.verify_any_permission(current_user, list(permissions))
        return current_user

    return permission_dependency


def require_role(role: UserRole) -> Callable:
    """
    Factory de dependency para requerir un rol específico.

    Uso:
        @router.get("/admin/settings")
        async def admin_settings(
            current_user: User = Depends(require_role(UserRole.ADMINISTRADOR))
        ):
            ...

    Args:
        role: Rol requerido

    Returns:
        Dependency function que verifica el rol
    """

    def role_dependency(current_user: User = Depends(get_current_active_user)) -> User:
        AuthorizationService.verify_role(current_user, role)
        return current_user

    return role_dependency


def require_any_role(*roles: UserRole) -> Callable:
    """
    Factory de dependency para requerir uno de varios roles.

    Uso:
        @router.get("/restricciones")
        async def get_restricciones(
            user: User = Depends(require_any_role(
                UserRole.ADMINISTRADOR,
                UserRole.DOCENTE
            ))
        ):
            ...

    Args:
        *roles: Roles válidos (requiere al menos uno)

    Returns:
        Dependency function que verifica los roles
    """

    def role_dependency(current_user: User = Depends(get_current_active_user)) -> User:
        AuthorizationService.verify_any_role(current_user, list(roles))
        return current_user

    return role_dependency
