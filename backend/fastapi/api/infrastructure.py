"""
Endpoints de infraestructura física (campus, edificios, salas).
"""

from infrastructure.controllers.campus_controller import router as campus_router
from infrastructure.controllers.edificio_controller import router as edificio_router
from infrastructure.controllers.sala_controller import router as sala_router

__all__ = ["campus_router", "edificio_router", "sala_router"]
