// Static server for the hello-there clone.
// Serves /public on the port Railway provides.
const express = require("express");
const path = require("path");

const app = express();
const PORT = process.env.PORT || 3000;

app.use(
  express.static(path.join(__dirname, "public"), {
    extensions: ["html"],
    maxAge: "1h",
  })
);

app.get("/health", (_req, res) => {
  res.json({ status: "ok", app: "hello-there", ts: new Date().toISOString() });
});

// Side page: /coaching (also /coaching/ and any casing) -> public/coaching.html
app.get(/^\/coaching\/?$/i, (_req, res) => {
  res.sendFile(path.join(__dirname, "public", "coaching.html"));
});

// Side page: /group -> public/group.html
app.get(/^\/group\/?$/i, (_req, res) => {
  res.sendFile(path.join(__dirname, "public", "group.html"));
});

// Anything else falls back to index.html so deep links work.
app.get("*", (_req, res) => {
  res.sendFile(path.join(__dirname, "public", "index.html"));
});

app.listen(PORT, () => {
  console.log(`hello-there clone listening on :${PORT}`);
});
