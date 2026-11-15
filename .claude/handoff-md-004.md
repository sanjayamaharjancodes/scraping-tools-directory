# md-004 hand-off (content audit + fixes across the three scaleturn.com sites)

Status: work done, branches pushed, waiting for manager verify + merge. Manager rule (15 Nov): push only `md-004`
branches, never main; the manager fast-forwards main (= deploy) and reads URLs back.

Branches (all pushed to origin as `md-004`):
- scaleturn-site: 7031988, 1081d21 (worktree F:/Lab/assets/scaleturn-site/.claude/worktrees/md-004)
- getting-paid-nepal: 0da5371, d600632 (worktree F:/Lab/assets/getting-paid-nepal/.claude/worktrees/md-004)
- scraping-tools-directory: 92f8a5c, 7b63e5f, 574a5ee, plus footer Contact + free-tier fixes and this note (local branch worktree-md-004)
- mandala: 46849f5 (audit, committed first), 0a43365 (record section, fact-check, proofs)

Proof folder: F:/Lab/mandala memory/business/assets/scrapetools-md-004/
- audit.md, factcheck.md, readback.py (35 changed URLs + expected text)
- readback: 35/35 on local previews, 0/35 live before merge (expected)
- sitelinks 697 links 0 problems; gp_examples PASS; st_freetier PASS; verify_gp 16/16; quotes 13/13

After merge: `python -I readback.py` must print 35/35. Then remove the three site worktrees with
`git -C <repo> worktree remove <repo>/.claude/worktrees/md-004`.

Follow-ups (not md-004): autopilot template footer lacks scaleturn.com link; itch chiptune listing's
"fails unless zero" claim; root favicon 404; re-review only after recrawl evidence (see record section).
