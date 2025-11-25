from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from application.use_cases.evento_use_cases import EventoUseCases
from domain.authorization import Permission
from domain.entities import Evento, EventoDetallado, User  # Response models
from domain.schemas import EventoSecureCreate, EventoSecurePatch  # ✅ SCHEMAS SEGUROS
from infrastructure.database.config import get_db
from infrastructure.dependencies import require_any_permission, require_permission
from infrastructure.repositories.docente_repository import DocenteRepository
from infrastructure.repositories.evento_repository import EventoRepository
from infrastructure.repositories.clase_repository import ClaseRepository

router = APIRouter()


def get_evento_use_cases(db: Session = Depends(get_db)) -> EventoUseCases:
    repo = EventoRepository(db)
    docente_repo = DocenteRepository(db)
    clase_repo = ClaseRepository(db)
    return EventoUseCases(repo, docente_repo, clase_repo)


@router.get(
    "/detallados",
    response_model=List[EventoDetallado],
    status_code=status.HTTP_200_OK,
    summary="Obtener eventos con detalles de clase",
    description="""
    Obtiene eventos con información enriquecida incluyendo:
    - Nombre y código de la asignatura
    - Código de la sección
    - Día de la semana del bloque
    - Horario del bloque
    - Código de la sala
    
    Si el evento no tiene clase_id, estos campos serán null.
    """,
    tags=["eventos"],
)
async def get_eventos_detallados(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=100, description="Número máximo de registros"),
    current_user: User = Depends(
        require_any_permission(
            Permission.EVENTO_READ_ALL,
            Permission.EVENTO_READ_OWN,
            Permission.EVENTO_READ,
        )
    ),
    use_cases: EventoUseCases = Depends(get_evento_use_cases),
):
    """
    Obtener eventos con detalles de clase según el rol del usuario.
    Útil para el frontend que necesita mostrar asignatura, día y horario.
    """
    try:
        eventos = use_cases.get_all_detallados(skip, limit)
        return eventos
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener los eventos: {str(e)}",
        )


@router.get(
    "/",
    response_model=List[Evento],
    status_code=status.HTTP_200_OK,
    summary="Obtener eventos",
    tags=["eventos"],
)
async def get_eventos(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=100, description="Número máximo de registros"),
    activos_solo: bool = Query(False, description="Filtrar solo eventos activos"),
    current_user: User = Depends(
        require_any_permission(
            Permission.EVENTO_READ_ALL,  # Admin: todos los eventos
            Permission.EVENTO_READ_OWN,  # Docente: solo los propios
            Permission.EVENTO_READ,  # Estudiante: consultar eventos
        )
    ),
    use_cases: EventoUseCases = Depends(get_evento_use_cases),
):
    """
    Obtener eventos según el rol del usuario:
    - Administradores: pueden ver todos los eventos
    - Docentes: pueden ver solo sus propios eventos
    - Estudiantes: pueden ver eventos activos
    """
    try:
        if current_user.rol == "administrador":
            if activos_solo:
                eventos = use_cases.get_all_active(skip, limit)
            else:
                eventos = use_cases.get_all(skip, limit)
        elif current_user.rol == "docente":
            if activos_solo:
                eventos = use_cases.get_active_by_docente_user(current_user, skip, limit)
            else:
                eventos = use_cases.get_by_docente_user(current_user, skip, limit)
        else:  # estudiante
            eventos = use_cases.get_all_active(skip, limit)
        
        return eventos
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener los eventos: {str(e)}",
        )


@router.get(
    "/{evento_id}",
    response_model=Evento,
    status_code=status.HTTP_200_OK,
    summary="Obtener evento por ID",
    tags=["eventos"],
)
async def obtener_evento(
    evento_id: int = Path(..., gt=0, description="ID del evento"),
    current_user: User = Depends(
        require_any_permission(
            Permission.EVENTO_READ_ALL,  # Admin: cualquier evento
            Permission.EVENTO_READ_OWN,  # Docente: solo los propios
            Permission.EVENTO_READ,  # Estudiante: consultar eventos
        )
    ),
    use_cases: EventoUseCases = Depends(get_evento_use_cases),
):
    """
    Obtener evento por ID (con verificación de propiedad para docentes)
    - Administradores y estudiantes: pueden ver cualquier evento
    - Docentes: solo pueden ver sus propios eventos
    """
    try:
        if current_user.rol == "administrador" or current_user.rol == "estudiante":
            evento = use_cases.get_by_id(evento_id)
        else:  # docente
            evento = use_cases.get_by_id_and_docente_user(evento_id, current_user)
        
        return evento
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener el evento: {str(e)}",
        )


