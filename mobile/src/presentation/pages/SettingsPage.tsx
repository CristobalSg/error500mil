// src/presentation/pages/SettingsPage.tsx
import { BellIcon, ChevronLeftIcon, ArrowRightOnRectangleIcon } from "@heroicons/react/24/outline";
import AppLayout from "../components/layout/AppLayout";
import { useAuth } from "../../app/providers/AuthProvider";
import { useNavigate } from "react-router-dom";
import { useMemo, useState } from "react";
import { Collapse, Button, Switch, Input, Modal, type CollapseProps } from "antd";
import { message } from "antd";
import { useChangePassword } from "../hooks/useChangePassword";
import AvatarSelector from "../components/AvatarSelector";
import { defaultAvatarMale, defaultAvatarFemale } from "../../utils/avatars";
import { useAvatarSelection } from "../hooks/useAvatarSelection";

const SettingsPage = () => {
  const { logout, user } = useAuth();
  const navigate = useNavigate();
  const { changePassword, loading: changing } = useChangePassword();
  const { selectAvatar, updating: updatingAvatar } = useAvatarSelection();
  const [pwdActual, setPwdActual] = useState("");
  const [pwdNueva, setPwdNueva] = useState("");
  const [notifModalOpen, setNotifModalOpen] = useState(false);
  const MIN_PASSWORD = 12;

  const handleLogout = async () => {
    await logout();
    navigate("/login", { replace: true });
  };

  // Ítems del Collapse para "Cuenta"
  const cuentaItems: CollapseProps["items"] = useMemo(() => {
    const handleAvatarSelect = async (avatarType: 'male' | 'female') => {
      try {
        await selectAvatar(avatarType);
        
        // Actualizar el estado local del usuario
        const newAvatarUrl = avatarType === 'male' ? defaultAvatarMale : defaultAvatarFemale;
        
        // TODO: Actualizar el estado del usuario en el contexto
        // setUser({ ...user, avatar_url: newAvatarUrl, gender: avatarType });
        
        console.log('Avatar seleccionado:', avatarType);
        console.log('URL del avatar:', newAvatarUrl);
      } catch (error) {
        // El error ya se muestra en el componente AvatarSelector
        console.error('Error al seleccionar avatar:', error);
      }
    };

    const perfilChildren = (
      <div className="space-y-4 pt-2">
        {/* Foto de perfil */}
        <div className="flex flex-col items-center py-2">
          <AvatarSelector
            currentAvatar={user?.avatar_url || null}
            currentGender={user?.gender || 'male'}
            userName={user?.name}
            size={120}
            onAvatarSelect={handleAvatarSelect}
            loading={updatingAvatar}
          />
          <p className="text-xs text-gray-500 mt-2 text-center">
            Haz clic en el ícono de la cámara para elegir tu avatar
          </p>
        </div>

        {/* Información del usuario */}
        <div>
          <p className="text-xs text-gray-500">Nombre</p>
          <p className="text-sm font-medium">{user?.name ?? "—"}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Correo</p>
          <p className="text-sm font-medium">{user?.email ?? "—"}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Rol</p>
          <p className="text-sm font-medium capitalize">{user?.role ?? "—"}</p>
        </div>
      </div>
    );

    const passwordChildren = (
      <div className="space-y-3 pt-2 text-sm text-gray-600">
        <div className="grid gap-3">
          <div>
            <p className="text-xs text-gray-500">Contraseña actual</p>
            <Input.Password
              value={pwdActual}
              onChange={(e) => setPwdActual(e.target.value)}
              placeholder="********"
            />
          </div>
          <div>
            <p className="text-xs text-gray-500">Nueva contraseña</p>
            <Input.Password
              value={pwdNueva}
              onChange={(e) => setPwdNueva(e.target.value)}
              placeholder="Mínimo 12 caracteres"
            />
            {pwdNueva && pwdNueva.length < MIN_PASSWORD && (
              <p className="text-xs text-red-500 mt-1">
                La contraseña debe tener al menos {MIN_PASSWORD} caracteres.
              </p>
            )}
          </div>
        </div>
        <Button
          type="primary"
          size="middle"
          loading={changing}
          disabled={!pwdActual || pwdNueva.length < MIN_PASSWORD}
          onClick={async () => {
            try {
              await changePassword(pwdActual, pwdNueva);
              message.success("Contraseña actualizada correctamente.");
              setPwdActual("");
              setPwdNueva("");
            } catch (e: any) {
              const apiMsg =
                e?.response?.data?.detail?.[0]?.msg ||
                e?.response?.data?.message ||
                e?.message ||
                "No se pudo cambiar la contraseña.";
              message.error(apiMsg);
            }
          }}
        >
          Cambiar contraseña
        </Button>
      </div>
    );

    const seguridadChildren = (
      <div className="space-y-3 pt-2">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium">Autenticación en dos pasos</p>
            <p className="text-xs text-gray-500">
              Añade una capa extra de seguridad a tu cuenta.
            </p>
          </div>
          <Switch /* TODO: wirear estado real de 2FA */ />
        </div>
        <div className="text-xs text-gray-500">
          Puedes usar app de autenticación o códigos de respaldo.
        </div>
      </div>
    );

    return [
      { key: "perfil", label: "Datos del perfil", children: perfilChildren },
      { key: "password", label: "Cambiar contraseña", children: passwordChildren },
      { key: "seguridad", label: "Seguridad", children: seguridadChildren },
    ];
  }, [user, pwdActual, pwdNueva, changing, updatingAvatar, selectAvatar]);

  return (
    <>
      <AppLayout
      title="Configuración"
      leftAction={
        <button
          aria-label="Volver"
          onClick={() => window.history.back()}
          className="p-1 rounded-md hover:bg-gray-100 active:bg-gray-200"
        >
          <ChevronLeftIcon className="h-6 w-6 text-gray-700" />
        </button>
      }
      rightAction={
        <button
          aria-label="Notificaciones"
          className="p-1 rounded-md hover:bg-gray-100 active:bg-gray-200"
          onClick={() => setNotifModalOpen(true)}
        >
          <BellIcon className="h-6 w-6 text-gray-700" />
        </button>
      }
    >
      <p className="text-gray-700 text-sm mt-4">
        Preferencias, ajustes de notificaciones y otros parámetros del sistema.
      </p>

      <section className="mt-4 space-y-3">
        {/* Cuenta con Collapse de AntD */}
        <div className="bg-white rounded-xl shadow-sm p-4">
          <h2 className="text-sm font-semibold text-gray-800">Cuenta</h2>
          <p className="text-xs text-gray-500 mt-1">
            Correo, contraseña y seguridad.
          </p>

          <div className="mt-3">
            <Collapse
              items={cuentaItems}
              defaultActiveKey={["perfil"]}
              bordered={false}
            />
          </div>
        </div>

        {/* Notificaciones (deja tu contenido actual o conviértelo también a Collapse si quieres) */}
        <div className="bg-white rounded-xl shadow-sm p-4">
          <h2 className="text-sm font-semibold text-gray-800">Notificaciones</h2>
          <p className="text-xs text-gray-500 mt-1">
            Push, correo y recordatorios.
          </p>
          {/* TODO: switches y preferencias de notificaciones */}
        </div>

        {/* Cerrar sesión */}
        <div className="bg-white rounded-xl shadow-sm p-4 flex items-center justify-between">
          <div>
            <h2 className="text-sm font-semibold text-gray-800">Cerrar sesión</h2>
            <p className="text-xs text-gray-500 mt-1">
              Cierra tu sesión actual de forma segura.
            </p>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-red-600 hover:text-red-700"
          >
            <ArrowRightOnRectangleIcon className="h-5 w-5" />
            Salir
          </button>
        </div>
      </section>
      </AppLayout>
      <Modal
        open={notifModalOpen}
        title="Notificaciones"
        centered
        onCancel={() => setNotifModalOpen(false)}
        footer={[
          <Button key="close" type="primary" onClick={() => setNotifModalOpen(false)}>
            Entendido
          </Button>,
        ]}
      >
        <div className="space-y-2 text-sm text-gray-600">
          <p>No hay mensajes nuevos por ahora.</p>
          <p>Mantendremos esta sección lista para cuando habilitemos las alertas.</p>
        </div>
      </Modal>
    </>
  );
};

export default SettingsPage;
