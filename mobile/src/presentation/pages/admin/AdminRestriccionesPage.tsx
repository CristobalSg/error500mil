import { useEffect, useMemo, useState } from "react";
import { Alert, Empty, Spin, Tag, message } from "antd";
import AppLayout from "../../components/layout/AppLayout";
import { useAdminUsers, type AdminUserView } from "../../hooks/useAdminUsers";
import {
  useAdminDocenteRestrictions,
  type AdminRestrictionView,
} from "../../hooks/useAdminDocenteRestrictions";
import { CheckIcon, XMarkIcon } from "@heroicons/react/24/solid";

const dayLabels = [
  "Domingo",
  "Lunes",
  "Martes",
  "Miércoles",
  "Jueves",
  "Viernes",
  "Sábado",
];

const roleLabels: Record<string, string> = {
  docente: "Docente",
  estudiante: "Estudiante",
  admin: "Administrador",
};

// 🟢 Tarjeta individual de restricción
// 🟢 Tarjeta individual de restricción
const RestrictionCard = ({
  restriction,
  onAccept,
  onReject,
  loading,
}: {
  restriction: AdminRestrictionView;
  onAccept: (id: number) => void;
  onReject: (id: number) => void;
  loading: boolean;
}) => (
  <div
    className={`rounded-2xl border px-4 py-3 shadow-sm transition 
      ${restriction.activa ? "border-green-300 bg-green-50" : "border-red-300 bg-red-50"}
    `}
  >
    <div className="flex flex-wrap items-center justify-between gap-3">
      <div>
        <p
          className={`text-sm font-semibold ${
            restriction.activa ? "text-green-700" : "text-red-700"
          }`}
        >
          {dayLabels[restriction.day]} · {restriction.start} - {restriction.end}
        </p>
        {restriction.descripcion && (
          <p className="text-xs text-gray-600">{restriction.descripcion}</p>
        )}
      </div>

      <div className="flex items-center gap-3">
        {/* Estado de disponibilidad */}
        <Tag color={restriction.disponible ? "green" : "red"} className="text-xs">
          {restriction.disponible ? "Disponible" : "No disponible"}
        </Tag>

        {/* Estado activa/inactiva */}
        <Tag
          color={restriction.activa ? "green" : "red"}
          className="text-xs font-medium"
        >
          {restriction.activa ? "Activa" : "Inactiva"}
        </Tag>

        {/* Botones */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => onAccept(restriction.id)}
            className={`rounded-full bg-green-100 p-1.5 text-green-600 hover:bg-green-200 transition ${
              loading ? "opacity-50 pointer-events-none" : ""
            }`}
            title="Aceptar restricción"
          >
            <CheckIcon className="h-4 w-4" />
          </button>
          <button
            onClick={() => onReject(restriction.id)}
            className={`rounded-full bg-red-100 p-1.5 text-red-600 hover:bg-red-200 transition ${
              loading ? "opacity-50 pointer-events-none" : ""
            }`}
            title="Rechazar restricción"
          >
            <XMarkIcon className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  </div>
);


// 🟣 Tarjeta de usuario
const UserRow = ({
  user,
  selected,
  onSelect,
}: {
  user: AdminUserView;
  selected: boolean;
  onSelect: (user: AdminUserView) => void;
}) => {
  const roleLabel = roleLabels[user.role] ?? user.role;

  return (
    <button
      type="button"
      onClick={() => onSelect(user)}
      className={[
        "w-full rounded-2xl border px-4 py-3 text-left transition",
        selected
          ? "border-indigo-500 bg-indigo-50 shadow-sm"
          : "border-gray-100 bg-white hover:border-indigo-200 hover:bg-indigo-50/60",
      ].join(" ")}
    >
      <div className="flex items-center justify-between gap-2">
        <div>
          <p className="text-sm font-semibold text-gray-900">{user.name}</p>
          <p className="text-xs text-gray-500">{user.email}</p>
        </div>
        <div className="flex flex-col items-end gap-1">
          <span className="text-xs font-medium text-indigo-600">{roleLabel}</span>
          {user.docenteId && (
            <span className="text-[11px] text-gray-500">
              ID Docente: {user.docenteId}
            </span>
          )}
        </div>
      </div>
    </button>
  );
};

