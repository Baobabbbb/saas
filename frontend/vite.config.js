import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
        debug: resolve(__dirname, 'supabase-debug.html'),
        test: resolve(__dirname, 'test-supabase-connection.html')
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
      '/admin': {
        target: 'http://localhost:5174',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/admin/, '')
      }
    }
  }
})
