import type { Role } from "../auth/user";

export interface UserSummary {
  id: number;
  name: string;
  email: string;
  role: Role;
  active: boolean;
  createdAt?: string;
  updatedAt?: string;
}

export interface DocenteSummary {
  id: number;
  userId: number;
  department?: string | null;
}
