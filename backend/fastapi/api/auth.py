"""
Endpoints de autenticación y gestión de usuarios.
"""

from infrastructure.controllers.auth_controller import router as auth_router
from infrastructure.controllers.user_controller import router as user_router
from infrastructure.controllers.password_reset_controller import router as password_reset_router

__all__ = ["auth_router", "user_router", "password_reset_router"]
