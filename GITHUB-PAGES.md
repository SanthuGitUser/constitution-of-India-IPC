# GitHub Pages — fix “404 File not found”

Your site URL:

`https://santhugituser.github.io/constitution-of-India-IPC/`

That URL only works after **built files** (including **`index.html`**) are published. A 404 usually means **nothing is deployed** or **Settings → Pages points at the wrong source**.

## How this repo deploys (recommended)

The workflow **`.github/workflows/deploy-pages.yml`**:

1. Builds the Vite app (`web/dist`).
2. Pushes those static files to the **`gh-pages`** branch (using [peaceiris/actions-gh-pages](https://github.com/peaceiris/actions-gh-pages)).

You must point GitHub Pages at **that branch**.

### Step A — Push the latest code

```powershell
git add -A
git commit -m "Deploy site to gh-pages branch"
git push origin main
```

(Use `master` if that is your default branch.)

### Step B — Enable Actions (if needed)

**Settings → Actions → General → Actions permissions** → allow workflows for this repository (at least “Allow all actions and reusable workflows” or allow the peaceiris action).

### Step C — Configure Pages (this fixes most 404s)

**Settings → Pages → Build and deployment**

- **Source**: **Deploy from a branch**
- **Branch**: **`gh-pages`** folder **`/` (root)**  
- Save

Wait **1–3 minutes**. The first run creates the `gh-pages` branch after the workflow succeeds.

### Step D — Confirm the workflow ran

**Actions** tab → workflow **“Deploy to GitHub Pages”** → latest run **green**.

If it is red, open the log and fix the error (e.g. `npm ci` failing).

### Step E — Hard refresh

Incognito window or **Ctrl+Shift+R** on the site URL.

---

## If you still see 404

| Check | What to do |
|--------|------------|
| Workflow never ran | Push again; open **Actions** and run **workflow_dispatch** if needed. |
| Pages still on “GitHub Actions” | Switch to **Deploy from a branch** + **`gh-pages`** as above. |
| `gh-pages` branch missing | Wait for green workflow; refresh the branch dropdown in Settings → Pages. |
| Private repo on free GitHub | Public project sites work on free accounts; **private** repos need **GitHub Pro** for public Pages in many cases. |
| Wrong repo URL | Path must match `base` in `web/vite.config.ts` (`constitution-of-India-IPC`). Rename repo → update `repoName` there. |

## Repo / URL name

Vite uses `base: /constitution-of-India-IPC/`. If you **rename** the GitHub repository, change `repoName` in **`web/vite.config.ts`** to match exactly, push, and let the workflow redeploy.
