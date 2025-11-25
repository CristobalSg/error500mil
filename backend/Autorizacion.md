# Sistema de Autorización Basado en Roles y Permisos

---

## 📚 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Arquitectura](#arquitectura)
3. [Componentes del Sistema](#componentes-del-sistema)
4. [Guía de Uso](#guía-de-uso)
5. [Ejemplos Prácticos](#ejemplos-prácticos)
6. [Matriz de Permisos](#matriz-de-permisos)
7. [Mejores Prácticas](#mejores-prácticas)
8. [Testing](#testing)
9. [Migración desde Sistema Anterior](#migración-desde-sistema-anterior)

---

## Introducción

El sistema de autorización basado en roles y permisos proporciona un control de acceso granular y centralizado para todas las operaciones del sistema.

### Características Principales

✅ **Control de acceso basado en roles (RBAC)**  
✅ **Permisos granulares por recurso y acción**  
✅ **Reglas de negocio centralizadas**  
✅ **Type-safe con enumeraciones**  
✅ **Fácil de testear y auditar**  
✅ **Compatible con arquitectura hexagonal**  

### Beneficios

- 🔒 **Seguridad**: Control preciso de quién puede hacer qué
- 📋 **Auditoría**: Fácil seguimiento de permisos
- 🧩 **Mantenibilidad**: Lógica centralizada
- 🚀 **Escalabilidad**: Fácil agregar nuevos roles/permisos
- ✨ **DX**: Autocompletado y validación en compile-time

---

## Arquitectura

El sistema sigue **arquitectura hexagonal** con separación clara de responsabilidades:

```
┌─────────────────────────────────────────────────────────────┐
│                    DOMAIN LAYER                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  domain/authorization.py                             │   │
│  │  - UserRole (enum)                                   │   │
│  │  - Permission (enum)                                 │   │
│  │  - ROLE_PERMISSIONS (matriz)                         │   │
│  │  - AuthorizationRules (reglas de negocio)            │   │
│  │  - PermissionChecker (utilidades)                    │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                 APPLICATION LAYER                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  application/services/authorization_service.py       │   │
│  │  - AuthorizationService                              │   │
│  │    · verify_permission()                             │   │
│  │    · verify_role()                                   │   │
│  │    · verify_can_access_user()                        │   │
│  │    · verify_can_access_restriccion()                 │   │
│  │    · etc.                                            │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│               INFRASTRUCTURE LAYER                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  infrastructure/dependencies.py                      │   │
│  │  - require_permission(permission)                    │   │
│  │  - require_role(role)                                │   │
│  │  - require_any_permission(*permissions)              │   │
│  │  - require_any_role(*roles)                          │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  infrastructure/controllers/*_controller.py          │   │
│  │  - Endpoints HTTP que usan las dependencies          │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Componentes del Sistema

### 1. **Roles (UserRole)**

Enumeración de roles de usuario en el sistema:

```python
class UserRole(str, Enum):
    ADMINISTRADOR = "administrador"
    DOCENTE = "docente"
    ESTUDIANTE = "estudiante"
```

### 2. **Permisos (Permission)**

Permisos granulares formato `RECURSO:ACCION`:

```python
class Permission(str, Enum):
    # Usuarios
    USER_READ = "user:read"
    USER_READ_ALL = "user:read:all"
    USER_WRITE = "user:write"
    USER_DELETE = "user:delete"
    
    # Docentes
    DOCENTE_READ = "docente:read"
    DOCENTE_WRITE = "docente:write"
    DOCENTE_DELETE = "docente:delete"
    
    # Restricciones
    RESTRICCION_READ = "restriccion:read"
    RESTRICCION_READ_OWN = "restriccion:read:own"
    RESTRICCION_WRITE = "restriccion:write"
    RESTRICCION_WRITE_OWN = "restriccion:write:own"
    
    # ... más permisos
```

### 3. **Matriz de Permisos (ROLE_PERMISSIONS)**

Mapeo de roles a permisos:

```python
ROLE_PERMISSIONS: Dict[UserRole, Set[Permission]] = {
    UserRole.ADMINISTRADOR: {
        Permission.USER_READ,
        Permission.USER_READ_ALL,
        Permission.USER_WRITE,
        # ... todos los permisos
    },
    UserRole.DOCENTE: {
        Permission.USER_READ,
        Permission.RESTRICCION_READ_OWN,
        Permission.RESTRICCION_WRITE_OWN,
        # ... permisos limitados
    },
    UserRole.ESTUDIANTE: {
        Permission.USER_READ,
        Permission.ASIGNATURA_READ,
        # ... solo lectura
    }
}
```

### 4. **Reglas de Negocio (AuthorizationRules)**

Lógica de negocio para casos especiales:

```python
class AuthorizationRules:
    @staticmethod
    def can_access_user_data(actor_role, actor_id, target_user_id):
        """Usuarios ven solo sus datos, admins ven todos"""
        
    @staticmethod
    def can_modify_restriccion(actor_role, actor_docente_id, restriccion_docente_id):
        """Docentes modifican solo sus restricciones"""
        
    # ... más reglas
```

### 5. **Servicio de Autorización (AuthorizationService)**

API principal para verificar permisos:

```python
class AuthorizationService:
    @staticmethod
    def verify_permission(user, permission):
        """Verificar permiso específico"""
        
    @staticmethod
    def verify_role(user, role):
        """Verificar rol específico"""
        
    @staticmethod
    def verify_can_access_user(actor, target_user_id):
        """Verificar acceso a usuario con reglas de negocio"""
        
    # ... más métodos
```

### 6. **Dependencies (FastAPI)**

Helpers para usar en endpoints:

```python
# Require permiso específico
require_permission(Permission.USER_DELETE)

# Require rol específico
require_role(UserRole.ADMINISTRADOR)

# Require uno de varios permisos
require_any_permission(Permission.X, Permission.Y)

# Require uno de varios roles
require_any_role(UserRole.ADMIN, UserRole.DOCENTE)
```

---

## Guía de Uso

### Opción 1: Usar Dependencies en Endpoints (Recomendado)

```python
from fastapi import APIRouter, Depends
from infrastructure.dependencies import require_permission, require_role
from domain.authorization import Permission, UserRole

router = APIRouter()

# Ejemplo 1: Permiso específico
@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_permission(Permission.USER_DELETE))
):
    # Si llegamos aquí, el usuario tiene el permiso
    # ...

# Ejemplo 2: Rol específico
@router.get("/admin/dashboard")
async def admin_dashboard(
    current_user: User = Depends(require_role(UserRole.ADMINISTRADOR))
):
    # Solo administradores
    # ...

# Ejemplo 3: Múltiples roles
@router.get("/restricciones")
async def get_restricciones(
    current_user: User = Depends(require_any_role(
        UserRole.ADMINISTRADOR,
        UserRole.DOCENTE
    ))
):
    # Admins o docentes
    # ...
```

### Opción 2: Verificar en Use Cases

```python
from application.services.authorization_service import AuthorizationService
from domain.authorization import Permission

class UserManagementUseCase:
    def get_user_by_id(self, actor: User, user_id: int) -> User:
        # 1. Verificar permiso básico
        AuthorizationService.verify_permission(actor, Permission.USER_READ)
        
        # 2. Verificar regla de negocio
        AuthorizationService.verify_can_access_user(actor, user_id)
        
        # 3. Ejecutar lógica
        return self.repository.get_by_id(user_id)
```

### Opción 3: Verificación Condicional

```python
from application.services.authorization_service import AuthorizationService

class RestriccionUseCase:
    def get_restricciones(self, actor: User) -> List[Restriccion]:
        # Lógica diferente según rol
        if AuthorizationService.is_admin(actor):
            # Admins ven todas
            return self.repository.get_all()
        elif AuthorizationService.is_docente(actor):
            # Docentes solo las suyas
            docente_id = self._get_docente_id(actor)
            return self.repository.get_by_docente(docente_id)
        else:
            raise HTTPException(403, "No autorizado")
```

---

## Ejemplos Prácticos

### Ejemplo 1: Endpoint de Lectura de Usuario

```python
# infrastructure/controllers/user_controller.py

from fastapi import APIRouter, Depends, Path
from infrastructure.dependencies import get_current_active_user
from application.services.authorization_service import AuthorizationService
from domain.authorization import Permission

router = APIRouter()

@router.get("/{user_id}", response_model=User)
async def get_user_by_id(
    user_id: int = Path(..., gt=0),
    current_user: User = Depends(get_current_active_user),
    use_case = Depends(get_user_use_case)
):
    """
    Obtener usuario por ID.
    
    Reglas:
    - Usuarios pueden ver solo sus propios datos
    - Administradores pueden ver cualquier usuario
    """
    # Verificación en el use case
    return use_case.get_user_by_id(current_user, user_id)


# application/use_cases/user_management_use_cases.py

class UserManagementUseCase:
    def get_user_by_id(self, actor: User, user_id: int) -> User:
        # Verificar permiso
        AuthorizationService.verify_permission(actor, Permission.USER_READ)
        
        # Verificar acceso (regla de negocio)
        AuthorizationService.verify_can_access_user(actor, user_id)
        
        # Obtener usuario
        user = self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(404, "Usuario no encontrado")
        
        return user
```

### Ejemplo 2: Endpoint de Eliminación de Sala

```python
# infrastructure/controllers/sala_controller.py

@router.delete("/{sala_id}", status_code=204)
async def delete_sala(
    sala_id: int,
    # ✅ Dependency verifica permiso automáticamente
    current_user: User = Depends(require_permission(Permission.SALA_DELETE)),
    use_case = Depends(get_sala_use_case)
):
    """
    Eliminar sala (solo administradores).
    
    El permiso SALA_DELETE solo lo tiene el rol ADMINISTRADOR.
    """
    use_case.delete_sala(sala_id)
```

### Ejemplo 3: Restricciones con Propiedad

```python
# infrastructure/controllers/restriccion_controller.py

@router.get("/", response_model=List[Restriccion])
async def get_restricciones(
    current_user: User = Depends(require_any_role(
        UserRole.ADMINISTRADOR,
        UserRole.DOCENTE
    )),
    use_case = Depends(get_restriccion_use_case)
):
    """
    Obtener restricciones.
    
    - Administradores: ven todas
    - Docentes: ven solo las suyas
    """
    return use_case.get_restricciones(current_user)


# application/use_cases/restriccion_use_cases.py

class RestriccionUseCases:
    def get_restricciones(self, actor: User) -> List[Restriccion]:
        if AuthorizationService.is_admin(actor):
            # Admin ve todas
            return self.repository.get_all()
        else:
            # Docente ve solo las suyas
            docente = self._get_docente_from_user(actor)
            return self.repository.get_by_docente(docente.id)
```

### Ejemplo 4: Verificación Compleja

```python
# application/use_cases/restriccion_use_cases.py

class RestriccionUseCases:
    def update_restriccion(
        self, 
        actor: User, 
        restriccion_id: int, 
        data: dict
    ) -> Restriccion:
        # 1. Obtener restricción
        restriccion = self.repository.get_by_id(restriccion_id)
        if not restriccion:
            raise HTTPException(404, "Restricción no encontrada")
        
        # 2. Verificar acceso
        actor_docente_id = None
        if AuthorizationService.is_docente(actor):
            docente = self._get_docente_from_user(actor)
            actor_docente_id = docente.id
        
        AuthorizationService.verify_can_access_restriccion(
            actor,
            restriccion.docente_id,
            actor_docente_id
        )
        
        # 3. Actualizar
        return self.repository.update(restriccion_id, data)
```

---

## Matriz de Permisos

### Administrador

| Recurso | Read | Read All | Write | Delete |
|---------|------|----------|-------|--------|
| Usuarios | ✅ | ✅ | ✅ | ✅ |
| Docentes | ✅ | ✅ | ✅ | ✅ |
| Estudiantes | ✅ | ✅ | ✅ | ✅ |
| Asignaturas | ✅ | ✅ | ✅ | ✅ |
| Secciones | ✅ | ✅ | ✅ | ✅ |
| Salas | ✅ | ✅ | ✅ | ✅ |
| Campus/Edificios | ✅ | ✅ | ✅ | ✅ |
| Restricciones | ✅ | ✅ | ✅ | ✅ |
| Clases | ✅ | ✅ | ✅ | ✅ |
| Bloques | ✅ | ✅ | ✅ | ✅ |
| Sistema | ✅ | ✅ | ✅ | ✅ |

### Docente

| Recurso | Read | Read All | Write | Delete |
|---------|------|----------|-------|--------|
| Usuarios | ✅ (propio) | ❌ | ❌ | ❌ |
| Docentes | ✅ | ❌ | ❌ | ❌ |
| Estudiantes | ❌ | ❌ | ❌ | ❌ |
| Asignaturas | ✅ | ❌ | ❌ | ❌ |
| Secciones | ✅ | ❌ | ❌ | ❌ |
| Salas | ✅ | ❌ | ❌ | ❌ |
| Campus/Edificios | ✅ | ❌ | ❌ | ❌ |
| **Restricciones** | **✅ (propias)** | **❌** | **✅ (propias)** | **✅ (propias)** |
| Clases | ✅ | ❌ | ❌ | ❌ |
| Bloques | ✅ | ❌ | ❌ | ❌ |
| Sistema | ❌ | ❌ | ❌ | ❌ |

### Estudiante

| Recurso | Read | Read All | Write | Delete |
|---------|------|----------|-------|--------|
| Usuarios | ✅ (propio) | ❌ | ❌ | ❌ |
| Docentes | ❌ | ❌ | ❌ | ❌ |
| Estudiantes | ❌ | ❌ | ❌ | ❌ |
| Asignaturas | ✅ | ❌ | ❌ | ❌ |
| Secciones | ✅ | ❌ | ❌ | ❌ |
| Salas | ✅ | ❌ | ❌ | ❌ |
| Campus/Edificios | ✅ | ❌ | ❌ | ❌ |
| Restricciones | ❌ | ❌ | ❌ | ❌ |
| Clases | ✅ | ❌ | ❌ | ❌ |
| Bloques | ✅ | ❌ | ❌ | ❌ |
| Sistema | ❌ | ❌ | ❌ | ❌ |

---

## Mejores Prácticas

### ✅ DO: Usar Dependencies para Endpoints

```python
# ✅ BIEN
@router.delete("/users/{id}")
async def delete_user(
    user_id: int,
    user: User = Depends(require_permission(Permission.USER_DELETE))
):
    ...
```

```python
# ❌ MAL
@router.delete("/users/{id}")
async def delete_user(
    user_id: int,
    user: User = Depends(get_current_active_user)
):
    if user.rol != "administrador":  # ❌ Lógica en controller
        raise HTTPException(403)
    ...
```

### ✅ DO: Verificar en Use Cases para Lógica Compleja

```python
# ✅ BIEN: Lógica en use case
class UserUseCase:
    def get_user(self, actor: User, target_id: int):
        AuthorizationService.verify_can_access_user(actor, target_id)
        return self.repo.get_by_id(target_id)
```

### ✅ DO: Usar Enums en Lugar de Strings

```python
# ✅ BIEN
AuthorizationService.verify_role(user, UserRole.ADMINISTRADOR)

# ❌ MAL
if user.rol == "administrador":  # Typo-prone
    ...
```

### ✅ DO: Centralizar Reglas de Negocio

```python
# ✅ BIEN: En AuthorizationRules
class AuthorizationRules:
    @staticmethod
    def can_modify_restriccion(actor_role, actor_id, restriccion_id):
        # Lógica centralizada
        ...

# ❌ MAL: Lógica dispersa en controllers
@router.put("/restricciones/{id}")
async def update(id: int, user: User):
    if user.rol == "docente":  # ❌ Lógica duplicada
        if user.docente.id != restriccion.docente_id:
            raise HTTPException(403)
    ...
```

### ✅ DO: Documentar Permisos en Endpoints

```python
@router.get("/{user_id}")
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtener usuario por ID.
    
    **Permisos requeridos:**
    - USER_READ
    
    **Reglas:**
    - Los usuarios pueden ver solo sus propios datos
    - Los administradores pueden ver cualquier usuario
    """
    ...
```

---

## Testing

### Unit Tests para Authorization

```python
# tests/test_authorization.py

import pytest
from domain.authorization import (
    UserRole, Permission, PermissionChecker,
    AuthorizationRules
)
from domain.entities import User

def test_admin_has_all_permissions():
    """Administrador tiene todos los permisos"""
    assert PermissionChecker.has_permission(
        UserRole.ADMINISTRADOR,
        Permission.USER_DELETE
    )
    assert PermissionChecker.has_permission(
        UserRole.ADMINISTRADOR,
        Permission.SALA_WRITE
    )

def test_docente_can_modify_own_restriccion():
    """Docente puede modificar solo sus restricciones"""
    assert AuthorizationRules.can_modify_restriccion(
        UserRole.DOCENTE,
        actor_docente_id=1,
        restriccion_docente_id=1
    )
    assert not AuthorizationRules.can_modify_restriccion(
        UserRole.DOCENTE,
        actor_docente_id=1,
        restriccion_docente_id=2  # Restricción de otro docente
    )

def test_estudiante_cannot_write():
    """Estudiante no puede escribir"""
    assert not PermissionChecker.has_permission(
        UserRole.ESTUDIANTE,
        Permission.USER_WRITE
    )
    assert not PermissionChecker.has_permission(
        UserRole.ESTUDIANTE,
        Permission.SALA_WRITE
    )
```

### Integration Tests para Endpoints

```python
# tests/test_user_controller_authorization.py

def test_user_cannot_access_other_user_data(client, auth_headers_user1, user2_id):
    """Usuario no puede acceder a datos de otro usuario"""
    response = client.get(
        f"/api/v1/users/{user2_id}",
        headers=auth_headers_user1
    )
    assert response.status_code == 403

def test_admin_can_access_any_user_data(client, auth_headers_admin, user1_id):
    """Administrador puede acceder a cualquier usuario"""
    response = client.get(
        f"/api/v1/users/{user1_id}",
        headers=auth_headers_admin
    )
    assert response.status_code == 200

def test_non_admin_cannot_delete_user(client, auth_headers_docente, user_id):
    """No administrador no puede eliminar usuarios"""
    response = client.delete(
        f"/api/v1/users/{user_id}",
        headers=auth_headers_docente
    )
    assert response.status_code == 403
```

---

## Migración desde Sistema Anterior

### Paso 1: Usar Métodos de Compatibilidad

El `AuthorizationService` mantiene métodos de compatibilidad:

```python
# Código anterior (sigue funcionando)
AuthorizationService.require_admin(user)
AuthorizationService.require_docente(user)

# Nuevo código (recomendado)
AuthorizationService.verify_role(user, UserRole.ADMINISTRADOR)
AuthorizationService.verify_permission(user, Permission.DOCENTE_WRITE)
```

### Paso 2: Migrar Dependencies Gradualmente

```python
# Anterior
@router.delete("/{id}")
async def delete(id: int, user: User = Depends(get_current_admin_user)):
    ...

# Nuevo (equivalente, más explícito)
@router.delete("/{id}")
async def delete(id: int, user: User = Depends(require_role(UserRole.ADMINISTRADOR))):
    ...

# O usando permisos
@router.delete("/{id}")
async def delete(id: int, user: User = Depends(require_permission(Permission.SALA_DELETE))):
    ...
```

### Paso 3: Agregar Permisos para Nuevos Recursos

```python
# 1. Agregar permisos en domain/authorization.py
class Permission(str, Enum):
    # Nuevos
    NUEVO_RECURSO_READ = "nuevo_recurso:read"
    NUEVO_RECURSO_WRITE = "nuevo_recurso:write"

# 2. Agregar a matriz de permisos
ROLE_PERMISSIONS = {
    UserRole.ADMINISTRADOR: {
        # ... permisos existentes
        Permission.NUEVO_RECURSO_READ,
        Permission.NUEVO_RECURSO_WRITE,
    }
}

# 3. Usar en endpoint
@router.post("/nuevo-recurso")
async def create(
    user: User = Depends(require_permission(Permission.NUEVO_RECURSO_WRITE))
):
    ...
```

---

## Configuración en Docker

El sistema se ejecuta con las variables de entorno de `.env.development`:

```bash
# Levantar contenedores
docker compose --env-file .env.development up -d

# Las variables de JWT ya están configuradas
```

No se requiere configuración adicional para el sistema de autorización.

---

## Resumen

### Lo que se agregó:

1. ✅ `domain/authorization.py` - Roles, permisos, reglas de negocio
2. ✅ `application/services/authorization_service.py` - Servicio de verificación
3. ✅ `infrastructure/dependencies.py` - Dependencies mejoradas
4. ✅ Documentación completa con ejemplos

### Cómo usar:

**En endpoints** (recomendado):
```python
@router.delete("/{id}")
async def delete(
    id: int,
    user: User = Depends(require_permission(Permission.RECURSO_DELETE))
):
    ...
```

**En use cases**:
```python
AuthorizationService.verify_permission(user, Permission.RECURSO_READ)
AuthorizationService.verify_can_access_user(actor, target_id)
```

### Próximos pasos:

1. Migrar endpoints existentes gradualmente
2. Agregar tests de autorización
3. Implementar logging de auditoría (siguiente fase)
4. Considerar ABAC para casos más complejos (futuro)

---

**Documentación completa del sistema de autorización basado en roles y permisos**
