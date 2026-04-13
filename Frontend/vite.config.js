import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { fileURLToPath, URL } from 'node:url'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    // Fuerza una sola instancia de React aunque la librería tenga la suya bundleada
    dedupe: ['react', 'react-dom'],
    alias: {
      'react': fileURLToPath(new URL('./node_modules/react', import.meta.url)),
      'react-dom': fileURLToPath(new URL('./node_modules/react-dom', import.meta.url)),
    },
  },
  optimizeDeps: {
    // Evita que Vite pre-bundle la librería con su propia copia de React
    exclude: ['@jikey8911/jeikei-ui'],
  },
  server: {
    host: true, // Importante para Docker
    port: 5173, // Vite usa 5173 por defecto, mapeado a 3000 en docker-compose
  },
  build: {
    cssMinify: false, // lightningcss no soporta @theme (Tailwind v4) de jeikei-ui
  },
})
