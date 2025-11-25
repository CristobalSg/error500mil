from typing import List

from fastapi import HTTPException, status

from domain.entities import Evento, EventoCreate, EventoDetallado, User
from domain.schemas import EventoSecureCreate, EventoSecurePatch
from infrastructure.repositories.docente_repository import DocenteRepository
from infrastructure.repositories.evento_repository import EventoRepository
from infrastructure.repositories.clase_repository import ClaseRepository


class EventoUseCases:
    def __init__(
        self,
        evento_repository: EventoRepository,
        docente_repository: DocenteRepository = None,
        clase_repository: ClaseRepository = None,
    ):
        self.evento_repository = evento_repository
        self.docente_repository = docente_repository
        self.clase_repository = clase_repository

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Evento]:
        """Obtener todos los eventos con paginación"""
        return self.evento_repository.get_all(skip=skip, limit=limit)

    def get_all_active(self, skip: int = 0, limit: int = 100) -> List[Evento]:
        """Obtener todos los eventos activos con paginación"""
        return self.evento_repository.get_all_active(skip=skip, limit=limit)

    def get_by_id(self, evento_id: int) -> Evento:
        """Obtener evento por ID"""
        evento = self.evento_repository.get_by_id(evento_id)
        if not evento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Evento no encontrado"
            )
        return evento

    def _enriquecer_evento_con_clase(self, evento: Evento) -> EventoDetallado:
        """
        Enriquece un evento con información de su clase asociada.
        
        Si el evento no tiene clase_id, retorna EventoDetallado con campos de clase en None.
        """
        # Convertir evento base a diccionario
        evento_dict = evento.model_dump()
        
        # Si no hay clase_id, retornar sin datos de clase
        if not evento.clase_id or not self.clase_repository:
            return EventoDetallado(**evento_dict)
        
        # Obtener la clase con sus relaciones
        clase = self.clase_repository.get_by_id(evento.clase_id)
        if not clase:
            # Si la clase no existe, retornar sin datos de clase
            return EventoDetallado(**evento_dict)
        
        # Agregar información de la clase
        evento_dict['asignatura_nombre'] = clase.seccion.asignatura.nombre if clase.seccion and clase.seccion.asignatura else None
        evento_dict['asignatura_codigo'] = clase.seccion.asignatura.codigo if clase.seccion and clase.seccion.asignatura else None
        evento_dict['seccion_codigo'] = clase.seccion.codigo if clase.seccion else None
        evento_dict['dia_semana'] = clase.bloque.dia_semana if clase.bloque else None
        evento_dict['bloque_hora_inicio'] = clase.bloque.hora_inicio if clase.bloque else None
        evento_dict['bloque_hora_fin'] = clase.bloque.hora_fin if clase.bloque else None
        evento_dict['sala_codigo'] = clase.sala.codigo if clase.sala else None
        
        return EventoDetallado(**evento_dict)

    def get_by_id_detallado(self, evento_id: int) -> EventoDetallado:
        """Obtener evento por ID con detalles de clase"""
        evento = self.get_by_id(evento_id)
        return self._enriquecer_evento_con_clase(evento)

    def get_all_detallados(self, skip: int = 0, limit: int = 100) -> List[EventoDetallado]:
        """Obtener todos los eventos con detalles de clase"""
        eventos = self.get_all(skip, limit)
        return [self._enriquecer_evento_con_clase(e) for e in eventos]

    def _get_docente_id_from_user(self, user: User) -> int:
        """Obtener el docente_id a partir del usuario autenticado con validaciones robustas"""
        if not self.docente_repository:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Repositorio de docentes no configurado",
            )

        # Verificar que el usuario está activo
        if not user.activo:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario inactivo. No puede gestionar eventos",
            )

        # Verificar que el usuario tiene rol de docente
        if user.rol != "docente":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo los docentes pueden gestionar eventos",
            )

        # Buscar el perfil de docente asociado al usuario
        docente = self.docente_repository.get_by_user_id(user.id)
        if not docente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Perfil de docente no encontrado. Contacte al administrador",
            )

        return docente.user_id

    def get_by_docente_user(
        self, user: User, skip: int = 0, limit: int = 100
    ) -> List[Evento]:
        """Obtener eventos del docente autenticado"""
        docente_id = self._get_docente_id_from_user(user)
        return self.evento_repository.get_by_docente(docente_id, skip, limit)

    def get_active_by_docente_user(
        self, user: User, skip: int = 0, limit: int = 100
    ) -> List[Evento]:
        """Obtener eventos activos del docente autenticado"""
        docente_id = self._get_docente_id_from_user(user)
        return self.evento_repository.get_active_by_docente(docente_id, skip, limit)

    def get_by_docente_id(
        self, user_id: int, activos_solo: bool = True, skip: int = 0, limit: int = 100
    ) -> List[Evento]:
        """Obtener eventos de un docente específico usando user_id"""
        if not self.docente_repository:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Repositorio de docentes no configurado",
            )

        docente = self.docente_repository.get_by_user_id(user_id)
        if not docente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Docente con user_id {user_id} no encontrado",
            )

        if activos_solo:
            return self.evento_repository.get_active_by_docente(docente.user_id, skip, limit)
        else:
            return self.evento_repository.get_by_docente(docente.user_id, skip, limit)

    def get_by_id_and_docente_user(self, evento_id: int, user: User) -> Evento:
        """Obtener evento por ID verificando que pertenezca al docente autenticado"""
        evento = self.evento_repository.get_by_id(evento_id)

        if not evento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Evento no encontrado"
            )

        # Si es admin, puede acceder a cualquier evento
        if user.rol == "administrador":
            return evento

        # Si es docente, solo puede acceder a sus propios eventos
        docente_id = self._get_docente_id_from_user(user)
        if evento.docente_id != docente_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evento no encontrado o no pertenece al docente",
            )

        return evento

    def create(self, evento_data: EventoSecureCreate, user: User) -> Evento:
        """
        Crear un nuevo evento.
        - Administradores: pueden crear para cualquier docente
        - Docentes: solo pueden crear para sí mismos
        """
        if not self.docente_repository:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Repositorio de docentes no configurado",
            )

        # Si el usuario es administrador, puede crear para cualquier docente
        if user.rol == "administrador":
            # Resolver user_id → docente_id
            docente = self.docente_repository.get_by_user_id(evento_data.user_id)
            if not docente:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Docente con user_id {evento_data.user_id} no encontrado",
                )
            docente_id = docente.user_id
        else:
            # Si es docente, obtener su propio docente_id
            docente_id = self._get_docente_id_from_user(user)

            # Validar que no se intente asignar el evento a otro docente
            if evento_data.user_id != user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No puede crear eventos para otros docentes",
                )

        # Si se proporciona clase_id, validar que la clase pertenece al docente
        if evento_data.clase_id is not None:
            if not self.clase_repository:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Repositorio de clases no configurado",
                )
            
            clase = self.clase_repository.get_by_id(evento_data.clase_id)
            if not clase:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Clase con ID {evento_data.clase_id} no encontrada",
                )
            
            # Verificar que la clase pertenece al docente
            if clase.docente_id != docente_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="La clase especificada no pertenece al docente",
                )
            
            # Validar que la fecha del evento coincida con el día de la semana del bloque
            if clase.bloque and evento_data.fecha:
                # Obtener el día de la semana de la fecha (0=Lunes, 6=Domingo en Python)
                # El bloque usa (0=Domingo, 6=Sábado)
                dia_semana_fecha = (evento_data.fecha.weekday() + 1) % 7  # Convertir a formato del bloque
                
                if dia_semana_fecha != clase.bloque.dia_semana:
                    dias = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"La fecha {evento_data.fecha} es un {dias[dia_semana_fecha]}, pero la clase seleccionada es los {dias[clase.bloque.dia_semana]}",
                    )

        # Preparar datos con docente_id
        data_dict = evento_data.model_dump()
        data_dict.pop("user_id", None)  # Remover user_id
        data_dict["docente_id"] = docente_id  # Agregar docente_id

        # Convertir schema seguro a entidad
        evento_create = EventoCreate(**data_dict)
        return self.evento_repository.create(evento_create)

    def update(
        self, evento_id: int, evento_data: EventoSecurePatch, user: User
    ) -> Evento:
        """
        Actualizar un evento.
        - Administradores: pueden modificar cualquier evento
        - Docentes: solo pueden modificar sus propios eventos
        """
        # Verificar que el evento existe
        existing_evento = self.evento_repository.get_by_id(evento_id)
        if not existing_evento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Evento no encontrado"
            )

        # Convertir schema seguro a diccionario y filtrar valores None
        update_data = {k: v for k, v in evento_data.model_dump().items() if v is not None}

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se proporcionaron campos para actualizar",
            )

        # Si es admin, puede modificar cualquier evento
        if user.rol != "administrador":
            # Si es docente, solo puede modificar sus propios eventos
            docente_id = self._get_docente_id_from_user(user)

            if existing_evento.docente_id != docente_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No puede modificar eventos de otros docentes",
                )

        updated_evento = self.evento_repository.update(evento_id, update_data)
        if not updated_evento:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al actualizar el evento",
            )
        return updated_evento

    def toggle_active(self, evento_id: int, activo: bool) -> Evento:
        """
        Activar o desactivar un evento (solo administradores).
        Esta función asume que el permiso ya fue validado por el dependency.
        """
        evento = self.evento_repository.get_by_id(evento_id)
        if not evento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Evento no encontrado"
            )

        updated_evento = self.evento_repository.toggle_active(evento_id, activo)
        if not updated_evento:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al cambiar el estado del evento",
            )
        return updated_evento

    def delete(self, evento_id: int, user: User) -> bool:
        """
        Eliminar un evento.
        - Administradores: pueden eliminar cualquier evento
        - Docentes: solo pueden eliminar sus propios eventos
        """
        # Verificar que el evento existe
        existing_evento = self.evento_repository.get_by_id(evento_id)
        if not existing_evento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Evento no encontrado"
            )

        # Si es admin, puede eliminar cualquier evento
        if user.rol != "administrador":
            # Si es docente, solo puede eliminar sus propios eventos
            docente_id = self._get_docente_id_from_user(user)

            if existing_evento.docente_id != docente_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No puede eliminar eventos de otros docentes",
                )

        success = self.evento_repository.delete(evento_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar el evento",
            )
        return success
