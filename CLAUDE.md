# chrisgraham.com

Static site, served by GitHub Pages from the `docs/` folder on `main`. `server.js` is only for local preview (`npm start`, then http://localhost:3000).

## Deploy

Merge to `main`. GitHub Pages rebuilds in about a minute. No Railway, no VM, no Mac. The only Actions workflow is the grooming tracker sweep, which commits data and the rebuilt page to main; the morning judge on Chris's Mac also pushes grooming data to main. The site left Railway in the 2026-09-11/12 New Albany cutover and left the `pete` VM for Pages on 2026-10-08.

**Verify after merge:** `curl -s https://chrisgraham.com/ | grep -c fugio-framework` (expect > 0). Hard refresh client-side.

Details and one-time setup: `DEPLOY.md`.

## Layout

- `docs/` is the only served directory (there is no `public/`; do not recreate it). `docs/index.html` homepage, `docs/coaching.html`, `docs/pete.html`. Pages resolves `/coaching` to `coaching.html`.
- `docs/404.html` redirects unknown paths to `/`.
- `docs/CNAME` holds the custom domain. Do not delete it.
- `docs/robots.txt` and `docs/sitemap.xml` are hand-kept. Add a new page to the sitemap when it ships.
- `docs/.nojekyll` stops Pages from running Jekyll. Keep it.
- `docs/assets`, `docs/img`, `docs/fonts` are the ClickFunnels export. Root-relative paths.
- `docs/grooming/` is the grooming-charge tracker's data feed (`cases.json`); chrisgraham.com/grooming redirects to the Claude artifact https://claude.ai/artifact/L2qaA61k6neUampn7kD24R, the public page, which the morning judge republishes from `data/grooming/cases.csv`. Built by `scripts/grooming/build.py`; fed by `scripts/grooming/crawl.py` on a daily 5am ET GitHub Actions schedule (`.github/workflows/grooming.yml`, free, no API key), then judged each morning by the Claude scheduled task `grooming-judge` on Chris's MacBook Pro following `scripts/grooming/JUDGE.md`, in its own worktree `/Users/h/code/grooming-judge`; both commit to main. Never hand-edit `docs/grooming/`; edit the CSV and rebuild. Details: `scripts/grooming/README.md`.
- `signature/` is the email signature HTML, not part of the site.
