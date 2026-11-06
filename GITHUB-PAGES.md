# GitHub Pages — fix “404 File not found”

Your site URL:

`https://santhugituser.github.io/constitution-of-India-IPC/`

GitHub shows **404** when **nothing has been deployed yet** or **Pages is not using the workflow build**.

## Checklist (do these in order)

### 1. Push the latest code

From your PC (PowerShell), in the project folder:

```powershell
git add -A
git status
git commit -m "Enable GitHub Pages workflow"
git push origin main
```

If GitHub’s default branch is `master`, use `master` instead of `main`.

### 2. Turn on GitHub Actions for Pages

On GitHub: **Repository → Settings → Pages**

- Under **Build and deployment**
- **Source**: choose **GitHub Actions** (not “Deploy from a branch”).
- Do **not** set Branch to `gh-pages` unless you really want branch deploy; this project uses Actions.

Save if there is a Save button.

### 3. Run the workflow once

**Repository → Actions → “Deploy to GitHub Pages”**

- Open the latest run. It must be **green** (success).
- If it failed: open the failed job and read the error (often missing `package-lock.json`, Node version, or permission).

### 4. Wait and hard-refresh

After a successful deploy, wait **1–5 minutes**, then open the site in a **private/incognito** window or press **Ctrl+Shift+R** (hard refresh).

### 5. Confirm the deployed files

After a green run, **Settings → Pages** sometimes shows the published URL. The workflow deploys the contents of `web/dist`, which must include **`index.html`** at the **root** of that deployment (that is what loads at `/constitution-of-India-IPC/`).

## Common mistakes

| Problem | Fix |
|--------|-----|
| Repo is private + free account | GitHub Pages for private repos may need **GitHub Pro** for users. Make the repo **public** or upgrade. |
| Never selected “GitHub Actions” under Pages | Step 2 above. |
| Workflow not in repo / not pushed | Ensure `.github/workflows/deploy-pages.yml` exists on the default branch. |
| Wrong branch | Default branch should be `main` or `master` (workflow triggers on both). |
| Old cached 404 | Incognito or hard refresh. |

## Repo / URL name

Vite uses `base: /constitution-of-India-IPC/`. If you **rename** the GitHub repository, update `repoName` in `web/vite.config.ts` to match the **new** repo name exactly, then push again.
