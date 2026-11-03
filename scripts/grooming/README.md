# chrisgraham.com/grooming

A public, self-updating record of every Ohioan charged under Ohio's grooming statute (ORC 2907.071, HB 322, effective 2025-04-09).

## Files
- `data/grooming/cases.csv`: the confirmed list. One row per person. **Editing this file is how a case gets on the page.** Columns: num, name, age, city, county, charged, charges, companion (`hands-on` | `exploitation` | `unspecified`), status, resolved (`convicted` | `pleaded guilty` | `plea on other counts` | blank), source_url, thumb (file in `docs/grooming/img/`, may be blank), summary (one neutral sentence).
- `data/grooming/excluded.csv`: grooming described but not charged. Shown under "not counted".
- `data/grooming/candidates.json`: what the crawler found, awaiting a human. Rendered in the "Newly found" lane. Never edited by hand; add a case to `cases.csv` with the same source_url and the candidate disappears on the next build.
- `data/grooming/dismissed.txt`: candidate ids or URLs to hide (false positives).
- `data/grooming/seen.json`: everything the crawler already looked at, with the reason it was skipped.
- `scripts/grooming/crawl.py`: the sweep (Bing News + Google News RSS, seven queries, stdlib only). Optional `ANTHROPIC_API_KEY` adds a Claude read of each new story (capped at 8 calls per run).
- `scripts/grooming/build.py`: renders `docs/grooming/index.html` and `docs/grooming/cases.json`.
- `.github/workflows/grooming.yml`: runs crawl + build every six hours and commits. Pages publishes the commit.

## Promote a candidate
1. Open the source. Confirm a formal grooming count (charged, indicted, pleaded, convicted), not just the word.
2. Add a row to `cases.csv` (next number, county, charges, companion category, one-sentence summary, the source URL). Optional: drop a 300px square booking photo in `docs/grooming/img/` and name it in `thumb`.
3. `python3 scripts/grooming/build.py`, commit, push to main. The map image (`docs/grooming/img/ohio_map.png`) is built separately in the Bonnie repo (`ohio_grooming_charges/build_map.py`); regenerate it when counties change.

## Run locally
    python3 scripts/grooming/crawl.py && python3 scripts/grooming/build.py
