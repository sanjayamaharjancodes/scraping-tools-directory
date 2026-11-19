# ct-003 hand-off (site branch worktree-ct-003; content-autopilot branch ct-003)

Goal: a third original-data page from the job index (manifest + shards, read-only), same method and gates as ct-001
items 1, 2, 4, 5. Brief: D:/Lab/manager/briefs/ct-003.md. Linear SAN-127. Do not push; the manager merges.

## State (19 Nov 2026)
- Premise (ct-003/PREMISE.md): GO, query `ai job titles`. Top 3 = Georgia Tech PE, Syracuse iSchool, a LinkedIn
  post; harder comparisons added: dbreunig.com (#4), ivanturkovic.com (#7, cited in the AI Overview).
- Page `ai-job-titles.html`; data `data/ai-job-titles-2026-11.{csv,json}`; facts `ct-003/facts.json`.
  Script `ct-003/build_data.py` imports ct-002's verify_inputs (SHA-256 refusal) and region().
- Index input: F:/Backups/ct-002-index-snapshot-20261119 (same SHA-256 as the Actor's data/index on 19 Nov).
- Wiring: sitemap, llms.txt (page + 2 data lines), data/pages.json, home card, one link from the posting-days page.
  Not in the shared nav (would need every page and the skeleton changed).
- content-autopilot worktree `.claude/worktrees/ct-003`, branch `ct-003` (7de3c6a): registry entry (kind data) and
  tests/test_data_pages.py for three data pages. Merge it with the site branch so the home card survives a publish.

## Checks (all pass)
- `python -I ct-003/build_data.py --index F:/Backups/ct-002-index-snapshot-20261119 --check ai-job-titles.html`:
  numbers, 108 table cells, widget. Byte-identical outputs across two runs. Positive control: 3 planted errors
  caught (number, table cell, data path).
- `python -I ct-003/run_gate.py --autopilot F:/Lab/assets/content-autopilot --work .tmp-ct003/gate`: 0 findings,
  1,399 words, 9.8 phone screens, interaction ok.
- ct-002 after its one-link edit: build_data --check 65 cells PASS; run_gate PASSED.
- content-autopilot ct-003: tests/test_data_pages.py 7 passed; full suite 191 passed (twice).
- Blind review (ct-003/REVIEW.md): headless `claude -p` in the job tmp folder, Read only, no MCP, no user
  settings; reported blind. Ours (P) 1st of 6 on originality, usefulness and trustworthiness; the top 3 Google
  results ranked 4th-6th on originality. Two defects fixed after (3,958 boards explained; Prolific share reconciled);
  gate after fixes: 0 findings, 1,415 words, 9.9 phone screens.
- `python -I ct-003/check_live.py` before the merge: 12 of 21 fail, as expected (page, data and wiring not live).
  One probe of ct-003/build_data.py gave 503 once, then 404 twice (transient GitHub Pages response).

## Post-merge (manager)
1. Merge the site branch `worktree-ct-003` and content-autopilot branch `ct-003` together.
2. `python -I ct-003/check_live.py` must print ALL PASS.
3. Facts expire after 3 days: `python -I ct-003/build_data.py --refresh-facts --check ai-job-titles.html`, then
   `python -I ct-003/run_gate.py --autopilot <content-autopilot> --live`.
4. The index snapshot is already durable at F:/Backups/ct-002-index-snapshot-20261119 (same build as ct-002).

## Attempts
- Classifier: 3 audit rounds (freelance rule, LLM = Master of Laws, founder/chief-of-staff, spaced-slash split,
  abbreviations merged so tables agree). Each cause found from sample titles.
- Gate: 2 misses on phone height (10.5, then 10.0 screens); fixed by cutting words and widget rows (9.8).
- Phone table clipped (header nowrap): 1 miss, fixed.
- Autopilot suite: first run 81 failed. Cause: the fresh worktree had no git-ignored site/ clone; an end-to-end
  test created it mid-run (19:45:34). Two reruns: 191 passed.

## Notes
- Constraint slip: the first two shell commands of this session began with `cd`. Absolute paths since then.
- Leftovers that go with the worktrees: `.tmp-ct003/` (git-ignored scratch); content-autopilot worktree `site/`
  (git-ignored clone made by its test suite).
