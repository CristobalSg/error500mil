Guía de Contribución al Proyecto SGH

Gracias por colaborar 🙌. Para mantener un flujo de trabajo ordenado, seguimos convenciones claras de ramas, commits y scripts.

🚀 Flujo de trabajo

Crear una rama a partir de develop (o main si aplica) siguiendo el formato:

feat/nombre-tarea      → nueva funcionalidad
fix/nombre-tarea       → corrección de bug
chore/nombre-tarea     → mantenimiento, dependencias, configuración
docs/nombre-tarea      → cambios en documentación


Ejemplos:

feat/consulta-clientes
fix/error-login
chore/update-dependencies
docs/guia-instalacion


Realiza tus cambios en la rama correspondiente.

Hacer commits siguiendo la convención Conventional Commits (ver sección siguiente).

Subir la rama y abrir un Pull Request hacia develop o main.

📝 Convención de Commits

Este repositorio usa Conventional Commits
:

<tipo>(alcance-opcional): descripción breve

Tipos permitidos

feat: Nueva funcionalidad

fix: Corrección de un error

docs: Cambios en documentación

style: Cambios de estilo (formato, espacios, punto y coma)

refactor: Refactorización sin cambiar funcionalidad

test: Agregar o modificar tests

chore: Mantenimiento, dependencias, configuración

Ejemplos
feat: agregar validación en login
fix(auth): corregir error de token expirado
docs: actualizar guía de instalación
chore: actualizar dependencias de seguridad


💡 Nota: Husky + Commitlint están activos, por lo que los commits que no respeten el formato serán rechazados automáticamente.

🧹 Estilo de código

Usa Prettier y ESLint para mantener un formato consistente.

Los commits deben ser pequeños y descriptivos.

Cada rama debe resolver una sola tarea o feature.

Antes de subir tu PR, asegúrate que el proyecto compila y pasa los tests.

🧪 Scripts comunes

Desde la raíz del monorepo puedes ejecutar:

pnpm dev:mobile     # Ejecuta la app móvil
pnpm dev:backend    # Inicia el servidor backend
pnpm build:all      # Compila todos los paquetes
pnpm lint           # Ejecuta linter
pnpm test           # Ejecuta tests

🥉 Centralización de configuraciones y scripts

Unificar scripts en el package.json principal (raíz):

{
  "name": "sgh-monorepo",
  "private": true,
  "scripts": {
    "dev:backend": "pnpm --filter backend dev",
    "dev:mobile": "pnpm --filter mobile dev",
    "build:all": "pnpm -r build",
    "lint": "pnpm -r lint",
    "test": "pnpm -r test"
  }
}


Eliminar configuraciones duplicadas en subproyectos (backend/, mobile/, etc.):

Mueve configuraciones comunes a la raíz (.eslintrc.json, .prettierrc, tailwind.config.js)

En cada subproyecto, deja solo referencias:

{
  "extends": "../../.eslintrc.json"
}


Commit final luego de centralizar:

git add .
git commit -m "chore: centralización de configuraciones compartidas y unificación de scripts"
git push origin <nombre-de-tu-rama>


```