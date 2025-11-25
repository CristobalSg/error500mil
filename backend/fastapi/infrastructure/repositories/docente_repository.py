from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from domain.entities import DocenteCreate
from domain.models import Docente


class DocenteRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, docente: DocenteCreate) -> Docente:
        """Crear un nuevo docente"""
        db_docente = Docente(user_id=docente.user_id, departamento=docente.departamento)
        self.session.add(db_docente)
        self.session.commit()
        self.session.refresh(db_docente)
        return db_docente

    def get_by_user_id(self, user_id: int) -> Optional[Docente]:
        """
        Obtener docente por user_id (que ahora es la PK).
        Este método es el principal para buscar docentes por ID.
        """
        return (
            self.session.query(Docente)
            .options(joinedload(Docente.user))
            .filter(Docente.user_id == user_id)
            .first()
        )
    
    def get_by_id(self, user_id: int) -> Optional[Docente]:
        """
        Alias de get_by_user_id para compatibilidad.
        NOTA: Ahora el ID del docente ES su user_id.
        """
        return self.get_by_user_id(user_id)

    def get_by_departamento(self, departamento: str) -> List[Docente]:
        """Obtener docentes por departamento"""
        return (
            self.session.query(Docente)
            .options(joinedload(Docente.user))
            .filter(Docente.departamento == departamento)
            .all()
        )

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Docente]:
        """Obtener todos los docentes con paginación"""
        return (
            self.session.query(Docente)
            .options(joinedload(Docente.user))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update(self, user_id: int, docente_data: dict) -> Optional[Docente]:
        """Actualizar un docente por su user_id (PK)"""
        db_docente = self.get_by_user_id(user_id)
        if db_docente:
            for key, value in docente_data.items():
                setattr(db_docente, key, value)
            self.session.commit()
            self.session.refresh(db_docente)
        return db_docente

    def delete(self, user_id: int) -> bool:
        """Eliminar un docente por su user_id (PK)"""
        db_docente = self.get_by_user_id(user_id)
        if db_docente:
            self.session.delete(db_docente)
            self.session.commit()
            return True
        return False

    def search_by_nombre(self, nombre: str) -> List[Docente]:
        """Buscar docentes por nombre"""
        return self.session.query(Docente).filter(Docente.nombre.ilike(f"%{nombre}%")).all()

    def get_active_docentes(self) -> List[Docente]:
        """Obtener solo docentes activos (si hubiera un campo activo)"""
        return self.session.query(Docente).all()  # Por ahora todos
