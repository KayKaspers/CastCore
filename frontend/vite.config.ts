import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  build: {
    // Disable Vite's module-preload polyfill: it injects an inline <script> into
    // index.html, which would violate `script-src 'self'` under the CSP (CC-WP-008a).
    // All target browsers support native modulepreload, so the polyfill is not needed.
    modulePreload: { polyfill: false }
  },
  server: {
    port: 5173,
    proxy: {
      // Dev: proxy API + websockets to the FastAPI backend.
      "/api": { target: "http://localhost:8000", changeOrigin: true, ws: true }
    }
  }
});
