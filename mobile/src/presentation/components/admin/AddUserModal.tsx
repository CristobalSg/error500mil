import { useEffect, useMemo, useState } from "react";
import type { ChangeEvent, FormEvent } from "react";
import { XMarkIcon } from "@heroicons/react/24/outline";
import { useRegisterUser } from "../../hooks/useRegisterUser";
import type { AdminUserView } from "../../hooks/useAdminUsers";

type Props = {
  visible: boolean;
  onClose: () => void;
  onSuccess: () => void;
  mode?: "create" | "edit";
  initialUser?: AdminUserView | null;
  onUpdate?: (id: number, data: { name: string; email: string; role: string; password?: string; department?: string }) => Promise<void>;
};

const roles = [
  { label: "Docente", value: "docente" },
  { label: "Estudiante", value: "estudiante" },
  { label: "Administrador", value: "admin" },
];

const MIN_PASSWORD = 12;

type FieldErrors = Partial<Record<"name" | "email" | "password" | "role", string>> & {
  general?: string | string[];
};

export default function AddUserModal({
  visible,
  onClose,
  onSuccess,
  mode = "create",
  initialUser,
  onUpdate,
}: Props) {
  const [form, setForm] = useState({ name: "", email: "", password: "", role: "docente" });
  const [errors, setErrors] = useState<FieldErrors>({});
  const { createUser, loading } = useRegisterUser();
  const [submitting, setSubmitting] = useState(false);

  // Agregar departamento en el estado del formulario
  const [department, setDepartment] = useState(initialUser?.department || "");

  const isEdit = mode === "edit";
  const saving = loading || submitting;

  useEffect(() => {
    if (!visible) {
      setForm({ name: "", email: "", password: "", role: "docente" });
      setErrors({});
      return;
    }
    if (isEdit && initialUser) {
      setForm({
        name: initialUser.name ?? "",
        email: initialUser.email ?? "",
        password: "",
        role: initialUser.role ?? "docente",
      });
      setErrors({});
      setDepartment(initialUser.department || ""); // Cargar departamento en edición
    }
  }, [visible, isEdit, initialUser]);

  // Validador de email con mensajes útiles
  function emailClientError(email: string): string | null {
    const trimmed = email.trim();
    if (!trimmed) return "Ingresa un correo.";
    if (!trimmed.includes("@")) return "Falta el símbolo @. Ej: nombre@empresa.com";
    const [local, domain] = trimmed.split("@");
    if (!local || !domain) return "Falta el dominio. Ej: nombre@empresa.com";
    if (!domain.includes(".")) return "El dominio debe contener un punto. Ej: empresa.com";
    const basic = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(trimmed);
    return basic ? null : "Correo inválido. Ej: nombre@empresa.com";
  }

  const canSubmit = useMemo(() => {
    const baseOk =
      form.name.trim().length >= 2 &&
      form.email.trim().length > 5 &&
      form.role &&
      (!isEdit ? form.password.length >= MIN_PASSWORD : (form.password.length === 0 || form.password.length >= MIN_PASSWORD));
    const deptOk = form.role !== 'docente' || department.trim().length >= 2;
    return baseOk && deptOk;
  }, [form, isEdit, department]);

  const setField =
    (key: keyof typeof form) =>
    (e: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
      const value = e.target.value;
      setForm((s) => ({ ...s, [key]: value }));
      setErrors((prev) => {
        const next = { ...prev, [key]: undefined, general: undefined };
        if (key === "email") {
          const err = emailClientError(value);
          if (err) next.email = err;
        }
        if (key === "password") {
          if (!isEdit && value.length < MIN_PASSWORD) {
            next.password = `La contraseña debe tener al menos ${MIN_PASSWORD} caracteres.`;
          }
          if (isEdit && value.length > 0 && value.length < MIN_PASSWORD) {
            next.password = `Si deseas cambiarla, usa al menos ${MIN_PASSWORD} caracteres.`;
          }
        }
        if (key === "name" && value.trim().length < 2) {
          next.name = "Ingresa un nombre válido.";
        }
        return next;
      });
    };

  const onSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!canSubmit) return;

    try {
      setSubmitting(true);

      if (!isEdit) {
        const payload = {
          name: form.name.trim(),
          email: form.email.trim(),
          role: form.role,
          password: form.password.trim(),
          department: form.role === 'docente' ? department.trim() : undefined,
        };
        console.debug('[AddUserModal.onSubmit] payload registro:', payload);
        await createUser(payload);
      } else if (isEdit && initialUser && onUpdate) {
        const upd: any = {
          name: form.name.trim(),
          email: form.email.trim(),
          role: form.role,
          department: form.role === 'docente' ? department.trim() : undefined,
        };
        if (form.password.trim().length >= MIN_PASSWORD) {
          upd.password = form.password.trim();
        }
        console.debug('[AddUserModal.onSubmit] payload update:', upd);
        await onUpdate(initialUser.id, upd);
      }

      onSuccess();
      onClose();
    } catch (err) {
      console.error('[AddUserModal.onSubmit] error:', err);
      setErrors({ general: 'Error al guardar usuario.' });
    } finally {
      setSubmitting(false);
    }
  };

  if (!visible) return null;

  const baseInput =
    "block w-full rounded-lg border bg-white px-3 py-2 text-slate-900 placeholder-slate-400 outline-none transition focus:border-blue-600 focus:ring-2 focus:ring-blue-600";
  const errorInput = "border-red-400 focus:border-red-500 focus:ring-red-500";
  const normalInput = "border-slate-300";

  return (
    <div className="fixed inset-0 z-50">
      <div className="absolute inset-0 bg-black/40 backdrop-blur-[1px]" aria-hidden="true" onClick={onClose} />
      <div className="absolute inset-0 flex items-center justify-center p-4">
        <div className="w-full max-w-md overflow-hidden rounded-2xl bg-white shadow-xl ring-1 ring-black/5">
          <div className="flex items-center justify-between border-b border-slate-100 px-5 py-4">
            <h3 className="text-base font-semibold text-slate-900">
              {isEdit ? "Editar usuario" : "Agregar usuario"}
            </h3>
            <button
              onClick={onClose}
              className="rounded-md p-2 text-slate-500 hover:bg-slate-100 hover:text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-600"
              aria-label="Cerrar"
            >
              <XMarkIcon className="h-5 w-5" />
            </button>
          </div>

          <form onSubmit={onSubmit} className="space-y-4 px-5 pb-5 pt-4">
            {errors.general && (
              <div className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700" role="alert" aria-live="assertive">
                {Array.isArray(errors.general) ? (
                  <ul className="list-disc space-y-1 pl-5">
                    {errors.general.map((m, i) => (
                      <li key={i}>{m}</li>
                    ))}
                  </ul>
                ) : (
                  errors.general
                )}
              </div>
            )}

            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">Nombre</label>
              <input
                type="text"
                value={form.name}
                onChange={setField("name")}
                placeholder="Ej: María Gómez"
                className={`${baseInput} ${errors.name ? errorInput : normalInput}`}
                aria-invalid={!!errors.name}
                aria-describedby={errors.name ? "name-error" : undefined}
              />
              <div id="name-error" className="mt-1 text-xs text-red-600">{errors.name}</div>
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">Correo</label>
              <input
                type="email"
                value={form.email}
                onChange={setField("email")}
                placeholder="nombre@empresa.com"
                className={`${baseInput} ${errors.email ? errorInput : normalInput}`}
                aria-invalid={!!errors.email}
                aria-describedby={errors.email ? "email-error" : "email-hint"}
              />
              {errors.email ? (
                <div id="email-error" className="mt-1 text-xs text-red-600">{errors.email}</div>
              ) : (
                <p id="email-hint" className="mt-1 text-xs text-slate-500">
                  Asegúrate de incluir @ y un dominio válido. Ej: nombre@empresa.com
                </p>
              )}
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">
                {isEdit ? "Nueva contraseña (opcional)" : "Contraseña"}
              </label>
              <input
                type="password"
                value={form.password}
                onChange={setField("password")}
                placeholder={isEdit ? "Dejar en blanco para no cambiar" : "••••••••••••"}
                className={`${baseInput} ${errors.password ? errorInput : normalInput}`}
                aria-invalid={!!errors.password}
                aria-describedby={errors.password ? "password-error" : "password-hint"}
              />
              {errors.password ? (
                <div id="password-error" className="mt-1 text-xs text-red-600">{errors.password}</div>
              ) : (
                <p id="password-hint" className="mt-1 text-xs text-slate-500">
                  {isEdit
                    ? `Si la cambias, usa al menos ${MIN_PASSWORD} caracteres.`
                    : `Mínimo ${MIN_PASSWORD} caracteres.`}
                </p>
              )}
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">Rol</label>
              <select
                value={form.role}
                onChange={setField("role")}
                className={`${baseInput} ${errors.role ? errorInput : normalInput}`}
                aria-invalid={!!errors.role}
                aria-describedby={errors.role ? "role-error" : undefined}
              >
                {roles.map((r) => (
                  <option key={r.value} value={r.value}>{r.label}</option>
                ))}
              </select>
              <div id="role-error" className="mt-1 text-xs text-red-600">{errors.role}</div>
            </div>

            {/* En el formulario visual: mostrar campo departamento solo si role === 'docente' */}
            {form.role === "docente" && (
              <div className="flex flex-col gap-1">
                <label className="text-xs font-medium text-gray-700">Departamento</label>
                <input
                  type="text"
                  value={department}
                  onChange={(e) => setDepartment(e.target.value)}
                  placeholder="Ej: Ciencias Básicas"
                  className="rounded-md border border-gray-300 px-3 py-2 text-sm outline-none focus:border-indigo-500 bg-white text-gray-900 placeholder-gray-400"
                />
                {department.trim().length < 2 && (
                  <p className="text-[11px] text-red-600">Ingresa al menos 2 caracteres.</p>
                )}
              </div>
            )}

            <div className="mt-6 flex items-center justify-end gap-3 border-t border-slate-100 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="inline-flex items-center rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-600"
              >
                Cancelar
              </button>
              <button
                type="submit"
                disabled={!canSubmit}
                className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-600 disabled:cursor-not-allowed disabled:bg-blue-400"
              >
                {saving && (
                  <svg className="h-4 w-4 animate-spin text-white" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
                  </svg>
                )}
                {isEdit ? "Guardar cambios" : "Crear usuario"}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
