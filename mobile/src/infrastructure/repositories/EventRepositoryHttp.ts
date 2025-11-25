// src/infrastructure/repositories/EventRepositoryHttp.ts
import type { EventRepository } from "../../domain/repositories/EventRepository";
import type { Event, CreateEventDTO, UpdateEventDTO, DetailedEvent } from "../../domain/events/event";
import http from "../http/httpClient";

export class EventRepositoryHttp implements EventRepository {
  private readonly baseUrl = "/eventos";

  async getAll(): Promise<Event[]> {
    const response = await http.get<Event[]>(`${this.baseUrl}/`);
    return response.data;
  }

  async create(event: CreateEventDTO): Promise<Event> {
    // Asegurarse de enviar todos los campos correctamente
    const payload = {
      nombre: event.nombre,
      descripcion: event.descripcion,
      fecha: event.fecha, // ✅ Campo obligatorio en formato YYYY-MM-DD
      hora_inicio: event.hora_inicio, // Formato HH:mm:ss
      hora_cierre: event.hora_cierre, // Formato HH:mm:ss
      active: event.active ?? true,
      user_id: event.user_id,
      clase_id: event.clase_id ?? null, // ✅ Campo opcional
    };
    
    const response = await http.post<Event>(`${this.baseUrl}/`, payload);
    return response.data;
  }

  async update(id: number, event: UpdateEventDTO): Promise<Event> {
    // PATCH en lugar de PUT para actualizaciones parciales
    const response = await http.patch<Event>(`${this.baseUrl}/${id}`, event);
    return response.data;
  }

  async delete(id: number): Promise<void> {
    await http.delete(`${this.baseUrl}/${id}`);
  }

  async getById(id: number): Promise<Event> {
    const response = await http.get<Event>(`${this.baseUrl}/${id}`);
    return response.data;
  }

  // ✅ Nuevo método para obtener eventos con información enriquecida
  async getDetailed(): Promise<DetailedEvent[]> {
    const response = await http.get<DetailedEvent[]>(`${this.baseUrl}/detallados`);
    return response.data;
  }
}

// Singleton
export const eventRepository = new EventRepositoryHttp();
