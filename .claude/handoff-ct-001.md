# ct-001 hand-off (branch worktree-ct-001)

Goal: one original-data page from the job-index refresh evidence, retire the 3 thinnest pages, blind review, publish.

## State (19 Nov 2026, about 10:00 local)
- Done: PREMISE.md (GO; query `ats public job posting api`; top 3 = fantastic.jobs, cavuno.com, developers.ashbyhq.com).
- Done: page `ats-job-posting-api-crawl-data.html`; data `data/ats-board-crawl-2026-11.{csv,json}`; `ct-001/facts.json`.
  Built from evidence incl. `refresh-2026-11-19.json` (second 19 Nov pass, complete; first pass crashed before its report).
- Checks (all pass): `python -I ct-001/build_data.py --evidence <ats-jobs-search>/evidence --crawler-src <...>/src
  --check ats-job-posting-api-crawl-data.html` (numbers + 42 table cells; positive control caught 3 planted numbers);
  `python ct-001/run_gate.py --autopilot <content-autopilot>`: 0 findings, 1,151 words, 8.1 phone screens, no JS errors.
- Done: retired web-scraping-apis-with-free-tier, scraperapi-free-trial, scrapingdog-vs-scrapingbee (RETIRED.md).
- Review: blind reviewer subagent running; pages A=fantastic.jobs, B=Ashby docs, C=ours, D=Cavuno; tiles and text in
  F:/Lab/ct-001-review-tmp (delete after). Record in ct-001/REVIEW.md.
- Not pushed (manager merges). Post-merge: `python -I ct-001/check_live.py` (pre-merge it fails 11/12 as expected)
  and `python ct-001/run_gate.py --autopilot <dir> --live`.

## Decisions
- BambooHR excluded (developer terms bar crawling).
- Lever 19 Nov: "job list returned" counts 126 no-public-page boards (feed answered), index excludes them.
- Workable: answered again on 19 Nov before the 18 Nov Retry-After ended (derived in build_data summary);
  heading says it stops after a few thousand requests, not "by the day".
- Nav still links two retired pages (autopilot skeleton); left for the manager. Autopilot registry must mark them.
