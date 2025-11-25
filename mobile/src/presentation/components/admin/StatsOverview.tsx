import React, { useMemo } from "react";
import { useAdminUsers } from "../../hooks/useAdminUsers";
import { useAllRestrictions } from "../../hooks/useAllRestrictions";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
} from "chart.js";
import { Bar, Doughnut } from "react-chartjs-2";

// Registrar solo una vez (no dentro de render condicional)
ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement);

// Tipos básicos locales (ajusta si tus hooks ya exportan tipos)
interface User {
  id: number;
  name: string;
  email: string;
  role?: string;
}

interface Restriccion {
  id: number;
  activa: boolean;
  disponible: boolean;
}

export default function StatsOverview() {
  const { users, loading: loadingUsers } = useAdminUsers();
  const {
    restricciones,
    loading: loadingRestr,
    error: restrError,
    refresh: refreshRestr,
  } = useAllRestrictions();

  // Normaliza roles para evitar valores inesperados
  const userStats = useMemo(() => {
    const base = { docente: 0, estudiante: 0, admin: 0 };
    (users as User[]).forEach((u) => {
      const r = (u.role || "").toLowerCase();
      if (r in base) base[r as keyof typeof base] += 1;
    });
    return {
      total: users.length,
      ...base,
    };
  }, [users]);

  const restrictionStats = useMemo(() => {
    let activas = 0;
    let inactivas = 0;
    let disponibles = 0;
    let noDisponibles = 0;

    (restricciones as Restriccion[]).forEach((r) => {
      if (r.activa) activas++;
      else inactivas++;
      if (r.disponible) disponibles++;
      else noDisponibles++;
    });

    return {
      total: restricciones.length,
      activas,
      inactivas,
      disponibles,
      noDisponibles,
    };
  }, [restricciones]);

  // Datos para gráfico de usuarios
  const barData = useMemo(
    () => ({
      labels: ["Docentes", "Estudiantes", "Admins"],
      datasets: [
        {
          label: "Usuarios por rol",
          data: [
            userStats.docente || 0,
            userStats.estudiante || 0,
            userStats.admin || 0,
          ],
          backgroundColor: ["#4F46E5", "#0EA5E9", "#16A34A"],
          borderRadius: 6,
        },
      ],
    }),
    [userStats],
  );

  const barOptions = useMemo(
    () => ({
      responsive: true,
      animation: { duration: 250 },
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { display: false }, ticks: { color: "#475569", font: { size: 11 } } },
        y: {
          beginAtZero: true,
          precision: 0,
          grid: { color: "#E2E8F0" },
          ticks: { color: "#475569", font: { size: 11 } },
        },
      },
    }),
    [],
  );

  // Doughnut estado
  const doughnutEstadoData = useMemo(
    () => ({
      labels: ["Activas", "Inactivas"],
      datasets: [
        {
          label: "Estado",
          data: [
            restrictionStats.activas || 0,
            restrictionStats.inactivas || 0,
          ],
          backgroundColor: ["#2563EB", "#F59E0B"],
          borderColor: "#FFFFFF",
          borderWidth: 2,
        },
      ],
    }),
    [restrictionStats],
  );

  // Doughnut disponibilidad
  const doughnutDisponData = useMemo(
    () => ({
      labels: ["Disponibles", "No disponibles"],
      datasets: [
        {
          label: "Disponibilidad",
          data: [
            restrictionStats.disponibles || 0,
            restrictionStats.noDisponibles || 0,
          ],
          backgroundColor: ["#16A34A", "#DC2626"],
          borderColor: "#FFFFFF",
          borderWidth: 2,
        },
      ],
    }),
    [restrictionStats],
  );

  const doughnutOptions = useMemo(
    () => ({
      responsive: true,
      animation: { duration: 250 },
      plugins: {
        legend: { position: "bottom" as const, labels: { font: { size: 11 }, color: "#475569" } },
        tooltip: { intersect: false },
      },
      cutout: "60%",
    }),
    [],
  );

  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      <StatCard
        title="Usuarios"
        loading={loadingUsers}
        value={userStats.total}
        items={[
          { label: "Docentes", value: userStats.docente },
          { label: "Estudiantes", value: userStats.estudiante },
          { label: "Admins", value: userStats.admin },
        ]}
      />
      <StatCard
        title="Restricciones"
        loading={loadingRestr}
        value={restrictionStats.total}
        items={[
          { label: "Activas", value: restrictionStats.activas },
          { label: "Inactivas", value: restrictionStats.inactivas },
        ]}
      />
      <StatCard
        title="Disponibilidad"
        loading={loadingRestr}
        value={restrictionStats.disponibles}
        items={[
          { label: "Disponibles", value: restrictionStats.disponibles },
          { label: "No disponibles", value: restrictionStats.noDisponibles },
        ]}
      />

      <ChartCard title="Usuarios por rol" loading={loadingUsers}>
        {loadingUsers ? (
          <SkeletonChart />
        ) : userStats.total === 0 ? (
          <EmptyChartMessage label="Sin usuarios" />
        ) : (
          <Bar data={barData} options={barOptions} />
        )}
      </ChartCard>

      <ChartCard title="Estado de restricciones" loading={loadingRestr}>
        {loadingRestr ? (
          <SkeletonChart />
        ) : restrictionStats.total === 0 ? (
          <EmptyChartMessage label="Sin restricciones" onRetry={refreshRestr} />
        ) : (
          <Doughnut data={doughnutEstadoData} options={doughnutOptions} />
        )}
      </ChartCard>

      <ChartCard title="Disponibilidad restricciones" loading={loadingRestr}>
        {loadingRestr ? (
          <SkeletonChart />
        ) : restrictionStats.total === 0 ? (
          <EmptyChartMessage label="Sin restricciones" onRetry={refreshRestr} />
        ) : (
          <Doughnut data={doughnutDisponData} options={doughnutOptions} />
        )}
      </ChartCard>

      {restrError && (
        <div className="col-span-full rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          Error cargando restricciones: {restrError}
          <button
            onClick={refreshRestr}
            className="ml-2 rounded-md bg-red-600 px-2 py-1 text-xs font-medium text-white hover:bg-red-700"
          >
            Reintentar
          </button>
        </div>
      )}
    </div>
  );
}

