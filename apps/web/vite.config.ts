import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { fileURLToPath } from "node:url";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@galley/shared-ui-tokens": fileURLToPath(
        new URL("../../packages/shared-ui-tokens/src/index.ts", import.meta.url)
      ),
    },
  },
  server: {
    port: 3000,
    proxy: {
      "/api": {
        // In Docker compose, set API_HOST=http://galley-api:8000 in the service environment.
        // Local dev without compose uses the default.
        target: process.env.API_HOST ?? "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: "dist",
    sourcemap: true,
  },
});
