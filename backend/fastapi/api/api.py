"""
Router principal de la API.
Agrega todos los routers de los diferentes módulos.
"""

from fastapi import APIRouter

from api.academic import asignatura_router, clase_router, seccion_router
from api.auth import auth_router, user_router, password_reset_router
from api.events import evento_router
from api.infrastructure import campus_router, edificio_router, sala_router
from api.personnel import docente_router, estudiante_router
from api.restrictions import restriccion_horario_router, restriccion_router
from api.schedule import bloque_router, timetable_router
from api.system import test_db_router

# Router principal de la API 
api_router = APIRouter()

# Autenticación y usuarios
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(user_router, prefix="/users", tags=["Users"])
api_router.include_router(password_reset_router, prefix="/auth", tags=["authentication"])

# Gestión académica
api_router.include_router(asignatura_router, prefix="/asignaturas", tags=["asignaturas"])
api_router.include_router(seccion_router, prefix="/secciones", tags=["secciones"])
api_router.include_router(clase_router, prefix="/clases", tags=["clases"])

# Infraestructura física
api_router.include_router(campus_router, prefix="/campus", tags=["campus"])
api_router.include_router(edificio_router, prefix="/edificios", tags=["edificios"])
api_router.include_router(sala_router, prefix="/salas", tags=["salas"])

# Horarios y bloques
api_router.include_router(bloque_router, prefix="/bloques", tags=["bloques"])
api_router.include_router(timetable_router, prefix="/timetable", tags=["timetable"])

# Personal académico
api_router.include_router(docente_router, prefix="/docentes", tags=["docentes"])
api_router.include_router(estudiante_router, prefix="/estudiantes", tags=["estudiantes"])

# Restricciones
api_router.include_router(restriccion_router, prefix="/restricciones", tags=["restricciones"])
api_router.include_router(
    restriccion_horario_router, prefix="/restricciones-horario", tags=["restricciones-horario"]
)

# Eventos
api_router.include_router(evento_router, prefix="/eventos", tags=["eventos"])

# Sistema
api_router.include_router(test_db_router, prefix="/db", tags=["database"])
