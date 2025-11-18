import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html')
      }
    }
  },
  server: {
    port: 5173,
    host: '192.168.1.21', // Configuration réseau qui fonctionnait
    strictPort: true,
    hmr: {
      port: 5173,
    },
    proxy: {
      '/ilmysv6iepwepoa4tj2k': {
        target: 'https://panneau-production.up.railway.app',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/ilmysv6iepwepoa4tj2k/, '')
      }
    }
  }
})
