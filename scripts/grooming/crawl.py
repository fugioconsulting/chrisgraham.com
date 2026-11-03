#!/usr/bin/env python3
"""Find new Ohio grooming-charge stories and queue them, then apply the judge's verdicts. Stdlib only, no paid API.
  python3 scripts/grooming/crawl.py               sweep the news feeds (GitHub Actions, daily at 5am ET)
  python3 scripts/grooming/crawl.py --apply FILE  apply the verdicts the Claude scheduled task on Chris's Mac wrote (JUDGE.md)
The sweep drops stories about people already listed and queues the rest in candidates.json. --apply appends a candidate to
cases.csv only when the judge said promote AND the code checks pass: a named person, an Ohio county, a reputable source, a
verbatim quote naming the person and the grooming count, and not already listed. Rejects and coverage go to seen.json; anything
unsure stays queued and is judged again next morning. No person reviews cases."""
import csv, json, os, re, sys, hashlib, html, datetime, urllib.request, urllib.parse, urllib.error, ssl, time
import xml.etree.ElementTree as ET
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
D = os.path.join(ROOT, "data", "grooming")
UA = "Mozilla/5.0 (compatible; chrisgraham.com grooming tracker; +https://chrisgraham.com/grooming)"
NOW = datetime.datetime.now(datetime.timezone.utc)
CTX = ssl.create_default_context()

QUERIES = [
    '"charged with grooming" Ohio',
    '"grooming" indicted Ohio',
    '"grooming" "grand jury" Ohio',
    '"grooming" arrested Ohio county',
    '"2907.071"',
    '"counts of grooming" Ohio',
    '"grooming charge" Ohio',
]
FEEDS = []
for q in QUERIES:
    e = urllib.parse.quote(q)
    FEEDS.append(("bing", f"https://www.bing.com/news/search?q={e}&format=rss"))
    FEEDS.append(("google", f"https://news.google.com/rss/search?q={e}&hl=en-US&gl=US&ceid=US:en"))

COUNTIES = """adams allen ashland ashtabula athens auglaize belmont brown butler carroll champaign clark clermont clinton
columbiana coshocton crawford cuyahoga darke defiance delaware erie fairfield fayette franklin fulton gallia geauga greene
guernsey hamilton hancock hardin harrison henry highland hocking holmes huron jackson jefferson knox lake lawrence licking
logan lorain lucas madison mahoning marion medina meigs mercer miami monroe montgomery morgan morrow muskingum noble ottawa
paulding perry pickaway pike portage preble putnam richland ross sandusky scioto seneca shelby stark summit trumbull
tuscarawas union van wert vinton warren washington wayne williams wood wyandot""".split()
CITIES = ["columbus","cleveland","cincinnati","toledo","akron","dayton","youngstown","lorain","elyria","bowling green",
          "mansfield","marysville","westerville","parma","kettering","cuyahoga falls","beavercreek","strongsville","findlay",
          "huber heights","grove city","reynoldsburg","upper arlington","gahanna","westlake","north olmsted","fairborn","massillon",
          "north royalton","garfield heights","zanesville","chillicothe","sandusky","portsmouth","steubenville","xenia","wooster",
          "piqua","tiffin","fremont","bucyrus","celina","deshler","marietta","mcconnelsville","pomeroy","gallipolis","circleville",
          "new lexington","austintown","boardman","canfield","brookfield","cortland","willoughby","wickliffe","oberlin","vermilion",
          "norwalk","port clinton","perrysburg","maumee","sylvania","fostoria","upper sandusky","wapakoneta","minster","germantown",
          "miamisburg","centerville","springboro","new philadelphia","coshocton","bellefontaine","ashtabula","painesville","chardon",
          "van wert","paulding","kenton","wauseon","lima","eaton","batavia","whitewater township","claridon","jackson township"]
CHARGE_WORDS = re.compile(r"\b(charg|indict|arrest|plead|guilty|sentenc|count|convict|bond|jail)", re.I)
COUNTY_SET = {c for c in COUNTIES if c not in ("van", "wert")} | {"van wert"}
GROOM = re.compile(r"\bgroom", re.I)
# What the judge's quote must say: grooming as the object of a charge, plea or conviction, or the statute number. "Groomed" never counts.
EVIDENCE_FORMAL = re.compile(r"\b(charged with|charges? of|counts? of|indicted (on|for)|plead(ed|s)? (guilty|no contest) to|convicted of|found guilty of|sentenced (on|for))\b[^.;]{0,120}\bgrooming\b"
                             r"|\bgrooming,? an? (first|second|third|fourth|fifth)[- ]degree (felony|misdemeanor)|\b2907\.071", re.I)
