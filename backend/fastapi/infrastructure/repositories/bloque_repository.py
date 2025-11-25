from typing import List, Optional

from sqlalchemy.orm import Session

from domain.entities import BloqueCreate
from domain.models import Bloque


class BloqueRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, bloque: BloqueCreate) -> Bloque:
        """Crear un nuevo bloque"""
        db_bloque = Bloque(**bloque.model_dump())
        self.session.add(db_bloque)
        self.session.commit()
        self.session.refresh(db_bloque)
        return db_bloque

    def get_by_id(self, bloque_id: int) -> Optional[Bloque]:
        """Obtener bloque por ID"""
        return self.session.query(Bloque).filter(Bloque.id == bloque_id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Bloque]:
        """Obtener todos los bloques con paginación"""
        return self.session.query(Bloque).offset(skip).limit(limit).all()

    def get_by_dia_semana(self, dia_semana: int) -> List[Bloque]:
        """Obtener bloques por día de la semana (1=Lunes, 7=Domingo)"""
        return self.session.query(Bloque).filter(Bloque.dia_semana == dia_semana).all()

    def get_by_horario(self, hora_inicio=None, hora_fin=None) -> List[Bloque]:
        """Obtener bloques por rango de horario"""
        query = self.session.query(Bloque)
        if hora_inicio:
            query = query.filter(Bloque.hora_inicio >= hora_inicio)
        if hora_fin:
            query = query.filter(Bloque.hora_fin <= hora_fin)
        return query.all()

    def get_bloques_disponibles(self, dia_semana: int = None) -> List[Bloque]:
        """Obtener bloques que no tienen clases asignadas"""
        from domain.models import Clase

        query = self.session.query(Bloque).outerjoin(Clase).filter(Clase.bloque_id == None)
        if dia_semana:
            query = query.filter(Bloque.dia_semana == dia_semana)
        return query.all()

    def update(self, bloque_id: int, bloque_data: dict) -> Optional[Bloque]:
        """Actualizar un bloque"""
        db_bloque = self.get_by_id(bloque_id)
        if db_bloque:
            for key, value in bloque_data.items():
                setattr(db_bloque, key, value)
            self.session.commit()
            self.session.refresh(db_bloque)
        return db_bloque

    def delete(self, bloque_id: int) -> bool:
        """Eliminar un bloque"""
        db_bloque = self.get_by_id(bloque_id)
        if db_bloque:
            self.session.delete(db_bloque)
            self.session.commit()
            return True
        return False

    def has_clases_assigned(self, bloque_id: int) -> bool:
        """Verificar si un bloque tiene clases asignadas"""
        from domain.models import Clase

        count = self.session.query(Clase).filter(Clase.bloque_id == bloque_id).count()
        return count > 0

    def get_by_numero_and_dia(self, numero: int, dia_semana: int) -> Optional[Bloque]:
        """Obtener bloque por número y día de la semana"""
        return (
            self.session.query(Bloque)
            .filter(Bloque.numero == numero, Bloque.dia_semana == dia_semana)
            .first()
        )

    def get_conflictos_horario(self, dia_semana: int, hora_inicio, hora_fin) -> List[Bloque]:
        """Obtener bloques que tienen conflictos de horario"""
        return (
            self.session.query(Bloque)
            .filter(
                Bloque.dia_semana == dia_semana,
                # Verificar solapamiento de horarios
                ((Bloque.hora_inicio <= hora_inicio) & (Bloque.hora_fin > hora_inicio))
                | ((Bloque.hora_inicio < hora_fin) & (Bloque.hora_fin >= hora_fin))
                | ((Bloque.hora_inicio >= hora_inicio) & (Bloque.hora_fin <= hora_fin)),
            )
            .all()
        )

    def tiene_clases_activas(self, bloque_id: int) -> bool:
        """Verificar si un bloque tiene clases activas"""
        from domain.models import Clase

        count = (
            self.session.query(Clase)
            .filter(Clase.bloque_id == bloque_id, Clase.estado.in_(["programada", "en_curso"]))
            .count()
        )
        return count > 0

    def get_bloques_libres(self, dia_semana: int = None) -> List[Bloque]:
        """Obtener bloques que no tienen clases asignadas (alias para compatibilidad)"""
        return self.get_bloques_disponibles(dia_semana)
