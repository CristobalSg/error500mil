from typing import List, Optional

from fastapi import HTTPException, status

from domain.entities import Sala, SalaCreate
from domain.schemas import SalaSecureCreate, SalaSecurePatch
from infrastructure.repositories.edificio_repository import SQLEdificioRepository
from infrastructure.repositories.sala_repository import SalaRepository


class SalaUseCases:
    def __init__(self, sala_repository: SalaRepository, edificio_repository: SQLEdificioRepository):
        self.sala_repository = sala_repository
        self.edificio_repository = edificio_repository

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Sala]:
        """Obtener todas las salas con paginación"""
        return self.sala_repository.get_all(skip=skip, limit=limit)

    def get_by_id(self, sala_id: int) -> Sala:
        """Obtener sala por ID"""
        sala = self.sala_repository.get_by_id(sala_id)
        if not sala:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sala no encontrada")
        return sala

    def get_by_codigo(self, codigo: str) -> Sala:
        """Obtener sala por código"""
        sala = self.sala_repository.get_by_codigo(codigo)
        if not sala:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sala no encontrada")
        return sala

    def create(self, sala_data: SalaSecureCreate) -> Sala:
        """Crear una nueva sala"""
        # Verificar que el edificio existe
        edificio = self.edificio_repository.get_by_id(sala_data.edificio_id)
        if not edificio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Edificio con id {sala_data.edificio_id} no encontrado",
            )

        # Verificar si el código ya existe
        existing_sala = self.sala_repository.get_by_codigo(sala_data.codigo)
        if existing_sala:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="El código de sala ya existe"
            )

        # Convertir schema seguro a entidad
        sala_create = SalaCreate(**sala_data.model_dump())
        return self.sala_repository.create(sala_create)

    def get_by_edificio(self, edificio_id: int) -> List[Sala]:
        """Obtener salas por edificio"""
        # Verificar que el edificio existe
        edificio = self.edificio_repository.get_by_id(edificio_id)
        if not edificio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Edificio con id {edificio_id} no encontrado",
            )

        salas = self.sala_repository.get_by_edificio(edificio_id)
        if not salas:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No hay salas en el edificio {edificio_id}",
            )
        return salas

    def update(self, sala_id: int, sala_data: SalaSecurePatch) -> Sala:
        """Actualizar una sala"""
        # Verificar que la sala existe
        existing_sala = self.sala_repository.get_by_id(sala_id)
        if not existing_sala:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sala no encontrada")

        # Convertir schema seguro a diccionario y filtrar valores None
        update_data = {k: v for k, v in sala_data.model_dump().items() if v is not None}

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se proporcionaron campos para actualizar",
            )

        # Si se actualiza el código, verificar que no exista otra sala con ese código
        if "codigo" in update_data:
            sala_with_codigo = self.sala_repository.get_by_codigo(update_data["codigo"])
            if sala_with_codigo and sala_with_codigo.id != sala_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El código ya está registrado por otra sala",
                )

        updated_sala = self.sala_repository.update(sala_id, update_data)
        if not updated_sala:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al actualizar la sala",
            )
        return updated_sala

    def delete(self, sala_id: int) -> bool:
        """Eliminar una sala"""
        # Verificar que la sala existe
        existing_sala = self.sala_repository.get_by_id(sala_id)
        if not existing_sala:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sala no encontrada")

        # Verificar si tiene clases asociadas
        if self.sala_repository.tiene_clases_activas(sala_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede eliminar la sala porque tiene clases activas",
            )

        success = self.sala_repository.delete(sala_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar la sala",
            )
        return success

    def get_by_tipo(self, tipo: str) -> List[Sala]:
        """Obtener salas por tipo"""
        return self.sala_repository.get_by_tipo(tipo)

    def get_by_capacidad(self, capacidad_min: int = None, capacidad_max: int = None) -> List[Sala]:
        """Obtener salas por rango de capacidad"""
        return self.sala_repository.get_by_capacidad(capacidad_min, capacidad_max)

    def get_salas_disponibles(self, bloque_id: int = None) -> List[Sala]:
        """Obtener salas disponibles en un bloque específico"""
        return self.sala_repository.get_salas_disponibles(bloque_id)
