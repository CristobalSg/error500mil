from typing import List

from fastapi import HTTPException, status

from domain.entities import Edificio, EdificioCreate
from domain.schemas import EdificioSecureCreate, EdificioSecurePatch
from infrastructure.repositories.campus_repository import SQLCampusRepository
from infrastructure.repositories.edificio_repository import SQLEdificioRepository


class EdificioUseCase:
    def __init__(
        self, edificio_repository: SQLEdificioRepository, campus_repository: SQLCampusRepository
    ):
        self.edificio_repository = edificio_repository
        self.campus_repository = campus_repository

    def create_edificio(self, edificio_data: EdificioSecureCreate) -> Edificio:
        """Crear un nuevo edificio"""
        # Verificar que el campus existe
        campus = self.campus_repository.get_by_id(edificio_data.campus_id)
        if not campus:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Campus con id {edificio_data.campus_id} no encontrado",
            )

        # Convertir schema seguro a entidad
        edificio_create = EdificioCreate(**edificio_data.model_dump())
        return self.edificio_repository.create(edificio_create)

    def get_all_edificios(self) -> List[Edificio]:
        """Obtener todos los edificios"""
        edificios = self.edificio_repository.get_all()
        if not edificios:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No hay edificios registrados"
            )
        return edificios

    def get_edificio_by_id(self, edificio_id: int) -> Edificio:
        """Obtener edificio por ID"""
        edificio = self.edificio_repository.get_by_id(edificio_id)
        if not edificio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Edificio con id {edificio_id} no encontrado",
            )
        return edificio

    def get_edificios_by_campus(self, campus_id: int) -> List[Edificio]:
        """Obtener edificios por campus"""
        # Verificar que el campus existe
        campus = self.campus_repository.get_by_id(campus_id)
        if not campus:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Campus con id {campus_id} no encontrado",
            )

        edificios = self.edificio_repository.get_by_campus(campus_id)
        if not edificios:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No hay edificios en el campus {campus_id}",
            )
        return edificios

    def delete_edificio(self, edificio_id: int) -> bool:
        """Eliminar un edificio"""
        edificio = self.edificio_repository.get_by_id(edificio_id)
        if not edificio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Edificio con id {edificio_id} no encontrado",
            )

        return self.edificio_repository.delete(edificio_id)

    def update_edificio(self, edificio_id: int, edificio_data: EdificioSecurePatch) -> Edificio:
        """Actualizar un edificio existente"""
        # Verificar que el edificio existe
        edificio = self.edificio_repository.get_by_id(edificio_id)
        if not edificio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Edificio con id {edificio_id} no encontrado",
            )

        # Convertir schema seguro a diccionario y filtrar valores None
        update_data = {k: v for k, v in edificio_data.model_dump().items() if v is not None}

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se proporcionaron campos para actualizar",
            )

        # Verificar que el campus existe si se está actualizando
        if "campus_id" in update_data:
            campus = self.campus_repository.get_by_id(update_data["campus_id"])
            if not campus:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Campus con id {update_data['campus_id']} no encontrado",
                )

        # Convertir a EdificioCreate para mantener compatibilidad con el repositorio
        edificio_create = EdificioCreate(**{**edificio_data.model_dump(exclude_unset=True)})
        return self.edificio_repository.update(edificio_id, edificio_create)
