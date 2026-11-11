# chrisgraham.com

Static site, served by GitHub Pages from the `docs/` folder on `main`. `server.js` is only for local preview (`npm start`, then http://localhost:3000).

## Deploy

Merge to `main`. GitHub Pages rebuilds in about a minute. No Railway, no VM, no Mac.

**`/prod` ships it.** Label a PR `prod-ready`, then press the **Ship it** workflow: `gh workflow run prod-train.yml --repo fugioconsulting/chrisgraham.com` (`-f dry_run=true` for the plan only). It runs `bin/prod-train` on a GitHub-hosted runner: squash-merges every open, non-draft `prod-ready` PR with no conflicts and no red checks (fixes first, then oldest, pinned to the labeled commit), asks Pages to rebuild, waits for Pages to build main's commit, checks the site answers, and comments "landed" or "held" on each PR. A held PR keeps its label and rides the next train once fixed. Don't `gh pr merge` by hand. Merges made by the train do not trigger other workflows, so a PR that touches `data/grooming/**` gets its page rebuilt by the next daily sweep, not at once.

Two Actions workflows: Ship it, and the grooming tracker sweep, which commits data and the rebuilt page to main; the morning judge on Chris's Mac also pushes grooming data to main. The site left Railway in the 2026-09-11/12 New Albany cutover and left the `pete` VM for Pages on 2026-10-08.

**Verify after merge:** `curl -s https://chrisgraham.com/ | grep -c fugio-framework` (expect > 0). Hard refresh client-side.

Details and one-time setup: `DEPLOY.md`.

## Layout

- `docs/index.html` homepage, `docs/coaching.html`, `docs/pete.html`, `docs/group.html`. Pages resolves `/coaching` to `coaching.html` and `/group` to `group.html`.
- `docs/studio.html` is a redirect shell (meta refresh plus `location.replace`) to the Riverside studio page. Not a real page.
- `docs/` is the only directory Pages serves, and `server.js` previews only `docs/`. Nothing under `public/` is served (there is no `public/`; do not recreate it); put pages in `docs/`.
- Favicon set, referenced from the page heads: `docs/favicon-32.png`, `docs/favicon.ico`, `docs/apple-touch-icon.png`. `docs/icon-192.png` is currently unused.
- `docs/404.html` redirects unknown paths to `/`.
- `docs/CNAME` holds the custom domain. Do not delete it.
- `docs/robots.txt` and `docs/sitemap.xml` are hand-kept. Add a new page to the sitemap when it ships.
- `docs/.nojekyll` stops Pages from running Jekyll. Keep it.
- `docs/assets` and `docs/img` are the ClickFunnels export. Root-relative paths. `docs/fonts` was removed (the files were commercial fonts and no `@font-face` remains); do not re-add it.
- `docs/grooming/` is the grooming-charge tracker's data feed (`cases.json`); chrisgraham.com/grooming redirects to the Claude artifact https://claude.ai/artifact/L2qaA61k6neUampn7kD24R, the public page, which the morning judge republishes from `data/grooming/cases.csv`. Built by `scripts/grooming/build.py`; fed by `scripts/grooming/crawl.py` on a daily 5am ET GitHub Actions schedule (`.github/workflows/grooming.yml`, free, no API key), then judged each morning by the Claude scheduled task `grooming-judge` on Chris's MacBook Pro following `scripts/grooming/JUDGE.md`, in its own worktree `/Users/h/code/grooming-judge`; both commit to main. Never hand-edit `docs/grooming/`; edit the CSV and rebuild. Details: `scripts/grooming/README.md`.
- `signature/` is the email signature HTML, not part of the site. `signature/email-signature.html` hotlinks `docs/img/chris-graham-sig-bw.png` (served at chrisgraham.com/img/), so never delete that file. `docs/img/chris-graham-sig.png` is an identical duplicate; leave it.
