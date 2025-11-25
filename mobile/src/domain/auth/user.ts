export type Role = "docente" | "estudiante" | "admin";
export type Gender = "male" | "female" | "other";

export interface User {
  id: string;
  name: string;
  email: string;
  role: Role; // Asegúrate que tu backend devuelva "role" o mapea en el repo
  avatar_url?: string | null; // URL de la foto de perfil
  gender?: Gender; // Género del usuario para avatar predeterminado
}

export interface AuthTokens {
  access_token: string;
  refresh_token?: string;
  token_type?: string;
}
