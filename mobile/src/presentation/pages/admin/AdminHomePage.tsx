import AppLayout from "../../components/layout/AppLayout";
import StatsOverview from "../../components/admin/StatsOverview";
import GenerateScheduleButton from "../../components/admin/GenerateScheduleButton";

export default function AdminHomePage() {
  return (
    <AppLayout title="Inicio" showBottomNav>
      <div className="space-y-6 py-4">
        <section className="rounded-3xl border border-gray-100 bg-white p-5 shadow-sm">
          <h2 className="text-base font-semibold text-gray-900">Panel del administrador</h2>
          <p className="mt-2 text-sm text-gray-600">
            Vista general del sistema. Agrega gráficos y reportes rápidos para apoyar la gestión.
          </p>
        </section>

        <GenerateScheduleButton />

        <StatsOverview />
      </div>
    </AppLayout>
  );
}
