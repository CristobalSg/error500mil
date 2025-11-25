// src/presentation/components/UserAvatar.tsx
import React from 'react';
import { getUserAvatar } from '../../utils/avatars';
import type { Gender } from '../../utils/avatars';

interface UserAvatarProps {
  /** URL del avatar del usuario (opcional) */
  avatarUrl?: string | null;
  /** Género del usuario para seleccionar avatar predeterminado */
  gender?: Gender | string;
  /** Nombre del usuario para el atributo alt */
  userName?: string;
  /** Tamaño del avatar en píxeles */
  size?: number;
  /** Clase CSS adicional */
  className?: string;
}

/**
 * Componente para mostrar el avatar del usuario
 * Si no tiene avatar personalizado, muestra uno predeterminado según el género
 */
export const UserAvatar: React.FC<UserAvatarProps> = ({
  avatarUrl,
  gender,
  userName = 'Usuario',
  size = 120,
  className = '',
}) => {
  const avatarSrc = getUserAvatar(avatarUrl, gender);

  return (
    <div 
      className={`relative inline-block ${className}`}
      style={{ width: size, height: size }}
    >
      <img
        src={avatarSrc}
        alt={`Avatar de ${userName}`}
        className="rounded-full object-cover w-full h-full border-2 border-gray-300"
      />
    </div>
  );
};

export default UserAvatar;
