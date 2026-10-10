#!/usr/bin/env python3
"""Build docs/grooming/index.html + cases.json from data/grooming/.
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
resolved = [c for c in cases if c["resolved"]]
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

def badge_status(c):
    r = c["resolved"]
    if r == "convicted": return '<span class="badge red">Convicted</span>'
    if r == "pleaded guilty": return '<span class="badge red">Pleaded guilty</span>'
    if r: return '<span class="badge amber">Plea on other counts</span>'
    return '<span class="badge blue">Charged, pending</span>'
def badge_comp(c):
    k = c["companion"]
    if k == "hands-on": return '<span class="badge dark">+ hands-on abuse charged</span>'
    if k == "exploitation": return '<span class="badge dark">+ exploitation charged</span>'
    if k == "none": return '<span class="badge gray">grooming only</span>'
    return '<span class="badge dark">+ other child sex felonies</span>'

def card(c):
    age = f", {H(c['age'])}" if c["age"] else ""
    img = f'<img src="img/{H(c["thumb"])}" alt="" loading="lazy" width="96" height="96">' if c["thumb"] else '<div class="noimg"></div>'
    return f'''<li class="case" id="case-{c["num"]}">
  <div class="num">{c["num"]}</div>
  {img}
  <div class="body">
    <h3><a href="{H(c["source_url"])}" rel="noopener">{H(c["name"])}</a>{age} &middot; {H(c["county"])} County</h3>
    <p class="meta">{H(c["charged"])} &middot; {H(c["charges"])} &middot; {H(c["status"])}</p>
    <p class="badges">{badge_status(c)} {badge_comp(c)}</p>
    <p class="sum">{H(c["summary"])}</p>
  </div>
</li>'''

def cand(c):
    ai = c.get("ai") or {}
    verdict = ai.get("formal_2907071")
    vb = ""
    if verdict == "yes": vb = '<span class="badge amber">AI read: formal grooming charge</span>'
    elif verdict == "no": vb = '<span class="badge gray">AI read: grooming described, not charged</span>'
    elif verdict == "unclear": vb = '<span class="badge gray">AI read: unclear</span>'
    elif c.get("formal_hint") is True: vb = '<span class="badge amber">Text pairs grooming with a charge</span>'
    who = ""
    if ai.get("name"):
        bits = [ai["name"]] + ([str(ai["age"])] if ai.get("age") else []) + ([f'{ai["county"]} County'] if ai.get("county") else [])
        who = f'<p class="meta">{H(", ".join(bits))}' + (f' &middot; {H(ai["charges"])}' if ai.get("charges") else "") + '</p>'
    when = (c.get("published") or c.get("found_at") or "")[:10]
    return f'''<li class="cand">
  <h3><a href="{H(c["url"])}" rel="noopener">{H(c["title"])}</a></h3>
  <p class="meta">{H(c.get("source",""))} &middot; {H(when)}</p>
  {who}
  <p class="badges">{vb}</p>
  {('<p class="sum">'+H(ai["one_sentence"])+'</p>') if ai.get("one_sentence") else ''}
</li>'''

def exrow(e):
    return f'<li><a href="{H(e["source_url"])}" rel="noopener">{H(e["name"])}</a>, {H(e["age"])}, {H(e["county"])} County: {H(e["charges"])}. {H(e["why"])}</li>'

cands_html = "\n".join(cand(c) for c in candidates[:40]) if candidates else '<li class="empty">Nothing new since the last sweep.</li>'
cov_html = "\n".join(f'<li><a href="{H(c["url"])}" rel="noopener">{H(c["title"])}</a> <span class="meta">{H(c.get("source",""))}, {H((c.get("published") or "")[:10])}, on {H(c["matches"])}</span></li>' for c in coverage[:40])

page = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="icon" type="image/x-icon" href="/img/c2e3b450f67cc23d729637b56ec75c23.png">
<title>Charged With Grooming in Ohio &middot; Chris Graham</title>
<meta name="description" content="Every Ohioan criminally charged under Ohio's new grooming law, ORC 2907.071, with a source on every case. Updated automatically.">
<meta property="og:type" content="website">
<meta property="og:url" content="https://chrisgraham.com/grooming">
<meta property="og:title" content="Charged With Grooming in Ohio: {n} cases, every one sourced">
<meta property="og:description" content="A running public record of every person charged under Ohio's grooming statute, ORC 2907.071. In {with_comp} of {n} cases the grooming count sits beside other child-abuse charges.">
<meta property="og:image" content="https://chrisgraham.com/grooming/img/ohio_map.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css?family=EB+Garamond:regular,bold,500|Open+Sans:regular,bold,500|">
<style>
:root {{ --purple:#a686c8; --lavender:rgb(193,151,238); --ink:#000; --paper:#fff; --muted:rgba(255,255,255,.62); --hairline:rgba(255,255,255,.14); --card:#0b0b0b; }}
* {{ box-sizing:border-box; }}
html,body {{ margin:0; padding:0; background:var(--ink); color:var(--paper); }}
body {{ font-family:'EB Garamond',Georgia,serif; font-size:20px; line-height:1.55; -webkit-font-smoothing:antialiased; }}
.wrap {{ width:100%; max-width:860px; margin:0 auto; padding:0 24px; }}
a {{ color:var(--lavender); }}
.hero {{ padding:110px 0 10px; }}
.eyebrow {{ font-family:'Open Sans',Helvetica,Arial,sans-serif; font-size:12px; letter-spacing:.18em; text-transform:uppercase; color:var(--muted); margin:0 0 20px; }}
h1 {{ font-size:clamp(34px,6vw,56px); font-weight:400; line-height:1.12; margin:0 0 20px; text-wrap:balance; }}
h2 {{ font-size:clamp(26px,4vw,34px); font-weight:400; line-height:1.2; margin:0 0 18px; text-wrap:balance; }}
h3 {{ font-size:22px; font-weight:500; margin:0 0 4px; line-height:1.25; }}
p {{ margin:0 0 18px; }}
.lede {{ color:var(--muted); }}
section {{ padding:48px 0; border-top:1px solid var(--hairline); }}
section:first-of-type {{ border-top:0; }}
.tiles {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(170px,1fr)); gap:12px; margin:26px 0 10px; }}
.tile {{ border:1px solid var(--hairline); border-radius:4px; padding:16px 16px 12px; background:var(--card); }}
.tile .n {{ font-size:44px; line-height:1; margin:0 0 6px; }}
.tile .l {{ font-family:'Open Sans',Helvetica,Arial,sans-serif; font-size:12px; letter-spacing:.1em; text-transform:uppercase; color:var(--muted); margin:0; }}
.stamp {{ font-family:'Open Sans',Helvetica,Arial,sans-serif; font-size:12px; color:var(--muted); margin:8px 0 0; }}
.cases {{ list-style:none; margin:0; padding:0; }}
.case {{ display:grid; grid-template-columns:34px 96px 1fr; gap:14px; padding:18px 0; border-top:1px solid var(--hairline); align-items:start; }}
.case .num {{ color:var(--muted); font-size:18px; padding-top:4px; }}
.case img, .noimg {{ width:96px; height:96px; object-fit:cover; border-radius:3px; background:#1a1a1a; filter:grayscale(100%); }}
.case .meta, .cand .meta {{ color:var(--muted); font-size:17px; margin:0 0 6px; }}
.case .sum {{ margin:0; font-size:18px; }}
.badges {{ margin:0 0 8px; display:flex; flex-wrap:wrap; gap:6px; }}
.badge {{ display:inline-block; font-family:'Open Sans',Helvetica,Arial,sans-serif; font-size:11px; letter-spacing:.08em; text-transform:uppercase; padding:4px 8px; border-radius:2px; border:1px solid var(--hairline); color:var(--paper); }}
.badge.red {{ background:#7a1b1b; border-color:#7a1b1b; }}
.badge.blue {{ background:#1d3a6b; border-color:#1d3a6b; }}
.badge.amber {{ background:#7a5a12; border-color:#7a5a12; }}
.badge.gray {{ color:var(--muted); }}
.badge.dark {{ background:#222; }}
.map {{ display:block; width:100%; height:auto; border-radius:4px; border:1px solid var(--hairline); margin:10px 0 12px; }}
.cap {{ color:var(--muted); font-size:16px; }}
table {{ width:100%; border-collapse:collapse; font-size:18px; margin:6px 0 18px; }}
th,td {{ text-align:left; padding:8px 10px; border-top:1px solid var(--hairline); vertical-align:top; }}
th {{ font-family:'Open Sans',Helvetica,Arial,sans-serif; font-size:12px; letter-spacing:.1em; text-transform:uppercase; color:var(--muted); font-weight:500; }}
td.n {{ text-align:right; white-space:nowrap; }}
.cands {{ list-style:none; margin:0; padding:0; }}
.cand {{ padding:16px 0; border-top:1px solid var(--hairline); }}
.cand h3 {{ font-size:20px; }}
.empty {{ color:var(--muted); padding:12px 0; }}
.ex {{ margin:0; padding-left:20px; }}
.ex li {{ margin:0 0 10px; font-size:18px; }}
.covh {{ margin:28px 0 10px; font-size:20px; color:var(--muted); font-weight:400; }}
.cov li {{ font-size:17px; }} .cov .meta {{ color:var(--muted); font-size:15px; }}
.btns {{ display:flex; flex-wrap:wrap; gap:12px; margin-top:8px; }}
.btn {{ display:inline-block; font-family:'Open Sans',Helvetica,Arial,sans-serif; font-size:13px; letter-spacing:.14em; text-transform:uppercase; color:#14031f; background:var(--lavender); padding:14px 28px; border-radius:2px; text-decoration:none; }}
.btn.ghost {{ background:transparent; color:var(--lavender); border:1px solid var(--lavender); }}
.site-footer {{ padding:40px 0 70px; border-top:1px solid var(--hairline); font-family:'Open Sans',Helvetica,Arial,sans-serif; font-size:13px; color:var(--muted); }}
.site-footer a {{ color:var(--muted); }}
@media (max-width:560px) {{ .case {{ grid-template-columns:26px 72px 1fr; gap:10px; }} .case img,.noimg {{ width:72px; height:72px; }} body {{ font-size:18px; }} }}
</style>
</head>
<body>
<main>
<section class="hero wrap">
  <p class="eyebrow">A public record, kept current by a crawler</p>
  <h1>Charged With Grooming in Ohio</h1>
  <p class="lede">Every Ohioan criminally charged under Ohio's new grooming law, <a href="https://codes.ohio.gov/ohio-revised-code/section-2907.071" rel="noopener">ORC 2907.071</a>, with a source on every case. Ohio made grooming its own crime with <a href="https://www.legislature.ohio.gov/legislation/135/hb322" rel="noopener">House Bill 322</a>, signed January 8, 2025 and in force April 9, 2025. Before that date nobody could be charged with grooming by name, so this page counts only people carrying the actual charge.</p>
  <div class="tiles">
    <div class="tile"><p class="n">{n}</p><p class="l">Charged with grooming</p></div>
    <div class="tile"><p class="n">{len(resolved)}</p><p class="l">Convicted or pleaded</p></div>
    <div class="tile"><p class="n">{with_comp} of {n}</p><p class="l">Also face other child-abuse charges</p></div>
    <div class="tile"><p class="n">{len(open_cases)}</p><p class="l">Open cases, presumed innocent</p></div>
  </div>
  <p class="stamp">Page built {built}.{(" Last news sweep " + last_sweep + ".") if last_sweep else ""} The crawler runs every six hours. Count as of the latest confirmed case.</p>
</section>

<section class="wrap" id="bigger-win">
  <h2>{"Grooming has not stood alone once" if not alone else ("Grooming has stood alone only once" if len(alone) == 1 else f"Grooming stands alone in only {len(alone)} cases")}</h2>
  <p>In {with_comp} of {n} cases the grooming count sits beside other child-abuse charges. The grooming statute is working as a door: the pattern-of-conduct charge gets investigators into a case that then surfaces the abuse itself. Grooming convictions matter. A grooming charge that delivers rape, sexual battery, or abuse-material convictions matters more, and that is the pattern so far.</p>
  <table>
    <tr><th>Companion charges beside grooming</th><th>Cases</th><th>Who</th></tr>
    <tr><td>Hands-on abuse (rape, sexual battery, gross sexual imposition, unlawful sexual conduct)</td><td class="n">{len(hands)}</td><td>{H(", ".join(lastname(c) for c in hands))}</td></tr>
    <tr><td>Exploitation (abuse material, pandering, importuning, trafficking, hidden camera)</td><td class="n">{len(expl)}</td><td>{H(", ".join(lastname(c) for c in expl))}</td></tr>
    <tr><td>Unspecified child sex felonies</td><td class="n">{len(unspec)}</td><td>{H(", ".join(c["name"].split()[-1] for c in unspec))}</td></tr>
    <tr><td>Grooming only</td><td class="n">{len(alone)}</td><td>{H(", ".join(lastname(c) for c in alone)) or "none"}</td></tr>
  </table>
  <p>Resolved so far: {H("; ".join(f'{c["name"]} ({c["status"].lower()})' for c in resolved))}.</p>
</section>

<section class="wrap" id="map">
  <h2>Where the cases were brought</h2>
  <img class="map" src="img/ohio_map.png" alt="Map of Ohio counties with numbered arrest locations" width="1200" height="1100" loading="lazy">
  <p class="cap">Numbers match the case list. Red is convicted or pleaded guilty. Blue is pending. Leading counties: {H(", ".join(f"{k} ({v})" for k,v in top_counties))}. The cluster in southwest Ohio most likely reflects which prosecutors moved fastest to use the new statute, not where grooming happens.</p>
</section>

<section class="wrap" id="cases">
  <h2>The {n} cases</h2>
  <p class="lede">One sentence each. Click a name to open the source story. Every open case is an allegation; the person is presumed innocent unless and until proven guilty.</p>
  <ul class="cases">
{chr(10).join(card(c) for c in cases)}
  </ul>
</section>

<section class="wrap" id="new">
  <h2>Newly found, awaiting verification</h2>
  <p class="lede">Stories the crawler found that pair the word grooming with a charge, arrest, indictment, plea, or sentence in Ohio. They are not counted above until a person reads the source and confirms a formal ORC 2907.071 count.</p>
  <ul class="cands">
{cands_html}
  </ul>
  {('<h3 class="covh">More coverage of listed cases</h3><ul class="ex cov">' + cov_html + '</ul>') if coverage else ''}
</section>

<section class="wrap" id="not-counted">
  <h2>Grooming described, not charged</h2>
  <p class="lede">The word appears in coverage, but no formal grooming count is confirmed, usually because the conduct predates the April 2025 law or the case was charged under other statutes. Not counted.</p>
  <ul class="ex">
{chr(10).join(exrow(e) for e in excluded)}
  </ul>
</section>

<section class="wrap" id="timing">
  <h2>The law is being applied backwards</h2>
  <p>No one was charged in the gap between signing and the effective date. But prosecutors have charged grooming for conduct that predates the statute: James Blair's grooming counts cover abuse reportedly beginning in 2018, and David Souza's cover 2024. Charging a brand-new offense for earlier conduct raises an ex post facto problem under both the Ohio and United States Constitutions. No defense challenge or appellate ruling has tested it yet.</p>
  <p>The Bethel police chief shows the line. Chad Essert was indicted on 70 felony counts in June 2026 and prosecutors say he began grooming the alleged victim at age 12, yet he was not charged with grooming: the alleged conduct ran from 2005 to 2010, fifteen years before the statute existed.</p>
</section>

<section class="wrap" id="method">
  <h2>How this page is kept</h2>
  <p>There is no official statewide tally of grooming charges, so this is a case-by-case sweep of news and prosecutor releases. Every six hours a crawler searches news feeds for Ohio stories pairing grooming with a charge, drops anything already listed, reads each new story, and posts what passes to the lane above. A person confirms each case before it joins the count. Big multi-agency stings (Operation Next Door, Operation Guardians' Watch, Operation Lifeboat) produced solicitation and importuning counts, not grooming, and are not listed.</p>
  <p>Corrections and additions: <a href="/">contact Chris Graham</a>. The research brief behind this page is a Fugio Consulting document.</p>
  <div class="btns">
    <a class="btn ghost" href="Charged-With-Grooming-in-Ohio-Fugio-Consulting-LLC.pdf">Read the brief (PDF)</a>
    <a class="btn ghost" href="cases.json">Data (JSON)</a>
    <a class="btn ghost" href="https://petethepigeon.com">Ask Pete about a bill</a>
  </div>
</section>
</main>
<footer class="site-footer">
  <div class="wrap">&copy; {datetime.date.today().year} Fugio Consulting, LLC. All Rights Reserved. &middot; Prepared by Chris Graham &amp; StatehouseAI &middot; <a href="/">chrisgraham.com</a></div>
</footer>
<script src="/assets/site-nav.js"></script>
</body>
</html>
'''
open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(page)
print(f"built {OUT}/index.html: {n} cases, {len(candidates)} candidates")
