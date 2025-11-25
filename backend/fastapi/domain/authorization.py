"""
Sistema de Autorización - Domain Layer
======================================

Define roles, permisos y reglas de acceso del sistema.
Esta es la capa de dominio, independiente de frameworks.

Arquitectura Hexagonal:
- Domain: Define QUÉ se puede hacer (reglas de negocio)
- Application: Define CÓMO se valida (casos de uso)
- Infrastructure: Define DÓNDE se aplica (endpoints, dependencies)
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Set

# ============================================================================
# ROLES DEL SISTEMA
# ============================================================================


class UserRole(str, Enum):
    """
    Roles de usuario en el sistema.

    Definidos como enumeración para:
    - Type safety
    - Autocompletado en IDEs
    - Validación en compile time
    - Documentación centralizada
    """

    ADMINISTRADOR = "administrador"
    DOCENTE = "docente"
    ESTUDIANTE = "estudiante"

    @classmethod
    def values(cls) -> List[str]:
        """Obtener lista de todos los roles válidos"""
        return [role.value for role in cls]

    @classmethod
    def is_valid(cls, role: str) -> bool:
        """Verificar si un rol es válido"""
        return role in cls.values()


# ============================================================================
# PERMISOS DEL SISTEMA
# ============================================================================


class Permission(str, Enum):
    """
    Permisos granulares del sistema.

    Formato: RECURSO_ACCION
    Ejemplo: USER_READ, USER_WRITE, USER_DELETE

    Permite control de acceso fino más allá de solo roles.
    """

    # Usuarios
    USER_READ = "user:read"
    USER_READ_ALL = "user:read:all"
    USER_CREATE = "user:create"
    USER_WRITE = "user:write"
    USER_DELETE = "user:delete"
    USER_ACTIVATE = "user:activate"

    # Docentes
    DOCENTE_READ = "docente:read"
    DOCENTE_WRITE = "docente:write"
    DOCENTE_DELETE = "docente:delete"

    # Estudiantes
    ESTUDIANTE_READ = "estudiante:read"
    ESTUDIANTE_WRITE = "estudiante:write"
    ESTUDIANTE_DELETE = "estudiante:delete"

    # Asignaturas
    ASIGNATURA_READ = "asignatura:read"
    ASIGNATURA_WRITE = "asignatura:write"
    ASIGNATURA_DELETE = "asignatura:delete"

    # Secciones
    SECCION_READ = "seccion:read"
    SECCION_WRITE = "seccion:write"
    SECCION_DELETE = "seccion:delete"

    # Salas
    SALA_READ = "sala:read"
    SALA_WRITE = "sala:write"
    SALA_DELETE = "sala:delete"

    # Campus y Edificios
    CAMPUS_READ = "campus:read"
    CAMPUS_WRITE = "campus:write"
    CAMPUS_DELETE = "campus:delete"

    EDIFICIO_READ = "edificio:read"
    EDIFICIO_WRITE = "edificio:write"
    EDIFICIO_DELETE = "edificio:delete"

    # Restricciones
    RESTRICCION_READ = "restriccion:read"
    RESTRICCION_READ_OWN = "restriccion:read:own"
    RESTRICCION_WRITE = "restriccion:write"
    RESTRICCION_WRITE_OWN = "restriccion:write:own"
    RESTRICCION_DELETE = "restriccion:delete"
    RESTRICCION_DELETE_OWN = "restriccion:delete:own"
    RESTRICCION_READ_ALL = "restriccion:read:all"

    # Restricciones de Horario
    RESTRICCION_HORARIO_READ = "restriccion_horario:read"
    RESTRICCION_HORARIO_READ_OWN = "restriccion_horario:read:own"
    RESTRICCION_HORARIO_READ_ALL = "restriccion_horario:read:all"
    RESTRICCION_HORARIO_WRITE = "restriccion_horario:write"
    RESTRICCION_HORARIO_WRITE_OWN = "restriccion_horario:write:own"
    RESTRICCION_HORARIO_DELETE = "restriccion_horario:delete"
    RESTRICCION_HORARIO_DELETE_OWN = "restriccion_horario:delete:own"

    # Clases
    CLASE_READ = "clase:read"
    CLASE_WRITE = "clase:write"
    CLASE_DELETE = "clase:delete"

    # Bloques
    BLOQUE_READ = "bloque:read"
    BLOQUE_WRITE = "bloque:write"
    BLOQUE_DELETE = "bloque:delete"

    # Eventos
    EVENTO_READ = "evento:read"
    EVENTO_READ_OWN = "evento:read:own"
    EVENTO_READ_ALL = "evento:read:all"
    EVENTO_WRITE = "evento:write"
    EVENTO_WRITE_OWN = "evento:write:own"
    EVENTO_DELETE = "evento:delete"
    EVENTO_DELETE_OWN = "evento:delete:own"
    EVENTO_ACTIVATE = "evento:activate"

    # Sistema
    SYSTEM_CONFIG = "system:config"
    SYSTEM_LOGS = "system:logs"


# ============================================================================
# MATRIZ DE PERMISOS POR ROL
# ============================================================================

ROLE_PERMISSIONS: Dict[UserRole, Set[Permission]] = {
    # ADMINISTRADOR: Acceso total al sistema
    UserRole.ADMINISTRADOR: {
        # Usuarios
        Permission.USER_READ,
        Permission.USER_READ_ALL,
        Permission.USER_CREATE,
        Permission.USER_WRITE,
        Permission.USER_DELETE,
        Permission.USER_ACTIVATE,
        # Docentes
        Permission.DOCENTE_READ,
        Permission.DOCENTE_WRITE,
        Permission.DOCENTE_DELETE,
        # Estudiantes
        Permission.ESTUDIANTE_READ,
        Permission.ESTUDIANTE_WRITE,
        Permission.ESTUDIANTE_DELETE,
        # Asignaturas
        Permission.ASIGNATURA_READ,
        Permission.ASIGNATURA_WRITE,
        Permission.ASIGNATURA_DELETE,
        # Secciones
        Permission.SECCION_READ,
        Permission.SECCION_WRITE,
        Permission.SECCION_DELETE,
        # Salas
        Permission.SALA_READ,
        Permission.SALA_WRITE,
        Permission.SALA_DELETE,
        # Campus y Edificios
        Permission.CAMPUS_READ,
        Permission.CAMPUS_WRITE,
        Permission.CAMPUS_DELETE,
        Permission.EDIFICIO_READ,
        Permission.EDIFICIO_WRITE,
        Permission.EDIFICIO_DELETE,
        # Restricciones
        Permission.RESTRICCION_READ,
        Permission.RESTRICCION_WRITE,
        Permission.RESTRICCION_DELETE,
        Permission.RESTRICCION_READ_ALL,
        # Restricciones de Horario
        Permission.RESTRICCION_HORARIO_READ,
        Permission.RESTRICCION_HORARIO_READ_ALL,
        Permission.RESTRICCION_HORARIO_WRITE,
        Permission.RESTRICCION_HORARIO_DELETE,
        # Clases
        Permission.CLASE_READ,
        Permission.CLASE_WRITE,
        Permission.CLASE_DELETE,
        # Bloques
        Permission.BLOQUE_READ,
        Permission.BLOQUE_WRITE,
        Permission.BLOQUE_DELETE,
        # Eventos
        Permission.EVENTO_READ,
        Permission.EVENTO_READ_ALL,
        Permission.EVENTO_WRITE,
        Permission.EVENTO_DELETE,
        Permission.EVENTO_ACTIVATE,
        # Sistema
        Permission.SYSTEM_CONFIG,
        Permission.SYSTEM_LOGS,
    },
    # DOCENTE: Gestión de sus propios datos y restricciones
    UserRole.DOCENTE: {
        # Lectura general
        Permission.USER_READ,  # Puede ver su propio perfil
        Permission.DOCENTE_READ,
        Permission.ASIGNATURA_READ,
        Permission.SECCION_READ,
        Permission.SALA_READ,
        Permission.CAMPUS_READ,
        Permission.EDIFICIO_READ,
        Permission.CLASE_READ,
        Permission.BLOQUE_READ,
        # Gestión de restricciones propias
        Permission.RESTRICCION_READ_OWN,
        Permission.RESTRICCION_WRITE_OWN,
        Permission.RESTRICCION_DELETE_OWN,
        # Gestión de restricciones de horario propias
        Permission.RESTRICCION_HORARIO_READ_OWN,
        Permission.RESTRICCION_HORARIO_WRITE_OWN,
        Permission.RESTRICCION_HORARIO_DELETE_OWN,
        # Gestión de eventos propios
        Permission.EVENTO_READ_OWN,
        Permission.EVENTO_WRITE_OWN,
        Permission.EVENTO_DELETE_OWN,
    },
    # ESTUDIANTE: Solo lectura de información pública y sus propios datos
    UserRole.ESTUDIANTE: {
        Permission.USER_READ,  # Su propio perfil
        Permission.ESTUDIANTE_READ,  # Sus propios datos de estudiante
        Permission.ASIGNATURA_READ,
        Permission.SECCION_READ,
        Permission.SALA_READ,
        Permission.CAMPUS_READ,
        Permission.EDIFICIO_READ,
        Permission.CLASE_READ,
        Permission.BLOQUE_READ,
        # Consulta de eventos
        Permission.EVENTO_READ,
    },
}


# ============================================================================
# REGLAS DE NEGOCIO
# ============================================================================


@dataclass
class AccessRule:
    """
    Regla de acceso para un recurso específico.

    Define condiciones adicionales más allá de permisos básicos.
    Por ejemplo: "Un docente solo puede modificar sus propias restricciones"
    """

    resource_type: str
    action: str
    requires_ownership: bool = False
    custom_validator: Optional[callable] = None
    description: str = ""


class AuthorizationRules:
    """
    Reglas de autorización del dominio.

    Define la lógica de negocio para control de acceso.
    """

    @staticmethod
    def can_access_user_data(actor_role: UserRole, actor_id: int, target_user_id: int) -> bool:
        """
        Verificar si un usuario puede acceder a datos de otro usuario.

        Reglas:
        - Administradores: pueden acceder a cualquier usuario
        - Usuarios normales: solo sus propios datos
        """
        if actor_role == UserRole.ADMINISTRADOR:
            return True
        return actor_id == target_user_id

    @staticmethod
    def can_modify_restriccion(
        actor_role: UserRole, actor_docente_id: Optional[int], restriccion_docente_id: int
    ) -> bool:
        """
        Verificar si un usuario puede modificar una restricción.

        Reglas:
        - Administradores: pueden modificar cualquier restricción
        - Docentes: solo sus propias restricciones
        """
        if actor_role == UserRole.ADMINISTRADOR:
            return True

        if actor_role == UserRole.DOCENTE:
            return actor_docente_id == restriccion_docente_id

        return False

    @staticmethod
    def can_list_all_users(actor_role: UserRole) -> bool:
        """
        Verificar si un usuario puede listar todos los usuarios.

        Reglas:
        - Solo administradores pueden listar todos los usuarios
        """
        return actor_role == UserRole.ADMINISTRADOR

    @staticmethod
    def can_create_resource(actor_role: UserRole, resource_type: str) -> bool:
        """
        Verificar si un usuario puede crear un tipo de recurso.

        Reglas generales:
        - Administradores: pueden crear cualquier recurso
        - Docentes: pueden crear sus propias restricciones
        - Estudiantes: no pueden crear recursos administrativos
        """
        admin_only_resources = [
            "user",
            "docente",
            "estudiante",
            "asignatura",
            "seccion",
            "sala",
            "campus",
            "edificio",
            "bloque",
            "clase",
        ]

        if resource_type in admin_only_resources:
            return actor_role == UserRole.ADMINISTRADOR

        if resource_type == "restriccion":
            return actor_role in [UserRole.ADMINISTRADOR, UserRole.DOCENTE]

        return False


# ============================================================================
# UTILIDADES
# ============================================================================


class PermissionChecker:
    """
    Verificador de permisos.

    Proporciona métodos útiles para verificar permisos de forma legible.
    """

    @staticmethod
    def has_permission(user_role: UserRole, permission: Permission) -> bool:
        """Verificar si un rol tiene un permiso específico"""
        role_perms = ROLE_PERMISSIONS.get(user_role, set())
        return permission in role_perms

    @staticmethod
    def has_any_permission(user_role: UserRole, permissions: List[Permission]) -> bool:
        """Verificar si un rol tiene al menos uno de los permisos"""
        role_perms = ROLE_PERMISSIONS.get(user_role, set())
        return any(perm in role_perms for perm in permissions)

    @staticmethod
    def has_all_permissions(user_role: UserRole, permissions: List[Permission]) -> bool:
        """Verificar si un rol tiene todos los permisos"""
        role_perms = ROLE_PERMISSIONS.get(user_role, set())
        return all(perm in role_perms for perm in permissions)

    @staticmethod
    def get_user_permissions(user_role: UserRole) -> Set[Permission]:
        """Obtener todos los permisos de un rol"""
        return ROLE_PERMISSIONS.get(user_role, set())


# ============================================================================
# EXCEPCIONES DE DOMINIO
# ============================================================================


class AuthorizationError(Exception):
    """Excepción base para errores de autorización"""

    pass


class InsufficientPermissionsError(AuthorizationError):
    """Usuario no tiene los permisos necesarios"""

    def __init__(self, required_permission: Permission, user_role: UserRole):
        self.required_permission = required_permission
        self.user_role = user_role
        super().__init__(
            f"El rol '{user_role.value}' no tiene el permiso '{required_permission.value}'"
        )


class OwnershipRequiredError(AuthorizationError):
    """Se requiere ser propietario del recurso"""

    def __init__(self, resource_type: str):
        self.resource_type = resource_type
        super().__init__(f"Solo el propietario puede acceder a este {resource_type}")


# ============================================================================
# DOCUMENTACIÓN DE USO
# ============================================================================

"""
EJEMPLO DE USO EN APPLICATION LAYER:

