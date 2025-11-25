from fastapi import APIRouter

from app.fet.router import router as fet_router

api_router = APIRouter()
api_router.include_router(fet_router, prefix="/fet", tags=["fet"])

__all__ = ["api_router"]
