// src/domain/repositories/AvatarRepository.ts

export interface AvatarUploadResponse {
  avatar_url: string;
  message?: string;
}

export interface AvatarRepository {
  /**
   * Sube un nuevo avatar para el usuario actual
   * @param file - Archivo de imagen a subir
   * @returns URL del avatar subido
   */
  uploadAvatar(file: File): Promise<AvatarUploadResponse>;

  /**
   * Elimina el avatar actual del usuario
   * @returns Confirmación de eliminación
   */
  deleteAvatar(): Promise<{ message: string }>;
}
