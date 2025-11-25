from typing import List

from fastapi import HTTPException, status

from domain.entities import Campus, CampusCreate
from domain.schemas import CampusSecureCreate, CampusSecurePatch
from infrastructure.repositories.campus_repository import SQLCampusRepository


class CampusUseCase:
    def __init__(self, campus_repository: SQLCampusRepository):
        self.campus_repository = campus_repository

    def create_campus(self, campus_data: CampusSecureCreate) -> Campus:
        """Crear un nuevo campus"""
        # Verificar que no exista un campus con el mismo nombre
        existing_campus = self.campus_repository.get_by_nombre(campus_data.nombre)
        if existing_campus:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un campus con el nombre '{campus_data.nombre}'",
            )

        # Convertir schema seguro a entidad
        campus_create = CampusCreate(**campus_data.model_dump())
        return self.campus_repository.create(campus_create)

    def get_all_campus(self) -> List[Campus]:
        """Obtener todos los campus"""
        campus = self.campus_repository.get_all()
        if not campus:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No hay campus registrados"
            )
        return campus

    def get_campus_by_id(self, campus_id: int) -> Campus:
        """Obtener campus por ID"""
        campus = self.campus_repository.get_by_id(campus_id)
        if not campus:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Campus con id {campus_id} no encontrado",
            )
        return campus

    def update_campus(self, campus_id: int, campus_data: CampusSecurePatch) -> Campus:
        """Actualizar parcialmente un campus"""
        # Verificar que el campus existe
        existing_campus = self.campus_repository.get_by_id(campus_id)
        if not existing_campus:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Campus no encontrado"
            )

        # Convertir schema seguro a diccionario y filtrar valores None
        update_dict = {k: v for k, v in campus_data.model_dump().items() if v is not None}

        if not update_dict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se proporcionaron campos para actualizar",
            )

        # Si se actualiza el nombre, verificar que no exista otro campus con el mismo nombre
        if "nombre" in update_dict:
            campus_with_nombre = self.campus_repository.get_by_nombre(update_dict["nombre"])
            if campus_with_nombre and campus_with_nombre.id != campus_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ya existe otro campus con el nombre '{update_dict['nombre']}'",
                )

        # Actualizar usando el repositorio
        updated_campus = self.campus_repository.update(campus_id, **update_dict)
        if not updated_campus:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al actualizar el campus",
            )

        return updated_campus

    def delete_campus(self, campus_id: int) -> bool:
        """Eliminar un campus"""
        campus = self.campus_repository.get_by_id(campus_id)
        if not campus:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Campus con id {campus_id} no encontrado",
            )

        return self.campus_repository.delete(campus_id)
