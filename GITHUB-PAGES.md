# GitHub Pages — stop the 404

Live URL (project site):

`https://santhugituser.github.io/constitution-of-India-IPC/`

That only works if GitHub is serving files that contain **`index.html`**. A **404** means GitHub Pages is **not** publishing your build yet.

---

## Option A — Automatic (recommended)

The workflow **`.github/workflows/pages.yml`** builds on every push and updates the **`gh-pages`** branch.

### 1) Push this repo to GitHub

Make sure the workflow file is on your default branch (`main` or `master`).

### 2) Allow Actions to write

**Settings → Actions → General** → **Workflow permissions**

- **Read and write permissions** → **Save**

### 3) Run the workflow

**Actions → “Publish GitHub Pages”** → should turn **green**.

If it fails, open the log and fix errors (e.g. `npm ci` failing).

### 4) Point Pages at `gh-pages`

**Settings → Pages**

| Field | Value |
|--------|--------|
| **Source** | **Deploy from a branch** |
| **Branch** | **`gh-pages`** |
| **Folder** | **`/` (root)** |

**Not** `main` with `/` (root) — `main` has no `index.html` at repo root.

### 5) Confirm

On GitHub, switch branch to **`gh-pages`**. You must see **`index.html`** at the **top** of the file list.

Wait 1–3 minutes, then open the site in **Incognito**.

---

## Option B — Manual (no Actions)

1. On your PC:

   ```powershell
   cd web
   npm ci
   npm run build
   ```

2. Commit **everything under `docs/`**:

   ```powershell
   cd ..
   git add docs
   git commit -m "Add site build"
   git push
   ```

3. **Settings → Pages**

   - Branch: **`main`** (or `master`)
   - Folder: **`/docs`**

---

## Quick checks

| Check | What you want |
|--------|----------------|
| **`gh-pages` branch** | Exists and contains **`index.html`** (Option A) |
| **`docs/` on `main`** | Exists and contains **`index.html`** (Option B) |
| **Pages settings** | Matches Option A (`gh-pages` / root) or B (`main` / `docs`) |
| **Public repo** | Private repos often cannot publish a **public** Pages site on a free account |

---

## Repo name vs URL

The build uses `base: /constitution-of-India-IPC/`. That path must match the **repository name** on GitHub. If you rename the repo, change **`repoName`** in **`web/vite.config.ts`** and redeploy.
