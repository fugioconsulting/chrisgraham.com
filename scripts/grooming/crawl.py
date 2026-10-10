#!/usr/bin/env python3
"""Find new Ohio grooming-charge stories and queue them for verification.
Stdlib only. Run: python3 scripts/grooming/crawl.py
Optional: ANTHROPIC_API_KEY in env -> a Claude model reads each new story and
extracts name/age/county/charges + whether the grooming count is formal ORC 2907.071.
AI calls are capped per run (MAX_AI). Nothing here edits cases.csv; a person does that."""
import csv, json, os, re, sys, hashlib, html, datetime, urllib.request, urllib.parse, ssl, time
import xml.etree.ElementTree as ET
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
D = os.path.join(ROOT, "data", "grooming")
UA = "Mozilla/5.0 (compatible; chrisgraham.com grooming tracker; +https://chrisgraham.com/grooming)"
MAX_AI = int(os.environ.get("GROOMING_MAX_AI", "8"))
MODEL = os.environ.get("GROOMING_MODEL", "claude-haiku-5-5")
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
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key: return None
    prompt = ("You are checking an Ohio news story for a grooming-charge tracker. Ohio's grooming offense is ORC 2907.071, "
              "created by HB 322, effective April 9, 2025. Answer in JSON only with keys: name (defendant full name or null), age (int or null), "
              "county (Ohio county where charged, or null), charges (short comma list), formal_2907071 (\"yes\" if the story says the person "
              "was charged, indicted, pleaded or convicted on a grooming count as a crime; \"no\" if grooming is only descriptive or the charges "
              "are other statutes or federal; \"unclear\" otherwise), status (short: pending, pleaded guilty, convicted, sentenced), "
              "one_sentence (one neutral sentence, under 45 words, that says who, where, when, charged with what; say 'allegedly' for open cases).\n\n"
              f"TITLE: {title}\nURL: {url}\nTEXT:\n{text[:12000]}")
    body = json.dumps({"model": MODEL, "max_tokens": 400, "messages": [{"role": "user", "content": prompt}]}).encode()
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=body, headers={
        "content-type": "application/json", "x-api-key": key, "anthropic-version": "2023-06-01", "User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=60, context=CTX) as r:
            resp = json.loads(r.read())
        txt = "".join(b.get("text", "") for b in resp.get("content", []))
        m = re.search(r"\{.*\}", txt, re.S)
        return json.loads(m.group(0)) if m else None
    except Exception as e:
        print("  ai error:", e, file=sys.stderr); return None

def main():
    cases = list(csv.DictReader(open(os.path.join(D, "cases.csv"), encoding="utf-8")))
    excluded = list(csv.DictReader(open(os.path.join(D, "excluded.csv"), encoding="utf-8")))
    known_urls = {c["source_url"].rstrip("/") for c in cases} | {e["source_url"].rstrip("/") for e in excluded}
    # alias -> person: surnames, full names, and the hand-kept "aka" phrases (e.g. "deshler pastor")
    aliases = {}
    for c in cases + excluded:
        last = c["name"].split()[-1].lower()
        if last != "jr." and len(last) > 4: aliases[last] = c["name"]
        aliases[c["name"].lower()] = c["name"]
        for a in (c.get("aka") or "").split(";"):
            if a.strip(): aliases[a.strip().lower()] = c["name"]
    try: cands = json.load(open(os.path.join(D, "candidates.json")))
    except Exception: cands = []
    try: seen = json.load(open(os.path.join(D, "seen.json")))
    except Exception: seen = {}
    by_id = {c["id"]: c for c in cands}
    ai_budget = MAX_AI
    found = 0
    for kind, furl in FEEDS:
        try: items = parse_feed(kind, get(furl))
        except Exception as e:
            print(f"feed error {kind}: {e}", file=sys.stderr); continue
        for it in items:
            if not it["url"] or not it["title"]: continue
            i = cid(it["url"], it["title"])
            if i in seen or i in by_id: continue
            blob = it["title"] + " " + it["snippet"]
            reason = None
            pubd = iso(it["published_raw"])
            if pubd and pubd < "2025-04-01": reason = "before the law"
            elif not GROOM.search(blob): reason = "no groom word"
            elif not CHARGE_WORDS.search(blob): reason = "no charge word"
            elif not (OHIO.search(blob) or "ohio" in it["url"].lower()
                      or OHIO_COUNTY.search(blob) and any(o in it["url"].lower() or o in it["source"].lower() for o in OHIO_OUTLETS)
                      or any(o in it["url"].lower() for o in OHIO_OUTLETS)): reason = "not ohio"
            elif it["url"].rstrip("/") in known_urls: reason = "known url"
            matched = next((who for a, who in aliases.items() if a in blob.lower()), None)
            if reason:
                seen[i] = {"url": it["url"], "title": it["title"], "first_seen": NOW.isoformat(), "reason": reason}
                continue
            text, formal_hint = "", None
            if matched: pass
            elif "news.google.com" not in it["url"]:
                try:
                    text = strip_html(get(it["url"]).decode("utf-8", "ignore"))
                    formal_hint = bool(FORMAL.search(text))
                    if not OHIO.search(text): formal_hint = False
                except Exception as e:
                    print(f"  fetch failed {it['url']}: {e}", file=sys.stderr)
            ai = None
            if text and ai_budget > 0:
                ai = ai_read(text, it["title"], it["url"]); ai_budget -= 1
                time.sleep(1)
            c = {"id": i, "title": it["title"], "url": it["url"], "source": it["source"], "published": iso(it["published_raw"]),
                 "found_at": NOW.strftime("%Y-%m-%d"), "snippet": it["snippet"][:300], "formal_hint": formal_hint, "ai": ai,
                 "status": "coverage" if matched else "new", "matches": matched}
            by_id[i] = c; found += 1
            print(f"+ {it['title']} [{it['source']}] formal_hint={formal_hint} ai={(ai or {}).get('formal_2907071')}")
    cands = list(by_id.values())
    # drop candidates that became known cases, and cap list size
    cands = [c for c in cands if c["url"].rstrip("/") not in known_urls]
    cands.sort(key=lambda c: (c.get("published") or c.get("found_at") or ""), reverse=True)
    cands = cands[:200]
    json.dump(cands, open(os.path.join(D, "candidates.json"), "w"), indent=1)
    json.dump(seen, open(os.path.join(D, "seen.json"), "w"), indent=0)
    open(os.path.join(D, "last_sweep.txt"), "w").write(NOW.strftime("%Y-%m-%d %H:%M UTC"))
    print(f"sweep done: {found} new candidates, {len(cands)} queued, {len(seen)} seen")

if __name__ == "__main__":
    main()
