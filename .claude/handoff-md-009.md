# md-009 hand-off (branch worktree-md-009-firecrawl)

Goal: first tested result on ScrapeTools: Firecrawl on the methodology.html method, free tier; add to the comparison
only if it earns a place. Brief: D:/Lab/manager/briefs/md-009.md. Linear SAN-161. Do not push; the manager merges.

## State (22 Nov 2026)
- Key: D:/Lab/secrets/firecrawl/.env (copied via the dashboard copy button + clipboard, never printed; clipboard
  cleared). Account: u/1 Google sign-in, existing team; free plan 1,000 credits, 1,025 remaining before any request,
  period ends 25 Nov.
- Pre-registered (commit before the run): data/benchmark-panel-2026-11.json (panel, settings, rule),
  md-009/RULING.md, scripts/firecrawl_benchmark.py. _config.yml excludes scripts and md-009.
- Stale premise: the "8 Tools Compared" home page was replaced 5 Nov (f857e04); index.html is now a 4-vendor
  credit-plan page; the 8-vendor table is cheapest-web-scraping-api.html.
- Firecrawl pricing checked 22 Nov on the page itself: Hobby $19/5k, Standard $99/100k, Growth $399/500k,
  Scale $749/1M (monthly billing); 1 credit per scrape incl. 403/404 documents; enhanced proxy +0.

## Next
1. smoke (1 request) and credit delta; 2. run --rounds 5 (background); 3. ruling in RULING.md; 4. page edits if yes;
5. originality gate (fresh subagent); 6. checks (check_live/run_gate where applicable, test_no_counter with scripts/
scanned, links 200, phone+desktop render); 7. md-009/reply.md; 8. report to manager.

## Attempts
- probe stdout encoding: `python -I` ignores PYTHONIOENCODING (2 misses); fixed with sys.stdout.reconfigure.
- Chrome: "Couldn't determine which page" errors after navigations; a tabs_context read before each action fixed it.
