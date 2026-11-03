# Grooming tracker: the morning judge

This is the prompt for the Claude scheduled task **grooming-judge** on the Mac mini (Minnie). It runs every morning at 5am ET, after the free GitHub Actions sweep (3am ET) has queued new stories in `data/grooming/candidates.json`. It reads each queued story and each new FOI records reply, decides by the rules, adds every case that passes to `data/grooming/cases.csv`, and republishes the Claude artifact, which is the public page (chrisgraham.com/grooming redirects to it). No paid API: this session does the reading. Chris never reviews cases, so never ask him to.

Work in the judge's own worktree, `~/code/grooming-judge`, pinned to `origin/main`. It runs on whichever Mac has the task (the Mac mini, Minnie, since 2026-11-03; Chris's MacBook Pro before). Never work in Chris's own chrisgraham.com checkout itself (`~/code/chrisgraham.com` on the MacBook, `~/chrisgraham.com` on Minnie): that is Chris's checkout, and its local main has commits of its own.

## The rules
A story is **promote** only if all four hold:
1. **Ohio court.** Watch for syndication: Gray TV and Nexstar sites (cleveland19, fox19, wsaz, wdtn...) carry other states' stories. Read the dateline. Kentucky and Illinois also have grooming laws.
2. **One named person**, full name as printed.
3. **A formal grooming count** under ORC 2907.071: charged, indicted, pleaded, or convicted. Not enough: "groomed", "a grooming pattern", "grooming-related offenses", "accused of grooming" with no count listed, federal charges, or other statutes only (importuning, disseminating, pandering without a grooming count).
4. **A reputable source that states it:** a news outlet, a prosecutor, police or court release, a public court docket, or a clerk of courts' or agency's own written reply to our R.C. 2907.071 records request (FOI). Cite a records reply as the court's docket search page plus the case number. Never social media, mugshot or booking sites, people-search sites, or a paywalled page you could not read.

**Never automate posting a police report or any raw records file (Chris, 2026-11-03).** They name victims and minors; an automated post can become one more failure for a survivor. Public pages cite a court case page or the court plus the case number. Exceptions are Chris's call, one record at a time, blacked out by hand. A records reply is cited as the court's case page or search page plus the case number (status reads "(case NUMBER)"), never as a link to the record itself.

**Case numbers (Chris, 2026-11-03).** Whenever any source shows the court case number, put it in `status` as "(case NUMBER)", e.g. "Pending, $100,000 bond (case B 2602888)". The tracker prints it on the card. Do the same when coverage of a listed person shows a number the row lacks.

Other verdicts:
- **coverage:** the story is about someone already in `data/grooming/cases.csv` or `excluded.csv`. A queued item whose `matches` field names a listed person is a hint, not a ruling: read the story and decide. If it reports a new outcome for a listed person (plea, conviction, sentence, dismissal), also edit that row's `status` and `resolved` in `cases.csv` (open the story first; note the outlet and date in the status, e.g. "Convicted, 4 years (WCPO, Nov 2026)").
- **reject:** fails a rule for good (out of state, pet grooming, no grooming count, federal only).
- **unsure:** anything you could not settle (page unreadable, name withheld, two possible defendants). It stays queued and is read again tomorrow. When in doubt, unsure. Never promote on a guess.

Someone in `data/grooming/held.csv` can be promoted the day a readable source shows the count. Then remove their line from `held.csv`.

## Steps
1. Get a clean copy of main:
   ```
   CG=$(ls -d ~/code/chrisgraham.com ~/chrisgraham.com 2>/dev/null | head -1)
   [ -d ~/code/grooming-judge ] || git -C "$CG" worktree add --detach ~/code/grooming-judge origin/main
   cd ~/code/grooming-judge && git fetch -q origin && git checkout -q --detach origin/main && git reset -q --hard origin/main
   ```
   If `data/grooming/last_sweep.txt` does not show today's UTC date, the 3am sweep has not run. Run `python3 scripts/grooming/crawl.py` here first (it's free).
