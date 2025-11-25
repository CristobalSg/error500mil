import path from "path"
import react from "@vitejs/plugin-react"
import tailwindcss from "@tailwindcss/vite"
import { defineConfig } from "vite"
import { VitePWA, type ManifestOptions } from "vite-plugin-pwa"

const pwaManifest: Partial<ManifestOptions> = {
  id: "/",
  name: "SGH",
  short_name: "SGH",
  lang: "es",
  description: "Sistema de Gestión de Horarios",
  start_url: "/",
  scope: "/",
  display: "fullscreen",
  display_override: ["fullscreen", "standalone", "minimal-ui"],
  orientation: "portrait-primary",
  background_color: "#ffffff",
  theme_color: "#1d4ed8",
  icons: [
    {
      src: "/icons/icon-192x192.png",
      sizes: "192x192",
      type: "image/png",
      purpose: "any",
    },
    {
      src: "/icons/icon-512x512.png",
      sizes: "512x512",
      type: "image/png",
      purpose: "maskable",
    },
  ],
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    VitePWA({
      registerType: "autoUpdate",
      injectRegister: "auto",
      manifestFilename: "manifest.json",
      workbox: {
        globPatterns: ["**/*.{js,css,html,ico,png,svg}"],
      },
      devOptions: { enabled: true },
      manifest: pwaManifest,
    }),
  ],
  resolve: {
    alias: { "@": path.resolve(__dirname, "./src") }
  },
  server: {
    port: 8100,
    host: true // esto permite acceder desde otras máquinas o dispositivos en la red
  }
})
