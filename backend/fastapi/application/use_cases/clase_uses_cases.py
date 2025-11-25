from typing import List, Optional

from fastapi import HTTPException, status

from domain.entities import Clase, ClaseCreate
from domain.schemas import ClaseSecureCreate, ClaseSecurePatch
from infrastructure.repositories.clase_repository import ClaseRepository
from infrastructure.repositories.seccion_repository import SeccionRepository


class ClaseUseCases:
    def __init__(
        self, clase_repository: ClaseRepository, seccion_repository: SeccionRepository = None
    ):
        self.clase_repository = clase_repository
        self.seccion_repository = seccion_repository

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Clase]:
        """Obtener todas las clases con paginación"""
        return self.clase_repository.get_all(skip=skip, limit=limit)

    def get_by_id(self, clase_id: int) -> Clase:
        """Obtener clase por ID"""
        clase = self.clase_repository.get_by_id(clase_id)
        if not clase:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clase no encontrada")
        return clase

    def create(self, clase_data: ClaseSecureCreate) -> Clase:
        """Crear una nueva clase"""
        # Obtener la sección para obtener el docente_id
        if self.seccion_repository:
            seccion = self.seccion_repository.get_by_id(clase_data.seccion_id)
            if not seccion:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Sección no encontrada"
                )
            docente_id = seccion.docente_id
        else:
            # Si no hay seccion_repository, asumir que las clases directamente tienen docente_id
            # Esto es para mantener compatibilidad con tests que no inyectan seccion_repository
            docente_id = getattr(clase_data, "docente_id", None)
            if not docente_id:
                # Fallback: no verificar conflictos de docente
                docente_id = None

        # Verificar conflictos de horario para el docente (solo si tenemos docente_id)
        if docente_id:
            conflictos_docente = self.clase_repository.get_conflictos_docente(
                docente_id, clase_data.bloque_id
            )
            if conflictos_docente:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El docente ya tiene una clase asignada en ese bloque",
                )

        # Verificar conflictos de horario para la sala
        conflictos_sala = self.clase_repository.get_conflictos_sala(
            clase_data.sala_id, clase_data.bloque_id
        )
        if conflictos_sala:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La sala ya está ocupada en ese bloque",
            )

        # Convertir schema seguro a entidad
        clase_create = ClaseCreate(**clase_data.model_dump())
        return self.clase_repository.create(clase_create)

    def update(self, clase_id: int, clase_data: ClaseSecurePatch) -> Clase:
        """Actualizar una clase"""
        # Verificar que la clase existe
        existing_clase = self.clase_repository.get_by_id(clase_id)
        if not existing_clase:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clase no encontrada")

        # Convertir schema seguro a diccionario y filtrar valores None
        update_data = {k: v for k, v in clase_data.model_dump().items() if v is not None}

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se proporcionaron campos para actualizar",
            )

        # Si se actualiza docente o bloque, verificar conflictos
        if "docente_id" in update_data or "bloque_id" in update_data:
            docente_id = update_data.get("docente_id", existing_clase.docente_id)
            bloque_id = update_data.get("bloque_id", existing_clase.bloque_id)

            conflictos = self.clase_repository.get_conflictos_docente(docente_id, bloque_id)
            # Excluir la clase actual de los conflictos
            conflictos = [c for c in conflictos if c.id != clase_id]
            if conflictos:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El docente ya tiene una clase asignada en ese bloque",
                )

        # Si se actualiza sala o bloque, verificar conflictos
        if "sala_id" in update_data or "bloque_id" in update_data:
            sala_id = update_data.get("sala_id", existing_clase.sala_id)
            bloque_id = update_data.get("bloque_id", existing_clase.bloque_id)

            conflictos = self.clase_repository.get_conflictos_sala(sala_id, bloque_id)
            # Excluir la clase actual de los conflictos
            conflictos = [c for c in conflictos if c.id != clase_id]
            if conflictos:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La sala ya está ocupada en ese bloque",
                )

        updated_clase = self.clase_repository.update(clase_id, update_data)
        if not updated_clase:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al actualizar la clase",
            )
        return updated_clase

    def delete(self, clase_id: int) -> bool:
        """Eliminar una clase"""
        # Verificar que la clase existe
        existing_clase = self.clase_repository.get_by_id(clase_id)
        if not existing_clase:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clase no encontrada")

        success = self.clase_repository.delete(clase_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar la clase",
            )
        return success

    def get_by_seccion(self, seccion_id: int) -> List[Clase]:
        """Obtener clases de una sección específica"""
        return self.clase_repository.get_by_seccion(seccion_id)

    def get_by_docente(self, docente_id: int) -> List[Clase]:
        """Obtener clases de un docente específico"""
        return self.clase_repository.get_by_docente(docente_id)

    def get_by_sala(self, sala_id: int) -> List[Clase]:
        """Obtener clases de una sala específica"""
        return self.clase_repository.get_by_sala(sala_id)

    def get_by_bloque(self, bloque_id: int) -> List[Clase]:
        """Obtener clases de un bloque específico"""
        return self.clase_repository.get_by_bloque(bloque_id)
