"""
Endpoints de horarios y bloques.
"""

from infrastructure.controllers.bloque_controller import router as bloque_router
from infrastructure.controllers.timetable_controller import router as timetable_router

__all__ = ["bloque_router", "timetable_router"]
