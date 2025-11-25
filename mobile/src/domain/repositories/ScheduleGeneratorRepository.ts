// src/domain/repositories/ScheduleGeneratorRepository.ts

export interface GenerateScheduleResponse {
  success: boolean;
  message: string;
  schedule_id?: number;
}

export interface ScheduleGeneratorRepository {
  /**
   * Generar el horario del semestre
   */
  generateSchedule(): Promise<GenerateScheduleResponse>;
  
  /**
   * Obtener el estado de la generación del horario
   */
  getGenerationStatus(): Promise<{
    status: 'pending' | 'in_progress' | 'completed' | 'failed';
    progress?: number;
    message?: string;
  }>;
}
