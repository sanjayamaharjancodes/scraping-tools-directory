# md-010 hand-off (branch worktree-md-010)

Goal: find why Google search impressions fell from about 20 a day to about 1 after 15 Nov 2026, and fix it at the cause.
Linear SAN-181. Do not push; the manager merges.

## State (25 Nov 2026, 22:06 NPT)
- **Cause.** No technical fault on the site (proven); the change came from outside it, and the mechanism is open.
  - Every page with impressions lost them on 15-16 Nov PT, in every position band and country. 0 clicks before or after.
  - All 5 main pages are still indexed, from copies of 5 and 12 Nov. The 15 Nov deploy was never indexed.
  - Favoured: (a) a ranking change during the November 2026 core update (10-24 Nov UTC).
  - Weaker: (b) deep-position impressions no longer being generated. It explains only the deep band. The 17-30 Sep dip was
    deep-only.
  - Full evidence: md-010/CAUSE.md. Raw reads: md-010/gsc-reads.txt.
- **Fix:** none, because nothing broke. No page changed and no Request indexing was made.
- **Live check:** `python -I md-010/check.py`: 19/19 PASS, exit 0 (25 Nov 21:58 NPT). It covers robots.txt, the sitemap,
  canonical, robots meta and X-Robots-Tag on the 7 pages, plus 7 planted faults.
- **Repo checks:** `python -I ct-005/test_no_counter.py --no-browser`: 10/10 PASS, with md-010/check.py added to TOOLS.
  Browser runs were skipped, because this change adds no browser tool.
- `_config.yml` excludes md-010/ from the Pages build.

## Attempts
- Rank check: Google results page 2 showed a CAPTCHA. Stopped, not solved (1 attempt).
- Other-property control: refused by the permission check, and out of scope (1 attempt, not retried).
- CAUSE.md v1 (commit 3e57af3) overclaimed three things, corrected in v2:
  - that top-10 impressions continued;
  - that September had the same signature;
  - that nothing reached Google before the drop.

## After merge (manager)
- `curl -sI https://scrapetools.scaleturn.com/md-010/CAUSE.md` must answer 404 (excluded from the build).
- `python -I md-010/check.py` must still print ALL PASS.

## Re-check dates (CAUSE.md section 5)
- **2 Dec 2026:** daily impressions for 24-30 Nov by page and country, plus check.py.
- **End of the December 2026 core update:** it began 24 Nov 15:02 UTC; expect the end by about 8 Dec.
- **About 15-16 Dec:** compare the week after that end with 3-9 Nov.

## Option for the manager (not taken; the brief allows Request indexing only for fixed URLs)
- Google's index copies of the 5 main pages are 13-20 days old, and the December core update is rolling. Requesting
  indexing for them would let Google assess the current pages. Recommended only if the manager agrees.

## Leftovers outside the repo
- F:/Lab/md-010-scratch-20261125/gsc-reads.txt (the same reads as md-010/gsc-reads.txt).
