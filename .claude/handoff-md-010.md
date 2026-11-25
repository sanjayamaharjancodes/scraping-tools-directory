# md-010 hand-off (branch worktree-md-010)

Goal: find why Google search impressions fell from about 20 a day to about 1 after 15 Nov 2026, and fix it at the cause.
Linear SAN-181. Do not push; the manager merges.

## State (25 Nov 2026, 22:00 NPT)
- Cause: Google-side, with no site fault. Only deep-position impressions (positions 40-100, mostly US desktop, 0 clicks
  ever) stopped. Top-10 impressions continue. All 7 impressed pages are indexed, and Google's copies date from
  5 Nov (and 12 Nov), before every deploy near the drop. Two Google-side mechanisms remain: a ranking change in the
  November core update (10-24 Nov), or deep impressions no longer being generated. A 17-30 Sep dip with no site change
  had the same signature. Full evidence: md-010/CAUSE.md; raw reads: md-010/gsc-reads.txt.
- Fix: none, because nothing broke. No page changed and no Request indexing was made.
- Live check: `python -I md-010/check.py`, 19/19 PASS, exit 0 (25 Nov 21:58 NPT). It covers robots.txt, the sitemap, and
  canonical, robots meta and X-Robots-Tag on the 7 pages, plus 7 planted faults.
- Repo checks: `python -I ct-005/test_no_counter.py --no-browser`: 10/10 PASS. md-010/check.py is added to TOOLS. The
  browser runs were skipped: this change adds no browser tool.
- `_config.yml` excludes md-010/ from the Pages build.

## Attempts
- Rank check: Google results page 2 showed a CAPTCHA. Stopped, not solved (1 attempt).
- Other-property control: the permission check refused it, and other properties are out of scope (1 attempt; not retried).

## After merge (manager)
- `curl -sI https://scrapetools.scaleturn.com/md-010/CAUSE.md` must answer 404 (excluded from the build).
- `python -I md-010/check.py` must still print ALL PASS.

## Re-check dates (CAUSE.md section 5)
- 2 Dec 2026: daily impressions 24-30 Nov, plus check.py.
- End of the December 2026 core update (began 24 Nov 15:02 UTC; expect by about 8 Dec).
- About 15-16 Dec: compare the week after that end with 3-9 Nov.

## Leftovers outside the repo
- F:/Lab/md-010-scratch-20261125/gsc-reads.txt (the same reads as md-010/gsc-reads.txt).
