import { http } from "../http/httpClient";

export type RegisterUserDto = {
  name: string;
  email: string;
  password: string;
  role: string;
  active?: boolean;
};

export class AuthRegisterRepositoryHttp {
  async registerUser(user: {
    name: string;
    email: string;
    role: string;
    password: string;
    department?: string;
    active?: boolean;
  }) {
    if (user.role === 'docente' && !user.department?.trim()) {
      throw new Error("El campo departamento es obligatorio para rol docente.");
    }

    const body: any = {
      nombre: user.name,
      email: user.email,
      rol: user.role,
      contrasena: user.password,
      activo: user.active ?? true,
    };

    if (user.role === 'docente') {
      body.departamento = user.department!.trim(); // clave requerida por backend
    }

    console.debug('[AuthRegisterRepositoryHttp.registerUser] body:', body);

    const { data } = await http.post('/auth/register', body);
    return data;
  }
}
