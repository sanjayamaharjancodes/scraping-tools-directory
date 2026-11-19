# ct-002 hand-off (branch worktree-ct-002)

Goal: a second original-data page from our job index (manifest + shards), plus ct-001's leftovers (nav, autopilot
registry, publish.py keeping data lines in llms.txt). Brief: D:/Lab/manager/briefs (ct-002 text is in the task
message); ct-001 brief at D:/Lab/manager/briefs/ct-001.md. Linear SAN-118.

## State (19 Nov 2026)
- Worktree: F:/Lab/assets/scraping-tools-directory/.claude/worktrees/ct-002, branch worktree-ct-002.
- Index snapshot (the build the brief cites, builtAt 2026-11-19T04:03:40Z, 23,287 boards, 461,985 jobs), copied
  at 10:28 Nepal time because the Actor keeps only the latest build in data/index:
  `ct-002/index-snapshot/` (git-ignored, not published). SHA-256:
  - index-manifest.json 4c302194d6386bdc305f804c78e82e2e75b3ff7fd7bbcaa370127cfec26e6c7e
  - index-ashby-0.gz 250ff59939e319f8b25e521b5fc4ef456d5af1d0e6ced94ac2b2d94a96c01c56
  - index-greenhouse-0.gz 8bbaac67b4e62e04f6e59fefe927e4501c746165001daec296d3636df004f9e7
  - index-lever-0.gz 51880d82b821dd182ab43dcd948b24797c025b034268ee8ec625ae2e898265dd
  - index-personio-0.gz b7eb3e494a299ccdac055568a4fd2a62c014442897926712741dded64bffdaea
  - index-recruitee-0.gz de78defc708dbb0cc2cad7ff1d68a06f4e73b1008bff1d3cd3ae3216b0097cd0
  - index-workable-0.gz 5c6a507c70a1b287d33a6d93ab4af88774e351621b174ffa06ec2553aa7eb1d3
- `_config.yml` excludes ct-002/ from the Pages build; `.gitignore` ignores the snapshot and `.tmp-ct002/`.
- Next: premise check (topic by data validity, then top-3 originality, then demand).

## Decisions
- Cross-ATS shares (market share, "where companies post") are weak: Workable's lane stopped on a 429 (3,681 ok of
  10,785), six ATSs only. Prefer within-ATS rates (posting age, weekday, remote rate).
- `remote` is defined per ATS in the crawler (src/ats.js); show both the vendor flag and the word "remote".

## Attempts
(none yet)
