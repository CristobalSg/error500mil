from typing import List, Optional

from sqlalchemy.orm import Session

from domain.entities import SalaCreate
from domain.models import Sala


class SalaRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, sala: SalaCreate) -> Sala:
        """Crear una nueva sala"""
        db_sala = Sala(
            edificio_id=sala.edificio_id,
            codigo=sala.codigo,
            capacidad=sala.capacidad,
            tipo=sala.tipo,
            disponible=sala.disponible,
            equipamiento=sala.equipamiento,
        )
        self.session.add(db_sala)
        self.session.commit()
        self.session.refresh(db_sala)
        return db_sala

    def get_by_id(self, sala_id: int) -> Optional[Sala]:
        """Obtener sala por ID"""
        return self.session.query(Sala).filter(Sala.id == sala_id).first()

    def get_by_codigo(self, codigo: str) -> Optional[Sala]:
        """Obtener sala por código"""
        return self.session.query(Sala).filter(Sala.codigo == codigo).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Sala]:
        """Obtener todas las salas con paginación"""
        return self.session.query(Sala).offset(skip).limit(limit).all()

    def get_by_tipo(self, tipo: str) -> List[Sala]:
        """Obtener salas por tipo (laboratorio, aula, auditorio, etc.)"""
        return self.session.query(Sala).filter(Sala.tipo == tipo).all()

    def get_by_capacidad(self, capacidad_min: int = None, capacidad_max: int = None) -> List[Sala]:
        """Obtener salas por rango de capacidad"""
        query = self.session.query(Sala)
        if capacidad_min is not None:
            query = query.filter(Sala.capacidad >= capacidad_min)
        if capacidad_max is not None:
            query = query.filter(Sala.capacidad <= capacidad_max)
        return query.all()

    def get_salas_disponibles(self, bloque_id: int = None) -> List[Sala]:
        """Obtener salas disponibles y opcionalmente que no tienen clases en un bloque específico"""
        from domain.models import Clase

        query = self.session.query(Sala).filter(Sala.disponible == True)
        if bloque_id:
            query = query.outerjoin(Clase).filter(
                (Clase.sala_id == None) | (Clase.bloque_id != bloque_id)
            )
        return query.all()

    def get_by_edificio(self, edificio_id: int) -> List[Sala]:
        """Obtener salas por edificio"""
        return self.session.query(Sala).filter(Sala.edificio_id == edificio_id).all()

    def search_by_codigo_or_tipo(self, search_term: str) -> List[Sala]:
        """Buscar salas por código o tipo"""
        return (
            self.session.query(Sala)
            .filter((Sala.codigo.ilike(f"%{search_term}%")) | (Sala.tipo.ilike(f"%{search_term}%")))
            .all()
        )

    def update(self, sala_id: int, sala_data: dict) -> Optional[Sala]:
        """Actualizar una sala"""
        db_sala = self.get_by_id(sala_id)
        if db_sala:
            for key, value in sala_data.items():
                setattr(db_sala, key, value)
            self.session.commit()
            self.session.refresh(db_sala)
        return db_sala

    def delete(self, sala_id: int) -> bool:
        """Eliminar una sala"""
        db_sala = self.get_by_id(sala_id)
        if db_sala:
            self.session.delete(db_sala)
            self.session.commit()
            return True
        return False

    def has_clases_assigned(self, sala_id: int) -> bool:
        """Verificar si una sala tiene clases asignadas"""
        from domain.models import Clase

        count = self.session.query(Clase).filter(Clase.sala_id == sala_id).count()
        return count > 0
