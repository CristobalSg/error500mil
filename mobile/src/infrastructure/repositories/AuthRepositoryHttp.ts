// src/infrastructure/repositories/AuthRepositoryHttp.ts
import type { AuthRepository, LoginResponse } from "../../domain/repositories/AuthRepository";
import { http } from "../http/httpClient";
import type { User } from "../../domain/auth/user";
import { normalizeRole } from "../../domain/auth/roleUtils";

export class AuthRepositoryHttp implements AuthRepository {
  async login(email: string, contrasena: string): Promise<LoginResponse> {
    const { data } = await http.post<LoginResponse>("/auth/login", { email, contrasena });
    return data;
  }

  async logout(): Promise<void> {
    // si tu API expone logout:
    try { await http.post("/auth/logout"); } catch { /* noop */ }
  }

  async me(): Promise<User> {
    const { data } = await http.get("/auth/me");
    // Normaliza el payload al shape User
    return {
      id: String(data.id),
      name: data.name ?? data.fullName ?? data.username ?? data.nombre ?? "",
      email: data.email,
      role: normalizeRole(data.role ?? data.rol),
    };
  }

  async changePassword(body: { contrasena_actual: string; contrasena_nueva: string }) {
    // NO agregar "api/" en la ruta. BaseURL ya lo incluye.
    const { data } = await http.post("/auth/change-password", body);
    return data;
  }
}
