# ct-005 premise check

Date: 20 Nov 2026. Result: **GO**. The topic is how old the jobs open on employers' own career pages are. The query
is `should i apply to a job posted 30 days ago`. Our job index answers its factual core (is a posting 30 days old
unusual?) from the posting time of 456,597 open jobs. Every top result is opinion; none has data on posting age.

## How the topic was chosen

The brief names three candidates, built only from our index and different from ct-001 (crawl reliability), ct-002
(posting day and hour) and ct-003 (AI job titles). Candidates were ranked as before: what the data can answer without
bias, whether the top results already publish first-hand data, then demand. No keyword-volume tool is connected, so
demand is what Google itself shows (AI Overview, "People also ask", "People also search for", pages targeting the
query). No volume figures are claimed.

| Candidate | Valid from our index? | Verdict |
|---|---|---|
| ATS market share among hiring companies | **No.** Board counts per ATS follow what discovery found and what each ATS let us crawl (Workable answered for 3,681 of 10,785 boards on 19 Nov); the index has none of Workday, iCIMS or SmartRecruiters. ct-002 and ct-003 reached the same verdict | Dropped |
| Remote share by ATS or industry | **No.** The remote flag is a vendor field on four ATSs and the word "remote" in the location on two (Workable: 24.1% flagged, 3.6% by the word), so shares across ATSs compare definitions. The index has no industry field | Dropped |
| How long postings stay open | **Reframed.** Every job carries the vendor's posting time, so the snapshot gives the age of every open posting. That answers "is a posting N days old unusual?" directly. It does not give durations; the page gives those only as a labelled estimate from how many jobs of each earlier week are still open | **Chosen, as the age of open postings** |

ct-002 dropped "how long postings stay open" because a snapshot does not give durations and because pages below the
top 3 already measure them. Neither reason holds for this page: it answers the age question, not the duration
question, and the two data pages that rank for the duration query (read 20 Nov, below) publish no ages of open
postings. JobGlance is a roundup of other people's studies; secondround.app gives shares with no sample, period or
method. JobNotify, named by ct-002, was not in the top 8 of any query read on 20 Nov.

## Queries read (Google, US English, `hl=en&gl=us&pws=0`, 20 Nov 2026)

