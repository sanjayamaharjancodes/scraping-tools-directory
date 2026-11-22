# md-009 hand-off (branch worktree-md-009-firecrawl)

Goal: first tested result on ScrapeTools: Firecrawl on the methodology.html method, free tier; add to the comparison
only if it earns a place. Brief: D:/Lab/manager/briefs/md-009.md. Linear SAN-161. Do not push; the manager merges.

## State (22 Nov 2026)
- Pre-registration committed before any keyed request (f541565): panel data/benchmark-panel-2026-11.json, rule R1-R4.
- Run 22 Nov 05:41-05:57 UTC: raw data/firecrawl-benchmark-2026-11-22.{csv,json}. 95 requests, 96 credits with the
  smoke request (1,025 -> 929). General panel 80/85 (94.1%); static 65/65; JS 15/20 (js-delayed 0/5); protected
  10/10; median 2.22 s, p95 2.97 s (n 80). $1.05 per 1,000 passed pages on Standard.
- Ruling YES (md-009/RULING.md). Pages: index.html, cheapest-web-scraping-api.html, methodology.html + truth fixes
  (about, scraperapi-free-trial, scraperapi-vs-bright-data), llms.txt, pages.json, sitemap, README, style.css.
- Checks: RULING.md section 4. Originality gate (section 5): blind headless `claude -p` in a neutral folder ranks the
  home page 1st of 4 on originality, usefulness and trust (counting run); two earlier subagent runs agreed but were
  not blind (git snapshot in context). Home-page gate still fails as on main: too_long 15.0 screens (main 12.2) and
  21 untraced numbers in the More-guides cards; option: move the results table to methodology.html.
- Rework done (RULING.md section 6): full results on methodology.html#firecrawl-results; index keeps a compact
  summary, the row and the widget entry; index 10,982 px vs main 11,001 px; untraced list identical to main.
- Rework 2 done (RULING.md section 7): ten review items; credits: free plan 1,000 (96 used) + 25 one-time credits
  (unused, source not shown); wording now "on a free-plan account". methodology.html back to LF.
- Reply draft: md-009/reply.md (link live only after merge).
- Key: D:/Lab/secrets/firecrawl/.env (never printed; clipboard cleared).

## Manager notes
- Stale premise: the "8 Tools Compared" page was replaced 5 Nov (f857e04); index.html is a credit-plan price page.
- ToS 5.d.1 bars commercial use "except as expressly authorized by Firecrawl"; Firecrawl's growth team invited the test.
- Reddit (Google result #3) unreadable by plain fetch (403) and blocked by the Chrome extension; #4 used instead.
- data/vendors.json not changed (other pages' widgets would change). A resumed autopilot refresh of the cheapest
  page could drop the hand-added Firecrawl row (the autopilot is paused by STOP).
- refs/backup/w-md-009 (not mine) still points at a pre-squash commit whose raw JSON had billing-period dates.
- One Chrome tab from the first tab group (Firecrawl billing docs, signed in) became unreachable after the extension
  reconnected; it may still be open in a separate window.

## Attempts
- probe stdout encoding: `python -I` ignores PYTHONIOENCODING (2 misses), fixed with sys.stdout.reconfigure.
- Chrome "Couldn't determine which page": a tabs_context read before each action fixed it.
- git index.lock: transient lock from another short-lived git process on this worktree; retry worked (1 miss).
- run_gate local fetch of the site root (5 Nov fact) read the folder: map "" to index.html (1 miss).
- Phone height: home 16.3 -> 15.4 -> 14.9 -> 15.0 screens (main 12.2); cheapest 10.7 -> 10.4 -> 10.1 -> 10.0 (x2) -> 8,984 px.
- Originality gate: subagent runs saw this repo's git snapshot (2 runs), so method changed to headless claude -p in a
  neutral folder (1 run, counts). Reviewer 1 found the $4.04 basis slip; fixed before the counting run.
