"""
Endpoints del sistema (health checks, database).
"""

from infrastructure.controllers.test_db_controller import router as test_db_router

__all__ = ["test_db_router"]
