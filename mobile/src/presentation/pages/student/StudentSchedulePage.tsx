import BottomNav from "../../components/BottomNav";
import ScheduleTable from "../../components/Schedule/ScheduleTable";

export default function StudentSchedulePage() {
  return (
    <div className="flex min-h-[var(--app-height)] flex-col bg-[#F4F7FB]">
      <header className="fixed top-0 left-0 right-0 z-10 bg-[#004F9F] shadow-md safe-top">
        <div className="mx-auto flex w-full max-w-md items-center justify-between px-4 py-4 text-white">
          <div>
            <p className="text-xs uppercase tracking-wide text-[#FDB813]">Panel estudiante</p>
            <h1 className="text-lg font-semibold">Horario</h1>
          </div>
        </div>
      </header>

      <main
        className="ios-scroll mx-auto flex w-full max-w-md flex-1 flex-col gap-5 overflow-y-auto px-4"
        style={{
          paddingTop: "calc(96px + env(safe-area-inset-top, 0px))",
          paddingBottom: "calc(120px + env(safe-area-inset-bottom, 0px))",
        }}
      >
        <section className="rounded-3xl bg-white p-5 shadow-sm">
          <h2 className="text-lg font-semibold text-[#004F9F]">Clases programadas</h2>
          <p className="mt-2 text-sm text-[#004F9FB3]">
            Consulta tu horario semanal actualizado.
          </p>
        </section>

        <ScheduleTable />
      </main>

      <BottomNav />
    </div>
  );
}
