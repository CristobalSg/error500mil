from typing import List, Optional

from sqlalchemy.orm import Session

from domain.entities import AsignaturaCreate
from domain.models import Asignatura


class AsignaturaRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, asignatura: AsignaturaCreate) -> Asignatura:
        """Crear una nueva asignatura"""
        db_asignatura = Asignatura(**asignatura.model_dump())
        self.session.add(db_asignatura)
        self.session.commit()
        self.session.refresh(db_asignatura)
        return db_asignatura

    def get_by_id(self, asignatura_id: int) -> Optional[Asignatura]:
        """Obtener asignatura por ID"""
        return self.session.query(Asignatura).filter(Asignatura.id == asignatura_id).first()

    def get_by_codigo(self, codigo: str) -> Optional[Asignatura]:
        """Obtener asignatura por código"""
        return self.session.query(Asignatura).filter(Asignatura.codigo == codigo).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Asignatura]:
        """Obtener todas las asignaturas con paginación"""
        return self.session.query(Asignatura).offset(skip).limit(limit).all()

    def search_by_nombre(self, nombre: str) -> List[Asignatura]:
        """Buscar asignaturas por nombre"""
        return self.session.query(Asignatura).filter(Asignatura.nombre.ilike(f"%{nombre}%")).all()

    def get_by_cantidad_creditos(
        self, creditos_min: int = None, creditos_max: int = None
    ) -> List[Asignatura]:
        """Obtener asignaturas por rango de cantidad de créditos"""
        query = self.session.query(Asignatura)
        if creditos_min is not None:
            query = query.filter(Asignatura.cantidad_creditos >= creditos_min)
        if creditos_max is not None:
            query = query.filter(Asignatura.cantidad_creditos <= creditos_max)
        return query.all()

    def update(self, asignatura_id: int, asignatura_data: dict) -> Optional[Asignatura]:
        """Actualizar una asignatura"""
        db_asignatura = self.get_by_id(asignatura_id)
        if db_asignatura:
            for key, value in asignatura_data.items():
                setattr(db_asignatura, key, value)
            self.session.commit()
            self.session.refresh(db_asignatura)
        return db_asignatura

    def delete(self, asignatura_id: int) -> bool:
        """Eliminar una asignatura"""
        db_asignatura = self.get_by_id(asignatura_id)
        if db_asignatura:
            self.session.delete(db_asignatura)
            self.session.commit()
            return True
        return False

    def has_secciones(self, asignatura_id: int) -> bool:
        """Verificar si una asignatura tiene secciones"""
        from domain.models import Seccion

        count = self.session.query(Seccion).filter(Seccion.asignatura_id == asignatura_id).count()
        return count > 0
