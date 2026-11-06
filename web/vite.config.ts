import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// GitHub Pages project site: https://<user>.github.io/<repo>/
// Must match repository name (case-sensitive in the URL path).
const repoName = "constitution-of-India-IPC";

// https://vite.dev/config/
export default defineConfig(({ mode }) => ({
  plugins: [react()],
  base: mode === "production" ? `/${repoName}/` : "/",
}));
