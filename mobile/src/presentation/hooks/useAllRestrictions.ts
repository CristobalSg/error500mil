import { useCallback, useEffect, useState } from "react";
import {
  AdminRestriccionHorarioRepositoryHttp,
  type AdminRestriccionHorarioDTO,
} from "../../infrastructure/repositories/AdminRestriccionHorarioRepositoryHttp";

interface UseAllRestrictionsOptions {
  page?: number;
  size?: number;
  docente_id?: number;
  auto?: boolean;
}

export function useAllRestrictions(opts: UseAllRestrictionsOptions = { auto: true }) {
  const repo = new AdminRestriccionHorarioRepositoryHttp();
  const [restricciones, setRestricciones] = useState<AdminRestriccionHorarioDTO[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(opts.page ?? 1);
  const [size, setSize] = useState(opts.size ?? 100);
  const [docenteId, setDocenteId] = useState<number | undefined>(opts.docente_id);

  const fetchAll = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await repo.list({ page, size, docente_id: docenteId });
      setRestricciones(data);
    } catch (e: any) {
      const msg =
        e?.response?.data?.detail ||
        e?.response?.data?.message ||
        e?.message ||
        "Error al cargar restricciones";
      setError(String(msg));
      setRestricciones([]);
    } finally {
      setLoading(false);
    }
  }, [page, size, docenteId]);

  useEffect(() => {
    if (opts.auto !== false) fetchAll();
  }, [fetchAll, opts.auto]);

  return {
    restricciones,
    loading,
    error,
    refresh: fetchAll,
    page,
    size,
    setPage,
    setSize,
    setDocenteId,
  };
}