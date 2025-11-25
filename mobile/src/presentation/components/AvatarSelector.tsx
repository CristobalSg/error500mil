// src/presentation/components/AvatarSelector.tsx
import { useState } from 'react';
import { Modal, message } from 'antd';
import { CameraIcon, CheckCircleIcon } from '@heroicons/react/24/outline';
import UserAvatar from './UserAvatar';
import { defaultAvatarMale, defaultAvatarFemale } from '../../utils/avatars';

interface AvatarSelectorProps {
  /** Avatar actual del usuario */
  currentAvatar?: string | null;
  /** Género actual del usuario */
  currentGender?: 'male' | 'female' | 'other';
  /** Nombre del usuario */
  userName?: string;
  /** Tamaño del avatar */
  size?: number;
  /** Callback cuando se selecciona un avatar */
  onAvatarSelect?: (avatarType: 'male' | 'female') => void;
  /** Si está cargando */
  loading?: boolean;
}

const AVATAR_OPTIONS = [
  { type: 'male' as const, label: 'Avatar Masculino', url: defaultAvatarMale },
  { type: 'female' as const, label: 'Avatar Femenino', url: defaultAvatarFemale },
];

/**
 * Componente para seleccionar entre avatares predeterminados
 */
export const AvatarSelector: React.FC<AvatarSelectorProps> = ({
  currentAvatar,
  currentGender,
  userName = 'Usuario',
  size = 120,
  onAvatarSelect,
  loading = false,
}) => {
  const [showModal, setShowModal] = useState(false);
  const [selectedAvatar, setSelectedAvatar] = useState<'male' | 'female' | null>(null);

  const handleOpenModal = () => {
    setShowModal(true);
    // Pre-seleccionar el avatar actual
    if (currentAvatar === defaultAvatarMale) {
      setSelectedAvatar('male');
    } else if (currentAvatar === defaultAvatarFemale) {
      setSelectedAvatar('female');
    } else if (currentGender) {
      setSelectedAvatar(currentGender === 'male' ? 'male' : 'female');
    }
  };

  const handleConfirm = () => {
    if (!selectedAvatar) {
      message.warning('Por favor selecciona un avatar');
      return;
    }

    onAvatarSelect?.(selectedAvatar);
    setShowModal(false);
    message.success('Avatar actualizado correctamente');
  };

  const handleCancel = () => {
    setShowModal(false);
    setSelectedAvatar(null);
  };

  // Determinar qué avatar mostrar
  const displayAvatar = currentAvatar || 
    (currentGender === 'male' ? defaultAvatarMale : defaultAvatarFemale);

  return (
    <>
      <div className="relative inline-block">
        <div className={`relative ${loading ? 'opacity-50' : ''}`}>
          <UserAvatar
            avatarUrl={displayAvatar}
            gender={currentGender}
            userName={userName}
            size={size}
          />
          
          {/* Botón de cámara */}
          <button
            type="button"
            onClick={handleOpenModal}
            disabled={loading}
            className="absolute bottom-0 right-0 bg-blue-600 hover:bg-blue-700 text-white rounded-full p-2 shadow-lg transition-colors disabled:bg-gray-400"
            aria-label="Cambiar foto de perfil"
          >
            <CameraIcon className="h-5 w-5" />
          </button>
        </div>

        {loading && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        )}
      </div>

      {/* Modal de selección */}
      <Modal
        title="Selecciona tu foto de perfil"
        open={showModal}
        onOk={handleConfirm}
        onCancel={handleCancel}
        okText="Confirmar"
        cancelText="Cancelar"
        width={500}
      >
        <div className="py-4">
          <p className="text-sm text-gray-600 mb-4">
            Elige uno de los avatares predeterminados:
          </p>
          
          <div className="grid grid-cols-2 gap-4">
            {AVATAR_OPTIONS.map((option) => (
              <button
                key={option.type}
                type="button"
                onClick={() => setSelectedAvatar(option.type)}
                className={`relative p-4 rounded-lg border-2 transition-all hover:shadow-md ${
                  selectedAvatar === option.type
                    ? 'border-blue-600 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="flex flex-col items-center space-y-2">
                  <div className="relative">
                    <img
                      src={option.url}
                      alt={option.label}
                      className="w-24 h-24 rounded-full border-2 border-gray-300"
                    />
                    {selectedAvatar === option.type && (
                      <div className="absolute -top-1 -right-1 bg-blue-600 rounded-full p-1">
                        <CheckCircleIcon className="h-5 w-5 text-white" />
                      </div>
                    )}
                  </div>
                  <span className={`text-sm font-medium ${
                    selectedAvatar === option.type ? 'text-blue-600' : 'text-gray-700'
                  }`}>
                    {option.label}
                  </span>
                </div>
              </button>
            ))}
          </div>
        </div>
      </Modal>
    </>
  );
};

export default AvatarSelector;
