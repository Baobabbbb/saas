import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: '192.168.1.21', // Configuration réseau qui fonctionnait
    strictPort: true,
    hmr: {
      port: 5173,
    },
    proxy: {
      '/admin': {
        target: 'http://localhost:5174',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/admin/, '')
      }
    }
  }
})
