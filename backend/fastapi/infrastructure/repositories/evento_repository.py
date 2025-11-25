from typing import List, Optional

from sqlalchemy.orm import Session

from domain.entities import EventoCreate
from domain.models import Evento


class EventoRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, evento: EventoCreate) -> Evento:
        """Crear un nuevo evento"""
        db_evento = Evento(**evento.model_dump())
        self.session.add(db_evento)
        self.session.commit()
        self.session.refresh(db_evento)
        return db_evento

    def get_by_id(self, evento_id: int) -> Optional[Evento]:
        """Obtener evento por ID"""
        return self.session.query(Evento).filter(Evento.id == evento_id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Evento]:
        """Obtener todos los eventos con paginación"""
        return self.session.query(Evento).offset(skip).limit(limit).all()

    def get_by_docente(self, docente_id: int, skip: int = 0, limit: int = 100) -> List[Evento]:
        """Obtener eventos de un docente específico"""
        return (
            self.session.query(Evento)
            .filter(Evento.docente_id == docente_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_active_by_docente(self, docente_id: int, skip: int = 0, limit: int = 100) -> List[Evento]:
        """Obtener eventos activos de un docente específico"""
        return (
            self.session.query(Evento)
            .filter(Evento.docente_id == docente_id, Evento.activo == True)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_all_active(self, skip: int = 0, limit: int = 100) -> List[Evento]:
        """Obtener todos los eventos activos"""
        return (
            self.session.query(Evento)
            .filter(Evento.activo == True)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update(self, evento_id: int, evento_data: dict) -> Optional[Evento]:
        """Actualizar un evento"""
        db_evento = self.get_by_id(evento_id)
        if db_evento:
            for key, value in evento_data.items():
                if value is not None:
                    setattr(db_evento, key, value)
            self.session.commit()
            self.session.refresh(db_evento)
        return db_evento

    def toggle_active(self, evento_id: int, activo: bool) -> Optional[Evento]:
        """Activar o desactivar un evento (para administradores)"""
        db_evento = self.get_by_id(evento_id)
        if db_evento:
            db_evento.activo = activo
            self.session.commit()
            self.session.refresh(db_evento)
        return db_evento

    def delete(self, evento_id: int) -> bool:
        """Eliminar un evento"""
        db_evento = self.get_by_id(evento_id)
        if db_evento:
            self.session.delete(db_evento)
            self.session.commit()
            return True
        return False

    def delete_by_docente(self, docente_id: int) -> int:
        """Eliminar todos los eventos de un docente"""
        count = self.session.query(Evento).filter(Evento.docente_id == docente_id).count()
        self.session.query(Evento).filter(Evento.docente_id == docente_id).delete()
        self.session.commit()
        return count

    def count_by_docente(self, docente_id: int) -> int:
        """Contar eventos de un docente"""
        return self.session.query(Evento).filter(Evento.docente_id == docente_id).count()

    def count_active(self) -> int:
        """Contar eventos activos en el sistema"""
        return self.session.query(Evento).filter(Evento.activo == True).count()
