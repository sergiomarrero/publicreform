import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Relative base so the static build loads correctly on Vercel.
export default defineConfig({
  plugins: [react()],
  base: "./",
  build: {
    outDir: "dist",
    emptyOutDir: true,
  },
});
