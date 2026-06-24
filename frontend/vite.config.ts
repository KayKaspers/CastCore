import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // Dev: proxy API + websockets to the FastAPI backend.
      "/api": { target: "http://localhost:8000", changeOrigin: true, ws: true }
    }
  }
});
