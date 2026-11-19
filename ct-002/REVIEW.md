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
| Hour chart: no values without hover (phones), defaults to UTC | Bars respond to a tap; the chart opens on US-located jobs in US Eastern time |
| Advice for job seekers is one sentence | Added: by 17:00 Eastern 78.1% of a day's US postings are up (78.4% by 17:00 CET in Europe) |
| Index not published, no named author, AI drafting, own product promoted | Kept: the CSV/JSON carry every count, the script and hashes are public, AI drafting is disclosed, links are labelled as Scaleturn's |
| First phone screen is the site navigation | Site-wide chrome shared by every page; not changed here |

- **Capture issues it noted:** ChiefJobs' cookie banner was not removed while CNBC's was; Recruiter.com's phone
  hero image did not load. Both were fixed for attempt 2: every page got the same banner removal (nothing clicked
  or accepted) and a scroll-through before the capture.

## Attempt 2: blind

(in progress)
