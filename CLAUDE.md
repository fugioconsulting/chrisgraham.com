# chrisgraham.com

Static Express clone of the ClickFunnels "hello-there" site (`server.js` serves `public/` with `extensions: ["html"]`, `maxAge: "1h"`).

## Deploy — NOT Railway

This site moved off Railway in the 2026-09-11/12 New Albany cutover. `git push origin main` deploys nothing by itself.

**To ship:** `bin/chrisgraham-deploy` in the Bonnie ops repo (`/Users/claw/Documents/Claude/Projects/💁🏿‍♀️ Bonnie/bin/chrisgraham-deploy`). It archives `main`, scp's it to GCP VM `pete` (project `pete-new-albany`, zone `us-east5-a`), rebuilds the `chrisgraham` Docker image there, and restarts the `chrisgraham` systemd service. `bin/chrisgraham-deploy --restart` for a plain restart with no rebuild.

**Verify after deploy:** `curl -s https://chrisgraham.com/health` and check the specific page (e.g. `curl -s https://chrisgraham.com/coaching | wc -c`) — a hard refresh may be needed client-side because of the 1h `maxAge`.

Details: [[reference_chrisgraham_com_deploy]] memory, and `CUTOVER_NEW_ALBANY.md` in the Bonnie project dir.
