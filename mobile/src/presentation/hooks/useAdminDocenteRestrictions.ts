import { useCallback, useMemo, useState } from "react";
import { RestriccionHorarioRepositoryHttp } from "../../infrastructure/repositories/RestriccionHorarioRepositoryHttp";
import { AdminRestriccionHorarioRepositoryHttp } from "../../infrastructure/repositories/AdminRestriccionHorarioRepositoryHttp";
import type { DayOfWeek } from "../../domain/restricciones/restriccionHorario";

export interface AdminRestrictionView {
  id: number;
  docenteId: number;
  day: DayOfWeek;
  start: string;
  end: string;
  disponible: boolean;
  descripcion?: string | null;
  activa: boolean;
}

const formatTime = (value: string) => (value ? value.slice(0, 5) : value);

const normalize = (item: AdminRestrictionView): AdminRestrictionView => ({
  ...item,
  start: formatTime(item.start),
  end: formatTime(item.end),
});

const sortByDayAndTime = (a: AdminRestrictionView, b: AdminRestrictionView) => {
  if (a.day !== b.day) return a.day - b.day;
  return a.start.localeCompare(b.start);
};

export function useAdminDocenteRestrictions() {
  // Repositorios
  const repo = useMemo(() => new RestriccionHorarioRepositoryHttp(), []);
  const adminRepo = useMemo(() => new AdminRestriccionHorarioRepositoryHttp(), []);

  // Estados
  const [docenteId, setDocenteId] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [restrictions, setRestrictions] = useState<AdminRestrictionView[]>([]);

  // Limpiar datos
  const clear = useCallback(() => {
    setDocenteId(null);
    setRestrictions([]);
    setError(null);
    setLoading(false);
  }, []);

  /**
   * Cargar restricciones de un docente por su user_id
   */
  const fetchForDocente = useCallback(
    async (targetUserId: number | null) => {
      if (!targetUserId) {
        clear();
        return;
      }

      setLoading(true);
      setError(null);
      setDocenteId(targetUserId);

      try {
        const data = await repo.listByDocente(targetUserId);
        const normalized = data.map((item) =>
          normalize({
            id: item.id,
            docenteId: item.docente_id,
            day: item.dia_semana,
            start: item.hora_inicio,
            end: item.hora_fin,
            disponible: item.disponible,
            descripcion: item.descripcion,
            activa: item.activa,
          }),
        );
        setRestrictions(normalized.sort(sortByDayAndTime));
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "No se pudieron cargar las restricciones."
        );
        setRestrictions([]);
      } finally {
        setLoading(false);
      }
    },
    [clear, repo],
  );

  /**
   * ✅ Aceptar o rechazar una restricción (activar/desactivar)
   */
  const toggleActiva = useCallback(
    async (id: number, activa: boolean) => {
      const prevLoading = loading;
      try {
        console.log(`[useAdminDocenteRestrictions] Cambiando restricción ${id} a activa=${activa}`);
        setLoading(true);
        await adminRepo.toggleActiva(id, activa);
        console.log(`[useAdminDocenteRestrictions] Restricción ${id} actualizada correctamente`);
        
        // Refresca la lista del docente actual si existe
        if (docenteId) {
          console.log(`[useAdminDocenteRestrictions] Recargando restricciones para usuario ${docenteId}`);
          await fetchForDocente(docenteId);
        }
      } catch (err) {
        console.error("[useAdminDocenteRestrictions] Error al cambiar el estado de la restricción:", err);
        const errorMessage = err instanceof Error ? err.message : "No se pudo actualizar el estado de la restricción.";
        setError(errorMessage);
        throw err;
      } finally {
        setLoading(prevLoading);
      }
    },
    [adminRepo, docenteId, fetchForDocente, loading],
  );

  /**
   * Wrapper: aceptar (activa = true)
   */
  const aceptarRestriccion = useCallback(
    async (id: number) => {
      return toggleActiva(id, true);
    },
    [toggleActiva],
  );

  /**
   * Wrapper: rechazar (activa = false)
   */
  const rechazarRestriccion = useCallback(
    async (id: number) => {
      return toggleActiva(id, false);
    },
    [toggleActiva],
  );

  return {
    docenteId,
    loading,
    error,
    restrictions,
    fetchForDocente,
    clear,
    toggleActiva,
    aceptarRestriccion,
    rechazarRestriccion,
  };
}
