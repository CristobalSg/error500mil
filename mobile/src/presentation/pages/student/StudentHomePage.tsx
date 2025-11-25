import { Link } from "react-router-dom";
import BottomNav from "../../components/BottomNav";
import ScheduleTodayPreview from "../../components/Schedule/ScheduleTodayPreview";

const StudentHomePage: React.FC = () => {
  return (
    <div className="flex min-h-[var(--app-height)] flex-col bg-[#F4F7FB]">
      <header className="fixed top-0 left-0 right-0 z-10 bg-[#004F9F] shadow-md safe-top">
        <div className="mx-auto flex w-full max-w-md items-center justify-between px-4 py-4 text-white">
          <div>
            <p className="text-xs uppercase tracking-wide text-[#FDB813]">Panel estudiante</p>
            <h1 className="text-lg font-semibold">Inicio</h1>
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
        <section className="rounded-3xl bg-white p-5 shadow-sm space-y-3">
          <div>
            <h2 className="text-lg font-semibold text-[#004F9F]">Hola 👋</h2>
            <p className="mt-1 text-sm text-[#004F9FB3]">
              Desde aquí puedes revisar tu horario y seguir próximos eventos.
            </p>
          </div>
          <div className="rounded-2xl bg-[#004F9F0D] px-4 py-3 text-sm text-[#004F9F]">
            Accede rápidamente a tu planificación semanal o ve al detalle completo.
          </div>
          <div className="flex flex-wrap gap-2">
            <Link
              to="/schedule"
              className="inline-flex items-center justify-center rounded-2xl bg-[#FDB813] px-4 py-2 text-sm font-semibold text-[#004F9F] shadow-sm"
            >
              Ver horario completo
            </Link>
            <Link
              to="/student/events"
              className="inline-flex items-center justify-center rounded-2xl border border-[#004F9F33] px-4 py-2 text-sm font-semibold text-[#004F9F]"
            >
              Ver eventos
            </Link>
          </div>
        </section>

        <section className="rounded-3xl bg-white p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-[#004F9F]">Clases de hoy</h2>
              <p className="text-sm text-[#004F9FB3]">Un vistazo rápido a tu agenda.</p>
            </div>
            <Link to="/schedule" className="text-sm font-semibold text-[#004F9F] underline">
              Ver más
            </Link>
          </div>
          <div className="mt-4">
            <ScheduleTodayPreview />
          </div>
        </section>
      </main>

      <BottomNav />
    </div>
  );
};

export default StudentHomePage;
