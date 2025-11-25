import type { Role } from "../../domain/auth/user";

export const getDefaultPathByRole = (role: Role | null | undefined) => {
  switch (role) {
    case "admin":
      return "/admin";
    case "estudiante":
      return "/student/home";
    case "docente":
    default:
      return "/home";
  }
};
