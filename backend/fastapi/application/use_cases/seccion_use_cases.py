from typing import List, Optional

from fastapi import HTTPException, status

from domain.entities import Seccion, SeccionCreate
from domain.schemas import SeccionSecureCreate, SeccionSecurePatch
from infrastructure.repositories.seccion_repository import SeccionRepository


class SeccionUseCases:
    def __init__(self, seccion_repository: SeccionRepository):
        self.seccion_repository = seccion_repository

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Seccion]:
        """Obtener todas las secciones con paginación"""
        return self.seccion_repository.get_all(skip=skip, limit=limit)

    def get_by_id(self, seccion_id: int) -> Seccion:
        """Obtener sección por ID"""
        seccion = self.seccion_repository.get_by_id(seccion_id)
        if not seccion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Sección no encontrada"
            )
        return seccion

    def create(self, seccion_data: SeccionSecureCreate) -> Seccion:
        """Crear una nueva sección"""
        # Convertir schema seguro a entidad
        seccion_create = SeccionCreate(**seccion_data.model_dump())
        return self.seccion_repository.create(seccion_create)

    def update(self, seccion_id: int, seccion_data: SeccionSecurePatch) -> Seccion:
        """Actualizar una sección"""
        # Verificar que la sección existe
        existing_seccion = self.seccion_repository.get_by_id(seccion_id)
        if not existing_seccion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Sección no encontrada"
            )

        # Convertir schema seguro a diccionario y filtrar valores None
        update_data = {k: v for k, v in seccion_data.model_dump().items() if v is not None}

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se proporcionaron campos para actualizar",
            )

        updated_seccion = self.seccion_repository.update(seccion_id, update_data)
        if not updated_seccion:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al actualizar la sección",
            )
        return updated_seccion

    def delete(self, seccion_id: int) -> bool:
        """Eliminar una sección"""
        # Verificar que la sección existe
        existing_seccion = self.seccion_repository.get_by_id(seccion_id)
        if not existing_seccion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Sección no encontrada"
            )

        # Verificar si tiene clases asociadas
        if self.seccion_repository.tiene_clases(seccion_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede eliminar la sección porque tiene clases asociadas",
            )

        success = self.seccion_repository.delete(seccion_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar la sección",
            )
        return success

    def get_by_asignatura(self, asignatura_id: int) -> List[Seccion]:
        """Obtener secciones de una asignatura específica"""
        return self.seccion_repository.get_by_asignatura(asignatura_id)

    def get_by_periodo(self, anio: int, semestre: int) -> List[Seccion]:
        """Obtener secciones por año y semestre"""
        return self.seccion_repository.get_by_periodo(anio, semestre)

    def get_secciones_activas(self) -> List[Seccion]:
        """Obtener secciones activas"""
        return self.seccion_repository.get_secciones_activas()

    def get_student_years_format(self) -> List[dict]:
        """Obtener secciones agrupadas por año académico en formato FET"""
        from collections import defaultdict
        from domain.entities import StudentYearResponse, StudentGroupResponse
        
        # Obtener todas las secciones
        secciones = self.seccion_repository.get_all()
        
        # Agrupar por año académico
        años_dict = defaultdict(lambda: {"grupos": [], "total": 0})
        
        for seccion in secciones:
            año = seccion.anio_academico
            
            # Generar ID del grupo según tipo
            if seccion.tipo_grupo == "seccion":
                group_id = f"g-{año}-seccion-{seccion.id}"
            elif seccion.tipo_grupo == "mencion":
                group_id = f"g-{año}-mencion-{seccion.id}"
            elif seccion.tipo_grupo == "base":
                group_id = f"g-{año}-seccion-{seccion.id}"
            else:
                group_id = f"g-{año}-grupo-{seccion.id}"
            
            # Agregar grupo
            años_dict[año]["grupos"].append(
                StudentGroupResponse(
                    id=group_id,
                    name=seccion.codigo,
                    students=seccion.numero_estudiantes
                )
            )
            años_dict[año]["total"] += seccion.numero_estudiantes
        
        # Construir lista de StudentYear
        student_years = []
        for año in sorted(años_dict.keys()):
            student_years.append(
                StudentYearResponse(
                    id=f"year-{año}",
                    name=str(año),
                    total_students=años_dict[año]["total"],
                    groups=años_dict[año]["grupos"]
                )
            )
        
        return student_years
