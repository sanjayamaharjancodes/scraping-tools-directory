# ct-003 review, 19 Nov 2026

Gate (brief): a fresh blind reviewer ranks our page first on originality against the top 3 Google results, and not
last on usefulness. Query `ai job titles`. Pages compared (ct-003/PREMISE.md): Georgia Tech PE (Google #1), Syracuse
iSchool (#2), a LinkedIn post (#3), and two harder comparisons on originality that analyse title naming:
dbreunig.com (#4) and ivanturkovic.com (#7, cited in Google's AI Overview). Google's top 8 were the same in three
reads on 19 Nov.

## Attempt 1: blind (counts for the gate)

- **Method (ct-002's attempt 2, which passed):** a separate headless Claude (`claude -p`), started in a neutral
  folder outside any repository (this job's temporary directory, `review-ct003/`), with the Read tool only
  (`--tools Read`), no MCP servers (`--strict-mcp-config`), project setting sources only (no user settings or
  hooks) and no saved session (`--no-session-persistence`). The prompt named no site, owner or commissioner.
  Exception to "temp folders under the worktree": the reviewer's inputs sat in the job temporary directory, because a
  folder inside the repository would show the reviewer whose page is whose.
- **Labels, drawn at random:** P ours, N Georgia Tech, M Syracuse, Q LinkedIn, K dbreunig.com, L ivanturkovic.com.
- **Inputs, the same for every page:** a fresh browser with no sign-in (LinkedIn shows its signed-out view);
  cookie and consent banners and any fixed overlay covering more than 40% of the viewport removed, with nothing
  clicked or accepted (this removed Syracuse's sign-up pop-up, and was then applied to all six); a scroll-through
  so lazy images load; desktop tiles 1280 x 900 CSS px and phone tiles 412 x 780 CSS px at 2x, capped at 16 and 12;
  and each page's main text. Our page was served from a local web server so its data file loads. 134 tiles in all.
- **Instructions:** read every text in full, view at least the first 4 desktop and 4 phone tiles of every page.
- **Files viewed (reported):** K 5+4, L 4+5, M 4+4, N 4+4, P 4+4, Q 4+4 (desktop+phone), all six texts in full.
- **Blindness (reported):** "No. Nothing in my instructions or environment said who commissioned this review or
  which page belongs to whom."

### Verdict

| Criterion | Order (1st to 6th) | Ours (P) |
|---|---|---|
| Originality | P > K > L > Q > M > N | **1st** |
| Usefulness | P > L > K > M > Q > N | **1st** |
| Trustworthiness | P > K > L > N > M > Q | **1st** |

**Gate (ours first on originality, not last on usefulness): PASSED.** The top 3 Google results ranked 4th to 6th on
originality.

Reasons, condensed:
- **Originality:** P is "the only page with first-hand data", counting titles across 456,681 listings with a CSV and
  JSON. K has its own analysis (a decoder ring, a trends chart, quoted job descriptions); L is a CTO's opinion with
  others' numbers; Q stitches others' statistics; M and N are career-guide summaries.
- **Usefulness:** P answers the search most directly: which titles employers post, four titles to search for, the
  23.1% training-gig warning and how rare entry-level titles are. It does not say what each job involves.
- **Trustworthiness:** P is dated, states its method and limits, and its counts reconcile (group counts sum to
  19,600; listings per ATS sum to 456,681).

### Its defects in our page, and what was done (after the verdict, not re-reviewed)

| Defect | Action |
|---|---|
| Says nothing about what each title involves, pays or requires | Kept: the index has titles only, no descriptions or salaries (stated in Method and limits). Adding role descriptions would restate public material |
| Headline "3,958 company job boards" not explained in the body | The short answer now says the 19,600 AI-named listings are on 3,958 of the 18,770 boards |
| Six ATSs only, Workday and iCIMS missing | Kept: disclosed in Method and limits |
| One-day snapshot, no trend | Kept: the page is dated; one snapshot is what the index holds |
| Publisher sells the index; AI-drafted | Kept: both disclosed on the page |
| Prolific's 2,874 over the group's 4,521 is 63.6%, not the table's 63.4% | Correct catch of a wording gap: 9 of Prolific's 2,874 AI-named titles fall outside the training group. The text now says it posts 2,865 of the group's listings (63.4%) and 2,874 AI-named titles in all. The script now records each group's largest board by name |

After these edits: `build_data.py --check` passes (108 table cells); `run_gate.py` gives 0 findings, 1,415 words and
9.9 phone screens, with no JS errors.

The reviewer's full reply (with every page's defects) is kept with the job's temporary files, not published;
the comparison pages' defects are not needed for the gate.
