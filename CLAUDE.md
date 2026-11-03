# chrisgraham.com

Static site, served by GitHub Pages from the `docs/` folder on `main`. `server.js` is only for local preview (`npm start`, then http://localhost:3000).

## Deploy

Merge to `main`. GitHub Pages rebuilds in about a minute. No Railway, no VM, no Mac. The only Actions workflow is the grooming tracker sweep, which commits data and the rebuilt page to main. The site left Railway in the 2026-09-11/12 New Albany cutover and left the `pete` VM for Pages on 2026-10-08.

**Verify after merge:** `curl -s https://chrisgraham.com/ | grep -c fugio-framework` (expect > 0). Hard refresh client-side.

Details and one-time setup: `DEPLOY.md`.

## Layout

- `docs/index.html` homepage, `docs/coaching.html`, `docs/pete.html`. Pages resolves `/coaching` to `coaching.html`.
- `docs/404.html` redirects unknown paths to `/`.
- `docs/CNAME` holds the custom domain. Do not delete it.
- `docs/.nojekyll` stops Pages from running Jekyll. Keep it.
- `docs/assets`, `docs/img`, `docs/fonts` are the ClickFunnels export. Root-relative paths.
- `docs/grooming/` is the self-updating grooming-charge tracker (chrisgraham.com/grooming). Built by `scripts/grooming/build.py` from `data/grooming/cases.csv`; fed by `scripts/grooming/crawl.py` on a six-hour GitHub Actions schedule (`.github/workflows/grooming.yml`), which commits to main. Never hand-edit `docs/grooming/index.html`; edit the CSV and rebuild. Details: `scripts/grooming/README.md`.
- `signature/` is the email signature HTML, not part of the site.
