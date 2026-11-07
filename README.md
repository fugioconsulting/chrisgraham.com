# chrisgraham.com

Static site, served by GitHub Pages from `docs/` on `main`. Merge to `main` to deploy. See `DEPLOY.md` for setup and verification, and `CLAUDE.md` for the layout and rules.

## Local preview

```bash
npm install
npm start
# open http://localhost:3000 (or set PORT)
```

`server.js` serves `docs/` the way Pages does, including the `docs/404.html` fallback. It is a local preview only and is not deployed anywhere.
