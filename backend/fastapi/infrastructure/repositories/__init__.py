# Repositorios especializados por entidad
from .asignatura_repository import AsignaturaRepository
from .bloque_repository import BloqueRepository
from .clase_repository import ClaseRepository
from .docente_repository import DocenteRepository
from .restriccion_horario_repository import RestriccionHorarioRepository
from .restriccion_repository import RestriccionRepository
from .sala_repository import SalaRepository
from .seccion_repository import SeccionRepository
from .user_repository import SQLUserRepository


# Clase que agrupa todos los repositorios para facilitar la inyección de dependencias
class RepositoryContainer:
    """Contenedor de todos los repositorios para facilitar la gestión de dependencias"""

    def __init__(self, session):
        self.session = session

        # Repositorios de entidades principales
        self.user = SQLUserRepository(session)
        self.docente = DocenteRepository(session)
        self.asignatura = AsignaturaRepository(session)
        self.seccion = SeccionRepository(session)
        self.sala = SalaRepository(session)
        self.bloque = BloqueRepository(session)
        self.clase = ClaseRepository(session)

        # Repositorios de restricciones
        self.restriccion = RestriccionRepository(session)
        self.restriccion_horario = RestriccionHorarioRepository(session)


# Exports públicos
__all__ = [
    "SQLUserRepository",
    "DocenteRepository",
    "RestriccionRepository",
    "RestriccionHorarioRepository",
    "BloqueRepository",
    "AsignaturaRepository",
    "SeccionRepository",
    "SalaRepository",
    "ClaseRepository",
    "RepositoryContainer",
]
