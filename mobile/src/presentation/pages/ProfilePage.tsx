import BottomNav from "../components/BottomNav";

const ProfilePage = () => {
  return (
    <div className="flex min-h-[var(--app-height)] flex-col bg-gray-50">
      <header className="bg-white shadow-md fixed top-0 left-0 right-0 z-10 safe-top">
        <div className="max-w-md mx-auto px-4 py-3">
          <h1 className="text-lg font-semibold text-gray-800">Perfil</h1>
        </div>
      </header>

      <main
        className="ios-scroll mx-auto flex w-full max-w-md flex-1 overflow-y-auto px-4"
        style={{
          paddingTop: "calc(80px + env(safe-area-inset-top, 0px))",
          paddingBottom: "calc(120px + env(safe-area-inset-bottom, 0px))",
        }}
      >
        <p className="text-gray-700 text-sm mt-4">
          Información del usuario, opciones de edición y configuración personal.
        </p>
      </main>

      {/* Barra de navegación inferior */}
      <BottomNav />
      
    </div>
  );
};

export default ProfilePage;
