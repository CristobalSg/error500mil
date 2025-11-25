from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from application.use_cases.restriccion_horario_use_cases import RestriccionHorarioUseCases
from domain.authorization import Permission
from domain.entities import RestriccionHorario, User  # Response models
from domain.schemas import (  # ✅ SCHEMAS SEGUROS
    RestriccionHorarioSecureCreate,
    RestriccionHorarioSecurePatch,
)
from infrastructure.database.config import get_db
from infrastructure.dependencies import require_any_permission, require_permission
from infrastructure.repositories.docente_repository import DocenteRepository
from infrastructure.repositories.restriccion_horario_repository import RestriccionHorarioRepository
from infrastructure.repositories.user_repository import SQLUserRepository

router = APIRouter()


def get_restriccion_horario_repository(
    db: Session = Depends(get_db),
) -> RestriccionHorarioRepository:
    """Dependency para obtener el repositorio de restricciones de horario"""
    return RestriccionHorarioRepository(db)


def get_restriccion_horario_use_cases(
    repository: RestriccionHorarioRepository = Depends(get_restriccion_horario_repository),
    db: Session = Depends(get_db),
) -> RestriccionHorarioUseCases:
    """Dependency para obtener los casos de uso de restricciones de horario"""
    docente_repo = DocenteRepository(db)
    user_repo = SQLUserRepository(db)
    return RestriccionHorarioUseCases(repository, docente_repo, user_repo)


@router.post(
    "/",
    response_model=RestriccionHorario,
    status_code=status.HTTP_201_CREATED,
    summary="Crear restricción de horario",
    description="""
    Crea una nueva restricción de horario para un docente.
    
    **IMPORTANTE**: Usa `user_id` (no `docente_id`) para consistencia con la API de docentes.
    Ejemplo: Si GET /api/docentes/25 funciona, usa user_id=25 aquí.
    
    Requiere permisos de administrador o coordinador.
    """,
)
def create_restriccion_horario(
    restriccion_data: RestriccionHorarioSecureCreate,
    restriccion_horario_use_cases: RestriccionHorarioUseCases = Depends(
        get_restriccion_horario_use_cases
    ),
    _: User = Depends(
        require_any_permission(Permission.RESTRICCION_HORARIO_WRITE, Permission.RESTRICCION_HORARIO_WRITE_OWN)
    ),
):
    """Crear una nueva restricción de horario con validaciones anti-inyección"""
    try:
        restriccion = restriccion_horario_use_cases.create(restriccion_data)
        return restriccion
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}",
        )


@router.get("/", response_model=List[RestriccionHorario], tags=["admin-restricciones-horario"])
async def obtener_restricciones_horario(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a devolver"),
    current_user: User = Depends(
        require_permission(Permission.RESTRICCION_HORARIO_READ_ALL)
    ),  # ✅ MIGRADO (admin)
    use_cases: RestriccionHorarioUseCases = Depends(get_restriccion_horario_use_cases),
):
    """Obtener todas las restricciones de horario con paginación (requiere permiso RESTRICCION_HORARIO:LIST - solo administradores)"""
    try:
        restricciones = use_cases.get_all(skip=skip, limit=limit)
        return restricciones
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}",
        )


@router.get(
    "/{restriccion_id}", response_model=RestriccionHorario, tags=["admin-restricciones-horario"]
)
async def obtener_restriccion_horario(
    restriccion_id: int,
    current_user: User = Depends(
        require_permission(Permission.RESTRICCION_HORARIO_READ)
    ),  # ✅ MIGRADO (admin)
    use_cases: RestriccionHorarioUseCases = Depends(get_restriccion_horario_use_cases),
):
    """Obtener una restricción de horario por ID (requiere permiso RESTRICCION_HORARIO:READ - solo administradores)"""
    try:
        restriccion = use_cases.get_by_id(restriccion_id)
        if not restriccion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Restricción de horario con ID {restriccion_id} no encontrada",
            )
        return restriccion
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}",
        )


@router.put(
    "/{restriccion_id}",
    response_model=RestriccionHorario,
    status_code=status.HTTP_200_OK,
    summary="Actualizar restricción de horario completa",
    tags=["admin-restricciones-horario"],
)
async def actualizar_restriccion_horario_completa(
    restriccion_id: int,
    restriccion_data: RestriccionHorarioSecurePatch,  # ✅ SCHEMA SEGURO PATCH
    current_user: User = Depends(require_permission(Permission.RESTRICCION_HORARIO_WRITE)),
    use_cases: RestriccionHorarioUseCases = Depends(get_restriccion_horario_use_cases),
):
    """Actualizar completamente una restricción de horario con validaciones anti-inyección (requiere permiso RESTRICCION_HORARIO:WRITE - solo administradores)"""
    try:
        restriccion = use_cases.update(restriccion_id, restriccion_data)
        return restriccion
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}",
        )


