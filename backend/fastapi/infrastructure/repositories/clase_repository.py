from typing import List, Optional

from sqlalchemy.orm import Session

from domain.entities import ClaseCreate
from domain.models import Clase


class ClaseRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, clase: ClaseCreate) -> Clase:
        """Crear una nueva clase"""
        db_clase = Clase(
            seccion_id=clase.seccion_id,
            docente_id=clase.docente_id,
            sala_id=clase.sala_id,
            bloque_id=clase.bloque_id,
            estado=clase.estado,
        )
        self.session.add(db_clase)
        self.session.commit()
        self.session.refresh(db_clase)
        return db_clase

    def get_by_id(self, clase_id: int) -> Optional[Clase]:
        """Obtener clase por ID"""
        return self.session.query(Clase).filter(Clase.id == clase_id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Clase]:
        """Obtener todas las clases con paginación"""
        return self.session.query(Clase).offset(skip).limit(limit).all()

    def get_by_seccion(self, seccion_id: int) -> List[Clase]:
        """Obtener clases de una sección específica"""
        return self.session.query(Clase).filter(Clase.seccion_id == seccion_id).all()

    def get_by_docente(self, docente_id: int) -> List[Clase]:
        """Obtener clases de un docente específico"""
        return self.session.query(Clase).filter(Clase.docente_id == docente_id).all()

    def get_by_sala(self, sala_id: int) -> List[Clase]:
        """Obtener clases en una sala específica"""
        return self.session.query(Clase).filter(Clase.sala_id == sala_id).all()

    def get_by_bloque(self, bloque_id: int) -> List[Clase]:
        """Obtener clases en un bloque horario específico"""
        return self.session.query(Clase).filter(Clase.bloque_id == bloque_id).all()

    def get_by_estado(self, estado: str) -> List[Clase]:
        """Obtener clases por estado (programada, confirmada, cancelada, etc.)"""
        return self.session.query(Clase).filter(Clase.estado == estado).all()

    def get_horario_docente(self, docente_id: int, dia_semana: int = None) -> List[Clase]:
        """Obtener horario completo de un docente, opcionalmente filtrado por día"""
        from domain.models import Bloque

        query = self.session.query(Clase).join(Bloque).filter(Clase.docente_id == docente_id)
        if dia_semana is not None:
            query = query.filter(Bloque.dia_semana == dia_semana)
        return query.order_by(Bloque.dia_semana, Bloque.hora_inicio).all()

    def get_horario_sala(self, sala_id: int, dia_semana: int = None) -> List[Clase]:
        """Obtener horario de ocupación de una sala"""
        from domain.models import Bloque

        query = self.session.query(Clase).join(Bloque).filter(Clase.sala_id == sala_id)
        if dia_semana is not None:
            query = query.filter(Bloque.dia_semana == dia_semana)
        return query.order_by(Bloque.dia_semana, Bloque.hora_inicio).all()

    def check_conflict(
        self, docente_id: int = None, sala_id: int = None, bloque_id: int = None
    ) -> List[Clase]:
        """Verificar conflictos de horario para docente o sala en un bloque específico"""
        query = self.session.query(Clase).filter(Clase.bloque_id == bloque_id)
        if docente_id:
            query = query.filter(Clase.docente_id == docente_id)
        if sala_id:
            query = query.filter(Clase.sala_id == sala_id)
        return query.all()

    def update(self, clase_id: int, clase_data: dict) -> Optional[Clase]:
        """Actualizar una clase"""
        db_clase = self.get_by_id(clase_id)
        if db_clase:
            for key, value in clase_data.items():
                setattr(db_clase, key, value)
            self.session.commit()
            self.session.refresh(db_clase)
        return db_clase

    def delete(self, clase_id: int) -> bool:
        """Eliminar una clase"""
        db_clase = self.get_by_id(clase_id)
        if db_clase:
            self.session.delete(db_clase)
            self.session.commit()
            return True
        return False

    def get_clases_by_periodo(self, anio: int, semestre: int) -> List[Clase]:
        """Obtener clases por periodo (año académico y semestre)"""
        return (
            self.db.query(Clase)
            .join(Seccion)
            .options(joinedload(Clase.seccion))
            .filter(Seccion.semestre == semestre)
            .all()
        )

    def get_by_sala_bloque_fecha(self, sala_id: int, bloque_id: int, fecha: str) -> Optional[Clase]:
        """Obtener clase por sala, bloque y fecha específica"""
        return (
            self.session.query(Clase)
            .filter(Clase.sala_id == sala_id, Clase.bloque_id == bloque_id, Clase.fecha == fecha)
            .first()
        )

    def get_conflictos_docente(
        self, docente_id: int, bloque_id: int, fecha: str = None
    ) -> List[Clase]:
        """Obtener conflictos de horario para un docente en un bloque y fecha específicos"""
        query = self.session.query(Clase).filter(
            Clase.docente_id == docente_id, Clase.bloque_id == bloque_id
        )
        if fecha:
            query = query.filter(Clase.fecha == fecha)
        return query.all()

    def get_conflictos_sala(self, sala_id: int, bloque_id: int, fecha: str = None) -> List[Clase]:
        """Obtener conflictos de horario para una sala en un bloque y fecha específicos"""
        query = self.session.query(Clase).filter(
            Clase.sala_id == sala_id, Clase.bloque_id == bloque_id
        )
        if fecha:
            query = query.filter(Clase.fecha == fecha)
        return query.all()
