import type { Role } from "./user";

export const normalizeRole = (rawRole: string | null | undefined): Role => {
  const normalized = rawRole?.toLowerCase();
  switch (normalized) {
    case "administrador":
    case "admin":
      return "admin";
    case "docente":
      return "docente";
    case "estudiante":
      return "estudiante";
    default:
      return "docente";
  }
};
