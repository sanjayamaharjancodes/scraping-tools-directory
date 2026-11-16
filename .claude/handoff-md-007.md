# md-007 hand-off

Task: privacy-policy disclosures, site-connection code, autopilot template, favicon and sitemap dates on the three
Scaleturn sites. Requirements: mandala branch `md-007`, `memory/business/assets/scrapetools-md-007/requirements.md`
(commit `99f7217`, written before any site change). Check scripts sit next to it.

Worktrees (branch `md-007` in each; remove after pushing):
- scraping-tools-directory: `.claude/worktrees/md-007` (this one)
- scaleturn-site, getting-paid-nepal, content-autopilot (base `8b5e2a7`, local main), mandala: `<repo>/.claude/worktrees/md-007`

Steps:
1. [x] Requirements committed (mandala `99f7217`).
2. [x] scaleturn-site `e543fbd` (pushed): code snippet in 5 heads, privacy rewrite, footer/About/README, favicon, sitemap.
3. [x] scrapetools `a89befc`, gettingpaid `1e6e711` (pushed): privacy says no ad code here; sitemap lastmod.
4. [ ] content-autopilot: skeleton footer, gate rules `footer` + `kept_links`, refresh brief, README,
       tests/test_refresh_links.py, tests/__init__.py (so `python -I -m unittest` runs the suite). Full suite pending.
5. [x] readback_md007.py: 36/36 on local previews; live before deploy 24/37 (negative control).
       Links 634/0, tags 30/0, publish list PASS, sitemap lastmod 16/16.
6. [ ] fresh reviewer on the privacy text; push content-autopilot; record section in mandala; report to manager.
