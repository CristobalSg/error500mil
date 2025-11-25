import { useEffect, useMemo, useState } from "react";
import ImportUsersCsvModal from "../../components/admin/ImportUsersCsvModal";
import AddUserModal from "../../components/admin/AddUserModal";
import { Alert, Spin, Input, Select } from "antd";
import AppLayout from "../../components/layout/AppLayout";
import { useAdminUsers, type AdminUserView } from "../../hooks/useAdminUsers";

const { Option } = Select;

const roleLabels: Record<string, string> = {
  docente: "Docente",
  estudiante: "Estudiante",
  admin: "Administrador",
};

// Tarjeta de usuario con acciones
const UserRow = ({
  user,
  selected,
  onSelect,
  onEdit,
  onDelete,
}: {
  user: AdminUserView;
  selected: boolean;
  onSelect: (user: AdminUserView) => void;
  onEdit: (user: AdminUserView) => void;
  onDelete: (user: AdminUserView) => void;
}) => {
  const roleLabel = roleLabels[user.role] ?? user.role;

  return (
    <div
      className={[
        "w-full rounded-2xl border px-4 py-3 transition",
        selected
          ? "border-indigo-500 bg-indigo-50 shadow-sm"
          : "border-gray-100 bg-white hover:border-indigo-200 hover:bg-indigo-50/60",
      ].join(" ")}
    >
      <div className="flex items-start justify-between gap-2">
        <button
          type="button"
          onClick={() => onSelect(user)}
          className="flex-1 text-left"
          title="Seleccionar"
        >
          <p className="text-sm font-semibold text-gray-900">{user.name}</p>
          <p className="text-xs text-gray-500">{user.email}</p>
          <div className="mt-1 flex flex-wrap items-center gap-2">
            <span className="text-xs font-medium text-indigo-600">{roleLabel}</span>
            {user.docenteId && (
              <span className="text-[11px] text-gray-500">
                ID Docente: {user.docenteId}
                {user.department ? ` · ${user.department}` : ""}
              </span>
            )}
          </div>
        </button>

        <div className="flex shrink-0 gap-2">
          <button
            type="button"
            onClick={() => onEdit(user)}
            className="rounded-md bg-blue-600 px-2 py-1 text-xs font-semibold text-white shadow-sm hover:bg-blue-700"
            title="Editar"
          >
            Editar
          </button>
          <button
            type="button"
            onClick={() => onDelete(user)}
            className="rounded-md bg-red-600 px-2 py-1 text-xs font-semibold text-white shadow-sm hover:bg-red-700"
            title="Eliminar"
          >
            Eliminar
          </button>
        </div>
      </div>
    </div>
  );
};

