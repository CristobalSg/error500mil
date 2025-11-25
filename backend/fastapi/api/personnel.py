"""
Endpoints de personal académico y estudiantes.
"""

from infrastructure.controllers.docente_controller import router as docente_router
from infrastructure.controllers.estudiante_controller import router as estudiante_router

__all__ = ["docente_router", "estudiante_router"]