@router.patch(
    "/{restriccion_id}", response_model=RestriccionHorario, tags=["admin-restricciones-horario"]
)
async def actualizar_restriccion_horario_parcial(
    restriccion_patch: RestriccionHorarioSecurePatch,  # ✅ SCHEMA SEGURO
    restriccion_id: int = Path(..., gt=0, description="ID de la restricción de horario"),
    current_user: User = Depends(require_permission(Permission.RESTRICCION_HORARIO_WRITE)),
    use_cases: RestriccionHorarioUseCases = Depends(get_restriccion_horario_use_cases),
):
    """Actualizar parcialmente una restricción de horario con validaciones anti-inyección (requiere permiso RESTRICCION_HORARIO:WRITE - solo administradores)"""
    try:
        # El use case maneja la validación de campos vacíos
        restriccion = use_cases.update(restriccion_id, restriccion_patch)
        return restriccion
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}",
        )


@router.delete(
    "/{restriccion_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["admin-restricciones-horario"],
)
async def eliminar_restriccion_horario(
    restriccion_id: int,
    current_user: User = Depends(
        require_permission(Permission.RESTRICCION_HORARIO_DELETE)
    ),  # ✅ MIGRADO (admin)
    use_cases: RestriccionHorarioUseCases = Depends(get_restriccion_horario_use_cases),
):
    """Eliminar una restricción de horario (requiere permiso RESTRICCION_HORARIO:DELETE - solo administradores)"""
    try:
        use_cases.delete(restriccion_id)
        return
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}",
        )


# =====================================
# ENDPOINTS PARA DOCENTES (SUS PROPIAS RESTRICCIONES DE HORARIO)
# IMPORTANTE: Estas rutas deben ir ANTES de las rutas con parámetros dinámicos
# para evitar que FastAPI las confunda con /docente/{docente_id}
# =====================================


@router.get(
    "/docente/mis-restricciones",
    response_model=List[RestriccionHorario],
    tags=["docente-restricciones-horario"],
)
async def docente_get_mis_restricciones_horario(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a devolver"),
    current_user: User = Depends(
        require_any_permission(
            Permission.RESTRICCION_HORARIO_READ_ALL,  # Admin: todas
            Permission.RESTRICCION_HORARIO_READ_OWN,  # Docente: solo las propias
        )
    ),
    use_cases: RestriccionHorarioUseCases = Depends(get_restriccion_horario_use_cases),
):
    """Obtener las restricciones de horario del docente autenticado (requiere permiso RESTRICCION_HORARIO:READ:ALL o :READ:OWN)"""
    try:
        restricciones = use_cases.get_by_docente_user(current_user, skip=skip, limit=limit)
        return restricciones
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}",
        )


@router.post(
    "/docente/mis-restricciones",
    response_model=RestriccionHorario,
    status_code=status.HTTP_201_CREATED,
    tags=["docente-restricciones-horario"],
)
async def docente_crear_restriccion_horario(
    restriccion_data: RestriccionHorarioSecureCreate,  # ✅ SCHEMA SEGURO
    current_user: User = Depends(
        require_any_permission(
            Permission.RESTRICCION_HORARIO_WRITE,  # Admin: crear para cualquiera
            Permission.RESTRICCION_HORARIO_WRITE_OWN,  # Docente: crear para sí mismo
        )
    ),
    use_cases: RestriccionHorarioUseCases = Depends(get_restriccion_horario_use_cases),
):
    """Crear una nueva restricción de horario para el docente autenticado con validaciones anti-inyección (requiere permiso RESTRICCION_HORARIO:WRITE o :WRITE:OWN)"""
    try:
        restriccion = use_cases.create_for_docente_user(restriccion_data, current_user)
        return restriccion
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}",
        )


