from typing import List

from fastapi import HTTPException, status

from domain.entities import Estudiante, EstudianteCreate
from domain.schemas import EstudianteSecureCreate, EstudianteSecurePatch
from infrastructure.repositories.estudiante_repository import SQLEstudianteRepository
from infrastructure.repositories.user_repository import SQLUserRepository


class EstudianteUseCase:
    def __init__(
        self, estudiante_repository: SQLEstudianteRepository, user_repository: SQLUserRepository
    ):
        self.estudiante_repository = estudiante_repository
        self.user_repository = user_repository

    def create_estudiante(self, estudiante_data: EstudianteSecureCreate) -> Estudiante:
        """Crear un nuevo estudiante"""
        # Verificar que el usuario existe y tiene rol de estudiante
        user = self.user_repository.get_by_id(estudiante_data.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con id {estudiante_data.user_id} no encontrado",
            )

        if user.rol != "estudiante":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El usuario debe tener rol de estudiante",
            )

        # Verificar que no exista ya un estudiante para este usuario
        existing_estudiante = self.estudiante_repository.get_by_user_id(estudiante_data.user_id)
        if existing_estudiante:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un estudiante asociado al usuario {estudiante_data.user_id}",
            )

        # Convertir schema seguro a entidad
        estudiante_create = EstudianteCreate(**estudiante_data.model_dump())
        return self.estudiante_repository.create(estudiante_create)

    def get_all_estudiantes(self, skip: int = 0, limit: int = 100) -> List[Estudiante]:
        """Obtener todos los estudiantes con paginación"""
        estudiantes = self.estudiante_repository.get_all(skip=skip, limit=limit)
        if not estudiantes:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No hay estudiantes registrados"
            )
        return estudiantes

    def get_estudiante_by_id(self, estudiante_id: int) -> Estudiante:
        """Obtener estudiante por ID"""
        estudiante = self.estudiante_repository.get_by_id(estudiante_id)
        if not estudiante:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Estudiante con id {estudiante_id} no encontrado",
            )
        return estudiante

    def get_estudiante_by_matricula(self, matricula: str) -> Estudiante:
        """Obtener estudiante por matrícula"""
        estudiante = self.estudiante_repository.get_by_matricula(matricula)
        if not estudiante:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Estudiante con matrícula {matricula} no encontrado",
            )
        return estudiante

    def update_estudiante(
        self, estudiante_id: int, estudiante_data: EstudianteSecurePatch
    ) -> Estudiante:
        """Actualizar parcialmente un estudiante"""
        # Verificar que el estudiante existe
        existing_estudiante = self.estudiante_repository.get_by_id(estudiante_id)
        if not existing_estudiante:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Estudiante no encontrado"
            )

        # Convertir schema seguro a diccionario y filtrar valores None
        update_dict = {k: v for k, v in estudiante_data.model_dump().items() if v is not None}

        if not update_dict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se proporcionaron campos para actualizar",
            )

        # Si se actualiza matrícula, verificar que no exista otro estudiante con la misma
        if "matricula" in update_dict:
            estudiante_with_matricula = self.estudiante_repository.get_by_matricula(
                update_dict["matricula"]
            )
            if estudiante_with_matricula and estudiante_with_matricula.id != estudiante_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ya existe otro estudiante con esa matrícula",
                )

        # Actualizar usando el repositorio
        updated_estudiante = self.estudiante_repository.update(estudiante_id, **update_dict)
        if not updated_estudiante:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al actualizar el estudiante",
            )

        return updated_estudiante

    def delete_estudiante(self, estudiante_id: int) -> bool:
        """Eliminar un estudiante"""
        estudiante = self.estudiante_repository.get_by_id(estudiante_id)
        if not estudiante:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Estudiante con id {estudiante_id} no encontrado",
            )

        return self.estudiante_repository.delete(estudiante_id)

    # =========================================================================
    # NUEVOS MÉTODOS QUE USAN user_id COMO IDENTIFICADOR (Arquitectura limpia)
    # =========================================================================

    def get_estudiante_by_user_id(self, user_id: int) -> Estudiante:
        """
        Obtener estudiante por user_id.
        
        Este es el método preferido para la API pública.
        Usa user_id como identificador principal en lugar del ID interno.
        """
        estudiante = self.estudiante_repository.get_by_user_id(user_id)
        if not estudiante:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Estudiante con user_id {user_id} no encontrado",
            )
        return estudiante

    def update_estudiante_by_user_id(
        self, user_id: int, estudiante_data: EstudianteSecurePatch
    ) -> Estudiante:
        """
        Actualizar estudiante usando user_id como identificador.
        
        Este método es preferido para la API pública.
        """
        # Obtener el estudiante por user_id
        estudiante = self.estudiante_repository.get_by_user_id(user_id)
        if not estudiante:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Estudiante con user_id {user_id} no encontrado",
            )

        # Reutilizar la lógica de actualización existente
        return self.update_estudiante(estudiante.id, estudiante_data)

    def delete_estudiante_by_user_id(self, user_id: int) -> bool:
        """
        Eliminar estudiante usando user_id como identificador.
        
        Este método es preferido para la API pública.
        NOTA: Solo elimina el registro de estudiante, no el usuario.
        """
        estudiante = self.estudiante_repository.get_by_user_id(user_id)
        if not estudiante:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Estudiante con user_id {user_id} no encontrado",
            )

        return self.estudiante_repository.delete(estudiante.id)
