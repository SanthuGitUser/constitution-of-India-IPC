# GitHub Pages — fix 404

URL: `https://santhugituser.github.io/constitution-of-India-IPC/`

A **404** here means GitHub is **not** publishing your built site. The usual mistake is picking the **wrong** “Source” in **Settings → Pages**.

---

## Use this setup (one workflow)

The repo has **`.github/workflows/pages.yml`**. It builds **`docs/`** and deploys with **GitHub Actions**.

### Step 1 — Push the workflow

Push your code so **`pages.yml`** is on **`main`** (or **`master`**).

### Step 2 — Pages source must be “GitHub Actions”

**Repository → Settings → Pages**

Under **Build and deployment**:

- **Source:** **GitHub Actions**  
- **Not** “Deploy from a branch” for this setup.

If you see “Deploy from a branch” with **`main` / `/`** or **`main` / `/docs`**, the site may still 404 because nothing matches what the workflow publishes.

### Step 3 — Let the workflow run

**Actions → “Deploy GitHub Pages”** → latest run **green**.

If it fails, open the log (often `npm ci`, missing `package-lock.json`, or permissions).

### Step 4 — First-time “github-pages” environment

The first deploy may ask you to **approve** the **`github-pages`** environment — do that if prompted.

### Step 5 — Wait + incognito

Wait **1–3 minutes**, then open the URL in a **private window**.

---

## If you insist on “Deploy from a branch”

Then **do not** use **`main` / `/`**: there is no **`index.html`** at repo root.

Either:

- Branch **`gh-pages`**, folder **`/`**, with **`index.html`** at top level (needs a separate process), **or**
- Branch **`main`**, folder **`/docs`**, **and** you **commit** the **`docs/`** folder after `cd web && npm run build`.

The workflow above avoids that and uses **GitHub Actions** only.

---

## Private repo

On a **free** GitHub account, **public** GitHub Pages often needs a **public** repo. Private + public site may be blocked.

---

## Repo name vs assets

`web/vite.config.ts` uses `repoName = "constitution-of-India-IPC"`. The GitHub repo name (in the URL) **must** match **exactly** (including case).
