from typing import List, Optional

from fastapi import HTTPException, status

from domain.entities import Bloque, BloqueCreate
from domain.schemas import BloqueSecureCreate, BloqueSecurePatch
from infrastructure.repositories.bloque_repository import BloqueRepository


class BloqueUseCases:
    def __init__(self, bloque_repository: BloqueRepository):
        self.bloque_repository = bloque_repository

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Bloque]:
        """Obtener todos los bloques con paginación"""
        return self.bloque_repository.get_all(skip=skip, limit=limit)

    def get_by_id(self, bloque_id: int) -> Bloque:
        """Obtener bloque por ID"""
        bloque = self.bloque_repository.get_by_id(bloque_id)
        if not bloque:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Bloque no encontrado"
            )
        return bloque

    def create(self, bloque_data: BloqueSecureCreate) -> Bloque:
        """Crear un nuevo bloque"""
        # Verificar si ya existe un bloque con el mismo horario
        conflictos = self.bloque_repository.get_conflictos_horario(
            bloque_data.dia_semana, bloque_data.hora_inicio, bloque_data.hora_fin
        )
        if conflictos:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un bloque con conflicto de horario",
            )

        # Convertir schema seguro a entidad
        bloque_create = BloqueCreate(**bloque_data.model_dump())
        return self.bloque_repository.create(bloque_create)

    def update(self, bloque_id: int, bloque_data: BloqueSecurePatch) -> Bloque:
        """Actualizar un bloque"""
        # Verificar que el bloque existe
        existing_bloque = self.bloque_repository.get_by_id(bloque_id)
        if not existing_bloque:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Bloque no encontrado"
            )

        # Convertir schema seguro a diccionario y filtrar valores None
        update_data = {k: v for k, v in bloque_data.model_dump().items() if v is not None}

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se proporcionaron campos para actualizar",
            )

        # Si se actualiza el horario, verificar conflictos
        if any(key in update_data for key in ["dia_semana", "hora_inicio", "hora_fin"]):
            dia_semana = update_data.get("dia_semana", existing_bloque.dia_semana)
            hora_inicio = update_data.get("hora_inicio", existing_bloque.hora_inicio)
            hora_fin = update_data.get("hora_fin", existing_bloque.hora_fin)

            conflictos = self.bloque_repository.get_conflictos_horario(
                dia_semana, hora_inicio, hora_fin
            )
            # Excluir el bloque actual de los conflictos
            conflictos = [b for b in conflictos if b.id != bloque_id]
            if conflictos:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ya existe un bloque con conflicto de horario",
                )

        updated_bloque = self.bloque_repository.update(bloque_id, update_data)
        if not updated_bloque:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al actualizar el bloque",
            )
        return updated_bloque

    def delete(self, bloque_id: int) -> bool:
        """Eliminar un bloque"""
        # Verificar que el bloque existe
        existing_bloque = self.bloque_repository.get_by_id(bloque_id)
        if not existing_bloque:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Bloque no encontrado"
            )

        # Verificar si tiene clases asociadas
        if self.bloque_repository.tiene_clases_activas(bloque_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede eliminar el bloque porque tiene clases activas",
            )

        success = self.bloque_repository.delete(bloque_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar el bloque",
            )
        return success

    def get_by_dia_semana(self, dia_semana: int) -> List[Bloque]:
        """Obtener bloques por día de la semana"""
        return self.bloque_repository.get_by_dia_semana(dia_semana)

    def get_by_horario(self, hora_inicio=None, hora_fin=None) -> List[Bloque]:
        """Obtener bloques por rango de horario"""
        return self.bloque_repository.get_by_horario(hora_inicio, hora_fin)

    def get_bloques_libres(self, dia_semana: int = None) -> List[Bloque]:
        """Obtener bloques que no tienen clases asignadas"""
        return self.bloque_repository.get_bloques_libres(dia_semana)
