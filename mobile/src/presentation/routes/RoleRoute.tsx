import { Navigate } from "react-router-dom";
import { useAuth } from "../../app/providers/AuthProvider";
import type { Role } from "../../domain/auth/user";
import type { ReactElement } from "react";

export default function RoleRoute({
  allowed,
  children,
}: {
  allowed: Role[]; 
  children: ReactElement;
}) {
  const { loading, user } = useAuth();

  if (loading) {
    return (
      <div className="grid place-items-center h-screen">
        <div className="animate-pulse text-sm text-gray-500">Cargando…</div>
      </div>
    );
  }

  if (!user) return <Navigate to="/login" replace />;

  if (!allowed.includes(user.role)) return <Navigate to="/unauthorized" replace />;

  return children;
}
