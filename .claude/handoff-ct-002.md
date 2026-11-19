# ct-002 hand-off (site branch worktree-ct-002; content-autopilot branch ct-002-leftovers)

Goal: a second original-data page from our job index (manifest + shards), plus ct-001's leftovers (nav, autopilot
registry, publish.py keeping data lines in llms.txt). Brief: D:/Lab/manager/briefs/ct-002.md. Linear SAN-118.

## State (19 Nov 2026)
- **Page:** `what-day-are-most-jobs-posted.html`, query `what day are most jobs posted` (ct-002/PREMISE.md: GO).
  Answer: Tuesday, narrowly (20.7% closure-adjusted; 18.6-19.9% other weekdays; weekend 2.9%; Tuesday led 3 of 4
  weeks). Hours by ATS/region/day chart, daily-refresh wait table. Data `data/job-posting-days-2026-11.{csv,json}`.
- **Index snapshot** (the build the brief cites, builtAt 2026-11-19T04:03:40.394Z; the Actor keeps only the latest
  build): `ct-002/index-snapshot/` in this worktree, git-ignored, not published. build_data.py refuses any other
  build by SHA-256 (hashes in the script; manifest 4c302194d638...).
- **Checks on the branch (all pass):**
  - `python -I ct-002/build_data.py --index ct-002/index-snapshot --check what-day-are-most-jobs-posted.html`:
    every number in the data, 65 table cells, widget block. Outputs byte-identical across runs. Positive control:
    3 planted errors, all caught.
  - `python -I ct-002/run_gate.py --autopilot F:/Lab/assets/content-autopilot/.claude/worktrees/ct-002`: 0
    findings, about 1,300 words, 8.4 phone screens.
  - ct-001 re-checked after its nav change: build_data --check (42 cells), run_gate 0 findings.
  - content-autopilot branch: `tests/test_data_pages.py` 7 pass (6 fail on main); full suite 191 passed.
  - `python -I ct-002/check_live.py` before merge: 11 of 19 fail, as expected.
- **Blind review:** running (5 pages: Recruiter.com, Facebook fb-answers, ChiefJobs, CNBC, ours; Reddit #1 is
  unreadable by our tools). Record in ct-002/REVIEW.md.

## Post-merge (manager)
1. Merge the site branch and content-autopilot `ct-002-leftovers` together (nav must match the skeleton).
2. `python -I ct-002/check_live.py` must print ALL PASS.
3. `python -I ct-002/build_data.py --refresh-facts --check what-day-are-most-jobs-posted.html` (facts expire after
   3 days), then `python -I ct-002/run_gate.py --autopilot <content-autopilot> --live`.

## Decisions
- Cross-ATS shares and remote share rejected (coverage and per-ATS definitions); posting-age rejected (others
  measure durations; a snapshot cannot).
- Snapshot bias: same-weekday counts fall 13.9%/week of age; closure-adjusted shares are the headline, raw shown.
- Region from location text (US / Europe / other); US Eastern and CET with DST rules coded in the script.
- Data pages are kind `data` in the autopilot registry (never refreshed or retired by the planner).
- CNBC consent banner removed from the capture only (nothing clicked or accepted).

## Left over / for the manager
- `F:/Lab/assets/content-autopilot/.claude/worktrees/ct-002/site/` is a git-ignored clone used for the test suite;
  deleting it was refused to this session. Delete it (or the whole autopilot worktree) after merge.
- Nothing pushed in either repo.

## Attempts
- Gate: 1 miss ("25" from "25 Oct" without a year; the gate strips only dates with years) -> dates carry years.
- Phone tables clipped: 1 miss -> fewer columns, day abbreviations.
- Headline misattribution and week stability (advisor) -> fixed once.
