// src/infrastructure/repositories/AvatarRepositoryHttp.ts
import httpClient from '../http/httpClient';
import type { AvatarRepository, AvatarUploadResponse } from '../../domain/repositories/AvatarRepository';

export class AvatarRepositoryHttp implements AvatarRepository {
  private static instance: AvatarRepositoryHttp;

  private constructor() {}

  public static getInstance(): AvatarRepositoryHttp {
    if (!AvatarRepositoryHttp.instance) {
      AvatarRepositoryHttp.instance = new AvatarRepositoryHttp();
    }
    return AvatarRepositoryHttp.instance;
  }

  async uploadAvatar(file: File): Promise<AvatarUploadResponse> {
    const formData = new FormData();
    formData.append('avatar', file);

    const response = await httpClient.post<AvatarUploadResponse>(
      '/users/me/avatar',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );

    return response.data;
  }

  async deleteAvatar(): Promise<{ message: string }> {
    const response = await httpClient.delete<{ message: string }>('/users/me/avatar');
    return response.data;
  }
}

// Singleton instance
export const avatarRepository = AvatarRepositoryHttp.getInstance();
