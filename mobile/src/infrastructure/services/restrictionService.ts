import { http } from "../http/httpClient";

export type RestriccionHorarioInput = {
  dia_semana: number;
  hora_inicio: string;
  hora_fin: string;
  disponible: boolean;
  descripcion: string;
  activa: boolean;
  user_id: number;
};

export type RestriccionHorarioView = RestriccionHorarioInput & { id: number };

export const restrictionService = {
  async getMisRestricciones() {
    const res = await http.get("/restricciones-horario/docente/mis-restricciones");
    return (res.data && (res.data.results ?? res.data)) as RestriccionHorarioView[];
  },
  async createForDocente(input: RestriccionHorarioInput) {
    const payload = { ...input };
    const res = await http.post("/restricciones-horario/docente/mis-restricciones", payload);
    return res.data;
  },
  async update(id: number, input: RestriccionHorarioInput) {
    const res = await http.put(`/restricciones-horario/docente/mis-restricciones/${id}`, input);
    return res.data;
  },
  async delete(id: number) {
    const res = await http.delete(`/restricciones-horario/docente/mis-restricciones/${id}`);
    return res.data;
  },
};