```python
from domain.authorization import (
    UserRole, Permission, PermissionChecker,
    AuthorizationRules, InsufficientPermissionsError
)

class UserService:
    def get_user_by_id(self, actor: User, target_user_id: int) -> User:
        # Verificar permiso básico
        if not PermissionChecker.has_permission(
            UserRole(actor.rol), 
            Permission.USER_READ
        ):
            raise InsufficientPermissionsError(
                Permission.USER_READ, 
                UserRole(actor.rol)
            )
        
        # Verificar regla de negocio
        if not AuthorizationRules.can_access_user_data(
            UserRole(actor.rol),
            actor.id,
            target_user_id
        ):
            raise HTTPException(status_code=403, detail="Acceso denegado")
        
        # Proceder con la lógica
        return self.repository.get_by_id(target_user_id)
```

EJEMPLO DE USO EN INFRASTRUCTURE LAYER (Dependencies):

```python
from domain.authorization import UserRole, Permission, PermissionChecker

def require_permission(permission: Permission):
    def dependency(current_user: User = Depends(get_current_user)):
        if not PermissionChecker.has_permission(
            UserRole(current_user.rol),
            permission
        ):
            raise HTTPException(status_code=403, detail="Permiso denegado")
        return current_user
    return dependency

# Uso en endpoint
@router.get("/admin/users")
async def list_users(
    user: User = Depends(require_permission(Permission.USER_READ_ALL))
):
    # ...
```
"""
