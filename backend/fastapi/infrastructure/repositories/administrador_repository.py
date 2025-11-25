from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from domain.entities import AdministradorCreate
from domain.models import Administrador


class SQLAdministradorRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, administrador: AdministradorCreate) -> Administrador:
        """Crear un nuevo administrador"""
        db_administrador = Administrador(
            user_id=administrador.user_id, permisos=administrador.permisos
        )
        self.session.add(db_administrador)
        self.session.commit()
        self.session.refresh(db_administrador)
        return db_administrador

    def get_by_id(self, administrador_id: int) -> Optional[Administrador]:
        """Obtener administrador por ID"""
        return (
            self.session.query(Administrador)
            .options(joinedload(Administrador.user))
            .filter(Administrador.id == administrador_id)
            .first()
        )

    def get_by_user_id(self, user_id: int) -> Optional[Administrador]:
        """Obtener administrador por user_id"""
        return (
            self.session.query(Administrador)
            .options(joinedload(Administrador.user))
            .filter(Administrador.user_id == user_id)
            .first()
        )

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Administrador]:
        """Obtener todos los administradores con paginación"""
        return (
            self.session.query(Administrador)
            .options(joinedload(Administrador.user))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def delete(self, administrador_id: int) -> bool:
        """Eliminar un administrador"""
        db_administrador = self.get_by_id(administrador_id)
        if db_administrador:
            self.session.delete(db_administrador)
            self.session.commit()
            return True
        return False
