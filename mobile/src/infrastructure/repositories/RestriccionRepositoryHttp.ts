import { http } from "../http/httpClient";

type ApiRestriccion = {
  id: string;
  docente_id: string;
  dia: string;
  hora_inicio: string;
  hora_fin: string;
  motivo?: string;
};

export class RestriccionRepositoryHttp {
  async listRestricciones(): Promise<ApiRestriccion[]> {
    const { data } = await http.get<ApiRestriccion[]>("/restricciones", { params: { limit: 500 } });
    return data;
  }

  async listRestriccionesByDocente(docenteId: string): Promise<ApiRestriccion[]> {
    const { data } = await http.get<ApiRestriccion[]>(`/restricciones/docente/${docenteId}`);
    return data;
  }
}