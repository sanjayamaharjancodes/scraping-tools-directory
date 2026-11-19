# ct-001 hand-off (branch worktree-ct-001)

Goal: one original-data page from the job-index refresh evidence, retire the 3 thinnest pages, blind review, publish.

## State (19 Nov 2026, 09:45 local)
- PREMISE.md done: query `ats public job posting api`; top 3 = fantastic.jobs, cavuno.com, developers.ashbyhq.com. GO.
- ct-001/build_data.py writes data/ats-board-crawl-2026-11.{csv,json} and ct-001/facts.json from the evidence dir.
  Run: `python -I ct-001/build_data.py --evidence <apify-actors>/ats-jobs-search/evidence --crawler-src <...>/src`
  `--check <page>` fails on any page number not in the data.
- 19 Nov figures: second pass (r2) when evidence/refresh-2026-11-19.json exists, else first pass (Lever partial).
- Retired (noindex, out of sitemap/llms/pages.json/index cards, note box links): web-scraping-apis-with-free-tier,
  scraperapi-free-trial, scrapingdog-vs-scrapingbee. Audit: ct-001/audit_pages.py.
- _config.yml excludes ct-001/ from the Pages build.

## Next
- Write ats-job-posting-api-crawl-data.html; run build_data --check; autopilot checks.py (check_net off pre-merge).
- Screenshots desktop+phone (ours + 3 results), blind reviewer subagent, REVIEW.md, RETIRED.md.
- No push (manager merges). Post-merge: live 200, sitemap lists the page, checks with network.

## Decisions
- BambooHR excluded (its developer terms bar crawling; dropped from the crawler on 18 Nov).
- Workable 19 Nov: lane stopped after ~3,840 answers in both passes; rest failed without a request.
- Nav still links two retired pages (shared skeleton in content-autopilot); left for the manager.
