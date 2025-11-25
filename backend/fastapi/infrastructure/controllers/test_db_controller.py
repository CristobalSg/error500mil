from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from domain.models import Docente
from infrastructure.database.config import get_db

router = APIRouter(tags=["test"])


@router.get("/test-db", summary="Probar conexión a la base de datos")
async def test_database(db: Session = Depends(get_db)):
    try:
        # Intentar hacer una consulta simple
        docente = db.query(Docente).first()
        return {
            "status": "success",
            "message": "Conexión a la base de datos exitosa",
            "data": {
                "primera_consulta": docente.__dict__ if docente else None,
                "tablas_disponibles": [
                    "docente",
                    "asignatura",
                    "seccion",
                    "sala",
                    "bloque",
                    "clase",
                    "restriccion",
                ],
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error de conexión a la base de datos: {str(e)}",
        )
