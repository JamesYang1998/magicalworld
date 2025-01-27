import path from "path"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    host: true,
    allowedHosts: [
      'ai-battle-website-tunnel-cgi8vfjn.devinapps.com',
      'localhost',
      '127.0.0.1',
      '.devinapps.com'
    ],
  },
})

