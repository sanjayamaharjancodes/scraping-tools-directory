# ct-002 hand-off (site branch worktree-ct-002; content-autopilot branch ct-002-leftovers)

Goal: a second original-data page from our job index (manifest + shards), plus ct-001's leftovers (nav, autopilot
registry, publish.py keeping data lines in llms.txt). Brief: D:/Lab/manager/briefs/ct-002.md. Linear SAN-118.

## State (19 Nov 2026): done on both branches, waiting for the manager's merge
- **Page:** `what-day-are-most-jobs-posted.html`, query `what day are most jobs posted` (ct-002/PREMISE.md: GO).
  Answer: Tuesday, narrowly. It holds 20.7% closure-adjusted; the other weekdays 18.6-19.9%; weekend 2.9%; Tuesday
  led 3 of 4 weeks (2 of 4 for US jobs). There is an hours chart by ATS/region/day and a daily-refresh wait table.
  Data: `data/job-posting-days-2026-11.{csv,json}`.
- **Index snapshot** (builtAt 2026-11-19T04:03:40.394Z; the Actor keeps only the latest build):
  `ct-002/index-snapshot/` in this worktree, git-ignored, not published. build_data.py refuses any other build by
  SHA-256 (hashes in the script).
- **Blind review** (ct-002/REVIEW.md): attempt 1 (subagent) was not blind, because it saw the repository context.
  Attempt 2 ran as a headless `claude -p` in a neutral folder and confirmed it was blind. Ours ranked 1st on
  originality, usefulness and trustworthiness against Recruiter.com, Facebook fb-answers, ChiefJobs and CNBC.
  Google #1 (Reddit) is unreadable by our tools.
- **Checks (all pass on the final commits):**
  - `python -I ct-002/build_data.py --index ct-002/index-snapshot --check what-day-are-most-jobs-posted.html`:
    every number in the data, 65 table cells, widget block. Outputs are byte-identical across runs. Positive
    control: 3 planted errors, all caught.
  - `python -I ct-002/run_gate.py --autopilot F:/Lab/assets/content-autopilot/.claude/worktrees/ct-002`:
    0 findings, 1,478 words, 9.0 phone screens.
  - ct-001 after its nav change: build_data --check (42 cells; CSV byte-identical to the commit), run_gate 0
    findings.
  - content-autopilot `ct-002-leftovers` 155b2a7: tests/test_data_pages.py 7 pass (6 fail on main); full suite 191
    passed.
  - `python -I ct-002/check_live.py` before the merge: 11 of 19 fail, as expected (the live nav still links the
    retired pages).

## Post-merge (manager)
1. Merge the site branch and content-autopilot `ct-002-leftovers` together: the gate compares a page's nav with
   the skeleton.
2. `python -I ct-002/check_live.py` must print ALL PASS.
3. Facts expire after 3 days. Run `python -I ct-002/build_data.py --refresh-facts --check
   what-day-are-most-jobs-posted.html`, then `python -I ct-002/run_gate.py --autopilot <content-autopilot> --live`.

## Left over
- `F:/Lab/assets/content-autopilot/.claude/worktrees/ct-002/site/` is a git-ignored clone used for the autopilot
  test suite. Deleting it was refused to this session; delete it with the autopilot worktree after the merge.
- `.tmp-ct002/` in this worktree (git-ignored: captures, review tiles, gate scratch). `rm -rf` was refused to
  this session; it goes with the worktree.
- Nothing pushed in either repo. STOP is untouched in F:/Lab/assets/content-autopilot.

## Attempts
- Gate: 1 miss ("25" from "25 Oct" without a year; the gate strips only dates with a year), fixed by giving dates
  their year.
- Phone tables clipped: 1 miss, fixed with fewer columns and day abbreviations.
- Headline misattribution and week stability (advisor): fixed once.
- Blind review: 1 miss (subagent saw repository context). Method changed to a headless reviewer in a neutral
  folder: passed.
- Facts sort was non-deterministic (set order of "17" vs "17.0"): fixed once.
