# ct-002 premise check

Date: 19 Nov 2026. Result: **GO**. The topic is the day and hour that companies post jobs. Our job index answers it
from about 460,000 dated open jobs. The top results for the query cite a 2015 vendor study, a Meta AI summary of
Facebook posts, and an advice article that names no data.

## How the topic was chosen

The brief asks for the topic to be chosen by search demand, from our own index data only. Candidates were ranked
in this order: what the data can answer without bias, then whether the top 3 results already have first-hand data,
then demand. No keyword-volume tool is connected, so demand below is what Google itself shows for each query (AI
Overview, "People also ask", "People also search for", and how many pages target it). No volume figures are claimed.

| Candidate | Valid from our index? | Top results (Google, read 19 Nov) | Verdict |
|---|---|---|---|
| ATS market share / where companies post jobs | **No.** Coverage decides the shares. On 19 Nov Workable answered for only 3,681 of 10,785 boards before its 429 stop. The index covers 6 ATSs and none of Workday, iCIMS or SmartRecruiters. ct-001 already says board counts are not market share | Not read | Dropped |
| Remote share by ATS | **Weak.** The crawler takes `remote` from a vendor field for Lever, Ashby, Recruitee and Workable, and from the word "remote" in the location for Greenhouse and Personio. For Workable that is 24.1% flagged against 0.1% by the word. The shares would compare definitions, not employers | Web search: Robert Half, FlexJobs and Indeed publish their own large datasets | Dropped: invalid, and no originality edge |
| How long job postings stay open | **Partly.** A single snapshot gives the age of the jobs still open. It does not give how long postings stay up | `how long do job postings stay open`: Reddit, Indeed career guide, Canvider. Below them, JobNotify and JobGlance publish 2026 duration-tracking data that answers the question directly | Dropped: the data does not answer the question literally, and others already measure it |
| **What day jobs are posted** | **Yes.** Every job has a posting timestamp from the vendor's own feed. The weekday and hour of a posting do not depend on how many boards were found or how long a job stays open. Workable gives a date only, so it counts for weekdays but not for hours | `what day are most jobs posted`: see below | **Chosen** |

Demand evidence for the chosen query (Google, US English, `hl=en&gl=us&pws=0`, 19 Nov 2026):
- an AI Overview answers it, and four "People also ask" questions follow ("What day do jobs usually get posted?",
  "What day of the week are most jobs offered?");
- "People also search for" lists seven variants: "What day are most jobs posted in usa", "When do new jobs get
  posted", "Best day to apply for a job", and others;
- pages updated in 2025-2026 target the topic (careeragents.org 1 Nov 2026, apollotechnical.com 2025).

## Target query and reader

- **Query:** `what day are most jobs posted`. Related questions the page also answers: what time jobs are posted,
  and whether this differs by ATS and region.
- **Reader:** a job seeker deciding when to check career pages, or a recruiter deciding when to post. The secondary
  reader suits this site: a developer running a job feed or job-board crawler who wants to know when new postings
  appear, so a daily refresh catches them.

## Top 3 Google results (organic; the AI Overview and forum carousels are not counted)

The first organic result is a Reddit thread (r/jobsearchhacks, "What time do recruiters usually post new job
openings..."). None of our tools can read it: the Chrome extension refuses reddit.com for safety reasons, and the
web fetcher refuses reddit.com and old.reddit.com. Its Google snippet shows a discussion of personal impressions.
The review therefore uses the first three organic results that can be read, results 2 to 4:

| # | Page | What it gives the reader | What it does not have |
|---|---|---|---|
| 2 | recruiter.com/recruiter-today/why-tuesday-is-a-job-seekers-favorite-day (6 Apr 2015) | A summary of SmartRecruiters' 2015 analysis of 270,000 US and Canadian jobs: Tuesday is the top posting day, 58% of jobs are posted Monday to Wednesday, and posting peaks around 11 AM. Then a Q&A with that vendor's CEO | Data from 2015, from one vendor's customers. No time zone for "11 AM", no per-day table, no breakdown by ATS or region, and the data is not published |
| 3 | facebook.com/fb-answers/what-day-of-the-week-are-most-jobs-posted ("Summarized by Meta AI") | An AI summary that says Wednesday and Friday, beside users' posts (one recruiter says Amazon posts on Fridays) | No data of its own. It contradicts result 2, and its sources are anecdotes |
| 4 | chiefjobs.com/the-best-days-and-times-of-the-week-to-post-on-job-boards (Dec 2024, updated Jul 2025) | Advice for employers on posting times, based on job-seeker behaviour | Says "studies indicate" but names no study and gives no numbers |

## What our page will have that they don't

All of it is measured from the job index that ATS Jobs Search built at 04:03 UTC on 19 Nov 2026: 23,287 company
boards and 461,985 open jobs across Greenhouse, Lever, Ashby, Recruitee, Personio and Workable. Each job's posting
time comes from the vendor's own feed.

1. **Weekday shares of current postings.** Jobs posted in the last four full weeks before the snapshot, by weekday,
   so every weekday is counted four times, with all open jobs alongside.
2. **Hour of day**, in UTC and, for jobs located in the US, in US Eastern time, so "11 AM" has a time zone. A
   selector shifts the hours to the reader's own time zone.
3. **By ATS and region.** The posting day and hour for each of the six ATSs, and for US-located against other jobs.
4. **Weighting stated.** Shares are job-weighted, with each board counted once alongside, because the top 1% of
   boards hold 16-45% of each ATS's jobs. Jobs listed identically on more than one board are counted once.
5. **For job-feed builders:** the share of a day's postings already published by each UTC hour, which shows when a
   daily refresh catches the previous day.
6. **A downloadable CSV/JSON and the script** that rebuilds every number from the index files (SHA-256 hashes
   recorded).

## Limits to state on the page

- It is one snapshot of open jobs, not a log of every posting. Jobs posted and closed before 19 Nov are missing.
  The four-week window keeps that loss about equal across weekdays.
- Posting time is the vendor's field: Greenhouse `first_published`, Lever `createdAt`, Ashby `publishedAt`,
  Recruitee `published_at`, Personio `createdAt`, Workable `published_on` (a date without a time). Workable
  counts for weekdays only.
- The boards are those our crawler found and could read, not all employers. Shares are within these boards.
- Region comes from the job's location text, so jobs whose location names no country are "other or unknown".
- Not covered: the topic of ct-001's page (crawl reliability, dead boards, rate limits). The board and job totals
  appear only as the size of the sample.
