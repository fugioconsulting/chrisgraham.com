# Grooming tracker: the morning judge

This is the prompt for the Claude scheduled task **grooming-judge** on Chris's MacBook Pro. It runs every morning after the free GitHub Actions sweep (5am ET) has queued new stories in `data/grooming/candidates.json`. It reads each queued story, decides by the rules, and adds every case that passes to chrisgraham.com/grooming. No paid API: this session does the reading. Chris never reviews cases, so never ask him to.

Work in the judge's own worktree, `/Users/h/code/grooming-judge`, pinned to `origin/main`. Never work in `/Users/h/code/chrisgraham.com` itself: that is Chris's checkout, and its local main has commits of its own.

## The rules
A story is **promote** only if all four hold:
1. **Ohio court.** Watch for syndication: Gray TV and Nexstar sites (cleveland19, fox19, wsaz, wdtn...) carry other states' stories. Read the dateline. Kentucky and Illinois also have grooming laws.
2. **One named person**, full name as printed.
3. **A formal grooming count** under ORC 2907.071: charged, indicted, pleaded, or convicted. Not enough: "groomed", "a grooming pattern", "grooming-related offenses", "accused of grooming" with no count listed, federal charges, or other statutes only (importuning, disseminating, pandering without a grooming count).
4. **A reputable source that states it:** a news outlet, a prosecutor, police or court release, or a public court docket. Never social media, mugshot or booking sites, people-search sites, or a paywalled page you could not read.

Other verdicts:
- **coverage:** the story is about someone already in `data/grooming/cases.csv` or `excluded.csv`. A queued item whose `matches` field names a listed person is a hint, not a ruling: read the story and decide. If it reports a new outcome for a listed person (plea, conviction, sentence, dismissal), also edit that row's `status` and `resolved` in `cases.csv` (open the story first; note the outlet and date in the status, e.g. "Convicted, 4 years (WCPO, Nov 2026)").
- **reject:** fails a rule for good (out of state, pet grooming, no grooming count, federal only).
- **unsure:** anything you could not settle (page unreadable, name withheld, two possible defendants). It stays queued and is read again tomorrow. When in doubt, unsure. Never promote on a guess.

Someone in `data/grooming/held.csv` can be promoted the day a readable source shows the count. Then remove their line from `held.csv`.

## Steps
1. Get a clean copy of main:
   ```
   [ -d /Users/h/code/grooming-judge ] || git -C /Users/h/code/chrisgraham.com worktree add --detach /Users/h/code/grooming-judge origin/main
   cd /Users/h/code/grooming-judge && git fetch -q origin && git checkout -q --detach origin/main && git reset -q --hard origin/main
   ```
   If `data/grooming/last_sweep.txt` does not show today's UTC date, the 5am sweep has not run. Run `python3 scripts/grooming/crawl.py` here first (it's free).
2. List the queue: `python3 -c "import json; [print(c['id'], c['url'], '|', c['title'], '| hint:', c.get('matches'), '| last:', c.get('judge')) for c in json.load(open('data/grooming/candidates.json'))]"`. If it's empty, report "queue empty" and stop.
3. Open every story. Use WebFetch. For a `news.google.com` link, WebSearch the exact headline and open the publisher's page. If a page blocks you, try the built-in browser, the AMP copy, or a syndicated copy (yahoo.com, msn.com). For a Hamilton County docket, use the clerk's case-number search form in the built-in browser. Never solve a CAPTCHA or get around a block. A page you could not read in full is **unsure**.
4. Write the verdicts to `$TMPDIR/grooming-verdicts.json`: a JSON list with one object per queued id:
   ```json
   {"id": "64e61b0cee7e", "verdict": "promote|reject|coverage|unsure", "reason": "one short line",
    "url": "the publisher page that states the count (this is what readers click)",
    "alt_urls": ["optional: other copies of the same story the code can fetch, e.g. yahoo/msn/AMP, if the publisher blocks scripts"],
    "evidence": "one sentence copied character for character from that page, with the person's first and last name and the grooming count",
    "matches": "listed person's name (coverage only)",
    "name": "", "age": 0, "city": "", "county": "Ohio county, no 'County'", "charged": "Oct 2026",
    "charges": "Grooming first, e.g. Grooming, 2 sexual battery",
    "companion": "hands-on | exploitation | none | unspecified",
    "status": "Pending, pleaded not guilty", "resolved": "convicted | pleaded guilty | plea on other counts | dismissed | (blank)",
    "summary": "one neutral sentence under 45 words: who, age, town, county, month, charges; open cases say 'was charged' or 'was indicted', never imply guilt"}
   ```
   companion: `hands-on` if rape, sexual battery, gross sexual imposition or unlawful sexual conduct is charged. `exploitation` if abuse material, pandering, importuning, trafficking or voyeurism. `none` if grooming alone.
5. `python3 scripts/grooming/crawl.py --apply "$TMPDIR/grooming-verdicts.json"`. The code fetches the page itself (or an `alt_urls` copy) and re-checks every promote: full name, Ohio county, a non-blocklisted host, your quote is on the page word for word and states a formal count, the full name and Ohio are on the page, no other state or federal court in the quote, not already listed, and not in `excluded.csv`. `HELD` keeps the story queued with the reason. `COVERAGE` means already listed. Fix a HELD only when it was your data error (a typo in the quote, a wrong county, a missing readable copy). Never loosen a check to get a case through. A "possible duplicate" or "matches not-counted" hold stays held unless the story plainly shows it is someone else, and then you say so in the report.
6. Photos, for PROMOTED rows only: if the page shows a booking photo that is plainly that person (captioned, or the only mugshot in the story), download it, crop it to a square (keep the top of a portrait), resize it to 300px with PIL, and save it as `docs/grooming/img/<num>_<lastname>.jpg`. Then set that row's `thumb` in `cases.csv`. If there's no face or any doubt, leave it blank.
7. Status updates: for coverage that reports a new outcome for a listed person, edit that row's `status` and `resolved` now.
8. `python3 scripts/grooming/build.py`. If a case was added and `python3 -c "import geopandas"` works, also run `python3 scripts/grooming/build_map.py`.
9. `git add data/grooming docs/grooming && git commit -m "grooming: judge <date>: +N (<names>)" && git push origin HEAD:main`. If the push is rejected (the Actions bot pushed first), don't rebase. Run `git fetch -q origin && git reset -q --hard origin/main`, repeat steps 5 to 8 with the same verdicts file (already-settled ids are skipped), and push again. Pages publishes in about a minute.
10. Artifact mirror, only if `cases.csv` changed and `grooming-tracker/from_chrisgraham.py` exists on claude-skills `origin/main`: in `~/Documents/claude-skills` (fetch first; use a temporary worktree of origin/main if that checkout is dirty), run `cd grooming-tracker && python3 from_chrisgraham.py /Users/h/code/grooming-judge && python3 build_map_svg.py && python3 build_html.py && python3 build_og.py`. Then publish `tracker.html` to https://claude.ai/artifact/L2qaA61k6neUampn7kD24R with `files: {"og.png": "og.png"}`. Otherwise skip it and say so.
11. Report in three lines at most: how many were queued, who was added (with links), and how many were held, rejected or unsure, and why. No questions for Chris.
