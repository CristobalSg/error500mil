import {
  HomeIcon,
  AdjustmentsHorizontalIcon,
  CalendarIcon,
  Cog6ToothIcon,
  UserGroupIcon,
} from "@heroicons/react/24/outline";
import {
  HomeIcon as HomeSolid,
  AdjustmentsHorizontalIcon as AdjustmentsHorizontalSolid,
  CalendarIcon as CalendarSolid,
  Cog6ToothIcon as CogSolid,
  UserGroupIcon as UserGroupSolid,
} from "@heroicons/react/24/solid";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../../app/providers/AuthProvider";
import type { Role } from "../../domain/auth/user";

type HeroIcon = typeof HomeIcon;

type Item = {
  id: string;
  label: string;
  path: string;
  outline: HeroIcon;
  solid: HeroIcon;
};

const docenteItems: Item[] = [
  { id: "home",          label: "Home",          outline: HomeIcon,                solid: HomeSolid,                path: "/home" },
  { id: "restrictions",  label: "Restricciones", outline: AdjustmentsHorizontalIcon, solid: AdjustmentsHorizontalSolid, path: "/restrictions" },
  { id: "events",        label: "Eventos",       outline: CalendarIcon,            solid: CalendarSolid,            path: "/events" },
  { id: "settings",      label: "Ajustes",       outline: Cog6ToothIcon,           solid: CogSolid,                 path: "/settings" },
];

const estudianteItems: Item[] = [
  { id: "home", label: "Home", outline: HomeIcon, solid: HomeSolid, path: "/student/home" },
  { id: "schedule", label: "Horario", outline: CalendarIcon, solid: CalendarSolid, path: "/schedule" },
  { id: "settings", label: "Ajustes", outline: Cog6ToothIcon, solid: CogSolid, path: "/settings" },
];

const adminItems: Item[] = [
  { id: "home", label: "Inicio", outline: HomeIcon, solid: HomeSolid, path: "/admin" },
  { id: "users", label: "Usuarios", outline: UserGroupIcon, solid: UserGroupSolid, path: "/admin/users" },
  { id: "restricciones", label: "Restricciones", outline: AdjustmentsHorizontalIcon, solid: AdjustmentsHorizontalSolid, path: "/admin/restricciones" },
  { id: "settings", label: "Ajustes", outline: Cog6ToothIcon, solid: CogSolid, path: "/settings" },
];


const menuByRole: Record<Role, Item[]> = {
  docente: docenteItems,
  estudiante: estudianteItems,
  admin: adminItems,
};

const activeClasses: Record<string, string> = {
  home: "bg-violet-500 text-white",
  restrictions: "bg-pink-500 text-white",
  events: "bg-emerald-500 text-white",
  schedule: "bg-emerald-500 text-white",
  settings: "bg-amber-500 text-white",
  users: "bg-blue-500 text-white",
  restricciones: "bg-pink-500 text-white",
};


const isPathActive = (basePath: string, currentPath: string) => {
  if (currentPath === basePath) return true;
  return currentPath.startsWith(`${basePath}/`);
};

export default function BottomNav() {
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const { role } = useAuth();

  const items = role ? menuByRole[role] ?? [] : [];

  if (items.length === 0) return null;

  const activeItem = items.reduce<Item | null>((activeAcc, item) => {
    if (!isPathActive(item.path, pathname)) return activeAcc;
    if (!activeAcc) return item;
    return item.path.length > activeAcc.path.length ? item : activeAcc;
  }, null);
  const active = activeItem?.id ?? items[0].id;

  const handleClick = (it: Item) => {
    if (pathname !== it.path) navigate(it.path);
  };

  return (
    <nav
      className="fixed bottom-3 left-1/2 -translate-x-1/2 z-20 w-full"
      style={{ paddingBottom: "env(safe-area-inset-bottom, 0px)" }}
      aria-label="Barra de navegación"
    >
      <div className="mx-auto max-w-md px-4">
        <div className="w-full rounded-3xl border border-black/5 bg-white/90 dark:bg-neutral-900/90 backdrop-blur-xl shadow-lg">
          <div className="flex items-center justify-between gap-1 px-2 py-2">
            {items.map((it) => {
              const isActive = active === it.id;
              const Icon = isActive ? it.solid : it.outline;
              return (
                <button
                  key={it.id}
                  onClick={() => handleClick(it)}
                  aria-current={isActive ? "page" : undefined}
                  aria-label={it.label}
                  className={[
                    "group relative flex items-center justify-center transition-all duration-200",
                    "rounded-2xl px-2 py-2",
                    isActive
                      ? `shadow-sm ${activeClasses[it.id] ?? "bg-gray-800 text-white"}`
                      : "text-gray-600 dark:text-gray-300 hover:bg-gray-100/70 dark:hover:bg-white/5",
                  ].join(" ")}
                  style={{ minWidth: isActive ? 96 : 48 }}
                >
                  <Icon className={`h-5 w-5 transition-transform duration-200 ${isActive ? "scale-100" : "scale-95"}`} />
                  <span
                    className={[
                      "ml-2 text-xs font-medium transition-opacity duration-200",
                      isActive ? "opacity-100" : "opacity-0 w-0 overflow-hidden",
                    ].join(" ")}
                  >
                    {it.label}
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </nav>
  );
}
