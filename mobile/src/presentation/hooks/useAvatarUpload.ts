// src/presentation/hooks/useAvatarUpload.ts
import { useState } from 'react';
import { avatarRepository } from '../../infrastructure/repositories/AvatarRepositoryHttp';

export const useAvatarUpload = () => {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const uploadAvatar = async (file: File): Promise<string> => {
    setUploading(true);
    setError(null);

    try {
      const response = await avatarRepository.uploadAvatar(file);
      return response.avatar_url;
    } catch (err: any) {
      const errorMessage = 
        err?.response?.data?.detail?.[0]?.msg ||
        err?.response?.data?.message ||
        err?.message ||
        'Error al subir la imagen';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setUploading(false);
    }
  };

  const deleteAvatar = async (): Promise<void> => {
    setUploading(true);
    setError(null);

    try {
      await avatarRepository.deleteAvatar();
    } catch (err: any) {
      const errorMessage = 
        err?.response?.data?.detail?.[0]?.msg ||
        err?.response?.data?.message ||
        err?.message ||
        'Error al eliminar la imagen';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setUploading(false);
    }
  };

  return {
    uploadAvatar,
    deleteAvatar,
    uploading,
    error,
  };
};
