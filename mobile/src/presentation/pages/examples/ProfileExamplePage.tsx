// Ejemplo de uso de avatares predeterminados en una página de perfil
import UserAvatar from '../../components/UserAvatar';

export default function ProfileExamplePage() {
  // Ejemplo 1: Usuario masculino sin avatar personalizado
  const maleUser = {
    name: 'Juan Pérez',
    gender: 'male' as const,
    avatarUrl: null,
  };

  // Ejemplo 2: Usuario femenino sin avatar personalizado
  const femaleUser = {
    name: 'María García',
    gender: 'female' as const,
    avatarUrl: null,
  };

  // Ejemplo 3: Usuario con avatar personalizado
  const userWithCustomAvatar = {
    name: 'Pedro López',
    gender: 'male' as const,
    avatarUrl: 'https://example.com/custom-avatar.jpg',
  };

  return (
    <div className="p-6 space-y-8">
      <h1 className="text-2xl font-bold mb-6">Ejemplos de Avatares</h1>

      {/* Ejemplo 1 */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Usuario masculino (avatar predeterminado)</h2>
        <div className="flex items-center space-x-4">
          <UserAvatar
            gender={maleUser.gender}
            userName={maleUser.name}
            size={100}
          />
          <div>
            <p className="font-medium">{maleUser.name}</p>
            <p className="text-sm text-gray-500">Género: {maleUser.gender}</p>
            <p className="text-sm text-gray-500">Avatar: Predeterminado</p>
          </div>
        </div>
      </div>

      {/* Ejemplo 2 */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Usuario femenino (avatar predeterminado)</h2>
        <div className="flex items-center space-x-4">
          <UserAvatar
            gender={femaleUser.gender}
            userName={femaleUser.name}
            size={100}
          />
          <div>
            <p className="font-medium">{femaleUser.name}</p>
            <p className="text-sm text-gray-500">Género: {femaleUser.gender}</p>
            <p className="text-sm text-gray-500">Avatar: Predeterminado</p>
          </div>
        </div>
      </div>

      {/* Ejemplo 3 */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Usuario con avatar personalizado</h2>
        <div className="flex items-center space-x-4">
          <UserAvatar
            avatarUrl={userWithCustomAvatar.avatarUrl}
            gender={userWithCustomAvatar.gender}
            userName={userWithCustomAvatar.name}
            size={100}
          />
          <div>
            <p className="font-medium">{userWithCustomAvatar.name}</p>
            <p className="text-sm text-gray-500">Género: {userWithCustomAvatar.gender}</p>
            <p className="text-sm text-gray-500">Avatar: Personalizado</p>
          </div>
        </div>
      </div>

      {/* Diferentes tamaños */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Diferentes tamaños</h2>
        <div className="flex items-center space-x-4">
          <UserAvatar gender="male" userName="Pequeño" size={40} />
          <UserAvatar gender="female" userName="Mediano" size={80} />
          <UserAvatar gender="male" userName="Grande" size={120} />
          <UserAvatar gender="female" userName="Extra Grande" size={160} />
        </div>
      </div>
    </div>
  );
}