- `how long do job postings stay up` (once): AI Overview ("Most job postings stay active for 30 days on standard
  online job boards"); "People also ask" ("What is the 3 month rule for jobs?", "How long should you leave a job
  posting up?"); eight "People also search for" variants. Top 9: Reddit r/careerguidance, Indeed career guide,
  Fishbowl, Glassdoor community, JobGlance, a LinkedIn post, Facebook answers, secondround.app, Hacker News. Not the
  target: it asks for durations, which one snapshot can only estimate.
- `how long after a job is posted is too late to apply` (twice, same order): AI Overview; "People also ask" includes
  "Should I apply to a job that was posted 30 days ago?". Top: Reddit r/AskHR, LifeShack (25 Sep 2026), WayUp
  (23 Oct 2026), Hacker News, Quora, Glassdoor. Not the target: a full answer needs outcome data (interview odds by
  application day), which the index lacks; WayUp cites such studies.
- **`should i apply to a job posted 30 days ago`** (three times; the top 8 organic results were the same, in the same
  order, every time): chosen. An AI Overview answers it ("Yes, you should still apply if the role is a strong match")
  and adds that "the company's official careers page is a better indicator" than job boards; the index is those
  career pages. "People also ask": "If a job was posted 30 days ago, should I still apply?", "Is it worth applying to
  jobs posted a month ago?", "How soon should you apply to a job after it's posted?", "How late is too late to apply
  for a job posting?". "People also search for" lists eight variants, among them "Should I apply to a job posted 2
  weeks ago", "Is it worth applying to a job posted 3 weeks ago" and "If a job was posted 30+ days ago". Recent
  threads target it (Reddit r/jobs, Sep 2026: "Will you apply for a job that was posted 22 days ago?"). Its first
  answer sentence can be a number from the index.

## Target query and reader

- **Query:** `should i apply to a job posted 30 days ago`. Related questions the page also answers: how old open job
  postings are, whether a posting 2 weeks, a month or a year old is unusual for its role, ATS and location, how long
  postings stay up (estimate), and how many old postings are talent pools rather than vacancies.
- **Reader:** a job seeker looking at a posting dated weeks or months ago. Secondary: a recruiter deciding when to
  close or re-post a job, and a developer building a job feed who wants to know how stale listings get.

## Top results (organic; the AI Overview, "People also ask" and video results are not counted)

| # | Page | What it gives the reader | What it does not have |
|---|---|---|---|
| 1 | reddit.com/r/jobs/comments/760uvh ("Found a job posted 30+ days ago on Indeed", about 9 years old) | Not readable by our tools (ct-002 found that the Chrome extension and the fetcher refuse reddit.com). Its snippet: personal views ("If it isn't [a fit], then you shouldn't apply even if the job was posted 30 seconds ago") | Any data |
| 2 | quora.com/Should-I-still-apply-if-the-job-posting-was-posted-over-30-days-ago (60+ answers, about 11 years old) | Not readable signed out: the fetcher got HTTP 403 and a fresh headless browser a Cloudflare bot check. Its snippet: individual answers ("Yes, you can absolutely submit a job application after the deadline") | Any data, by its snippet |
| 3 | facebook.com/Loopmycv/posts/... (Loopcv, about a month old) | Not readable signed out (a login wall). Its snippet: "Should you still apply? Probably. The date on a job posting doesn't always tell you what's happening behind the scenes" | Any data, by its snippet |
| 4 | smarttalentstaffing.com/2019/06/04/should-you-bother-with-job-postings-that-are-over-30-days-old | A staffing firm's blog post: newer postings are more likely open; check for a newer copy of the ad and the company's own site, contact HR, apply if it takes one click | No data or cited source; written in 2019 |
| 6 | linkedin.com/posts/salesmastermind_why-are-job-postings-left-open-for-over-... (Nico C., about a year old) | A post asking why postings stay open over 30 days, with 169 comments from hiring managers and job seekers | Opinions only; no data |

Result 5 is a video, and results 7 (Fishbowl) and 8 (Ask a Manager) show the same Cloudflare check to a fresh
headless browser. Bot checks are not worked around, so those pages are left out. The readable results of the target
query are #4 and #6. Two readable advice pages that rank for the sibling query `how long after a job is posted is too
late to apply`, whose "People also ask" holds the target question, complete the set:

| # (sibling query) | Page | What it gives the reader | What it does not have |
|---|---|---|---|
| 2 | lifeshack.com/resources/job-search/how-soon-after-job-posted-should-you-apply (25 Sep 2026) | Advice by posting age (a week, two weeks, a month or more): check closing dates, review dates and applicant caps on the employer's own site; notes that some systems re-date evergreen postings | No data on how old postings are |
| 3 | wayup.com/guide/community/how-soon-should-you-apply-after-a-job-is-posted (23 Oct 2026) | "Apply within the first two to four days"; cites a Boston University study, StartWire's placement data and TalentWorks' 2017 data (interview odds fall after about 10 days) | Only others' figures; no data on how old open postings are |

Harder comparisons on originality, from `how long do job postings stay up`, because they present data:

| # | Page | What it gives the reader | What it does not have |
|---|---|---|---|
| 5 | jobglance.app/blog/how-long-do-job-postings-stay-up (16 Nov 2026) | A roundup of studies: a 23-day median vacancy duration (30 million postings, 2007-2018), 9.8 days online (St. Louis Fed), The Role Desk's 59% still online after 30 days, a survey of hiring managers | No data of its own ("These papers don't publish durations per job board"); no ages of open postings; nothing to download |
| 8 | secondround.app/guides/how-long-do-job-postings-stay-up (2 Nov 2026) | "about nine in ten are still listed a week after they go up, about four in five after two weeks, and a little more than half after a month", from "the career pages we track" | No sample size, period or method; no breakdown; nothing to download; says a posting's age "tells you little" without showing ages |

Google's top 3 for the target query cannot be read signed out by any of our tools, so, as ct-002 did for an
unreadable Reddit thread, the next readable results stand in: #4 and #6, then LifeShack and WayUp from the sibling
query. JobGlance and secondround.app are added because they are the hardest comparisons on originality. The review
compares these six pages and ours.

## What our page has that they don't

All of it is measured from the job index that ATS Jobs Search built at 04:03 UTC on 19 Nov 2026 (Greenhouse, Lever,
Ashby, Recruitee, Personio, Workable): 456,597 open listings on 18,767 boards after copies and 84 zero timestamps are
removed.

1. **How old open jobs are:** age bands, the median (69.5 days) and the share older than 30 days (69.5%), 90 days
   and a year, so "30 days old" can be read against what employers actually keep open.
2. **An age check:** enter the age of a posting and compare it with all open jobs or with its ATS, location,
   seniority word or role group.
3. **Talent pools versus vacancies:** how many open postings collect applications for no vacancy, how old they are,
   and how small a share of year-old postings they are; how few boards hold half of the year-old postings; boards
   whose every listing looks new.
4. **How fast postings come down (estimate):** open jobs by week posted, against the last 7 days, with its assumption
   stated.
5. **By ATS, role group, seniority and location**, with each ATS's posting-time field named, and board-weighted
   figures beside listing-weighted ones.
6. **A downloadable CSV/JSON and the script** that rebuilds every number from the index files (SHA-256 hashes).

## Limits to state on the page

- One snapshot of open jobs: the ages of postings still up, not how long postings last. Long-lived postings weigh
  more than among all postings ever made.
- Each ATS's posting-time field differs (first_published, createdAt, publishedAt, published_at, published_on);
  a field reset on re-posting makes a job look new. Compare within an ATS more than across.
- Boards, not companies; six ATSs only (no Workday or iCIMS).
- Role groups, pools and seniority come from keyword rules on titles; 27.5% of listings fall in "Other roles".
- Not covered: crawl reliability (ct-001), posting day or hour (ct-002), AI job titles (ct-003).
