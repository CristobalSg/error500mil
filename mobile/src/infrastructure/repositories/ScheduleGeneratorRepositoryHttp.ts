// src/infrastructure/repositories/ScheduleGeneratorRepositoryHttp.ts
import type { ScheduleGeneratorRepository, GenerateScheduleResponse } from "../../domain/repositories/ScheduleGeneratorRepository";
import http from "../http/httpClient";

export class ScheduleGeneratorRepositoryHttp implements ScheduleGeneratorRepository {
  private readonly baseUrl = "/horarios";

  async generateSchedule(): Promise<GenerateScheduleResponse> {
    const response = await http.post<GenerateScheduleResponse>(`${this.baseUrl}/generar`, {});
    return response.data;
  }

  async getGenerationStatus(): Promise<{
    status: 'pending' | 'in_progress' | 'completed' | 'failed';
    progress?: number;
    message?: string;
  }> {
    const response = await http.get(`${this.baseUrl}/estado-generacion`);
    return response.data;
  }
}

// Singleton
export const scheduleGeneratorRepository = new ScheduleGeneratorRepositoryHttp();