@router.get(
    "/docente/mis-restricciones/{restriccion_id}",
    response_model=RestriccionHorario,
    tags=["docente-restricciones-horario"],
)
async def docente_get_restriccion_horario(
    restriccion_id: int,
    current_user: User = Depends(
        require_any_permission(
            Permission.RESTRICCION_HORARIO_READ_ALL,  # Admin: cualquier restricción
            Permission.RESTRICCION_HORARIO_READ_OWN,  # Docente: solo las propias
        )
    ),
    use_cases: RestriccionHorarioUseCases = Depends(get_restriccion_horario_use_cases),
):
    """Obtener una restricción de horario específica del docente autenticado (requiere permiso RESTRICCION_HORARIO:READ:ALL o :READ:OWN)"""
    try:
        restriccion = use_cases.get_by_id_and_docente_user(restriccion_id, current_user)
        return restriccion
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}",
        )


@router.put(
    "/docente/mis-restricciones/{restriccion_id}",
    response_model=RestriccionHorario,
    status_code=status.HTTP_200_OK,
    summary="Actualizar restricción de horario completa (docente)",
    tags=["docente-restricciones-horario"],
)
async def docente_actualizar_restriccion_horario_completa(
    restriccion_id: int,
    restriccion_data: RestriccionHorarioSecurePatch,  # ✅ SCHEMA SEGURO PATCH
    current_user: User = Depends(
        require_any_permission(
            Permission.RESTRICCION_HORARIO_WRITE,  # Admin: actualizar cualquiera
            Permission.RESTRICCION_HORARIO_WRITE_OWN,  # Docente: actualizar solo las propias
        )
    ),
    use_cases: RestriccionHorarioUseCases = Depends(get_restriccion_horario_use_cases),
):
    """Actualizar completamente una restricción de horario del docente autenticado con validaciones anti-inyección (requiere permiso RESTRICCION_HORARIO:WRITE o :WRITE:OWN)"""
    try:
        restriccion = use_cases.update_for_docente_user(
            restriccion_id, current_user, restriccion_data
        )
        return restriccion
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}",
        )


@router.patch(
    "/docente/mis-restricciones/{restriccion_id}",
    response_model=RestriccionHorario,
    tags=["docente-restricciones-horario"],
)
async def docente_actualizar_restriccion_horario(
    restriccion_patch: RestriccionHorarioSecurePatch,  # ✅ SCHEMA SEGURO
    restriccion_id: int = Path(..., gt=0, description="ID de la restricción de horario"),
    current_user: User = Depends(
        require_any_permission(
            Permission.RESTRICCION_HORARIO_WRITE,  # Admin: actualizar cualquiera
            Permission.RESTRICCION_HORARIO_WRITE_OWN,  # Docente: actualizar solo las propias
        )
    ),
    use_cases: RestriccionHorarioUseCases = Depends(get_restriccion_horario_use_cases),
):
    """Actualizar parcialmente una restricción de horario del docente autenticado con validaciones anti-inyección (requiere permiso RESTRICCION_HORARIO:WRITE o :WRITE:OWN)"""
    try:
        # El use case maneja la validación de campos vacíos y verifica propiedad
        restriccion = use_cases.update_for_docente_user(
            restriccion_id, current_user, restriccion_patch
        )
        return restriccion
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}",
        )


@router.delete(
    "/docente/mis-restricciones/{restriccion_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["docente-restricciones-horario"],
)
async def docente_eliminar_restriccion_horario(
    restriccion_id: int,
    current_user: User = Depends(
        require_any_permission(
            Permission.RESTRICCION_HORARIO_DELETE,  # Admin: eliminar cualquiera
            Permission.RESTRICCION_HORARIO_DELETE_OWN,  # Docente: eliminar solo las propias
        )
    ),
    use_cases: RestriccionHorarioUseCases = Depends(get_restriccion_horario_use_cases),
):
    """Eliminar una restricción de horario del docente autenticado (requiere permiso RESTRICCION_HORARIO:DELETE o :DELETE:OWN)"""
    try:
        use_cases.delete_for_docente_user(restriccion_id, current_user)
        return
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}",
        )


@router.get(
    "/docente/mi-disponibilidad",
    response_model=List[RestriccionHorario],
    tags=["docente-restricciones-horario"],
)
async def docente_get_mi_disponibilidad(
    dia_semana: Optional[int] = Query(None, ge=0, le=6, description="Día de la semana (opcional)"),
    current_user: User = Depends(
        require_any_permission(
            Permission.RESTRICCION_HORARIO_READ_ALL,  # Admin: ver disponibilidad de todos
            Permission.RESTRICCION_HORARIO_READ_OWN,  # Docente: ver su propia disponibilidad
        )
    ),
    use_cases: RestriccionHorarioUseCases = Depends(get_restriccion_horario_use_cases),
):
    """Obtener la disponibilidad del docente autenticado (requiere permiso RESTRICCION_HORARIO:READ)"""
    try:
        disponibilidad = use_cases.get_disponibilidad_docente_user(current_user, dia_semana)
        return disponibilidad
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}",
        )


