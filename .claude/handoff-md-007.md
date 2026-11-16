# md-007 hand-off (final)

Task: privacy-policy disclosures, site-connection code, autopilot template and links, favicon, sitemap dates on the
three Scaleturn sites. Full record: mandala branch `md-007` (head `183a43c`, not pushed), file
`memory/business/assets/scraping-tools-directory.md`, section "AdSense readiness ... (md-007)"; requirements and check
scripts in `memory/business/assets/scrapetools-md-007/`.

Branches `md-007` (pushed; each fast-forwards from its main at hand-off time):
- scaleturn-site `eed3130`, scraping-tools-directory (this repo, head = this note's commit), getting-paid-nepal `e32f14b`,
  content-autopilot `f08c752` (merge of the 16 Nov run-state commit; tomorrow's 10:30 run-state commit will need
  another merge or rebase).

Status: all steps done. Auxiliary worktrees removed. Deploy scaleturn-site with or before the subdomains, then run
`python -I readback_md007.py` (from the mandala folder above): must print 38/38.
