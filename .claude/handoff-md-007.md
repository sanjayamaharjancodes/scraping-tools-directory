# md-007 hand-off

Task: privacy-policy disclosures, site-connection code, autopilot template, favicon and sitemap dates on the three
Scaleturn sites. Requirements: mandala branch `md-007`, `memory/business/assets/scrapetools-md-007/requirements.md`
(commit `99f7217`, written before any site change).

Worktrees (branch `md-007` in each; remove after pushing):
- scraping-tools-directory: `.claude/worktrees/md-007` (this one)
- scaleturn-site, getting-paid-nepal, content-autopilot (base `8b5e2a7`, local main), mandala: `<repo>/.claude/worktrees/md-007`

Steps:
1. [x] Requirements committed (mandala `99f7217`).
2. [ ] scaleturn-site: code snippet on 5 pages, privacy rewrite, footer/about/README, favicon, sitemap lastmod.
3. [ ] scrapetools + gettingpaid: privacy text true to "no ad code here"; gettingpaid about; sitemap lastmod.
4. [ ] content-autopilot: skeleton footer, gate rules (footer links, kept body links on refresh), tests.
5. [ ] readback_md007.py on local previews; repo checks; fresh reviewer on privacy text.
6. [ ] push md-007 (site repos, content-autopilot); record section in mandala; report to manager.
