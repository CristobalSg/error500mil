"""
Endpoints de gestión académica (asignaturas, secciones, clases).
"""

from infrastructure.controllers.asignatura_controller import router as asignatura_router
from infrastructure.controllers.clase_controller import router as clase_router
from infrastructure.controllers.seccion_controller import router as seccion_router

__all__ = ["asignatura_router", "seccion_router", "clase_router"]
