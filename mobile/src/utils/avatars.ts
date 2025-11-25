// Utilidad para manejar avatares predeterminados
import defaultAvatarMale from '../assets/images/avatars/default-avatar-male.svg';
import defaultAvatarFemale from '../assets/images/avatars/default-avatar-female.svg';

export type Gender = 'male' | 'female' | 'other';

/**
 * Obtiene la URL del avatar predeterminado según el género
 * @param gender - Género del usuario ('male', 'female', u 'other')
 * @returns URL del avatar predeterminado
 */
export const getDefaultAvatar = (gender?: Gender | string): string => {
  switch (gender?.toLowerCase()) {
    case 'male':
    case 'masculino':
    case 'm':
      return defaultAvatarMale;
    case 'female':
    case 'femenino':
    case 'f':
      return defaultAvatarFemale;
    default:
      // Por defecto, usar el avatar masculino
      return defaultAvatarMale;
  }
};

/**
 * Obtiene la URL del avatar del usuario, usando uno predeterminado si no tiene
 * @param userAvatarUrl - URL del avatar del usuario (puede ser null/undefined)
 * @param gender - Género del usuario para seleccionar avatar predeterminado
 * @returns URL del avatar a mostrar
 */
export const getUserAvatar = (userAvatarUrl?: string | null, gender?: Gender | string): string => {
  return userAvatarUrl || getDefaultAvatar(gender);
};

export { defaultAvatarMale, defaultAvatarFemale };