2. List the queue: `python3 -c "import json; [print(c['id'], c['url'], '|', c['title'], '| hint:', c.get('matches'), '| last:', c.get('judge')) for c in json.load(open('data/grooming/candidates.json'))]"`. If it is empty and step 2b finds nothing new, skip to step 10 (the artifact and the note still go out every run).
2b. FOI records. The anonymous FOI desk on Minnie asked every county clerk of courts, sheriff and many police departments for their R.C. 2907.071 cases, and replies keep arriving. Read them, never write: `cd ~/Code/foi-mail/data && grep -l 2907.071 requests/*/*-out-request.txt` on Minnie (from another Mac, prefix `ssh claw@minnie`) lists the grooming requests. Their replies are the inbound folders `requests/FOI-NNNN/<date>-in-*` (`body.txt` plus attachments). Look only at folders not yet listed in `data/grooming/foi_read.txt`, and copy each one to `$TMPDIR/foi/` with `scp -r`. Read PDFs with `pdftotext -layout`; render scanned ones with `pdftoppm -png` and read the image.
   For every defendant the reply shows with a 2907.071 / grooming count who is not already listed, add a verdict with no `id` and `"origin": "FOI-NNNN <agency>"`. Try to find a news, prosecutor or public docket page first; if you find one, use it as `url` the normal way. Otherwise use the reply itself:
   - `"url"`: the court's public docket search page.
   - `"record_file"`: the local copy of the reply file (body.txt, CSV or a text PDF).
   - `"evidence"`: the reply's line naming the person, copied character for character.
   - `"record_scope_quote"`: if that line doesn't itself say grooming or 2907.071, a second verbatim line from the same file that does (e.g. "results of our search for cases charging 2907.071").

   Put the case number in `status` and `summary`. If the reply is a scanned image with no text, the code can't check it: add the person yourself only if you read the image plainly, cite the case number, and say so in the report. Fill in what the record shows; don't guess age or town. Append every folder you read to `foi_read.txt`.
2c. FOI booking photos (Chris, 2026-11-03: they go through the same photo process as every other image; see /groomerphoto). After step 5 has added any new people, run `python3 scripts/grooming/foi_photos.py $TMPDIR/foi/*` to see what it finds, then the same with `--apply`. It takes a picture from a reply only when the record itself names exactly one listed person on it (file name, the PDF page it sits on, or a reply holding just one face photo), it shows exactly one face, and that person has no photo yet. It saves `docs/grooming/img/<num>_<last>.jpg`, sets `thumb` and logs the source in `data/grooming/photo_sources.csv`. Open each saved photo and look at it before you commit; if it is not a booking or court photo of one person, delete it and clear `thumb`. HOLD lines stay out; list them in the report. Never run `foi pull`, send, reply or close anything; the FOI desk owns that.
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
6. Photos, for PROMOTED rows only: if the page shows a booking photo that is plainly that person (captioned, or the only mugshot in the story), download it and keep as much of the original as possible: trim only logos, borders, TV graphics and blur padding, never crop tight to the face or to a square, longest side 700px JPEG, saved as `docs/grooming/img/<num>_<lastname>.jpg` (the tracker's /groomerphoto step lines up the eyes from it, and a tight crop breaks that). Then set that row's `thumb` in `cases.csv`. If there's no face or any doubt, leave it blank.
7. Status updates: for coverage that reports a new outcome for a listed person, edit that row's `status` and `resolved` now.
8. `python3 scripts/grooming/build.py`. If a case was added and `python3 -c "import geopandas"` works, also run `python3 scripts/grooming/build_map.py`.
9. `git add data/grooming docs/grooming && git commit -m "grooming: judge <date>: +N (<names>)" && git push origin HEAD:main`. If the push is rejected (the Actions bot pushed first), don't rebase. Run `git fetch -q origin && git reset -q --hard origin/main`, repeat steps 5 to 8 with the same verdicts file (already-settled ids are skipped), and push again. Pages publishes in about a minute.
10. Republish the artifact every run, even when nothing was added, so its "updated" date shows the morning check happened (it's the public page; `check_regression.py` must pass first). In `~/Documents/claude-skills`, `git fetch -q origin`, then make a temporary worktree of `origin/main` if it has `grooming-tracker/from_chrisgraham.py`, else of `origin/grooming-tracker-mirror`. In its `grooming-tracker/`, run `python3 from_chrisgraham.py ~/code/grooming-judge && python3 photos.py && python3 build_map_svg.py && python3 build_html.py`. For `og.png`, run `python3 build_og.py`. If Playwright is missing, the script still writes `og.html`; render it with `"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --hide-scrollbars --window-size=1200,630 --virtual-time-budget=4000 --screenshot=og.png "file://$PWD/og.html"`. Then publish `tracker.html` to https://claude.ai/artifact/L2qaA61k6neUampn7kD24R with `files: {"og.png": "og.png"}` (read the artifact once first). Remove the temporary worktree.
11. Report in three lines at most: how many were queued, who was added (with links), and how many were held, rejected or unsure, and why. No questions for Chris. Send the same lines to Chris every run, even "0 new": `cd ~/Code/foi-mail && ./foi.js notify "Grooming judge <date>: <report>"` (from another Mac, prefix `ssh claw@minnie`). If any step failed, say which in that note.
12. Log the run, every run, even a failed one: append one line to `data/grooming/judge_log.csv` (header `started_utc,finished_utc,queued,foi_read,added,held,rejected,unsure,published,notified,failed_step`; `published`/`notified` are `yes` or `no`, `failed_step` is blank or the step number and a few words). Commit it with `git add data/grooming/judge_log.csv && git commit -m "grooming: judge log <date>" && git push origin HEAD:main` (on rejection: fetch, reset to origin/main, re-append, push). This file is the receipt that the morning run happened.
