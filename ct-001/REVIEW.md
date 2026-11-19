# ct-001 blind review, 19 Nov 2026

## Set-up

- **Reviewer:** a fresh general-purpose subagent with none of the writer's context, read-only. It had no web access
  and was told not to run commands or change files.
- **Query:** `ats public job posting api`. The reader is a developer choosing ATS public job feeds for a job board,
  data pipeline or agent tool.
- **Pages:** labeled at random. The reviewer was not told which page was ours.

| Label | Page |
|---|---|
| A | fantastic.jobs/article/ats-with-api (Google #1) |
| B | developers.ashbyhq.com/docs/public-job-posting-api (Google #3) |
| C | **ours**: ats-job-posting-api-crawl-data.html, served locally from this branch |
| D | cavuno.com/blog/ats-platforms-public-job-posting-apis (Google #2) |

- **Inputs, the same for every page:**
  - desktop screens at 1280 px wide, as 900 px tiles at full resolution;
  - phone screens at 412 CSS px and 2x pixel density, as 780 px tiles;
  - the page's full visible text.
- **Caps:** 16 desktop and 12 phone tiles per page, identical for all four. Only Cavuno (D) reached both caps; its text
  file covered the rest.
- **Files viewed (reported by the reviewer):** every tile: A 22 (10 desktop + 12 phone), B 13 (6 + 7), C 16 (6 + 10),
  D 28 (16 + 12). It read all four text files in full.

## Verdict

| Criterion | Order (1st to 4th) | Ours (C) |
|---|---|---|
| Originality | C > D > B > A | **1st** |
| Usefulness | D > C > A > B | **2nd** (not last) |
| Trustworthiness | C > D > B > A | **1st** |

**Gate (ours first on originality and not last on usefulness): PASSED.**

Reviewer's reasons, condensed:
- **Originality:** C is "the only page with first-hand measurements". These are the dead-address shares, re-check
  rates, seconds per board, Workable's 429 and Personio's burst stop. The planner and the CSV/JSON downloads let the
  reader reuse the data. D did one live call per endpoint. B is the vendor's own documentation. A restates endpoints
  in one repeated paragraph.
- **Usefulness:** D ranks first on breadth: 11 documented, 5 undocumented and 8 gated feeds, with curl calls and
  sample responses. C is "the only page that says how to run these feeds at volume": the rate that held, the
  dead-address rate and the planner. C covers 6 ATSs and has no code or response samples.
- **Trustworthiness:** C states its method, dates, exclusions and AI drafting, and publishes its data. Its core
  figures check out: the address counts sum to 30,928, 11,123 is 36.0% of that, 19,768 of 19,805 is 99.8%, and 37
  failures = 28 vanished boards + 9 Recruitee addresses. D trims its samples without saying so and promises doc links
  it does not give. B's example contradicts its own field table. A has no date, author or sources.

## Defects the reviewer found in our page, and what was done (after the verdict)

| # | Defect | Action |
|---|---|---|
| 1 | The headline "what 30,590 job boards returned" counts all 10,785 Workable addresses, most never requested | Title and H1 now name the 30,928 addresses actually read on 18 Nov. Meta description, JSON-LD, llms.txt, pages.json and the home card were updated to match |
| 2 | "Job list returned" was defined as "answered with jobs", yet 14.6% of lists were empty | Redefined as "a valid job list, empty or not" |
| 3 | The Workable row under an "18 Nov" caption used the second 19 Nov pass (3,834), while the first pass read 3,840 | Footnote now says the row is from the second 19 Nov pass, and names 3,840 for the first |
| 4 | 3,834 + 6,785 leaves 166 of 10,785 unexplained | Now reads: 6,951 checks failed, and at least 6,785 ended within 0.8 s without a request (`workable_failed_outside_timed_burst_19nov` = 166 in the JSON) |
| 5 | Lever lost a net 4 boards, but 8 vanished | Explained from the data: boards without a public page fell from 130 to 126 |
| 6 | Personio: 6,682 boards in 2.8 h is about 1.5 s each, against one a second | That pass also made 3,232 company-name lookups on the same lane: at least 9,914 requests at 1.01 s each (new fields in the JSON) |
| 7 | "57.1% to 75.5%" left out Workable, and the 461,985 total did not say whether Workable was in it | Both stated: five ATSs on 18 Nov, Workable at 96.0% of the addresses it answered; the total includes Workable's 67,009 |
| 8 | A count sat in a percentage column | Cell now reads "96.0% of 3,834 read, then stopped" |
| 9 | "Our job search index" was not explained | The hero and method name and link ATS Jobs Search, made by Scaleturn, which publishes the site |
| 10 | The report files are not published | Kept unpublished: one also holds BambooHR figures, which the page excludes. The page now says so, and that the CSV/JSON carry every count used |
| 11 | The library and Actor links did not say who makes them | Now says Scaleturn makes both and that these are not affiliate links |
| 12 | Endpoints had no `https://` | Added |
| 13 | The planner applies re-check pace to new addresses | The planner now says new addresses were not timed separately |
| 14 | Six ATSs only; no code or response samples; no human author | Left as is. Coverage is what the crawl measured, field docs are linked, and the footer and method disclose AI drafting |
| 15 | The phone navigation takes about 40% of the first screen; the footer's "before buying" line | Site-wide chrome shared by every page; not changed here |

After these fixes:
- `build_data.py --check`: every number traced, 42 table cells matched.
- `ct-001/run_gate.py`: 0 findings, 1,287 words, 8.7 phone screens, no JS errors, interaction probe ok.
- The changed phone areas (hero, re-check table) were inspected at full resolution: no overflow.

The fixes were not re-reviewed by a second fresh reviewer.
