import { useCallback, useEffect, useState } from "react";
import {
  UserRepositoryHttp,
  type AdminUserUpdateInput,
} from "../../infrastructure/repositories/UserRepositoryHttp";

// Tipo expuesto a la UI
export type AdminUserView = {
  id: number;
  name: string;
  email: string;
  role: string;
  docenteId?: number | null;
  department?: string | null;
};

// Ejemplo de mapeo:
const toView = (u: any): AdminUserView => ({
  id: u.id,
  name: u.name,
  email: u.email,
  role: (u.role ?? u.rol ?? "").toString().toLowerCase(),
  docenteId: u.docenteId ?? u.docente_id ?? u.docente_info?.id ?? null,
  department: u.department ?? u.departamento ?? u.docente_info?.department ?? null,
});

export function useAdminUsers() {
  const repo = new UserRepositoryHttp();
  const [users, setUsers] = useState<AdminUserView[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await repo.list();
      setUsers(data.map(toView));
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || "Error al cargar usuarios");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const createUser = useCallback(
    async (data: { name: string; email: string; role: string; password?: string; department?: string }) => {
      await repo.create(data);
      await refresh();
    },
    [refresh]
  );

  const updateUser = useCallback(
    async (id: number, data: AdminUserUpdateInput) => {
      try {
        await repo.update(id, data);
      } catch (e: any) {
        throw new Error(e?.response?.data?.detail || e?.message || "No se pudo actualizar el usuario");
      }
    },
    []
  );

  const deleteUser = useCallback(async (id: number) => {
    try {
      await repo.delete(id);
    } catch (e: any) {
      throw new Error(e?.response?.data?.detail || e?.message || "No se pudo eliminar el usuario");
    }
  }, []);

  return { users, loading, error, refresh, createUser, updateUser, deleteUser };
}
