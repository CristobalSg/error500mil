// src/presentation/hooks/useEvents.ts
import { useState, useEffect, useCallback } from "react";
import { message } from "antd";
import type { Event, CreateEventDTO, UpdateEventDTO } from "../../domain/events/event";
import { eventRepository } from "../../infrastructure/repositories/EventRepositoryHttp";
import { useAuth } from "./useAuth";

export function useEvents() {
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { user } = useAuth();

  // Cargar todos los eventos
  const fetchEvents = useCallback(async () => {
    if (!user) return;
    
    setLoading(true);
    setError(null);
    try {
      const data = await eventRepository.getAll();
      setEvents(data);
    } catch (err: any) {
      const errorMsg = err?.response?.data?.detail || "Error al cargar eventos";
      setError(errorMsg);
      message.error(errorMsg);
    } finally {
      setLoading(false);
    }
  }, [user]);

  // Crear evento
  const createEvent = useCallback(
    async (eventData: Omit<CreateEventDTO, "user_id">) => {
      if (!user?.id) {
        message.error("No se pudo identificar el usuario");
        return null;
      }

      setLoading(true);
      try {
        const newEvent = await eventRepository.create({
          ...eventData,
          user_id: parseInt(user.id, 10),
          active: eventData.active ?? true,
        });
        setEvents((prev) => [...prev, newEvent]);
        message.success("Evento creado exitosamente");
        return newEvent;
      } catch (err: any) {
        const errorMsg = err?.response?.data?.detail || "Error al crear evento";
        message.error(errorMsg);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [user]
  );

  // Actualizar evento
  const updateEvent = useCallback(async (id: number, eventData: UpdateEventDTO) => {
    setLoading(true);
    try {
      const updated = await eventRepository.update(id, eventData);
      setEvents((prev) => prev.map((e) => (e.id === id ? updated : e)));
      message.success("Evento actualizado exitosamente");
      return updated;
    } catch (err: any) {
      const errorMsg = err?.response?.data?.detail || "Error al actualizar evento";
      message.error(errorMsg);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  // Eliminar evento
  const deleteEvent = useCallback(async (id: number) => {
    setLoading(true);
    try {
      await eventRepository.delete(id);
      setEvents((prev) => prev.filter((e) => e.id !== id));
      message.success("Evento eliminado exitosamente");
      return true;
    } catch (err: any) {
      const errorMsg = err?.response?.data?.detail || "Error al eliminar evento";
      message.error(errorMsg);
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  // Cargar eventos al montar
  useEffect(() => {
    fetchEvents();
  }, [fetchEvents]);

  return {
    events,
    loading,
    error,
    fetchEvents,
    createEvent,
    updateEvent,
    deleteEvent,
  };
}