ELSEWHERE = re.compile(r"\b(kentucky|ky\.|indiana|ind\.|illinois|ill\.|michigan|mich\.|pennsylvania|pa\.|west virginia|w\.va\.|krs|federal|u\.s\. (district|attorney))", re.I)
BROWSER_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
FORMAL = re.compile(r"(charged with|counts? of|charge of|indicted (on|for)|plead(ed|s)? guilty to|convicted of|found guilty of)[^.]{0,140}\bgrooming\b|\bgrooming\b[^.]{0,80}\b(charge|count|indictment|felony|misdemeanor)|2907\.071", re.I)
# Ohio gate: the word Ohio, or an Ohio county name followed by "county" paired with the word Ohio elsewhere, or a known Ohio city.
OHIO = re.compile(r"\bohio\b|\b(" + "|".join(re.escape(c) for c in CITIES) + r")\b", re.I)
OHIO_COUNTY = re.compile(r"\b(" + "|".join(COUNTIES) + r")\s+(county|co\.)", re.I)
OHIO_OUTLETS = ("wcpo","fox19","wlwt","local12","wkrc","wxix","nbc4i","10tv","abc6","myfox28","wbns","wsyx","dispatch.com","cleveland.com",
  "fox8","wkyc","news5cleveland","wews","wkbn","wfmj","wtol","13abc","wtvg","wdtn","whio","dayton247now","daytondailynews","journal-news",
  "sent-trib","bgindependentmedia","richlandsource","mansfieldnewsjournal","geaugamapleleaf","clermontsun","hcpros.org","clermontprosecutor",
  "tiffinohio","northwestsignal","dailyadvocate","record-courier","cantonrep","the-daily-record","timesreporter","newarkadvocate",
  "lancastereaglegazette","chillicothegazette","marionstar","the-news-herald","morningjournal","chroniclet","news-herald","vindy","tribtoday",
  "limaohio","crescent-news","thecourier","advertiser-tribune","sanduskyregister","norwalkreflector","star-beacon","zanesvilletimesrecorder",
  "marysvillematters","delgazette","thisweeknews","ohiocapitaljournal","statenews","wosu","ideastream","wyso","wcbe","wvxu")

# Never promote from these: social posts, forums, mugshot and people-search sites, press-release mills.
UNREPUTABLE = ("facebook.com", "instagram.com", "tiktok.com", "x.com", "twitter.com", "reddit.com", "youtube.com", "nextdoor.com",
  "mugshot", "bustednewspaper", "arrests.org", "jailbase", "recentlybooked", "headtopics", "newsbreak.com", "einpresswire", "prnewswire",
  "medium.com", "substack.com", "blogspot", "wordpress.com", "news.google.com")

def get(url, timeout=20, ua=UA):
    req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
        return r.read()

def strip_html(s):
    s = re.sub(r"<script.*?</script>|<style.*?</style>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", html.unescape(s)).strip()

def parse_feed(kind, raw):
    out = []
    try: root = ET.fromstring(raw)
    except ET.ParseError: return out
    for it in root.iter("item"):
        t = (it.findtext("title") or "").strip()
        link = (it.findtext("link") or "").strip()
        desc = strip_html(it.findtext("description") or "")
        pub = (it.findtext("pubDate") or "").strip()
        src = ""
        s = it.find("source")
        if s is not None: src = (s.text or "").strip() or s.get("url", "")
        if kind == "bing":
            m = re.search(r"[?&]url=([^&]+)", link)
            if m: link = urllib.parse.unquote(m.group(1))
            if not src:
                m2 = re.search(r"^(.*?) - ", t)
        if kind == "google" and " - " in t and not src:
            t, src = t.rsplit(" - ", 1)
        if not src:
            try: src = urllib.parse.urlparse(link).netloc.replace("www.", "")
            except Exception: pass
        out.append({"title": t, "url": link, "snippet": desc, "published_raw": pub, "source": src, "feed": kind})
    return out

