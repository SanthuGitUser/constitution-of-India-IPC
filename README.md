# Indian Law — Plain Guide

Web app for the **Constitution of India** and **Indian Penal Code (IPC)**: plain-language summaries, search, and official text side by side with a simple summary.

## Deploy on GitHub Pages

**Easiest:** push the repo, run **`.github/workflows/pages.yml`**, then **Settings → Pages** → **Source: GitHub Actions** (not “Deploy from a branch”).

**Or** build locally (`cd web` → `npm run build`), commit **`docs/`**, set Pages to **`main`** / **`/docs`**.

Site: `https://santhugituser.github.io/constitution-of-India-IPC/`

Full checklist: **[GITHUB-PAGES.md](GITHUB-PAGES.md)**.

The build uses `base: /constitution-of-India-IPC/`. If you rename the repository, edit `repoName` in `web/vite.config.ts`.

## Quick start

```powershell
pip install -r requirements.txt
python scripts/extract_constitution.py
python scripts/extract_ipc.py

cd web
npm install
npm run dev
```

Open the local URL (usually `http://localhost:5173`).

- **Constitution tab**: `?law=constitution` (default)
- **IPC tab**: `?law=ipc`
- Deep links: `#constitution-article-21`, `#ipc-section-302`

## Data files

| PDF | Script | JSON |
|-----|--------|------|
| `20240716890312078.pdf` | `scripts/extract_constitution.py` | `web/public/data/constitution.json` |
| `ipc-english.pdf` | `scripts/extract_ipc.py` | `web/public/data/ipc.json` |

Re-run the matching script after replacing a PDF.

## Disclaimer

Plain-language summaries are for learning only. Use the official Gazette or government publication for legal proceedings.
