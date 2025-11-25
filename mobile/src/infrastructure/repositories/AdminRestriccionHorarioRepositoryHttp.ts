import { http } from "../http/httpClient";

// Si no tienes un tipo DayOfWeek definido, puedes reemplazarlo por: type DayOfWeek = number;
type DayOfWeek = number;

export interface AdminRestriccionHorarioDTO {
  id: number;
  docente_id: number;
  dia_semana: DayOfWeek;
  hora_inicio: string;
  hora_fin: string;
  disponible: boolean;
  descripcion?: string | null;
  activa: boolean;
}

type Raw = any;

function extractArray(payload: Raw): Raw[] {
  if (!payload) return [];
  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload.results)) return payload.results;
  if (Array.isArray(payload.items)) return payload.items;
  if (Array.isArray(payload.data)) return payload.data;
  return [];
}

function normalize(r: Raw): AdminRestriccionHorarioDTO {
  return {
    id: r.id,
    docente_id: r.docente_id ?? r.teacher_id ?? r.user_id ?? 0,
    dia_semana: r.dia_semana ?? r.day_of_week ?? r.dia ?? 0,
    hora_inicio: r.hora_inicio ?? r.start_time ?? r.horaInicio ?? "",
    hora_fin: r.hora_fin ?? r.end_time ?? r.horaFin ?? "",
    disponible: r.disponible ?? r.available ?? r.is_available ?? false,
    descripcion: r.descripcion ?? r.description ?? null,
    activa: r.activa ?? r.active ?? r.is_active ?? true,
  };
}

export class AdminRestriccionHorarioRepositoryHttp {
  private baseUrl = "/restricciones-horario";

  /**
   * Lista todas las restricciones (admin). Soporta paginación opcional.
   */
  async list(params?: { page?: number; size?: number; docente_id?: number }) {
    const response = await http.get(`${this.baseUrl}/`, { params });
    return extractArray(response.data).map(normalize) as AdminRestriccionHorarioDTO[];
  }

  async getById(id: number) {
    const response = await http.get(`${this.baseUrl}/${id}`);
    return normalize(response.data);
  }

  async create(payload: Partial<AdminRestriccionHorarioDTO>) {
    const response = await http.post(this.baseUrl, payload);
    return normalize(response.data);
  }

  async update(id: number, payload: Partial<AdminRestriccionHorarioDTO>) {
    const response = await http.put(`${this.baseUrl}/${id}`, payload);
    return normalize(response.data);
  }

  async delete(id: number) {
    await http.delete(`${this.baseUrl}/${id}`);
  }

  async toggleActiva(id: number, activa: boolean) {
    try {
      console.log(`[AdminRestriccionHorarioRepo] Obteniendo restricción ${id}...`);
      
      // Primero obtenemos la restricción completa
      const current = await this.getById(id);
      console.log(`[AdminRestriccionHorarioRepo] Restricción actual:`, current);
      
      // Actualizamos con todos los campos, cambiando solo 'activa'
      const payload = {
        dia_semana: current.dia_semana,
        hora_inicio: current.hora_inicio,
        hora_fin: current.hora_fin,
        disponible: current.disponible,
        descripcion: current.descripcion,
        activa: activa,
      };
      
      console.log(`[AdminRestriccionHorarioRepo] Actualizando con payload:`, payload);
      
      const response = await http.put(`${this.baseUrl}/${id}`, payload);
      console.log(`[AdminRestriccionHorarioRepo] Respuesta del servidor:`, response.data);
      
      return normalize(response.data);
    } catch (error) {
      console.error(`[AdminRestriccionHorarioRepo] Error al actualizar restricción ${id}:`, error);
      throw error;
    }
  }
}
