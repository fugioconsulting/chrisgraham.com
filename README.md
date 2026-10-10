# hello-there

Static clone of `chrisgraham.com/hello-there`. Self-contained: HTML, CSS, JS bundles, and all images live in `docs/` (served by GitHub Pages).

## Local

```bash
npm install
npm start
# open http://localhost:3000
```

## Railway

`Procfile` runs `node server.js`. Railway sets `PORT`. No env vars required.

## Pages

- `/` → `public/index.html` (the hello-there clone; also the fallback for unknown paths)
- `/fugio` → `public/fugio.html` (Fugio Consulting side page; `server.js` also maps `/fugio/` and any casing to it)
