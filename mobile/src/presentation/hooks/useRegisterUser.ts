import { useState } from "react";
import { AuthRegisterRepositoryHttp } from "../../infrastructure/repositories/AuthRegisterRepositoryHttp";

export function useRegisterUser() {
  const [loading, setLoading] = useState(false);
  const repo = new AuthRegisterRepositoryHttp();

  async function createUser(data: { name: string; email: string; role: string; password: string; department?: string }) {
    setLoading(true);
    try {
      console.debug('[useRegisterUser.createUser] data:', data);
      await repo.registerUser({
        name: data.name,
        email: data.email,
        role: data.role,
        password: data.password,
        department: data.department,
      });
    } finally {
      setLoading(false);
    }
  }

  return { createUser, loading };
}
