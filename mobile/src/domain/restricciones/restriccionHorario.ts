export type DayOfWeek = 0 | 1 | 2 | 3 | 4 | 5 | 6;

export interface RestriccionHorario {
  id: number;
  docente_id: number;
  dia_semana: DayOfWeek;
  hora_inicio: string; // formato HH:mm[:ss] según backend
  hora_fin: string;    // formato HH:mm[:ss] según backend
  disponible: boolean;
  descripcion?: string | null;
  activa: boolean;
}

export interface RestriccionHorarioCreate {
  docente_id: number;
  dia_semana: DayOfWeek;
  hora_inicio: string;
  hora_fin: string;
  disponible: boolean;
  descripcion?: string | null;
  activa?: boolean;
}

export type RestriccionHorarioUpdate = Partial<Omit<RestriccionHorarioCreate, "docente_id">> & {
  docente_id?: number;
};
