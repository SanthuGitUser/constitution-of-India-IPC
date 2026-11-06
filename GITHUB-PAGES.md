# GitHub Pages — fix “404 File not found”

Your site URL:

`https://santhugituser.github.io/constitution-of-India-IPC/`

---

## Easiest fix (no Actions required)

The app builds into a **`docs/`** folder in the repo root. GitHub Pages can serve that folder from **`main`**.

### 1. Build on your computer

```powershell
cd web
npm ci
npm run build
cd ..
```

This creates/updates **`docs/`** (including **`docs/index.html`**).

### 2. Commit and push `docs/`

```powershell
git add docs
git commit -m "Add GitHub Pages build output"
git push origin main
```

(Use `master` instead of `main` if that is your default branch.)

### 3. Configure Pages (this step fixes most 404s)

On GitHub: **Settings → Pages → Build and deployment**

| Setting | Value |
|--------|--------|
| **Source** | **Deploy from a branch** |
| **Branch** | **`main`** (or **`master`**) |
| **Folder** | **`/docs`** |

Not **`/` (root)** — your `index.html` is under **`docs/`**, not the repo root.

Save. Wait **1–3 minutes**, then open the site in **Incognito** or **Ctrl+Shift+R**.

### 4. Public repo

Project sites on a **free account** are normally **public** repos. If the repo is **private**, Pages may not work the same way.

---

## After you change source code

Whenever you change `web/`, run **`npm run build`** in **`web/`** again, commit **`docs/`**, and push.

---

## Optional: GitHub Actions

If you use **`.github/workflows/deploy-pages.yml`**, you must still set **Pages** to either:

- **Branch `gh-pages` / root** (if that workflow successfully updates that branch), or  
- **`main` / `docs`** after you build and commit **`docs/`** locally (simplest).

Do **not** leave Pages on **`main` / `/`** — there is no **`index.html`** at the repository root (only under **`docs/`** or **`gh-pages`**).

---

## Troubleshooting

| Symptom | Fix |
|--------|-----|
| 404 at project URL | Pages must be **`/docs`** on the branch you pushed, or **`gh-pages` / root**. |
| Works locally, not on GitHub | Forgot to **`git push`** **`docs/`** or wrong branch/folder in Settings. |
| Assets 404 | In **`web/vite.config.ts`**, **`repoName`** must match the GitHub repo name exactly. |
