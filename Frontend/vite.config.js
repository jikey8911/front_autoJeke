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
    port: 3000, strictPort: true, // Vite ahora corre nativamente en el puerto 3000
    proxy: {
      '/api': {
        target: process.env.BACKEND_URL || 'http://automata_backend:5000', // IP (172.21.0.2) o hostname del contenedor del backend
        changeOrigin: true,
        // rewrite: (path) => path.replace(/^\/api/, ''), // Se elimina el rewrite porque el backend recibe rutas con el prefijo /api/
      },
    },
  },
  build: {
    cssMinify: false, // lightningcss no soporta @theme (Tailwind v4) de jeikei-ui
  },
})
