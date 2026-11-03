# chrisgraham.com/grooming

A public, self-updating record of every Ohioan charged under Ohio's grooming statute (ORC 2907.071, HB 322, effective 2025-04-09). No person reviews cases: the sweep adds every story that passes the rules, and keeps anything doubtful out.

## The rules (a case is counted only if all hold)
1. Ohio court.
2. One named person.
3. A formal grooming count under ORC 2907.071: charged, indicted, pleaded, or convicted. "Groomed", "a grooming pattern", or "grooming-related offenses" in coverage is not a count.
4. A reputable source that states the count: a news outlet, prosecutor or court release, or a public court docket. Not social media, mugshot sites, aggregators of aggregators, or paywalled posts that don't show it.

The page uses charged-not-convicted wording for every open case.

## Files
- `data/grooming/cases.csv`: the confirmed list, and the only source for the page. One row per person. Columns: num, name, age, city, county, charged, charges, companion (`hands-on` | `exploitation` | `none` | `unspecified`), status, resolved (`convicted` | `pleaded guilty` | `plea on other counts` | `dismissed` | blank), source_url, thumb (file in `docs/grooming/img/`, may be blank), aka (`;`-separated: the surname plus specific multi-word phrases headlines use for this person, never generic ones like "miami county"), summary (one neutral sentence), lat, lon.
- `data/grooming/excluded.csv`: grooming described but no formal count. Shown under "not counted".
- `data/grooming/held.csv`: people another tracker listed but whose only source could not be opened or did not show the count. Not rendered. Re-check before adding.
- `data/grooming/candidates.json`: stories the crawler could not settle yet (unreadable, no name, or the model and the checks disagree). Shown in the "Queued" lane, never counted.
- `data/grooming/dismissed.txt`: candidate ids or URLs to hide, with the reason (out of state, pet grooming, coverage of a listed person).
- `data/grooming/seen.json`: everything the crawler already settled, with the reason (promoted, rejected, coverage, no groom word, not ohio...).
- `data/grooming/county_centroids.json`: map position for a promoted case.
- `scripts/grooming/crawl.py`: the sweep. Bing News + Google News RSS, seven queries, stdlib only. Google links are resolved to the publisher URL through Bing.
- `scripts/grooming/build.py`: renders `docs/grooming/index.html` and `docs/grooming/cases.json`.
- `scripts/grooming/build_map.py`: draws `docs/grooming/img/ohio_map.png` (local only, needs geopandas).
- `.github/workflows/grooming.yml`: runs crawl + build every six hours and commits to main. Pages publishes the commit.

## How a story becomes a case
For each new story, and each queued story the model has not read yet:
1. Drop it if its URL is already a source, or it names a listed person (first and last name, surname plus their town or county, or a multi-word aka). That is coverage.
2. Fetch the article. Claude (`GROOMING_MODEL`, default `claude-sonnet-5-5`) returns a verdict (`promote` | `reject` | `unsure`) plus every `cases.csv` field.
3. `promote` is necessary but not sufficient. The code also checks: full name, an Ohio county, a non-blocklisted source host, the surname and the word grooming in the article text, formal charge wording near grooming, grooming in the charges, and not already listed. All pass: the row is appended to `cases.csv` with the next number and a map position.
4. `reject`: logged to `seen.json`. Anything else stays queued and is read again next sweep.

`GROOMING_MAX_AI` caps model calls per run (default 60). If the API key is rejected (401/403) the run logs a `::error::` annotation, stops calling the model, and still commits the sweep.

## Fix or add a case by hand
Edit the row in `cases.csv` (open the source first), then `python3 scripts/grooming/build.py` and push to main. For a photo, save a 300px square JPEG in `docs/grooming/img/` and name it in `thumb`. When counties change, regenerate the map: `python3 scripts/grooming/build_map.py`.

## The Claude artifact
The "Ohio Grooming Charge Tracker" artifact (https://claude.ai/artifact/L2qaA61k6neUampn7kD24R) is a mirror of this CSV, not a separate list. It was built from `grooming-tracker/` in fugioconsulting/claude-skills; that folder's CSV is retired as a source. To refresh the artifact, republish it from `docs/grooming/cases.json` and the photos here.

## Run locally
    python3 scripts/grooming/crawl.py && python3 scripts/grooming/build.py
