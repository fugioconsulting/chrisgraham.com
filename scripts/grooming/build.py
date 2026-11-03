#!/usr/bin/env python3
"""Build docs/grooming/cases.json (the data feed) and docs/grooming/index.html (a redirect to the artifact) from data/grooming/.
Stdlib only. Run: python3 scripts/grooming/build.py"""
import csv, json, os, html, datetime, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
D = os.path.join(ROOT, "data", "grooming")
OUT = os.path.join(ROOT, "docs", "grooming")
os.makedirs(OUT, exist_ok=True)
H = html.escape

cases = list(csv.DictReader(open(os.path.join(D, "cases.csv"), encoding="utf-8")))
excluded = list(csv.DictReader(open(os.path.join(D, "excluded.csv"), encoding="utf-8")))
try: candidates = json.load(open(os.path.join(D, "candidates.json")))
except Exception: candidates = []
dismissed = set()
p = os.path.join(D, "dismissed.txt")
if os.path.exists(p):
    dismissed = {l.split("#")[0].strip() for l in open(p) if l.split("#")[0].strip()}
known_urls = {c["source_url"].rstrip("/") for c in cases} | {e["source_url"].rstrip("/") for e in excluded}
candidates = [c for c in candidates if c.get("id") not in dismissed and c.get("url","").rstrip("/") not in dismissed and c.get("url","").rstrip("/") not in known_urls]
candidates.sort(key=lambda c: c.get("published") or c.get("found_at") or "", reverse=True)
aliases = {}
for c in cases + excluded:
    last = c["name"].split()[-1].lower()
    if last != "jr." and len(last) > 4: aliases[last] = c["name"]
    aliases[c["name"].lower()] = c["name"]
    for a in (c.get("aka") or "").split(";"):
        if a.strip(): aliases[a.strip().lower()] = c["name"]
for c in candidates:
    if not c.get("matches"):
        blob = (c.get("title", "") + " " + c.get("snippet", "")).lower()
        c["matches"] = next((who for a, who in aliases.items() if a in blob), None)
coverage = [c for c in candidates if c.get("matches")]
candidates = [c for c in candidates if not c.get("matches")]
try: last_sweep = open(os.path.join(D, "last_sweep.txt")).read().strip()
except Exception: last_sweep = ""
built = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

n = len(cases)
resolved = [c for c in cases if c["resolved"] and c["resolved"] != "dismissed"]
dismissed_cases = [c for c in cases if c["resolved"] == "dismissed"]
hands = [c for c in cases if c["companion"] == "hands-on"]
expl = [c for c in cases if c["companion"] == "exploitation"]
unspec = [c for c in cases if c["companion"] == "unspecified"]
alone = [c for c in cases if c["companion"] == "none"]
with_comp = n - len(alone)
def lastname(c):
    p = c["name"].split(); return p[-2] if p[-1] in ("Jr.",) else p[-1]
open_cases = [c for c in cases if not c["resolved"]]
counties = {}
for c in cases: counties[c["county"]] = counties.get(c["county"], 0) + 1
top_counties = sorted(counties.items(), key=lambda kv: (-kv[1], kv[0]))[:5]

json.dump({"as_of": built, "last_sweep": last_sweep, "count": n, "cases": cases, "not_counted": excluded,
           "candidates": candidates}, open(os.path.join(OUT, "cases.json"), "w"), indent=1)

# The public page is the Claude artifact (a mirror of cases.csv, republished by the morning judge). /grooming just sends people there.
ARTIFACT = "https://claude.ai/artifact/L2qaA61k6neUampn7kD24R"
page = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Ohio Grooming Charge Tracker</title>
<meta http-equiv="refresh" content="0; url={ARTIFACT}">
<link rel="canonical" href="{ARTIFACT}">
<meta name="description" content="Every Ohioan charged under Ohio's grooming law, ORC 2907.071, with a source on every case.">
<meta property="og:title" content="{n} Ohioans charged with grooming">
<meta property="og:description" content="Every Ohioan charged under ORC 2907.071, with charges, status and a source on every case.">
<meta property="og:url" content="https://chrisgraham.com/grooming">
<meta property="og:image" content="https://chrisgraham.com/grooming/img/ohio_map.png">
<meta name="twitter:card" content="summary_large_image">
<script>location.replace("{ARTIFACT}")</script>
</head>
<body><p><a href="{ARTIFACT}">Ohio Grooming Charge Tracker</a></p></body>
</html>
'''
open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(page)
print(f"built {OUT}/index.html (redirect to the artifact) + cases.json: {n} cases, {len(candidates)} candidates")
