from typing import List, Optional

from sqlalchemy.orm import Session

from domain.entities import EdificioCreate
from domain.models import Edificio


class SQLEdificioRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, edificio: EdificioCreate) -> Edificio:
        """Crear un nuevo edificio"""
        db_edificio = Edificio(
            campus_id=edificio.campus_id, nombre=edificio.nombre, pisos=edificio.pisos
        )
        self.session.add(db_edificio)
        self.session.commit()
        self.session.refresh(db_edificio)
        return db_edificio

    def get_by_id(self, edificio_id: int) -> Optional[Edificio]:
        """Obtener edificio por ID"""
        return self.session.query(Edificio).filter(Edificio.id == edificio_id).first()

    def get_by_campus(self, campus_id: int) -> List[Edificio]:
        """Obtener edificios por campus"""
        return self.session.query(Edificio).filter(Edificio.campus_id == campus_id).all()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Edificio]:
        """Obtener todos los edificios con paginación"""
        return self.session.query(Edificio).offset(skip).limit(limit).all()

    def delete(self, edificio_id: int) -> bool:
        """Eliminar un edificio"""
        db_edificio = self.get_by_id(edificio_id)
        if db_edificio:
            self.session.delete(db_edificio)
            self.session.commit()
            return True
        return False

    def update(self, edificio_id: int, edificio_data: EdificioCreate) -> Edificio:
        """Actualizar un edificio existente"""
        db_edificio = self.get_by_id(edificio_id)
        if db_edificio:
            db_edificio.nombre = edificio_data.nombre
            db_edificio.pisos = edificio_data.pisos
            db_edificio.campus_id = edificio_data.campus_id
            self.session.commit()
            self.session.refresh(db_edificio)
        return db_edificio