export default function AdminUsersPage() {
  const { users, loading, error, refresh, updateUser, deleteUser } = useAdminUsers();

  const [searchTerm, setSearchTerm] = useState("");
  const [filterRole, setFilterRole] = useState<string>("todos");
  const [selectedUserId, setSelectedUserId] = useState<number | null>(null);

  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingUser, setEditingUser] = useState<AdminUserView | null>(null);

  // Banner superior (éxito/error)
  const [banner, setBanner] = useState<{ type: "success" | "error" | "info"; text: string } | null>(null);

  // Confirmación de eliminación
  const [confirmState, setConfirmState] = useState<{
    open: boolean;
    user: AdminUserView | null;
    loading: boolean;
  }>({ open: false, user: null, loading: false });

  const [page, setPage] = useState(1);
  const PAGE_SIZE = 20;

  const [openCsv, setOpenCsv] = useState(false);

  useEffect(() => {
    setPage(1);
  }, [searchTerm, filterRole]);

  const sortedUsers = useMemo(
    () =>
      users
        .slice()
        .sort((a, b) => a.name.localeCompare(b.name, "es", { sensitivity: "base" })),
    [users]
  );

  const filteredUsers = useMemo(() => {
    return sortedUsers.filter((user) => {
      const matchesRole =
        filterRole === "todos" || user.role?.toLowerCase() === filterRole;
      const term = searchTerm.toLowerCase();
      const matchesSearch =
        user.name.toLowerCase().includes(term) ||
        user.email.toLowerCase().includes(term);
      return matchesRole && matchesSearch;
    });
  }, [sortedUsers, searchTerm, filterRole]);

  const totalPages = Math.max(1, Math.ceil(filteredUsers.length / PAGE_SIZE));

  const paginatedUsers = useMemo(() => {
    const start = (page - 1) * PAGE_SIZE;
    return filteredUsers.slice(start, start + PAGE_SIZE);
  }, [filteredUsers, page]);

  const handleSelectUser = (u: AdminUserView) => {
    setSelectedUserId(u.id);
  };

  const handleEdit = (user: AdminUserView) => {
    setEditingUser(user);
    setShowEditModal(true);
  };

  // Abrir modal de confirmación (no usar window.confirm)
  const requestDelete = (user: AdminUserView) => {
    setConfirmState({ open: true, user, loading: false });
  };

  const confirmDelete = async () => {
    if (!confirmState.user) return;
    try {
      setConfirmState((s) => ({ ...s, loading: true }));
      await deleteUser(confirmState.user.id);
      await refresh();
      setBanner({ type: "success", text: `Usuario "${confirmState.user.name}" eliminado.` });
    } catch (e: any) {
      setBanner({ type: "error", text: e?.message || "No se pudo eliminar el usuario." });
    } finally {
      setConfirmState({ open: false, user: null, loading: false });
    }
  };

  const cancelDelete = () => setConfirmState({ open: false, user: null, loading: false });

  const handleUpdateUser = async (
    id: number,
    data: { name: string; email: string; role: string; password?: string; department?: string }
  ) => {
    try {
      await updateUser(id, data);
      setShowEditModal(false);
      setEditingUser(null);
      await refresh();
      setBanner({ type: "success", text: "Usuario actualizado." });
    } catch (e: any) {
      setBanner({ type: "error", text: e?.message || "No se pudo actualizar el usuario." });
      throw e;
    }
  };

  const goToPage = (p: number) => {
    if (p < 1 || p > totalPages) return;
    setPage(p);
  };

  return (
    <AppLayout title="Usuarios" showBottomNav>
      {/* Contenedor centrado: listado arriba, botones abajo */}
      <div className="mx-auto max-w-2xl space-y-6 pb-24">
        {/* Filtros y búsqueda */}
        <div className="rounded-3xl border border-gray-100 bg-white p-4 shadow-sm">
          <h2 className="mb-3 text-base font-semibold text-gray-900">Filtros de búsqueda</h2>
          <div className="flex flex-col gap-3 sm:flex-row">
            <Input
              placeholder="Buscar por nombre o correo..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              allowClear
              className="sm:w-2/3"
            />
            <Select
              value={filterRole}
              onChange={(v) => setFilterRole(v)}
              className="sm:w-1/3"
            >
              <Option value="todos">Todos</Option>
              <Option value="admin">Administrador</Option>
              <Option value="docente">Docente</Option>
              <Option value="estudiante">Estudiante</Option>
            </Select>
          </div>
        </div>

        {/* Listado de usuarios */}
        <div className="rounded-3xl border border-gray-100 bg-white p-4 shadow-sm">
          {/* Título + botones (debajo del título) */}
          <div className="mb-3">
            <h2 className="text-base font-semibold text-gray-900 text-center">Listado</h2>
            <div className="mt-3 flex flex-wrap items-center justify-center gap-2">
              <button
                type="button"
                onClick={() => { refresh(); }}
                className="rounded-md border border-gray-300 bg-white px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
              >
                Actualizar
              </button>

              <button
                type="button"
                onClick={() => setShowAddModal(true)}
                className="rounded-md bg-blue-600 px-3 py-2 text-sm font-semibold text-white hover:bg-blue-700"
              >
                Agregar usuario
              </button>

              <button
                type="button"
                onClick={() => setOpenCsv(true)}
                className="rounded-md border border-blue-600 bg-white px-3 py-2 text-sm font-medium text-blue-600 hover:bg-blue-50"
              >
                Agregar usuarios por CSV
              </button>
            </div>
          </div>

          {/* Banner de estado */}
          {banner && (
            <Alert
              type={banner.type}
              message={banner.text}
              showIcon
              closable
              onClose={() => setBanner(null)}
              className="mb-3"
            />
          )}

          <div className="mb-2 text-xs text-gray-500">
            {filteredUsers.length} usuario(s) · Página {page} de {totalPages}
          </div>

          {error && (
            <Alert
              type="error"
              message="No se pudieron cargar los usuarios"
              description={error}
              showIcon
              className="mb-3"
              action={
                <button
                  onClick={refresh}
                  className="text-sm font-medium text-indigo-600 hover:text-indigo-700"
                >
                  Reintentar
                </button>
              }
            />
          )}

          {loading ? (
            <div className="py-10 text-center">
              <Spin />
            </div>
          ) : filteredUsers.length === 0 ? (
            <div className="py-6 text-center text-sm text-gray-500">
              No se encontraron usuarios.
            </div>
          ) : (
            <>
              <div className="space-y-2">
                {paginatedUsers.map((user) => (
                  <UserRow
                    key={user.id}
                    user={user}
                    selected={selectedUserId === user.id}
                    onSelect={handleSelectUser}
                    onEdit={handleEdit}
                    onDelete={requestDelete}
                  />
                ))}
              </div>

              {/* Paginación */}
              <div className="mt-6 flex flex-wrap items-center justify-center gap-2">
                <button
                  type="button"
                  onClick={() => goToPage(page - 1)}
                  disabled={page === 1}
                  className="rounded-md border border-gray-300 bg-white px-3 py-1 text-xs font-medium text-gray-700 disabled:cursor-not-allowed disabled:opacity-40 hover:bg-gray-50"
                >
                  ← Anterior
                </button>
                {Array.from({ length: totalPages }, (_, i) => i + 1)
                  .filter((p) => {
                    const delta = 2;
                    if (p === 1 || p === totalPages) return true;
                    if (Math.abs(page - p) <= delta) return true;
                    return false;
                  })
                  .map((p, idx, arr) => {
                    const prev = arr[idx - 1];
                    if (prev && p - prev > 1) {
                      return (
                        <span key={`gap-${prev}-${p}`} className="px-2 text-xs text-gray-400">
                          …
                        </span>
                      );
                    }
                    return (
                      <button
                        key={p}
                        type="button"
                        onClick={() => goToPage(p)}
                        className={`rounded-md border px-3 py-1 text-xs font-medium ${
                          p === page
                            ? "border-indigo-500 bg-indigo-50 text-indigo-600"
                            : "border-gray-300 bg-white text-gray-700 hover:bg-gray-50"
                        }`}
                      >
                        {p}
                      </button>
                    );
                  })}
                <button
                  type="button"
                  onClick={() => goToPage(page + 1)}
                  disabled={page === totalPages}
                  className="rounded-md border border-gray-300 bg-white px-3 py-1 text-xs font-medium text-gray-700 disabled:cursor-not-allowed disabled:opacity-40 hover:bg-gray-50"
                >
                  Siguiente →
                </button>
              </div>
            </>
          )}
        </div>

        {/* Modal crear */}
        <AddUserModal
          visible={showAddModal}
          onClose={() => setShowAddModal(false)}
          onSuccess={refresh}
          mode="create"
        />
        {/* Modal editar */}
        {editingUser && (
          <AddUserModal
            visible={showEditModal}
            onClose={() => {
              setShowEditModal(false);
              setEditingUser(null);
            }}
            onSuccess={refresh}
            mode="edit"
            initialUser={editingUser}
            onUpdate={handleUpdateUser}
          />
        )}
        {/* Confirmación eliminar */}
        <ConfirmDialog
          open={confirmState.open}
          title="Eliminar usuario"
          description={
            confirmState.user
              ? `¿Seguro que deseas eliminar a "${confirmState.user.name}"? Esta acción no se puede deshacer.`
              : ""
          }
          confirmText={confirmState.loading ? "Eliminando…" : "Eliminar"}
          cancelText="Cancelar"
          onConfirm={confirmDelete}
          onCancel={cancelDelete}
          loading={confirmState.loading}
        />
        <ImportUsersCsvModal open={openCsv} onClose={() => setOpenCsv(false)} />
      </div>
    </AppLayout>
  );
}