def iso(pub):
    for fmt in ("%a, %d %b %Y %H:%M:%S %Z", "%a, %d %b %Y %H:%M:%S %z"):
        try: return datetime.datetime.strptime(pub, fmt).strftime("%Y-%m-%d")
        except Exception: pass
    return ""

def norm_title(t): return re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()
def cid(url, title): return hashlib.sha1((url.rstrip("/") + "|" + norm_title(title)).encode()).hexdigest()[:12]

def norm_name(n): return re.sub(r"[^a-z ]+", "", re.sub(r"\b(jr|sr|ii|iii|iv)\b\.?", "", (n or "").lower())).split()

def flat(t): return " " + " ".join(re.sub(r"[^a-z0-9]+", " ", (t or "").lower()).split()) + " "

def same_person(name, county, row):
    """'same' when first and last name match a row; 'maybe' when only the last name matches in the same county; else None."""
    x, y = norm_name(name), norm_name(row["name"])
    if not x or not y or x[-1] != y[-1]: return None
    if x[0] == y[0]: return "same"
    return "maybe" if county and county.lower() == (row.get("county") or "").lower() else None

def page_has_name(name, text):
    """First name, then up to two middle names or initials, then last name."""
    n = norm_name(name)
    return bool(re.search(rf"\b{re.escape(n[0])}\b(\s+\w+){{0,2}}\s+{re.escape(n[-1])}\b", " ".join(norm_name(text))))

def passes(v, text, url, cases, excluded):
    """The code half of the rules. The judge's 'promote' is necessary, never sufficient. text is the page the code itself fetched.
    Returns (ok, reason, route): route 'coverage' when the person or source is already listed, else 'hold' (stays queued)."""
    if v.get("verdict") != "promote": return False, "judge did not say promote", "hold"
    name = (v.get("name") or "").strip(); n = norm_name(name)
    if len(n) < 2: return False, "no full name", "hold"
    county = (v.get("county") or "").replace("County", "").strip()
    if county.lower() not in COUNTY_SET: return False, f"county not in Ohio: {county!r}", "hold"
    host = urllib.parse.urlparse(url).netloc.lower()
    if not host or any(b in host for b in UNREPUTABLE): return False, f"source not reputable: {host or url}", "hold"
    if url.rstrip("/") in {r["source_url"].rstrip("/") for r in cases + excluded}: return False, "source already used", "coverage"
    for r in cases:
        m = same_person(name, county, r)
        if m == "same": return False, f"already listed as {r['name']}", "coverage"
        if m == "maybe": return False, f"possible duplicate of {r['name']}; say coverage, or promote by hand after checking", "hold"
    for r in excluded:
        if same_person(name, county, r): return False, f"matches not-counted {r['name']}; excluded.csv decisions are not overridden here", "hold"
    ev = v.get("evidence") or ""
    if not (f" {n[0]} " in flat(ev) and f" {n[-1]} " in flat(ev)): return False, "quote must give first and last name", "hold"
    if not EVIDENCE_FORMAL.search(ev): return False, "quote does not state a formal grooming count", "hold"
    if ELSEWHERE.search(ev): return False, "quote mentions another state or a federal case", "hold"
    if len(text) < 1500: return False, "page not readable by code (blocked or too short); give a readable copy in alt_urls", "hold"
    if flat(ev).strip() not in flat(text): return False, "quote is not on the fetched page", "hold"
    if not page_has_name(name, text): return False, "full name not on the fetched page", "hold"
    if not (re.search(r"\bohio\b", text, re.I) or f" {county.lower()} county " in flat(text)): return False, "page never says Ohio or the county", "hold"
    if "groom" not in (v.get("charges") or "").lower(): return False, "charges do not list grooming", "hold"
    return True, "", ""

