#!/usr/bin/env python3
"""Find new Ohio grooming-charge stories, judge them, and add the ones that pass to cases.csv.
Stdlib only. Run: python3 scripts/grooming/crawl.py
With ANTHROPIC_API_KEY set, a Claude model reads each new story (and every queued story it has not
read yet) and returns a verdict plus the row fields. A story is appended to cases.csv only when the
model says "promote" AND the code checks pass: a named person, an Ohio county, a formal ORC 2907.071
count (charged, indicted, pleaded or convicted), a reputable source, and the name and the word
grooming both in the story text. Anything unsure stays queued in candidates.json; it is never promoted.
No person reviews cases. AI calls are capped per run (MAX_AI)."""
import csv, json, os, re, sys, hashlib, html, datetime, urllib.request, urllib.parse, urllib.error, ssl, time
import xml.etree.ElementTree as ET
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
D = os.path.join(ROOT, "data", "grooming")
UA = "Mozilla/5.0 (compatible; chrisgraham.com grooming tracker; +https://chrisgraham.com/grooming)"
MAX_AI = int(os.environ.get("GROOMING_MAX_AI", "60"))
MODEL = os.environ.get("GROOMING_MODEL", "claude-sonnet-5-5")
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
GROOM = re.compile(r"\bgroom", re.I)
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
API_DEAD = False   # set when the key is rejected, so one bad key does not burn the whole budget on 401s

