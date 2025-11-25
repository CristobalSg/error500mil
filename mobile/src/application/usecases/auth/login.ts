// src/application/usecases/auth/login.ts
import type { AuthRepository } from "../../../domain/repositories/AuthRepository";
import type { AuthTokens } from "../../../domain/auth/user";

export function makeLoginUseCase(repo: AuthRepository) {
  return (email: string, password: string): Promise<AuthTokens> =>
    // Aquí puedes agregar validaciones de dominio antes/después
    repo.login(email, password);
}
