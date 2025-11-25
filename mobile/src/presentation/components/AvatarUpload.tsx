// src/presentation/components/AvatarUpload.tsx
import { useState, useRef } from 'react';
import { CameraIcon } from '@heroicons/react/24/outline';
import { message, Modal } from 'antd';
import UserAvatar from './UserAvatar';
import type { Gender } from '../../utils/avatars';

interface AvatarUploadProps {
  /** URL actual del avatar */
  currentAvatar?: string | null;
  /** Género del usuario */
  gender?: Gender | string;
  /** Nombre del usuario */
  userName?: string;
  /** Tamaño del avatar en píxeles */
  size?: number;
  /** Callback cuando se selecciona una nueva imagen */
  onAvatarChange?: (file: File) => void;
  /** Callback cuando se sube la imagen al servidor */
  onAvatarUpload?: (file: File) => Promise<string>;
  /** Si está cargando */
  loading?: boolean;
}

/**
 * Componente para subir/cambiar el avatar del usuario
 */
export const AvatarUpload: React.FC<AvatarUploadProps> = ({
  currentAvatar,
  gender,
  userName = 'Usuario',
  size = 120,
  onAvatarChange,
  onAvatarUpload,
  loading = false,
}) => {
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validar tipo de archivo
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
    if (!validTypes.includes(file.type)) {
      message.error('Solo se permiten imágenes (JPG, PNG, GIF, WEBP)');
      return;
    }

    // Validar tamaño (máximo 5MB)
    const maxSize = 5 * 1024 * 1024; // 5MB
    if (file.size > maxSize) {
      message.error('La imagen no debe superar los 5MB');
      return;
    }

    // Crear preview local
    const reader = new FileReader();
    reader.onloadend = () => {
      setPreviewUrl(reader.result as string);
    };
    reader.readAsDataURL(file);

    // Notificar cambio
    onAvatarChange?.(file);

    // Si hay callback de upload, subir automáticamente
    if (onAvatarUpload) {
      Modal.confirm({
        title: '¿Cambiar foto de perfil?',
        content: '¿Deseas actualizar tu foto de perfil con esta imagen?',
        okText: 'Sí, cambiar',
        cancelText: 'Cancelar',
        onOk: async () => {
          setUploading(true);
          try {
            const newAvatarUrl = await onAvatarUpload(file);
            message.success('Foto de perfil actualizada correctamente');
            setPreviewUrl(null);
            // Resetear input
            if (fileInputRef.current) {
              fileInputRef.current.value = '';
            }
            return newAvatarUrl;
          } catch (error: any) {
            message.error(error?.message || 'Error al subir la imagen');
            setPreviewUrl(null);
          } finally {
            setUploading(false);
          }
        },
        onCancel: () => {
          setPreviewUrl(null);
          if (fileInputRef.current) {
            fileInputRef.current.value = '';
          }
        },
      });
    }
  };

  const handleButtonClick = () => {
    fileInputRef.current?.click();
  };

  const displayAvatar = previewUrl || currentAvatar;
  const isLoading = loading || uploading;

  return (
    <div className="relative inline-block">
      <div className={`relative ${isLoading ? 'opacity-50' : ''}`}>
        <UserAvatar
          avatarUrl={displayAvatar}
          gender={gender}
          userName={userName}
          size={size}
        />
        
        {/* Botón de cámara */}
        <button
          type="button"
          onClick={handleButtonClick}
          disabled={isLoading}
          className="absolute bottom-0 right-0 bg-blue-600 hover:bg-blue-700 text-white rounded-full p-2 shadow-lg transition-colors disabled:bg-gray-400"
          aria-label="Cambiar foto de perfil"
        >
          <CameraIcon className="h-5 w-5" />
        </button>
      </div>

      {/* Input oculto para seleccionar archivo */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/jpeg,image/jpg,image/png,image/gif,image/webp"
        onChange={handleFileSelect}
        className="hidden"
        disabled={isLoading}
      />

      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      )}
    </div>
  );
};

export default AvatarUpload;
