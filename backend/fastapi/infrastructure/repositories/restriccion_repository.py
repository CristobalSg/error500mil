from typing import List, Optional

from sqlalchemy.orm import Session

from domain.entities import RestriccionCreate
from domain.models import Restriccion


class RestriccionRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, restriccion: RestriccionCreate) -> Restriccion:
        """Crear una nueva restricción"""
        db_restriccion = Restriccion(**restriccion.model_dump())
        self.session.add(db_restriccion)
        self.session.commit()
        self.session.refresh(db_restriccion)
        return db_restriccion

    def get_by_id(self, restriccion_id: int) -> Optional[Restriccion]:
        """Obtener restricción por ID"""
        return self.session.query(Restriccion).filter(Restriccion.id == restriccion_id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Restriccion]:
        """Obtener todas las restricciones con paginación"""
        return self.session.query(Restriccion).offset(skip).limit(limit).all()

    def get_by_docente(self, user_id: int) -> List[Restriccion]:
        """
        Obtener restricciones de un docente específico.
        NOTA: docente_id en la tabla ahora apunta a docente.user_id (PK).
        """
        return self.session.query(Restriccion).filter(Restriccion.docente_id == user_id).all()

    def get_by_tipo(self, tipo: str) -> List[Restriccion]:
        """Obtener restricciones por tipo"""
        return self.session.query(Restriccion).filter(Restriccion.tipo == tipo).all()

    def get_by_prioridad(
        self, prioridad_min: int = 1, prioridad_max: int = 10
    ) -> List[Restriccion]:
        """Obtener restricciones por rango de prioridad"""
        return (
            self.session.query(Restriccion)
            .filter(Restriccion.prioridad >= prioridad_min, Restriccion.prioridad <= prioridad_max)
            .all()
        )

    def update(self, restriccion_id: int, restriccion_data: dict) -> Optional[Restriccion]:
        """Actualizar una restricción"""
        db_restriccion = self.get_by_id(restriccion_id)
        if db_restriccion:
            for key, value in restriccion_data.items():
                setattr(db_restriccion, key, value)
            self.session.commit()
            self.session.refresh(db_restriccion)
        return db_restriccion

    def delete(self, restriccion_id: int) -> bool:
        """Eliminar una restricción"""
        db_restriccion = self.get_by_id(restriccion_id)
        if db_restriccion:
            self.session.delete(db_restriccion)
            self.session.commit()
            return True
        return False

    def delete_by_docente(self, user_id: int) -> int:
        """
        Eliminar todas las restricciones de un docente.
        NOTA: user_id es el ID del docente (user_id es la PK de docente).
        """
        count = self.session.query(Restriccion).filter(Restriccion.docente_id == user_id).count()
        self.session.query(Restriccion).filter(Restriccion.docente_id == user_id).delete()
        self.session.commit()
        return count
