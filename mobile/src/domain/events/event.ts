// src/domain/events/event.ts
export interface Event {
  id?: number;
  nombre: string;
  descripcion?: string;
  fecha: string; // ✅ OBLIGATORIO - Formato YYYY-MM-DD
  hora_inicio: string; // Formato HH:mm:ss
  hora_cierre: string; // Formato HH:mm:ss
  active: boolean;
  user_id: number;
  clase_id?: number | null; // ✅ OPCIONAL - ID de la clase vinculada
  created_at?: string;
  updated_at?: string;
}

export interface CreateEventDTO {
  nombre: string;
  descripcion?: string;
  fecha: string; // ✅ OBLIGATORIO - Formato YYYY-MM-DD
  hora_inicio: string;
  hora_cierre: string;
  active?: boolean;
  user_id: number;
  clase_id?: number | null; // ✅ OPCIONAL - ID de la clase vinculada
}

export interface UpdateEventDTO {
  nombre?: string;
  descripcion?: string;
  fecha?: string; // OPCIONAL en PATCH - Formato YYYY-MM-DD
  hora_inicio?: string;
  hora_cierre?: string;
  active?: boolean;
  clase_id?: number | null; // ✅ OPCIONAL - ID de la clase vinculada
}

// Tipo para eventos con información enriquecida
export interface DetailedEvent extends Event {
  asignatura_nombre?: string;
  asignatura_codigo?: string;
  seccion_codigo?: string;
  dia_semana?: number; // 0=Domingo, 6=Sábado
  bloque_hora_inicio?: string;
  bloque_hora_fin?: string;
  sala_codigo?: string;
}
