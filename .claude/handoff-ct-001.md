# ct-001 hand-off (branch worktree-ct-001)

Goal: one original-data page from the job-index refresh evidence, retire the 3 thinnest pages, blind review, publish.

## State (19 Nov 2026): steps 1-4 done, step 5 waits on the manager's merge
- ct-001/PREMISE.md: GO. Query `ats public job posting api`; top 3 = fantastic.jobs, cavuno.com, Ashby docs.
- Page `ats-job-posting-api-crawl-data.html`; data `data/ats-board-crawl-2026-11.{csv,json}`; facts `ct-001/facts.json`.
  Built from the refresh evidence, including the complete second 19 Nov pass. The first pass crashed before writing
  its report; its log is used for the comparison.
- Checks, all passing on the branch:
  - `python -I ct-001/build_data.py --evidence <ats-jobs-search>/evidence --crawler-src <ats-jobs-search>/src
    --check ats-job-posting-api-crawl-data.html`: every number traced, 42 table cells matched. A positive control
    caught 3 planted numbers.
  - `python ct-001/run_gate.py --autopilot <content-autopilot>`: 0 findings, about 1,300 words, 8.8 phone screens.
- Blind review (ct-001/REVIEW.md): originality C>D>B>A, usefulness D>C>A>B, ours C. Gate passed. Its defects were
  fixed afterwards; the fixes were not re-reviewed.
- Retired (ct-001/RETIRED.md): web-scraping-apis-with-free-tier, scraperapi-free-trial, scrapingdog-vs-scrapingbee.
- Not pushed. Post-merge:
  - `python -I ct-001/check_live.py`. Before the merge it fails 11 of 13, as expected.
  - Re-run build_data (facts expire 3 days after their date), then `python ct-001/run_gate.py --autopilot <dir> --live`.

## Decisions
- BambooHR excluded: its developer terms bar crawling. The page names it once, as excluded.
- Lever "job list returned" counts boards whose feed answered but whose hosted page is gone; the index excludes them.
- Workable answered again on 19 Nov before the 18 Nov Retry-After ended (derived in the JSON summary).
- `_config.yml` excludes ct-001/ from the Pages build. It can only be verified after the merge.
- For the manager: the shared nav and the autopilot registry still list retired pages, and publish.py would drop the
  two crawl-data lines from llms.txt (RETIRED.md, "Left for the manager").
