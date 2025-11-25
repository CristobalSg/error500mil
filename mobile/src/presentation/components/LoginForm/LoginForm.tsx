import React, { useState } from "react";
import PasswordInput from "../ui/PasswordInput";
import Card from "../ui/Card";
import Input from "../ui/Input";
import Button from "../ui/Button";
import { useAuth } from "../../../app/providers/AuthProvider";
import { useLocation, useNavigate, type Location } from "react-router-dom";
import { getDefaultPathByRole } from "../../routes/rolePaths";

const LoginForm: React.FC = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation() as { state?: { from?: Location } };


  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const loggedRole = await login(email, password);
      if (!loggedRole) {
        setError("Credenciales incorrectas");
        return;
      }
      const returnTo = location.state?.from?.pathname ?? getDefaultPathByRole(loggedRole);
      navigate(returnTo, { replace: true });
    } catch (err) {
      const detail = err instanceof Error ? err.message : "No se pudo iniciar sesión";
      setError(detail);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="flex min-h-[var(--app-height)] w-full flex-col items-center justify-center p-5
      bg-gradient-to-br from-[var(--color-primary-light)] to-[var(--color-primary-dark)]
      dark:from-[var(--color-secondary-dark)] dark:to-[var(--color-background-dark)]"
    >
      <Card>
        <form onSubmit={handleSubmit} className="flex flex-col w-full gap-6">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-extrabold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-200">
              ¡Bienvenido de nuevo!
            </h2>
            <p className="text-white/80 text-base font-normal">
              Inicia sesión en tu cuenta
            </p>
          </div>

          {error && <div className="text-sm text-red-600 font-medium">{error}</div>}

          <div className="flex flex-col gap-4">
            <Input
              label="Correo electrónico"
              type="text"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="admin"
              variant="solid"
              required
            />
            <PasswordInput
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              variant="solid"
            />
          </div>

          <Button type="submit" variant="special" loading={loading} disabled={loading}>
            Iniciar sesión
          </Button>
        </form>
      </Card>
    </div>
  );
};

export default LoginForm;