@router.post(
    "/",
    response_model=Evento,
    status_code=status.HTTP_201_CREATED,
    summary="Crear evento",
    tags=["eventos"],
)
async def crear_evento(
    evento: EventoSecureCreate,
    current_user: User = Depends(
        require_any_permission(
            Permission.EVENTO_WRITE,  # Admin: crear cualquier evento
            Permission.EVENTO_WRITE_OWN,  # Docente: crear sus propios eventos
        )
    ),
    use_cases: EventoUseCases = Depends(get_evento_use_cases),
):
    """
    Crear un nuevo evento
    - Administradores: pueden crear eventos para cualquier docente
    - Docentes: solo pueden crear eventos para sí mismos
    """
    try:
        nuevo_evento = use_cases.create(evento, current_user)
        return nuevo_evento
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el evento: {str(e)}",
        )


@router.patch(
    "/{evento_id}",
    response_model=Evento,
    status_code=status.HTTP_200_OK,
    summary="Actualizar evento",
    tags=["eventos"],
)
async def actualizar_evento(
    evento_id: int = Path(..., gt=0, description="ID del evento"),
    evento_data: EventoSecurePatch = ...,
    current_user: User = Depends(
        require_any_permission(
            Permission.EVENTO_WRITE,  # Admin: modificar cualquier evento
            Permission.EVENTO_WRITE_OWN,  # Docente: modificar solo los propios
        )
    ),
    use_cases: EventoUseCases = Depends(get_evento_use_cases),
):
    """
    Actualizar evento existente (con verificación de propiedad para docentes)
    - Administradores: pueden modificar cualquier evento
    - Docentes: solo pueden modificar sus propios eventos
    """
    try:
        evento_actualizado = use_cases.update(evento_id, evento_data, current_user)
        return evento_actualizado
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar el evento: {str(e)}",
        )


@router.patch(
    "/{evento_id}/toggle",
    response_model=Evento,
    status_code=status.HTTP_200_OK,
    summary="Habilitar/Deshabilitar evento",
    tags=["eventos"],
)
async def toggle_evento(
    evento_id: int = Path(..., gt=0, description="ID del evento"),
    activo: bool = Query(..., description="Estado activo del evento"),
    current_user: User = Depends(require_permission(Permission.EVENTO_ACTIVATE)),
    use_cases: EventoUseCases = Depends(get_evento_use_cases),
):
    """
    Habilitar o deshabilitar un evento (solo administradores)
    - Permite a los administradores controlar la visibilidad de eventos
    """
    try:
        evento_actualizado = use_cases.toggle_active(evento_id, activo)
        return evento_actualizado
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al cambiar el estado del evento: {str(e)}",
        )


@router.delete(
    "/{evento_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar evento",
    tags=["eventos"],
)
async def eliminar_evento(
    evento_id: int = Path(..., gt=0, description="ID del evento"),
    current_user: User = Depends(
        require_any_permission(
            Permission.EVENTO_DELETE,  # Admin: eliminar cualquier evento
            Permission.EVENTO_DELETE_OWN,  # Docente: eliminar solo los propios
        )
    ),
    use_cases: EventoUseCases = Depends(get_evento_use_cases),
):
    """
    Eliminar evento (con verificación de propiedad para docentes)
    - Administradores: pueden eliminar cualquier evento
    - Docentes: solo pueden eliminar sus propios eventos
    """
    try:
        use_cases.delete(evento_id, current_user)
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar el evento: {str(e)}",
        )


@router.get(
    "/docente/{user_id}/eventos",
    response_model=List[Evento],
    status_code=status.HTTP_200_OK,
    summary="Obtener eventos de un docente específico",
    tags=["eventos"],
)
async def get_eventos_by_docente(
    user_id: int = Path(..., gt=0, description="ID del usuario docente"),
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=100, description="Número máximo de registros"),
    activos_solo: bool = Query(True, description="Filtrar solo eventos activos"),
    current_user: User = Depends(
        require_any_permission(
            Permission.EVENTO_READ_ALL,  # Admin: ver eventos de cualquier docente
            Permission.EVENTO_READ,  # Estudiante: ver eventos activos de docentes
        )
    ),
    use_cases: EventoUseCases = Depends(get_evento_use_cases),
):
    """
    Obtener eventos de un docente específico por su user_id
    - Administradores: pueden ver todos los eventos del docente
    - Estudiantes: solo pueden ver eventos activos del docente
    """
    try:
        eventos = use_cases.get_by_docente_id(user_id, activos_solo, skip, limit)
        return eventos
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener los eventos del docente: {str(e)}",
        )
