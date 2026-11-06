import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// GitHub Pages project site: https://<user>.github.io/<repo>/
// Must match repository name (case-sensitive in the URL path).
const repoName = "constitution-of-India-IPC";

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const isProd = mode === "production";
  const docsRoot = path.resolve(__dirname, "../docs");

  return {
    plugins: [
      react(),
      isProd && {
        name: "gh-pages-spa-404",
        writeBundle() {
          const index = path.join(docsRoot, "index.html");
          const notFound = path.join(docsRoot, "404.html");
          if (fs.existsSync(index)) fs.copyFileSync(index, notFound);
        },
      },
    ].filter(Boolean),
    base: isProd ? `/${repoName}/` : "/",
    build: isProd
      ? {
          outDir: docsRoot,
          emptyOutDir: true,
        }
      : undefined,
  };
});
