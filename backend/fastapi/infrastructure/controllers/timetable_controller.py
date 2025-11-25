"""
Controlador para generación de horarios
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from application.services.timetable_service import TimetableService
from domain.authorization import Permission
from domain.entities import User
from domain.timetable_schemas import TimetableGenerationRequest, TimetableGenerationResponse
from infrastructure.database.config import get_db
from infrastructure.dependencies import require_permission
from infrastructure.repositories.asignatura_repository import AsignaturaRepository
from infrastructure.repositories.docente_repository import DocenteRepository
from infrastructure.repositories.edificio_repository import SQLEdificioRepository
from infrastructure.repositories.clase_repository import ClaseRepository
from infrastructure.repositories.sala_repository import SalaRepository
from infrastructure.repositories.seccion_repository import SeccionRepository
from infrastructure.repositories.user_repository import SQLUserRepository

router = APIRouter()


def get_timetable_service(db: Session = Depends(get_db)) -> TimetableService:
    """Dependencia para obtener el servicio de horarios"""
    return TimetableService(
        docente_repository=DocenteRepository(db),
        asignatura_repository=AsignaturaRepository(db),
        seccion_repository=SeccionRepository(db),
        clase_repository=ClaseRepository(db),
        sala_repository=SalaRepository(db),
        edificio_repository=SQLEdificioRepository(db),
        user_repository=SQLUserRepository(db),
    )


@router.post(
    "/generate",
    response_model=TimetableGenerationResponse,
    status_code=status.HTTP_200_OK,
    summary="Generar horario con FET",
    tags=["timetable"],
)
async def generate_timetable(
    semester: str,
    institution_name: str = "Departamento de Ingeniería Civil en Informática",
    current_user: User = Depends(require_permission(Permission.SYSTEM_CONFIG)),
    timetable_service: TimetableService = Depends(get_timetable_service),
):
    """
    Generar un horario completo usando el algoritmo FET.
    
    Este endpoint:
    1. Obtiene todos los docentes, asignaturas, secciones y restricciones
    2. Construye el JSON en formato FET
    3. Envía al agente para generar el horario
    4. Retorna el resultado
    
    Requiere permisos de administrador (SYSTEM:CONFIG).
    """
    try:
        result = await timetable_service.generate_timetable(semester, institution_name)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Error al generar horario: {str(e)}",
    )


@router.get(
    "/generate/preview",
    response_model=TimetableGenerationRequest,
    status_code=status.HTTP_200_OK,
    summary="Previsualizar payload que se enviaría al agente",
    tags=["timetable"],
)
async def preview_timetable_payload(
    semester: str,
    institution_name: str = "Departamento de Ingeniería Civil en Informática",
    current_user: User = Depends(require_permission(Permission.SYSTEM_CONFIG)),
    timetable_service: TimetableService = Depends(get_timetable_service),
):
    """
    Construye y retorna el JSON completo que se enviaría al agente para generar horarios,
    sin llamar al agente ni ejecutar la generación.
    """
    try:
        request = timetable_service.build_generation_request(semester, institution_name)
        return request
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al construir payload: {str(e)}",
        )


@router.get(
    "/status/{timetable_id}",
    status_code=status.HTTP_200_OK,
    summary="Consultar estado de generación",
    tags=["timetable"],
)
async def get_timetable_status(
    timetable_id: str,
    current_user: User = Depends(require_permission(Permission.SYSTEM_CONFIG)),
):
    """
    Consultar el estado de una generación de horario.
    
    Este endpoint permitirá verificar si el horario está listo,
    en proceso o ha fallado.
    
    TODO: Implementar cuando el agente soporte estados asíncronos.
    """
    return {
        "timetable_id": timetable_id,
        "status": "pending",
        "message": "Función no implementada aún",
    }