function StatCard({
  title,
  value,
  items,
  loading,
}: {
  title: string;
  value: number;
  items: { label: string; value: number }[];
  loading?: boolean;
}) {
  return (
    <div className="rounded-2xl border border-gray-100 bg-white p-4 shadow-sm">
      <h3 className="text-sm font-semibold text-gray-700">{title}</h3>
      <div className="mt-2 text-3xl font-bold text-indigo-600">{loading ? "…" : value}</div>
      <ul className="mt-3 space-y-1">
        {items.map((i) => (
          <li key={i.label} className="flex justify-between text-xs text-gray-600">
            <span>{i.label}</span>
            <span className="font-medium">{loading ? "…" : i.value}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function ChartCard({
  title,
  children,
  loading,
}: {
  title: string;
  children: React.ReactNode;
  loading?: boolean;
}) {
  return (
    <div className="flex flex-col rounded-2xl border border-gray-100 bg-white p-4 shadow-sm">
      <h3 className="text-sm font-semibold text-gray-700">{title}</h3>
      <div className="mt-3 flex-1">{children}</div>
      {loading && <div className="mt-2 text-center text-xs text-gray-400">Cargando…</div>}
    </div>
  );
}

function SkeletonChart() {
  return (
    <div className="flex h-40 items-center justify-center rounded-md border border-dashed border-gray-200 bg-gray-50 text-xs text-gray-400">
      Cargando gráfico…
    </div>
  );
}

function EmptyChartMessage({ label, onRetry }: { label: string; onRetry?: () => void }) {
  return (
    <div className="flex h-40 flex-col items-center justify-center rounded-md border border-dashed border-gray-200 bg-gray-50 text-xs text-gray-500">
      {label}
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-2 rounded-md bg-indigo-600 px-2 py-1 text-white hover:bg-indigo-700"
        >
          Reintentar
        </button>
      )}
    </div>
  );
}