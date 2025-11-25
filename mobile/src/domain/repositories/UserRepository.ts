import type { DocenteSummary, UserSummary } from "../users/user";

export interface UserRepository {
  listUsers(): Promise<UserSummary[]>;
  listDocentes(): Promise<DocenteSummary[]>;
}
