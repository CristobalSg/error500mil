import { useState, useEffect } from "react";
import { restrictionService, type RestriccionHorarioInput, type RestriccionHorarioView } from "../../infrastructure/services/restrictionService";

export const useDocenteHorarioRestrictions = () => {
  const [restricciones, setRestricciones] = useState<RestriccionHorarioView[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [pendingDelete, setPendingDelete] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchMisRestricciones = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await restrictionService.getMisRestricciones();
      setRestricciones(data);
    } catch (e: any) {
      setError(e?.message ?? "Error al cargar restricciones");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMisRestricciones();
  }, []);

  const addRestriction = async (input: RestriccionHorarioInput) => {
    setSaving(true);
    setError(null);
    try {
      await restrictionService.createForDocente(input);
      await fetchMisRestricciones();
    } catch (e: any) {
      setError(e?.message ?? "Error al agregar restricción");
      throw e;
    } finally {
      setSaving(false);
    }
  };

  const updateRestriction = async (id: number, input: RestriccionHorarioInput) => {
    setSaving(true);
    setError(null);
    try {
      await restrictionService.update(id, input);
      await fetchMisRestricciones();
    } catch (e: any) {
      setError(e?.message ?? "Error al actualizar restricción");
      throw e;
    } finally {
      setSaving(false);
    }
  };

  const deleteRestriction = async (id: number) => {
    setPendingDelete(id);
    setError(null);
    try {
      await restrictionService.delete(id);
      await fetchMisRestricciones();
    } catch (e: any) {
      setError(e?.message ?? "Error al eliminar restricción");
      throw e;
    } finally {
      setPendingDelete(null);
    }
  };

  return {
    restricciones,
    loading,
    saving,
    pendingDelete,
    error,
    addRestriction,
    updateRestriction,
    deleteRestriction,
    refetch: fetchMisRestricciones,
  };
};




export type { RestriccionHorarioInput, RestriccionHorarioView };
