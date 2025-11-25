import { http } from "../http/httpClient";

type ApiDocente = {
  id: string;
  user_id: string;
  departamento?: string | null;
  user?: {
    id: string;
    nombre: string;
    email: string;
    rol: string;
  };
};

type DocenteSummary = {
  id: string;
  userId: string;
  nombre: string;
  email: string;
  rol: string;
  departamento: string | null;
};

const normalizeDocente = (item: ApiDocente): DocenteSummary => ({
  id: item.id,
  userId: item.user_id,
  nombre: item.user?.nombre ?? "",
  email: item.user?.email ?? "",
  rol: item.user?.rol ?? "",
  departamento: item.departamento ?? null,
});

export class DocenteRepositoryHttp {
  async listDocentes(): Promise<DocenteSummary[]> {
    const { data } = await http.get<ApiDocente[]>("/docentes", { params: { limit: 500 } });
    return data.map(normalizeDocente);
  }
}
