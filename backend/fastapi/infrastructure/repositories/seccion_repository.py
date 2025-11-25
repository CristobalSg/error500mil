from typing import List, Optional

from sqlalchemy.orm import Session

from domain.entities import SeccionCreate
from domain.models import Seccion


class SeccionRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, seccion: SeccionCreate) -> Seccion:
        """Crear una nueva sección"""
        db_seccion = Seccion(**seccion.model_dump())
        self.session.add(db_seccion)
        self.session.commit()
        self.session.refresh(db_seccion)
        return db_seccion

    def get_by_id(self, seccion_id: int) -> Optional[Seccion]:
        """Obtener sección por ID"""
        return self.session.query(Seccion).filter(Seccion.id == seccion_id).first()

    def get_by_codigo(self, codigo: str) -> Optional[Seccion]:
        """Obtener sección por código"""
        return self.session.query(Seccion).filter(Seccion.codigo == codigo).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Seccion]:
        """Obtener todas las secciones con paginación"""
        return self.session.query(Seccion).offset(skip).limit(limit).all()

    def get_by_asignatura(self, asignatura_id: int) -> List[Seccion]:
        """Obtener secciones de una asignatura específica"""
        return self.session.query(Seccion).filter(Seccion.asignatura_id == asignatura_id).all()

    def get_by_periodo(self, anio: int, semestre: int) -> List[Seccion]:
        """Obtener secciones por periodo (año y semestre)"""
        return (
            self.db.query(Seccion)
            .filter(Seccion.semestre == semestre)
            .all()
        )

    def existe_seccion_en_periodo(
        self, asignatura_id: int, anio: int, semestre: int
    ) -> bool:
        """Verificar si existe una sección de una asignatura en un periodo específico"""
        return (
            self.db.query(Seccion)
            .filter(
                Seccion.asignatura_id == asignatura_id,
                Seccion.semestre == semestre,
            )
            .first()
            is not None
        )

    def get_secciones_con_cupos(self, cupos_min: int = 1) -> List[Seccion]:
        """Obtener secciones que tienen cupos disponibles"""
        return self.session.query(Seccion).filter(Seccion.cupos >= cupos_min).all()

    def update(self, seccion_id: int, seccion_data: dict) -> Optional[Seccion]:
        """Actualizar una sección"""
        db_seccion = self.get_by_id(seccion_id)
        if db_seccion:
            for key, value in seccion_data.items():
                setattr(db_seccion, key, value)
            self.session.commit()
            self.session.refresh(db_seccion)
        return db_seccion

    def delete(self, seccion_id: int) -> bool:
        """Eliminar una sección"""
        db_seccion = self.get_by_id(seccion_id)
        if db_seccion:
            self.session.delete(db_seccion)
            self.session.commit()
            return True
        return False

    def has_clases(self, seccion_id: int) -> bool:
        """Verificar si una sección tiene clases programadas"""
        from domain.models import Clase

        count = self.session.query(Clase).filter(Clase.seccion_id == seccion_id).count()
        return count > 0

    def tiene_clases(self, seccion_id: int) -> bool:
        """Alias para has_clases - verificar si una sección tiene clases programadas"""
        return self.has_clases(seccion_id)

    def get_by_codigo(self, codigo: str) -> Optional[Seccion]:
        """Obtener sección por código"""
        return self.session.query(Seccion).filter(Seccion.codigo == codigo).first()
