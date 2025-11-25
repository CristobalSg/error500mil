// src/presentation/hooks/useAvatarSelection.ts
import { useState } from 'react';
import httpClient from '../../infrastructure/http/httpClient';

export const useAvatarSelection = () => {
  const [updating, setUpdating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const selectAvatar = async (avatarType: 'male' | 'female'): Promise<void> => {
    setUpdating(true);
    setError(null);

    try {
      // Enviar al backend la selección del avatar
      await httpClient.patch('/users/me/avatar', {
        avatar_type: avatarType,
      });
    } catch (err: any) {
      const errorMessage = 
        err?.response?.data?.detail?.[0]?.msg ||
        err?.response?.data?.message ||
        err?.message ||
        'Error al actualizar el avatar';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setUpdating(false);
    }
  };

  return {
    selectAvatar,
    updating,
    error,
  };
};