def promote(v, url, cases, cols, centroids):
    county = v["county"].replace("County", "").strip().title()
    lat, lon = centroids.get(county, ["", ""])
    thumb = v.get("thumb") or ""
    if thumb and not os.path.exists(os.path.join(ROOT, "docs", "grooming", "img", thumb)): thumb = ""
    row = {k: "" for k in cols}
    row.update(num=str(max([int(c["num"]) for c in cases] + [0]) + 1), name=v["name"].strip(), age=str(v.get("age") or ""),
               city=v.get("city") or "", county=county, charged=v.get("charged") or "", charges=v["charges"],
               companion=v.get("companion") if v.get("companion") in ("hands-on", "exploitation", "none", "unspecified") else "unspecified",
               status=v.get("status") or "Pending",
               resolved=v.get("resolved") if v.get("resolved") in ("convicted", "pleaded guilty", "plea on other counts", "dismissed") else "",
               source_url=url, thumb=thumb, aka=norm_name(v["name"])[-1], summary=v.get("summary") or "", lat=str(lat), lon=str(lon))
    cases.append(row)
    return row

def resolve_google(it):
    """Google News RSS links are opaque redirects. Find the same headline in Bing News, which gives the real URL."""
    q = urllib.parse.quote(f'"{it["title"]}"')
    try:
        for b in parse_feed("bing", get(f"https://www.bing.com/news/search?q={q}&format=rss")):
            if norm_title(b["title"]) == norm_title(it["title"]) and "news.google.com" not in b["url"]: return b["url"]
    except Exception: pass
    return None

def load():
    with open(os.path.join(D, "cases.csv"), encoding="utf-8") as f:
        rd = csv.DictReader(f); cols = rd.fieldnames; cases = list(rd)
    excluded = list(csv.DictReader(open(os.path.join(D, "excluded.csv"), encoding="utf-8")))
    def js(name, empty):   # a missing file is empty; a corrupt one stops the run rather than silently wiping the queue
        p = os.path.join(D, name)
        return json.load(open(p)) if os.path.exists(p) else empty
    cands, seen = js("candidates.json", []), js("seen.json", {})
    dismissed = {l.split("#")[0].strip() for l in open(os.path.join(D, "dismissed.txt")) if l.split("#")[0].strip()}
    return cols, cases, excluded, {c["id"]: c for c in cands}, seen, dismissed

