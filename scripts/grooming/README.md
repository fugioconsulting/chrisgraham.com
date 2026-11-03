# Ohio grooming charge tracker

The public page is the Claude artifact https://claude.ai/artifact/L2qaA61k6neUampn7kD24R. chrisgraham.com/grooming redirects to it. This folder holds the data, the sweep and the judge that keep the artifact current.

A public, self-updating record of every Ohioan charged under Ohio's grooming statute (ORC 2907.071, HB 322, effective 2025-04-09). No person reviews cases, and no paid API is used. A free crawler queues stories every morning. A Claude scheduled task on Chris's MacBook Pro reads them and adds every one that passes the rules. Anything doubtful stays out.

## The rules (a case is counted only if all hold)
1. Ohio court.
2. One named person.
3. A formal grooming count under ORC 2907.071: charged, indicted, pleaded, or convicted. "Groomed", "a grooming pattern", or "grooming-related offenses" in coverage is not a count.
4. A reputable source that states the count: a news outlet, prosecutor or court release, a public court docket, or a clerk's or agency's own reply to our 2907.071 records request (cited as the court's docket search page plus the case number). Not social media, mugshot sites, aggregators of aggregators, or paywalled posts that don't show it.

The page uses charged-not-convicted wording for every open case.

## Files
- `data/grooming/cases.csv`: the confirmed list, and the only source for the page. One row per person. Columns: num, name, age, city, county, charged, charges, companion (`hands-on` | `exploitation` | `none` | `unspecified`), status, resolved (`convicted` | `pleaded guilty` | `plea on other counts` | `dismissed` | blank), source_url, thumb (file in `docs/grooming/img/`, may be blank), aka (`;`-separated: the surname plus specific multi-word phrases headlines use for this person and nobody else, never generic ones like "miami county" or "police chief"; a multi-word aka in a headline settles a story as coverage), summary (one neutral sentence), lat, lon.
- `data/grooming/excluded.csv`: grooming described but no formal count. Shown under "not counted".
- `data/grooming/held.csv`: people another tracker listed but whose only source could not be opened or did not show the count. Not rendered. Re-check before adding.
- `data/grooming/candidates.json`: stories waiting for the morning judge, or that it could not settle (unreadable, no name, a code check failed: see each item's `judge`). Shown in the "Queued" lane, never counted.
- `data/grooming/dismissed.txt`: candidate ids or URLs to hide, with the reason (out of state, pet grooming, coverage of a listed person).
- `data/grooming/seen.json`: everything the crawler already settled, with the reason (promoted, rejected, coverage, no groom word, not ohio...).
- `data/grooming/county_centroids.json`: map position for a promoted case.
- `scripts/grooming/crawl.py`: the sweep (Bing News + Google News RSS, seven queries, stdlib only; Google links resolved to the publisher URL through Bing) and `--apply FILE`, which applies the judge's verdicts.
- `scripts/grooming/JUDGE.md`: the prompt for the scheduled task `grooming-judge` (Claude desktop app, scheduled tasks, on Chris's MacBook Pro), every morning after the sweep.
- `scripts/grooming/foi_photos.py` (+ `eyes.swift`): booking photos from FOI records replies; ties a photo to a person only when the record names them on it, one face, no existing photo. Sources logged in `data/grooming/photo_sources.csv`.
- `scripts/grooming/build.py`: writes `docs/grooming/cases.json` (the data feed other systems can read) and `docs/grooming/index.html` (a redirect to the artifact).
- `data/grooming/foi_read.txt`: FOI reply folders on Minnie the judge has already read.
- `scripts/grooming/build_map.py`: draws `docs/grooming/img/ohio_map.png` (local only, needs geopandas).
- `.github/workflows/grooming.yml`: runs crawl + build daily at 08:00 UTC (3am ET) and commits to main. Pages publishes the commit. No secrets.

## How a story becomes a case
1. **Sweep (GitHub Actions, 3am ET, free).** New stories that pass the Ohio/charge/grooming word filters are checked against the list. A known source URL, or a headline with a listed person's first and last name or a curated multi-word aka, drops out as coverage. A surname plus that person's town or county is only a hint (`matches`) for the judge. Pet-grooming stories (animal or salon words, no child words) are skipped. The rest go to `candidates.json`. A run where no feed returns RSS fails without touching `last_sweep.txt`, so the judge can tell. Stories still unsettled after 90 days expire into `seen.json`.
2. **Judge (Claude desktop scheduled task `grooming-judge` on the Mac mini, every morning at 5:00, in its own worktree `~/code/grooming-judge`).** Claude opens each queued story and writes a verdict (`promote` | `reject` | `coverage` | `unsure`) with every `cases.csv` field and a verbatim quote, following `JUDGE.md`. It also updates the status of listed people when coverage reports a plea, conviction or dismissal.
3. **Apply (`crawl.py --apply`).** `promote` is necessary but not sufficient. The code fetches the page itself (or a readable copy the judge lists in `alt_urls`) and re-checks: full name and an Ohio county; a non-blocklisted host; the judge's quote is on the page word for word, names the person, and states a formal count (charged with / counts of / indicted on / pleaded guilty to ... grooming, or 2907.071); the full name and Ohio are on the page; no other state or federal court in the quote; not already listed (first and last name, or the same source URL), which makes it coverage; not a surname-and-county near match or an `excluded.csv` person, which stays held. All pass: the row is appended with the next number and a map position. A failed check keeps the story queued with the reason. `reject` and `coverage` go to `seen.json`. `unsure` waits for tomorrow.
4. Build, commit, push to main, then republish the artifact from the new `cases.csv` (JUDGE.md step 10).

If the Mac is off, stories simply wait in the queue; nothing is lost.

## Fix or add a case by hand
Edit the row in `cases.csv` (open the source first), then `python3 scripts/grooming/build.py` and push to main. For a photo, save a 300px square JPEG in `docs/grooming/img/` and name it in `thumb`. When counties change, regenerate the map: `python3 scripts/grooming/build_map.py`.

## The Claude artifact
The "Ohio Grooming Tracker" artifact (https://claude.ai/artifact/L2qaA61k6neUampn7kD24R) is a mirror of this CSV, not a separate list. It was built from `grooming-tracker/` in fugioconsulting/claude-skills; that folder's CSV is retired as a source. To refresh the artifact, republish it from `docs/grooming/cases.json` and the photos here.

## Run locally
    python3 scripts/grooming/crawl.py && python3 scripts/grooming/build.py
