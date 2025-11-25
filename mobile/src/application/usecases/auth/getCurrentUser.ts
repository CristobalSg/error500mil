// src/application/usecases/authgetCurrentUser.ts
import type { AuthRepository } from "../../../domain/repositories/AuthRepository";
import type { User } from "../../../domain/auth/user";

export function makeGetCurrentUserUseCase(repo: AuthRepository) {
  return (): Promise<User> => repo.me();
}