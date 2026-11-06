# Indian Law — Plain Guide

Web app for the **Constitution of India** and **Indian Penal Code (IPC)**: plain-language summaries, search, and official text side by side with a simple summary.

## Deploy on GitHub Pages

The repo includes a workflow (`.github/workflows/deploy-pages.yml`) that builds the Vite app and publishes `web/dist`.

1. Push these files to GitHub.
2. On the repo: **Settings → Pages → Build and deployment → Source**: choose **GitHub Actions** (not “Deploy from a branch”).
3. Open **Actions**, run **Deploy to GitHub Pages** (or push to `main` so it runs).
4. After it finishes, the site is at  
   `https://santhugituser.github.io/constitution-of-India-IPC/`  
   (wait a minute for the first deploy.)

The build uses `base: /constitution-of-India-IPC/` so assets load correctly. If you rename the repository, edit `repoName` in `web/vite.config.ts` to match the new name exactly.

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
