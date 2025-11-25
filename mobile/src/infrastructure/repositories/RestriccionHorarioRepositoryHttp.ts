import { http } from "../http/httpClient";
import type {
  RestriccionHorario,
  RestriccionHorarioCreate,
  RestriccionHorarioUpdate,
} from "../../domain/restricciones/restriccionHorario";

type ApiRestriction = {
  id: number;
  docente_id: number; // el backend sigue respondiendo con docente_id
  dia_semana: number;
  hora_inicio: string;
  hora_fin: string;
  disponible: boolean;
  descripcion?: string | null;
  activa: boolean;
};

type CreateRestrictionBody = {
  dia_semana: number;
  hora_inicio: string;
  hora_fin: string;
  disponible: boolean;
  descripcion?: string | null;
  activa: boolean;
  user_id: number;
};

type MeDetailedResponse = {
  docente_info?: { id: number };
};

const normalize = (item: ApiRestriction): RestriccionHorario => ({
  id: item.id,
  docente_id: item.docente_id,
  dia_semana: item.dia_semana as RestriccionHorario["dia_semana"],
  hora_inicio: item.hora_inicio,
  hora_fin: item.hora_fin,
  disponible: item.disponible,
  descripcion: item.descripcion,
  activa: item.activa,
});

export class RestriccionHorarioRepositoryHttp {
  async getMyDocenteId(): Promise<number> {
    const { data } = await http.get<MeDetailedResponse>("/auth/me/detailed");
    const docenteId = data?.docente_info?.id;
    if (!docenteId) {
      throw new Error("No se encontró un perfil de docente para el usuario autenticado.");
    }
    return docenteId;
  }

  async listMine(): Promise<RestriccionHorario[]> {
    const { data } = await http.get<ApiRestriction[]>("/restricciones-horario/docente/mis-restricciones");
    return data.map(normalize);
  }

  async listByDocente(userId: number): Promise<RestriccionHorario[]> {
    const { data } = await http.get<ApiRestriction[]>(`/restricciones-horario/docente/${userId}`);
    return data.map(normalize);
  }

  async createMine(payload: RestriccionHorarioCreate & { user_id?: number }): Promise<RestriccionHorario> {
    // Construimos el cuerpo usando user_id. Si viene docente_id lo reutilizamos como user_id.
    const body: CreateRestrictionBody = {
      dia_semana: payload.dia_semana,
      hora_inicio: payload.hora_inicio,
      hora_fin: payload.hora_fin,
      disponible: payload.disponible,
      descripcion: payload.descripcion ?? null,
      activa: payload.activa ?? true,
      user_id: (payload as any).user_id ?? (payload as any).docente_id
    };

    if (!body.user_id) {
      throw new Error("user_id requerido para crear la restricción.");
    }

    console.debug("[RestriccionHorarioRepositoryHttp.createMine] POST body:", body);

    const { data } = await http.post<ApiRestriction>("/restricciones-horario/docente/mis-restricciones", body);
    return normalize(data);
  }

  async updateMine(id: number, payload: RestriccionHorarioUpdate & { user_id?: number }): Promise<RestriccionHorario> {
    // Para update, también aseguramos user_id si el backend lo exige.
    const patchBody = { ...payload } as any;
    if ((payload as any).user_id) {
      patchBody.user_id = (payload as any).user_id;
    } else if ((payload as any).docente_id) {
      patchBody.user_id = (payload as any).docente_id;
      delete patchBody.docente_id;
    }
    console.debug("[RestriccionHorarioRepositoryHttp.updateMine] PATCH body:", patchBody);
    const { data } = await http.patch<ApiRestriction>(`/restricciones-horario/docente/mis-restricciones/${id}`, patchBody);
    return normalize(data);
  }

  async deleteMine(id: number): Promise<void> {
    await http.delete(`/restricciones-horario/docente/mis-restricciones/${id}`);
  }
}