# =====================================
# ENDPOINTS ADMIN CON PARÁMETROS DINÁMICOS
# IMPORTANTE: Estas rutas van DESPUÉS de las rutas específicas
# =====================================


@router.get(
    "/docente/{user_id}",
    response_model=List[RestriccionHorario],
    tags=["admin-restricciones-horario"],
)
async def obtener_restricciones_por_docente(
    user_id: int = Path(..., gt=0, description="ID del usuario docente (user_id, no docente_id)"),
    current_user: User = Depends(
        require_permission(Permission.RESTRICCION_HORARIO_READ_ALL)
    ),  # ✅ MIGRADO (solo admin)
    use_cases: RestriccionHorarioUseCases = Depends(get_restriccion_horario_use_cases),
):
    """
    Obtener todas las restricciones de horario de un docente específico.
    
    **IMPORTANTE**: Usa user_id (no docente_id) para consistencia con la API de docentes.
    Ejemplo: Si GET /api/docentes/25 funciona, usa user_id=25 aquí.
    
    (requiere permiso RESTRICCION_HORARIO:LIST - solo administradores)
    """
    try:
        restricciones = use_cases.get_by_user_id(user_id)
        return restricciones
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}",
        )


@router.get(
    "/dia/{dia_semana}",
    response_model=List[RestriccionHorario],
    tags=["admin-restricciones-horario"],
)
async def obtener_restricciones_por_dia(
    dia_semana: int = Path(..., ge=0, le=6, description="Día de la semana (0=Domingo, 6=Sábado)"),
    current_user: User = Depends(
        require_permission(Permission.RESTRICCION_HORARIO_READ_ALL)
    ),  # ✅ MIGRADO (solo admin)
    use_cases: RestriccionHorarioUseCases = Depends(get_restriccion_horario_use_cases),
):
    """Obtener todas las restricciones de horario para un día específico de la semana (requiere permiso RESTRICCION_HORARIO:LIST - solo administradores)"""
    try:
        restricciones = use_cases.get_by_dia_semana(dia_semana)
        return restricciones
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}",
        )


@router.get(
    "/disponibilidad/{user_id}",
    response_model=List[RestriccionHorario],
    tags=["admin-restricciones-horario"],
)
async def obtener_disponibilidad_docente(
    user_id: int = Path(..., gt=0, description="ID del usuario docente (user_id, no docente_id)"),
    dia_semana: Optional[int] = Query(None, ge=0, le=6, description="Día de la semana (opcional)"),
    current_user: User = Depends(
        require_permission(Permission.RESTRICCION_HORARIO_READ)
    ),  # ✅ MIGRADO (solo admin)
    use_cases: RestriccionHorarioUseCases = Depends(get_restriccion_horario_use_cases),
):
    """
    Obtener la disponibilidad de un docente (solo restricciones marcadas como disponibles).
    
    **IMPORTANTE**: Usa user_id (no docente_id) para consistencia con la API de docentes.
    Ejemplo: Si GET /api/docentes/25 funciona, usa user_id=25 aquí.
    
    (requiere RESTRICCION_HORARIO:READ - Solo administradores)
    """
    try:
        disponibilidad = use_cases.get_disponibilidad_by_user_id(user_id, dia_semana)
        return disponibilidad
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}",
        )


@router.delete(
    "/docente/{user_id}", status_code=status.HTTP_200_OK, tags=["admin-restricciones-horario"]
)
async def eliminar_restricciones_por_docente(
    user_id: int = Path(..., gt=0, description="ID del usuario docente (user_id, no docente_id)"),
    current_user: User = Depends(
        require_permission(Permission.RESTRICCION_HORARIO_DELETE)
    ),  # ✅ MIGRADO (solo admin)
    use_cases: RestriccionHorarioUseCases = Depends(get_restriccion_horario_use_cases),
):
    """
    Eliminar todas las restricciones de horario de un docente.
    
    **IMPORTANTE**: Usa user_id (no docente_id) para consistencia con la API de docentes.
    Ejemplo: Si GET /api/docentes/25 funciona, usa user_id=25 aquí.
    
    (requiere permiso RESTRICCION_HORARIO:DELETE - solo administradores)
    """
    try:
        count = use_cases.delete_by_user_id(user_id)
        return {
            "mensaje": f"Se eliminaron {count} restricciones de horario del docente con user_id {user_id}",
            "eliminadas": count,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}",
        )
