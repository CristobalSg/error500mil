// src/domain/repositories/AuthRepository.ts
import type { User, AuthTokens } from "../auth/user";

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface AuthRepository {
  login(email: string, contrasena: string): Promise<LoginResponse>;
  logout(): Promise<void>;                 // lo dejamos por futuro
  me(): Promise<User>;           // idem, por si el backend lo soporta
}

export interface AuthRepository {
  login(email: string, password: string): Promise<AuthTokens>;
  logout(): Promise<void>;
  me(): Promise<User>;
}