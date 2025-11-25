import { useState } from "react";
import { AuthRepositoryHttp } from "../../infrastructure/repositories/AuthRepositoryHttp";

export function useChangePassword() {
  const [loading, setLoading] = useState(false);
  const repo = new AuthRepositoryHttp();

  async function changePassword(contrasena_actual: string, contrasena_nueva: string) {
    setLoading(true);
    try {
      return await repo.changePassword({ contrasena_actual, contrasena_nueva });
    } finally {
      setLoading(false);
    }
  }

  return { changePassword, loading };
}