// Modal de confirmación simple (sin dependencias)
function ConfirmDialog({
  open,
  title,
  description,
  confirmText,
  cancelText,
  onConfirm,
  onCancel,
  loading,
}: {
  open: boolean;
  title: string;
  description?: string;
  confirmText?: string;
  cancelText?: string;
  onConfirm: () => void | Promise<void>;
  onCancel: () => void;
  loading?: boolean;
}) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-[60]">
      <div className="absolute inset-0 bg-black/40 backdrop-blur-[1px]" aria-hidden="true" onClick={onCancel} />
      <div className="absolute inset-0 flex items-center justify-center p-4">
        <div className="w-full max-w-md overflow-hidden rounded-2xl bg-white shadow-xl ring-1 ring-black/5">
          <div className="border-b border-slate-100 px-5 py-4">
            <h3 className="text-base font-semibold text-slate-900">{title}</h3>
          </div>
          <div className="px-5 py-4 text-sm text-slate-600">{description}</div>
          <div className="flex items-center justify-end gap-3 border-t border-slate-100 px-5 py-4">
            <button
              type="button"
              onClick={onCancel}
              className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
            >
              {cancelText || "Cancelar"}
            </button>
            <button
              type="button"
              onClick={onConfirm}
              disabled={loading}
              className="rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-red-700 disabled:cursor-not-allowed disabled:bg-red-400"
            >
              {confirmText || "Eliminar"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
