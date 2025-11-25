import { http } from "../http/httpClient";

type ApiSchedule = {
  id: string;
  docente_id: string;
  asignatura_id: string;
  dia: string;
  hora_inicio: string;
  hora_fin: string;
};

export class ScheduleRepositoryHttp {
  async listSchedules(): Promise<ApiSchedule[]> {
    const { data } = await http.get<ApiSchedule[]>("/horarios", { params: { limit: 500 } });
    return data;
  }

  async getSchedule(id: string): Promise<ApiSchedule> {
    const { data } = await http.get<ApiSchedule>(`/horarios/${id}`);
    return data;
  }

  async createSchedule(schedule: Partial<ApiSchedule>): Promise<void> {
    await http.post("/horarios", schedule);
  }

  async updateSchedule(id: string, schedule: Partial<ApiSchedule>): Promise<void> {
    await http.put(`/horarios/${id}`, schedule);
  }

  async deleteSchedule(id: string): Promise<void> {
    await http.delete(`/horarios/${id}`);
  }
}
