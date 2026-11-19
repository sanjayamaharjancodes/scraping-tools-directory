# ct-005 review, 20 Nov 2026

Gate (brief, as ct-003): a fresh blind reviewer ranks our page first on originality against Google's top 3, and not
last on usefulness. Query `should i apply to a job posted 30 days ago`. Google's top 3 for it (Reddit, Quora, a
Facebook post) cannot be read signed out (PREMISE.md), so the next readable results stand in, as on ct-002: #4
smarttalentstaffing.com and #6 a LinkedIn post, then LifeShack (#2) and WayUp (#3) for the sibling query `how long
after a job is posted is too late to apply`, plus two harder comparisons on originality that present data on how long
postings stay up: jobglance.app and secondround.app. Seven pages in all.

## Attempt 1: blind (counts for the gate)

- **Method (ct-002's attempt 2 and ct-003's):** a separate headless Claude (`claude -p`), started in a neutral folder
  outside any repository (this job's temporary directory, `review-ct005/`), with the Read tool only (`--tools Read`),
  no MCP servers (`--strict-mcp-config`), project setting sources only (there are none there) and no saved session
  (`--no-session-persistence`). The prompt named no site, owner or commissioner. The reviewer's inputs sat in the job
  temporary directory, because a folder inside the repository would show whose page is whose.
- **Labels, drawn at random:** R ours, Q smarttalentstaffing, K LinkedIn, P LifeShack, L WayUp, M JobGlance,
  N secondround.app.
- **Inputs, the same for every page:** a fresh browser with no sign-in; cookie and consent banners and any fixed
  overlay covering more than 40% of the viewport removed, with nothing clicked or accepted, but never an element that
  holds more than 30% of the page's text; requests to advertising and analytics hosts blocked on every page (so
  capturing ours loaded no GoatCounter script); a scroll-through so lazy images load; desktop tiles 1280 x 900 CSS px
  and phone tiles 412 x 780 CSS px at 2x, capped at 16 and 12; and each page's main text. Our page was served from a
  local web server so its data file loads. 122 files.
- **Instructions:** read every text in full, view at least the first 4 desktop and 4 phone tiles of every page.
- **Files viewed (reported):** 4 desktop + 4 phone tiles of every page (K has 2 + 3 in all); all seven texts in full.
- **Blindness (reported):** "No. Nothing in my instructions or environment said who commissioned this review or
  which page belongs to whom."

### Verdict

| Criterion | Order (1st to 7th) | Ours (R) |
|---|---|---|
| Originality | R > N > M > P > L > Q > K | **1st** |
| Usefulness | R > M > P > N > L > Q > K | **1st** |
| Trustworthiness | R > P > M > N > L > Q > K | **1st** |

**Gate (ours first on originality, not last on usefulness): passed against the pages that could be read.** None of
Google's top 3 for the target query (Reddit, Quora, the Loopcv Facebook post) could be reviewed: all three refuse a
signed-out reader. Ours ranked first against the target query's #4 (Q) and #6 (K), the sibling query's #2 (P) and #3
(L), and both data pages (N, M). The readable target-query results ranked 6th and 7th on originality; the data
pages 2nd and 3rd. Whether this stands in for the top 3 is the manager's call.

Reasons, condensed:
- **Originality:** R is "the only page built on its own data that you can see": a dated count of 456,597 open jobs
  with tables by age, week posted, ATS and role. N claims tracking data but shows three rounded figures; M combines
  outside studies; the rest are advice or opinion.
- **Usefulness:** R answers the exact search with a conditional answer backed by the share of open jobs older than a
  month, and the age check lets a reader place their own posting.
- **Trustworthiness:** R is dated, states its method and gaps, and its numbers reconcile (bands sum to 456,597; the
  year-old listings 34,422 + 37,150 = 71,572; 22,151 / 36,710 = 60.3%).

### Its defects in our page, and what was done (after the verdict, not re-reviewed)

| Defect | Action |
|---|---|
| The short answer's "Yes" goes further than age data can support (it cannot say whether a posting is still being reviewed) | The answer now opens "Its age alone is no reason to skip it" and ends by saying the figures cannot show whether a given posting is still being reviewed |
| The short answer does not mention coverage (no Workday or iCIMS; Greenhouse is 191,270 of 456,597) | The short answer now says "six ATSs (not Workday or iCIMS)"; the ATS mix is in the ATS table |
| The index files are not published | Kept: the CSV and JSON carry every figure; the index is the Actor's working data |
| Publisher is a scraping-tools site promoting its own job search; drafted with AI | Kept: both disclosed on the page |
| "60.3" in the short answer reads as false precision for an estimate | Kept: 60.3 is an exact count ratio (22,151 of 36,710); the estimate is what it implies about duration, and the page labels that as an estimate |
| No practical steps beyond checking the careers page; a few large boards shape the year-old tail | Kept: advice beyond the data would restate public material; the concentration is stated (163 boards hold half) |

Three more edits from a self-check after the review, not from the reviewer:

| Claim | Edit |
|---|---|
| Six boards "re-date every listing" | The rule only sees boards with 50+ listings and none 14+ days old; one (92 listings, all 1.9 days old) fits a single bulk publish as well. Page, table note and script now say they "re-post their listings or post them all at once" |
| "Old postings are mostly ordinary vacancies" | A title that misses the pool keywords is not a confirmed vacancy: now "mostly carry ordinary job titles", as the section heading says |
| 60.3 open per 100 four weeks back | It leaves those six boards out; the table note now gives the figure with them, 50.8 (already in the JSON) |

After these edits: `build_data.py --check` passes (103 table cells); `run_gate.py` gives 0 findings, 1,317 words and
8.7 phone screens, with no JS errors. The three earlier data pages, each with one added link, also pass their gates
(0 findings; 8.9, 9.1 and 9.9 phone screens).

The reviewer's full reply (with every page's defects) is kept with the job's temporary files, not published.
