# ct-002 reviews, 19 Nov 2026

Gate (brief): a fresh blind reviewer ranks our page first on originality against the top Google results.
Query `what day are most jobs posted`. Pages compared (ct-002/PREMISE.md): Recruiter.com (Google #2), Facebook
fb-answers (#3), ChiefJobs and CNBC (each #4 in different reads). Google #1, a Reddit thread, could not be read by
any of our tools (the Chrome extension and the web fetcher both refuse reddit.com).

## Attempt 1: not blind (does not count for the gate)

- **Set-up:** a fresh general-purpose subagent, read-only by instruction. It got desktop tiles (1280 px, 900 px
  tall), phone tiles (412 CSS px at 2x, 780 CSS px tall) and each page's full text, labelled A-E: A Recruiter.com,
  B Facebook, C ChiefJobs, D ours, E CNBC.
- **Why it was not blind:** the reviewer reported that its session context (this repository and its commit log,
  which name the page) showed that D was ours. A subagent inherits the parent session's git context, and the file
  paths named the site's repository. It said it credited D only for what appears on the page.
- **Verdict:** originality D > A > E > B > C; usefulness D > E > A > C > B; trustworthiness D > E > A > C > B.
- **Its defects in our page, and what was done:**

| Defect | Action |
|---|---|
| Tuesday leads only after the fitted closure rate; raw Thursday 20.3% > Tuesday 20.1% | Already stated on the page, with the raw column shown; kept |
| The short answer says "3 of the 4 weeks"; US and European jobs led only 2 of 4 | Short answer now adds "(2 of 4 for US jobs alone)" |
| Tuesday tops only 2 of 6 ATSs | Already shown (Top day, Weeks led columns, "read close shares as a tie"); kept |
| 12,228 boards in the title against 23,287 in the body | The weekday section now says 12,228 of the 23,287 boards posted the 117,153 jobs |
| US share 46.5% "of open jobs" against 61,239 of 117,153 in the window | Region note gives both bases |
| Hour chart: no values without hover (phones), defaults to UTC | Bars respond to a tap; the chart opens on US-located jobs in US Eastern time. Checked at 412 px with touch: the default group was "US-located jobs (US Eastern time)", and tapping the 14:00 bar showed "14:00 to 14:59: 9.4% (4,966 jobs)" |
| Advice for job seekers is one sentence | Added: by 17:00 Eastern 78.1% of a day's US postings are up (78.4% by 17:00 CET in Europe) |
| Index not published, no named author, AI drafting, own product promoted | Kept: the CSV/JSON carry every count, the script and hashes are public, AI drafting is disclosed, links are labelled as Scaleturn's |
| First phone screen is the site navigation | Site-wide chrome shared by every page; not changed here |

- **Capture issues it noted:** ChiefJobs' cookie banner was not removed while CNBC's was; Recruiter.com's phone
  hero image did not load. Both were fixed for attempt 2: every page got the same banner removal (nothing clicked
  or accepted) and a scroll-through before the capture.

## Attempt 2: blind (counts for the gate)

- **Method change, and why:** a subagent inherits the session's repository context, so the reviewer ran as a
  separate headless Claude (`claude -p`) started in a neutral folder outside any repository, under this job's
  temporary directory. User settings and hooks (`--setting-sources project`) and MCP servers
  (`--strict-mcp-config`) were left out, with the Read tool only and no saved session. The prompt and files named no
  site or owner. Pages were relabelled at random: P ours, Q ChiefJobs, R Recruiter.com, S Facebook, T CNBC.
- **Inputs, the same for every page:**
  - desktop tiles (1280 px, 900 px tall) and phone tiles (412 CSS px at 2x, 780 CSS px tall), with each page's
    full text;
  - the same cookie and consent banner removal on every page, with nothing clicked or accepted;
  - a scroll-through before each capture so that lazy images load;
  - caps of 16 desktop and 12 phone tiles, none exceeded.
- **Files viewed (reported):** 78 tiles, P 16, Q 17, R 13, S 10, T 22, and all five text files in full.
- **Blindness (reported):** "Nothing in my instructions or environment said who commissioned this review or which
  page belongs to whom." It added that its environment held the user's general working rules and account details,
  and that none of them named or referred to any of these sites, companies or pages.

### Verdict

| Criterion | Order (1st to 5th) | Ours (P) |
|---|---|---|
| Originality | P > T > R > S > Q | **1st** |
| Usefulness | P > T > R > Q > S | **1st** |
| Trustworthiness | P > T > R > Q > S | **1st** |

**Gate (ours first on originality against the top Google results): PASSED.**

Reasons, condensed:
- **Originality:** P is "the only page with first-hand data". It also does its own analysis: the closure
  correction, one vote per board, the split by ATS, posting hours and the refresh model. T passes on ZipRecruiter's
  figures. R restates a 2015 SmartRecruiters study. S is a Meta AI summary of anecdotes. Q is advice with no data.
- **Usefulness:** P answers in its first box, hedges ("but only just, and not every week") and gives job seekers,
  recruiters and feed builders something to act on.
- **Trustworthiness:** P dates and sizes everything, names the vendor field it reads, and states its limits. Its
  counts sum to 117,153 and the shares match the counts.

### Its defects in our page, and what was done (after the verdict, not re-reviewed)

| Defect | Action |
|---|---|
| Tuesday's pooled lead rests on Greenhouse (52,601 of 117,153 jobs); by jobs Tuesday tops only Greenhouse and Personio | The ATS note says so, and adds that counting each board once Tuesday tops five of the six ATSs |
| Sample skew not flagged: six ATSs, one autumn window | Method now says employers on other systems (Workday, iCIMS) are not covered, so the shares describe these boards, not the whole job market. The four-week window was already stated |
| Lever and Personio `createdAt` may be creation, not publication | Method says so |
| 461,985 becomes 456,597 without reconciliation | Method says: 5,304 copies and 84 undated jobs left out, leaving 456,597 |
| The 9:00-10:00 Eastern dip is not discussed | Left: the chart shows it and the JSON has every hour |
| Index not published; AI-drafted; own product promoted (disclosed) | Kept as in attempt 1 |

After these edits: `build_data.py --check` passes (65 table cells); `run_gate.py` gives 0 findings, 1,478 words and
9.0 phone screens, with no JS errors.
