// src/domain/repositories/EventRepository.ts
import type { Event, CreateEventDTO, UpdateEventDTO, DetailedEvent } from "../events/event";

export interface EventRepository {
  /**
   * Obtener todos los eventos del usuario autenticado
   */
  getAll(): Promise<Event[]>;

  /**
   * Crear un nuevo evento
   */
  create(event: CreateEventDTO): Promise<Event>;

  /**
   * Actualizar un evento existente
   */
  update(id: number, event: UpdateEventDTO): Promise<Event>;

  /**
   * Eliminar un evento
   */
  delete(id: number): Promise<void>;

  /**
   * Obtener un evento por ID
   */
  getById(id: number): Promise<Event>;

  /**
   * Obtener eventos con información enriquecida (asignatura, sección, sala, etc.)
   */
  getDetailed(): Promise<DetailedEvent[]>;
}
