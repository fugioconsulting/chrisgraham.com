// Local preview of docs/ (GitHub Pages). Not deployed.
const express = require("express");
const path = require("path");

const app = express();
const PORT = process.env.PORT || 3000;

app.use(
  express.static(path.join(__dirname, "docs"), {
    extensions: ["html"],
    maxAge: "1h",
    // HTML revalidates on every load so a deploy shows up immediately.
    // Hashed assets (/assets, /img) keep the 1h cache.
    setHeaders(res, filePath) {
      if (filePath.endsWith(".html")) {
        res.setHeader("Cache-Control", "no-cache");
      }
    },
  })
);

app.get("/health", (_req, res) => {
  res.json({ status: "ok", app: "chrisgraham.com", ts: new Date().toISOString() });
});

// Unknown paths get docs/404.html, same as Pages (it redirects to /).
app.use((_req, res) => {
  res.status(404).sendFile(path.join(__dirname, "docs", "404.html"));
});

app.listen(PORT, () => {
  console.log(`chrisgraham.com local preview listening on :${PORT}`);
});
