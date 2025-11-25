// src/presentation/hooks/useScheduleGenerator.ts
import { useState, useCallback } from "react";
import { message } from "antd";
import { scheduleGeneratorRepository } from "../../infrastructure/repositories/ScheduleGeneratorRepositoryHttp";

export function useScheduleGenerator() {
  const [generating, setGenerating] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const generateSchedule = useCallback(async () => {
    setGenerating(true);
    setProgress(0);
    setError(null);

    try {
      // Simular progreso mientras se genera
      const progressInterval = setInterval(() => {
        setProgress((prev) => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 500);

      const response = await scheduleGeneratorRepository.generateSchedule();

      clearInterval(progressInterval);
      setProgress(100);

      if (response.success) {
        message.success(response.message || "Horario generado exitosamente");
        
        // Esperar un momento para mostrar el 100% antes de resetear
        setTimeout(() => {
          setGenerating(false);
          setProgress(0);
        }, 1500);
        
        return true;
      } else {
        throw new Error(response.message || "Error al generar el horario");
      }
    } catch (err: any) {
      const errorMsg = err?.response?.data?.detail || err?.message || "Error al generar el horario";
      setError(errorMsg);
      message.error(errorMsg);
      setGenerating(false);
      setProgress(0);
      return false;
    }
  }, []);

  const resetProgress = useCallback(() => {
    setGenerating(false);
    setProgress(0);
    setError(null);
  }, []);

  return {
    generating,
    progress,
    error,
    generateSchedule,
    resetProgress,
  };
}
