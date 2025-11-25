import { Link } from "react-router-dom";
import BottomNav from "../../components/BottomNav";

export default function StudentEventsPlaceholderPage() {
  return (
    <div className="flex min-h-[var(--app-height)] flex-col bg-[#F4F7FB]">
      <header className="fixed top-0 left-0 right-0 z-10 bg-[#004F9F] shadow-md safe-top">
        <div className="mx-auto flex w-full max-w-md items-center justify-between px-4 py-4 text-white">
          <div>
            <p className="text-xs uppercase tracking-wide text-[#FDB813]">Panel estudiante</p>
            <h1 className="text-lg font-semibold">Eventos</h1>
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
        <section className="flex flex-1 flex-col items-center justify-center rounded-3xl bg-white p-6 text-center shadow-sm">
          <div className="rounded-full bg-[#004F9F0D] p-5">
            <span role="img" aria-hidden="true" className="text-4xl">
              🚧
            </span>
          </div>
          <h2 className="mt-4 text-xl font-semibold text-[#004F9F]">Página en construcción</h2>
          <p className="mt-2 text-sm text-[#004F9FB3]">
            Estamos trabajando para habilitar los eventos para estudiantes. Muy pronto podrás revisar y gestionar tus actividades desde aquí.
          </p>
          <Link
            to="/student/home"
            className="mt-6 inline-flex items-center justify-center rounded-2xl bg-[#FDB813] px-4 py-2 text-sm font-semibold text-[#004F9F] shadow-sm"
          >
            Volver al inicio
          </Link>
        </section>
      </main>

      <BottomNav />
    </div>
  );
}
