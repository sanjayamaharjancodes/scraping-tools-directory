# md-004 hand-off (content audit + fixes across the three scaleturn.com sites)

Status: work done, branches pushed, waiting for manager verify + merge. Manager rule (15 Nov): push only `md-004`
branches, never main; the manager fast-forwards main (= deploy) and reads URLs back.

Branches (all pushed to origin as `md-004`, all fast-forward from origin/main):
- scaleturn-site: 7031988, 1081d21, ecf6769 (worktree F:/Lab/assets/scaleturn-site/.claude/worktrees/md-004)
- getting-paid-nepal: 0da5371, d600632 (worktree F:/Lab/assets/getting-paid-nepal/.claude/worktrees/md-004)
- scraping-tools-directory: 92f8a5c, 7b63e5f, 574a5ee, 4a6d0a5, c84910e + this note (local branch worktree-md-004)
- mandala: 46849f5 (audit, committed first), then the record section, fact-check and proofs

Proof folder: F:/Lab/mandala memory/business/assets/scrapetools-md-004/
- audit.md, factcheck.md, readback.py (35 changed URLs + 1 must-not-serve path)
- readback: 35/35 on local previews (dot-folder check skipped locally), 1/36 live before merge (expected)
- sitelinks 711 links 0 problems; tags balanced on 33 pages; gp_examples PASS; st_freetier PASS;
  verify_gp 16/16; quotes 13/13

After merge: `python -I readback.py` must print 36/36. Then remove the three site worktrees with
`git -C <repo> worktree remove <repo>/.claude/worktrees/md-004`.

Follow-ups (not md-004): the autopilot template footer lacks the scaleturn.com and Contact links; the itch.io
chiptune listing's "fails unless zero" claim; root favicon 404; when to re-review is in the record section.
