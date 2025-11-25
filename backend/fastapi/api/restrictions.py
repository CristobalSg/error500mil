"""
Endpoints de restricciones (generales y de horario).
"""

from infrastructure.controllers.restriccion_controller import router as restriccion_router
from infrastructure.controllers.restriccion_horario_controller import (
    router as restriccion_horario_router,
)

__all__ = ["restriccion_router", "restriccion_horario_router"]