def save(cols, cases, by_id, seen, cases_changed):
    if cases_changed:
        with open(os.path.join(D, "cases.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(cases)
    cands = sorted(by_id.values(), key=lambda c: (c.get("published") or c.get("found_at") or ""), reverse=True)[:200]
    json.dump(cands, open(os.path.join(D, "candidates.json"), "w"), indent=1)
    json.dump(seen, open(os.path.join(D, "seen.json"), "w"), indent=0)
    return cands

def settle(c, status, by_id, seen, note=""):
    if status == "new":
        c["status"] = "new"; by_id[c["id"]] = c; return
    by_id.pop(c["id"], None)
    seen[c["id"]] = {"url": c["url"], "title": c["title"], "first_seen": c.get("found_at") or NOW.isoformat(),
                     "reason": status + (f": {note}" if note else "")}

def listed_in(blob, people):
    """Who a headline is about, as (name, sure). Sure: first and last name, or a curated multi-word aka. Not sure: last name plus
    their town or county; that stays queued with the hint so the judge decides. A bare surname never matches."""
    b = flat(blob); maybe = None
    for c in people:
        n = norm_name(c["name"])
        if page_has_name(c["name"], blob) or any(" " in a.strip() and flat(a) in b for a in (c.get("aka") or "").split(";")):
            return c["name"], True
        places = [p for p in (c.get("city", ""), c.get("county", "")) if p]
        if not maybe and f" {n[-1]} " in b and any(flat(p) in b for p in places): maybe = c["name"]
    return maybe, False

def sweep():
    cols, cases, excluded, by_id, seen, dismissed = load()
    known = {c["source_url"].rstrip("/") for c in cases} | {e["source_url"].rstrip("/") for e in excluded}

    def classify(c):
        if "news.google.com" in c["url"]:
            real = resolve_google(c)
            if real: c["url"] = real
        if c["url"].rstrip("/") in known: return "known", ""
        who, sure = listed_in(c["title"] + " " + c.get("snippet", ""), cases + excluded)
        c["matches"] = who
        if sure: return "coverage", who
        try: c["formal_hint"] = bool(FORMAL.search(strip_html(get(c["url"]).decode("utf-8", "ignore"))))
        except Exception: pass
        return "new", ""

    for c in list(by_id.values()):   # tidy the queue: dismissed ids, and stories that became known since
        if c["id"] in dismissed or c["url"].rstrip("/") in dismissed: by_id.pop(c["id"]); continue
        st, note = classify(c); settle(c, st, by_id, seen, note)
    found = 0
    for kind, furl in FEEDS:
        try: items = parse_feed(kind, get(furl))
        except Exception as e:
            print(f"feed error {kind}: {e}", file=sys.stderr); continue
        for it in items:
            if not it["url"] or not it["title"]: continue
            i = cid(it["url"], it["title"])
            if i in seen or i in by_id or i in dismissed: continue
            blob = it["title"] + " " + it["snippet"]
            reason = None
            pubd = iso(it["published_raw"])
            if pubd and pubd < "2025-04-01": reason = "before the law"
            elif not GROOM.search(blob): reason = "no groom word"
            elif not CHARGE_WORDS.search(blob): reason = "no charge word"
            elif not (OHIO.search(blob) or "ohio" in it["url"].lower()
                      or OHIO_COUNTY.search(blob) and any(o in it["url"].lower() or o in it["source"].lower() for o in OHIO_OUTLETS)
                      or any(o in it["url"].lower() for o in OHIO_OUTLETS)): reason = "not ohio"
            if reason:
                seen[i] = {"url": it["url"], "title": it["title"], "first_seen": NOW.isoformat(), "reason": reason}
                continue
            c = {"id": i, "title": it["title"], "url": it["url"], "source": it["source"], "published": pubd,
                 "found_at": NOW.strftime("%Y-%m-%d"), "snippet": it["snippet"][:300], "formal_hint": None, "status": "new", "matches": None}
            st, note = classify(c); settle(c, st, by_id, seen, note); found += 1
            print(f"+ {it['title']} [{it['source']}] -> {st}")
    cands = save(cols, cases, by_id, seen, False)
    open(os.path.join(D, "last_sweep.txt"), "w").write(NOW.strftime("%Y-%m-%d %H:%M UTC"))
    print(f"sweep done: {found} new stories, {len(cands)} queued for the judge, {len(seen)} seen")

def apply(path):
    """Apply the judge's verdicts (a JSON list, one object per candidate id; format in JUDGE.md)."""
    cols, cases, excluded, by_id, seen, dismissed = load()
    centroids = json.load(open(os.path.join(D, "county_centroids.json")))
    added = []
    for v in json.load(open(path)):
        c = by_id.get(v.get("id"))
        if not c: print(f"  skip {v.get('id')}: not in the queue"); continue
        verdict = v.get("verdict")
        c["judge"] = {"verdict": verdict, "reason": v.get("reason", ""), "on": NOW.strftime("%Y-%m-%d")}
        if verdict == "promote":
            url, text = v.get("url") or c["url"], ""
            for u in [url] + list(v.get("alt_urls") or []):   # the first copy the code itself can read that carries the quote
                if "news.google.com" in u: continue
                try: t = strip_html(get(u, ua=BROWSER_UA).decode("utf-8", "ignore"))
                except Exception as e: print(f"  fetch failed {u}: {e}", file=sys.stderr); continue
                if len(t) >= 1500 and flat(v.get("evidence")).strip() in flat(t): text = t; break
                if not text: text = t
            ok, why, route = passes(v, text, url, cases, excluded)
            if ok:
                c["url"] = url
                row = promote(v, url, cases, cols, centroids); added.append(row)
                settle(c, "promoted", by_id, seen, row["name"])
                print(f"  PROMOTED #{row['num']} {row['name']} ({row['county']}) <- {url}")
            elif route == "coverage":
                settle(c, "coverage", by_id, seen, why); print(f"  COVERAGE {v.get('name')}: {why}")
            else:
                c["judge"]["held"] = why; settle(c, "new", by_id, seen)
                print(f"  HELD {v.get('name')}: {why}")
        elif verdict in ("reject", "coverage"):
            settle(c, "rejected" if verdict == "reject" else "coverage", by_id, seen, v.get("matches") or v.get("reason", ""))
        else:
            settle(c, "new", by_id, seen)
    cands = save(cols, cases, by_id, seen, bool(added))
    print(f"applied: {len(added)} promoted to cases.csv, {len(cands)} still queued")
    return added

if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--apply": apply(sys.argv[2])
    else: sweep()
