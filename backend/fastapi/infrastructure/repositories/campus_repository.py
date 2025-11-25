from typing import List, Optional

from sqlalchemy.orm import Session

from domain.entities import CampusCreate
from domain.models import Campus


class SQLCampusRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, campus: CampusCreate) -> Campus:
        """Crear un nuevo campus"""
        db_campus = Campus(nombre=campus.nombre, direccion=campus.direccion)
        self.session.add(db_campus)
        self.session.commit()
        self.session.refresh(db_campus)
        return db_campus

    def get_by_id(self, campus_id: int) -> Optional[Campus]:
        """Obtener campus por ID"""
        return self.session.query(Campus).filter(Campus.id == campus_id).first()

    def get_by_nombre(self, nombre: str) -> Optional[Campus]:
        """Obtener campus por nombre"""
        return self.session.query(Campus).filter(Campus.nombre == nombre).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Campus]:
        """Obtener todos los campus con paginación"""
        return self.session.query(Campus).offset(skip).limit(limit).all()

    def delete(self, campus_id: int) -> bool:
        """Eliminar un campus"""
        db_campus = self.get_by_id(campus_id)
        if db_campus:
            self.session.delete(db_campus)
            self.session.commit()
            return True
        return False
