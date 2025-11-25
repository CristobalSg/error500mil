from fastapi import APIRouter, Depends, status

from app.fet.schemas import FetRunRequest, FetRunSummary
from app.fet.service import FetService
from app.settings import AppSettings, get_settings

router = APIRouter()


def get_fet_service(
    settings: AppSettings = Depends(get_settings),
) -> FetService:
    return FetService(settings=settings)


@router.post(
    "/run",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=FetRunSummary,
    summary="Ejecuta el algoritmo FET a partir de un payload ya consolidado",
)
async def run_fet(
    payload: FetRunRequest,
    service: FetService = Depends(get_fet_service),
) -> FetRunSummary:
    """
    Ejecuta el flujo completo de generación de horarios a partir de un payload ya consolidado:

    1. Valida y normaliza la data recibida.
    2. Genera el archivo .fet esperado por FET.
    3. Ejecuta el binario de FET y retorna un resumen simple.
    """
    return service.run(payload)