def get(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
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

def ai_read(text, title, url):
    """Ask Claude for a verdict and the cases.csv fields. Returns a dict, or None if no key / the call failed."""
    global API_DEAD
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key or API_DEAD: return None
    prompt = ("You judge news stories for a public tracker of people charged under Ohio's grooming statute, ORC 2907.071 "
              "(HB 322, effective April 9, 2025). Real people are named, so be strict.\n"
              "verdict rules:\n"
              "- \"promote\": the story names one person and says, as fact, that this person was charged, indicted, pleaded guilty or was "
              "convicted on a grooming count in an Ohio court. Formal count only: words like \"groomed\" or \"a grooming pattern\" "
              "describing behavior are not enough, and neither are \"grooming-related offenses\".\n"
              "- \"reject\": not Ohio, not a person (pet grooming, etc.), federal charges only, other statutes only, or grooming is "
              "only descriptive. Also reject sting roundups with no grooming count.\n"
              "- \"unsure\": anything else, including a story that is truncated, paywalled, or names more than one possible defendant.\n"
              "When in doubt, say unsure. Never guess a field; use null.\n"
              "Answer with JSON only, keys: verdict, reason (one short line), name (full name as printed), age (int or null), "
              "city (or null), county (Ohio county name without the word County, or null), charged (month and year of the charge "
              "or indictment like \"Oct 2026\", or null), charges (short list with grooming first, e.g. \"Grooming, 2 sexual battery\"), "
              "companion (\"hands-on\" if rape, sexual battery, gross sexual imposition or unlawful sexual conduct is charged; "
              "\"exploitation\" if abuse material, pandering, importuning, trafficking or voyeurism; \"none\" if grooming alone; "
              "else \"unspecified\"), status (short, e.g. \"Pending, pleaded not guilty\"), resolved (\"convicted\", "
              "\"pleaded guilty\", \"plea on other counts\", \"dismissed\", or \"\" if open), "
              "summary (one neutral sentence under 45 words: who, age, town, county, month, the charges; for open cases say "
              "\"was charged\" or \"was indicted\", never imply guilt).\n\n"
              f"TITLE: {title}\nURL: {url}\nTEXT:\n{text[:14000]}")
    body = json.dumps({"model": MODEL, "max_tokens": 700, "messages": [{"role": "user", "content": prompt}]}).encode()
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=body, headers={
        "content-type": "application/json", "x-api-key": key, "anthropic-version": "2023-06-01", "User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=90, context=CTX) as r:
            resp = json.loads(r.read())
        txt = "".join(b.get("text", "") for b in resp.get("content", []))
        m = re.search(r"\{.*\}", txt, re.S)
        return json.loads(m.group(0)) if m else None
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            API_DEAD = True
            print(f"::error::Anthropic API returned {e.code}: the ANTHROPIC_API_KEY secret is invalid. Reset it with "
                  "gh secret set ANTHROPIC_API_KEY --repo fugioconsulting/chrisgraham.com", file=sys.stderr)
        else: print("  ai error:", e.code, e.read()[:300], file=sys.stderr)
        return None
    except Exception as e:
        print("  ai error:", e, file=sys.stderr); return None

def norm_name(n): return re.sub(r"[^a-z ]+", "", re.sub(r"\b(jr|sr|ii|iii|iv)\b\.?", "", (n or "").lower())).split()

def same_person(name, county, row):
    """True when this name is already on the list as row (same first and last name, or same last name in the same county)."""
    x, y = norm_name(name), norm_name(row["name"])
    if not x or not y: return False
    return (x[0] == y[0] and x[-1] == y[-1]) or (x[-1] == y[-1] and bool(county) and county.lower() == row.get("county", "").lower())

def passes(ai, text, url, cases):
    """The code half of the rules. Returns (ok, reason). The model's 'promote' is necessary, never sufficient."""
    if not ai or ai.get("verdict") != "promote": return False, "model did not say promote"
    name = (ai.get("name") or "").strip()
    if len(norm_name(name)) < 2: return False, "no full name"
    county = (ai.get("county") or "").replace("County", "").strip().title()
    if county.lower() not in COUNTIES and county.lower() != "van wert": return False, f"county not in Ohio: {county!r}"
    host = urllib.parse.urlparse(url).netloc.lower()
    if any(b in host for b in UNREPUTABLE): return False, f"source not reputable: {host}"
    low = text.lower()
    if norm_name(name)[-1] not in low: return False, "name not in story text"
    if not GROOM.search(text): return False, "grooming not in story text"
    if not FORMAL.search(text): return False, "no formal grooming wording"
    if not ai.get("charges") or "groom" not in ai["charges"].lower(): return False, "charges do not list grooming"
    if any(same_person(name, county, c) for c in cases): return False, "already listed"
    return True, ""

def promote(ai, url, cases, cols, centroids):
    county = ai["county"].replace("County", "").strip().title()
    lat, lon = centroids.get(county, ["", ""])
    row = {k: "" for k in cols}
    row.update(num=str(max([int(c["num"]) for c in cases] + [0]) + 1), name=ai["name"].strip(), age=str(ai.get("age") or ""),
               city=ai.get("city") or "", county=county, charged=ai.get("charged") or "", charges=ai["charges"],
               companion=ai.get("companion") if ai.get("companion") in ("hands-on", "exploitation", "none", "unspecified") else "unspecified",
               status=ai.get("status") or "Pending",
               resolved=ai.get("resolved") if ai.get("resolved") in ("convicted", "pleaded guilty", "plea on other counts", "dismissed") else "",
               source_url=url, thumb="", aka=norm_name(ai["name"])[-1], summary=ai.get("summary") or "", lat=str(lat), lon=str(lon))
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

def main():
    cases_path = os.path.join(D, "cases.csv")
    with open(cases_path, encoding="utf-8") as f:
        rd = csv.DictReader(f); cols = rd.fieldnames; cases = list(rd)
    excluded = list(csv.DictReader(open(os.path.join(D, "excluded.csv"), encoding="utf-8")))
    centroids = json.load(open(os.path.join(D, "county_centroids.json")))
    dismissed = {l.split("#")[0].strip() for l in open(os.path.join(D, "dismissed.txt")) if l.split("#")[0].strip()}
    def known_urls(): return {c["source_url"].rstrip("/") for c in cases} | {e["source_url"].rstrip("/") for e in excluded}
    # A story is about a listed person when it has their first and last name, their last name plus their town or county,
    # or one of their multi-word aka phrases. A bare surname like "Arthur" or "Hammer" would swallow stories about new people.
    def listed(blob):
        b = " " + " ".join(norm_name(blob)) + " "
        for c in cases + excluded:
            n = norm_name(c["name"])
            places = [p for p in (c.get("city", ""), c.get("county", "")) if p]
            if f" {n[0]} {n[-1]} " in b or (f" {n[-1]} " in b and any(f" {' '.join(norm_name(p))} " in b for p in places)) \
               or any(" " in a.strip() and f" {' '.join(norm_name(a))} " in b for a in (c.get("aka") or "").split(";")):
                return c["name"]
        return None
    try: cands = json.load(open(os.path.join(D, "candidates.json")))
    except Exception: cands = []
    try: seen = json.load(open(os.path.join(D, "seen.json")))
    except Exception: seen = {}
    by_id = {c["id"]: c for c in cands}
    budget = [MAX_AI]
    added, found = [], 0

    def judge(c):
        """Fetch, read, and either promote, drop, or keep queued. Returns the new status."""
        url = c["url"]
        if "news.google.com" in url:
            real = resolve_google(c)
            if real: c["url"] = url = real
        if url.rstrip("/") in known_urls(): return "known"
        who = listed(c["title"] + " " + c.get("snippet", ""))
        if who: c["matches"] = who; return "coverage"
        if "news.google.com" in url or budget[0] <= 0 or not os.environ.get("ANTHROPIC_API_KEY") or API_DEAD: return "new"
        try: text = strip_html(get(url).decode("utf-8", "ignore"))
        except Exception as e:
            print(f"  fetch failed {url}: {e}", file=sys.stderr); return "new"
        c["formal_hint"] = bool(FORMAL.search(text)) and bool(OHIO.search(text))
        ai = ai_read(text, c["title"], url); budget[0] -= 1; time.sleep(1)
        if ai is None: return "new"
        c["ai"] = ai
        if ai.get("name") and any(same_person(ai["name"], (ai.get("county") or "").replace("County", "").strip(), x) for x in cases + excluded):
            c["matches"] = ai["name"]; return "coverage"
        ok, why = passes(ai, text, url, cases)
        c["why"] = why
        if ok:
            row = promote(ai, url, cases, cols, centroids); added.append(row)
            print(f"  PROMOTED #{row['num']} {row['name']} ({row['county']}) <- {url}")
            return "promoted"
        if ai.get("verdict") == "reject": return "rejected"
        return "new"   # unsure, or the model said promote but a code check failed: stay queued, never promote

    def settle(c, status):
        if status in ("promoted", "known", "coverage", "rejected"):
            by_id.pop(c["id"], None)
            seen[c["id"]] = {"url": c["url"], "title": c["title"], "first_seen": c.get("found_at") or NOW.isoformat(),
                             "reason": status + (f": {c.get('matches')}" if status == "coverage" else "") +
                                       (f": {(c.get('ai') or {}).get('reason', '')}" if status == "rejected" else "")}
        else:
            c["status"] = "new"; by_id[c["id"]] = c

    # 1. re-judge everything already queued that the model has not read yet
    for c in list(by_id.values()):
        if c["id"] in dismissed or c["url"].rstrip("/") in dismissed: by_id.pop(c["id"]); continue
        if c.get("ai") is None or c.get("status") == "coverage": settle(c, judge(c))
    # 2. sweep the feeds
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
                 "found_at": NOW.strftime("%Y-%m-%d"), "snippet": it["snippet"][:300], "formal_hint": None, "ai": None,
                 "status": "new", "matches": None}
            st = judge(c); settle(c, st); found += 1
            print(f"+ {it['title']} [{it['source']}] -> {st}")
    if added:
        with open(cases_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(cases)
    cands = sorted(by_id.values(), key=lambda c: (c.get("published") or c.get("found_at") or ""), reverse=True)[:200]
    json.dump(cands, open(os.path.join(D, "candidates.json"), "w"), indent=1)
    json.dump(seen, open(os.path.join(D, "seen.json"), "w"), indent=0)
    open(os.path.join(D, "last_sweep.txt"), "w").write(NOW.strftime("%Y-%m-%d %H:%M UTC"))
    print(f"sweep done: {found} new stories, {len(added)} promoted to cases.csv, {len(cands)} still queued, "
          f"{MAX_AI - budget[0]} AI reads, {len(seen)} seen" + (" (API key rejected)" if API_DEAD else ""))

if __name__ == "__main__":
    main()