// 🟣 Página principal
export default function AdminRestriccionesPage() {
  const { users, loading, error, refresh } = useAdminUsers();
  const [selectedUserId, setSelectedUserId] = useState<number | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [actionLoading, setActionLoading] = useState(false);

  const {
    restrictions,
    loading: restrictionsLoading,
    error: restrictionsError,
    fetchForDocente,
    clear,
    aceptarRestriccion,
    rechazarRestriccion,
  } = useAdminDocenteRestrictions();

  // 🔹 Solo docentes
  const filteredUsers = useMemo(() => {
    return users
      .filter((u) => u.role === "docente")
      .slice()
      .sort((a, b) => a.name.localeCompare(b.name, "es", { sensitivity: "base" }))
      .filter((u) =>
        u.name.toLowerCase().includes(searchTerm.trim().toLowerCase())
      );
  }, [users, searchTerm]);

  const selectedUser = useMemo(
    () =>
      selectedUserId
        ? filteredUsers.find((u) => u.id === selectedUserId) ?? null
        : null,
    [filteredUsers, selectedUserId]
  );

  // Selección automática
  useEffect(() => {
    if (filteredUsers.length === 0) {
      setSelectedUserId(null);
      return;
    }
    if (!selectedUserId) {
      setSelectedUserId(filteredUsers[0].id);
    } else {
      const exists = filteredUsers.some((u) => u.id === selectedUserId);
      if (!exists) setSelectedUserId(filteredUsers[0].id);
    }
  }, [filteredUsers, selectedUserId]);

  // Cargar restricciones usando user_id en lugar de docenteId
  useEffect(() => {
    if (!selectedUser) {
      clear();
      return;
    }
    // Usar user.id que es el user_id del backend
    fetchForDocente(selectedUser.id);
  }, [selectedUser, fetchForDocente, clear]);

  // ✅ Acciones reales
  const handleAccept = async (id: number) => {
    try {
      setActionLoading(true);
      await aceptarRestriccion(id);
      message.success("Restricción aceptada");
      if (selectedUser?.id) await fetchForDocente(selectedUser.id);
    } catch (err) {
      console.error("Error al aceptar restricción:", err);
      message.error("Error al aceptar restricción");
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async (id: number) => {
    try {
      setActionLoading(true);
      await rechazarRestriccion(id);
      message.info("Restricción rechazada");
      if (selectedUser?.id) await fetchForDocente(selectedUser.id);
    } catch (err) {
      console.error("Error al rechazar restricción:", err);
      message.error("Error al rechazar restricción");
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <AppLayout title="Usuarios" showBottomNav>
      <div className="space-y-6 pb-6">
        {/* 🔍 Buscador */}
        <div className="rounded-3xl border border-gray-100 bg-white p-4 shadow-sm">
          <h2 className="text-base font-semibold text-gray-900 mb-2">Buscar Docente</h2>
          <input
            type="text"
            placeholder="Escribe un nombre..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-900 placeholder-gray-400 focus:border-indigo-500 focus:ring focus:ring-indigo-200"
          />
        </div>

        {/* Listado de docentes */}
        <div className="rounded-3xl border border-gray-100 bg-white p-4 shadow-sm">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="text-base font-semibold text-gray-900">Listado de Docentes</h2>
            <button
              onClick={refresh}
              className="text-xs font-medium text-indigo-600 hover:text-indigo-700"
              type="button"
            >
              Actualizar
            </button>
          </div>

          {error && (
            <Alert
              type="error"
              message="No se pudieron cargar los docentes"
              description={error}
              showIcon
            />
          )}

          {loading ? (
            <div className="py-10 text-center">
              <Spin />
            </div>
          ) : filteredUsers.length === 0 ? (
            <div className="py-6 text-center text-sm text-gray-500">
              No se encontraron docentes.
            </div>
          ) : (
            <div className="space-y-2">
              {filteredUsers.map((user) => (
                <UserRow
                  key={user.id}
                  user={user}
                  selected={selectedUserId === user.id}
                  onSelect={(u) => setSelectedUserId(u.id)}
                />
              ))}
            </div>
          )}
        </div>

        {/* Restricciones */}
        <div className="rounded-3xl border border-gray-100 bg-white p-4 shadow-sm">
          <div className="mb-3">
            <h2 className="text-base font-semibold text-gray-900">Restricciones</h2>
            {selectedUser && (
              <p className="text-xs text-gray-500">
                {selectedUser.name} · {selectedUser.email}
              </p>
            )}
          </div>

          {!selectedUser ? (
            <div className="rounded-3xl border border-dashed border-gray-200 p-6 text-center text-sm text-gray-500">
              Selecciona un docente para revisar sus restricciones.
            </div>
          ) : restrictionsLoading ? (
            <div className="py-10 text-center">
              <Spin />
            </div>
          ) : restrictionsError ? (
            <Alert
              type="error"
              message="No se pudieron cargar las restricciones"
              description={restrictionsError}
              showIcon
            />
          ) : restrictions.length === 0 ? (
            <div className="rounded-3xl border border-gray-100 bg-white py-10 text-center">
              <Empty description="Sin restricciones registradas" />
            </div>
          ) : (
            <div className="space-y-3">
              {restrictions.map((item) => (
                <RestrictionCard
                  key={item.id}
                  restriction={item}
                  onAccept={handleAccept}
                  onReject={handleReject}
                  loading={actionLoading}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  );
}
