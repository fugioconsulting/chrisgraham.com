// Static server for the hello-there clone.
// Serves /public on the port Railway provides.
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
  res.json({ status: "ok", app: "hello-there", ts: new Date().toISOString() });
});

// Anything else falls back to index.html so deep links work.
app.get("*", (_req, res) => {
  res.sendFile(path.join(__dirname, "public", "index.html"));
});

app.listen(PORT, () => {
  console.log(`hello-there clone listening on :${PORT}`);
});
