import { Link } from "react-router-dom";
import { useAuth } from "../../app/providers/AuthProvider";
import { getDefaultPathByRole } from "../routes/rolePaths";

export default function UnauthorizedPage() {
  const { role } = useAuth();
  const backHref = role ? getDefaultPathByRole(role) : "/login";

  return (
    <div className="min-h-[var(--app-height)] grid place-items-center bg-gray-50 px-6">
      <div className="max-w-md text-center">
        <h1 className="text-2xl font-semibold mb-2">No autorizado</h1>
        <p className="text-gray-600 mb-4">
          No tienes permisos para acceder a esta sección.
        </p>
        <Link className="text-indigo-600 underline" to={backHref}>
          Volver al inicio
        </Link>
      </div>
    </div>
  );
}
