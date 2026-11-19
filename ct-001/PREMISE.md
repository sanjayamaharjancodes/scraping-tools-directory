# ct-001 premise check

Date: 19 Nov 2026. Result: **GO**. Our crawl data beats the current top 3 on originality.

## Target query and reader

- **Query:** `ats public job posting api` (Google, US English, `hl=en&gl=us&pws=0`, read 19 Nov 2026).
- **Reader:** a developer building a job board, a job-data pipeline or an AI-agent tool. They already know that
  Greenhouse, Lever, Ashby, Workable, Recruitee and Personio publish keyless job feeds. They need to know what happens
  when those feeds are read at scale: how many discovered board addresses are dead, which feeds fail or rate-limit
  and why, how many jobs a board holds, and how long a full pass takes.

## Top 3 Google results (organic; the AI Overview above them is not counted)

| # | Page | What it gives the reader | What it does not have |
|---|---|---|---|
| 1 | fantastic.jobs/article/ats-with-api, "6 ATS Platforms with Public Job Posting APIs" | One endpoint and a curl/PowerShell line for each of Ashby, Greenhouse, Lever, Personio, Recruitee and Workable, then a pitch for the vendor's aggregated jobs API | No measurement of any kind; no failure, rate-limit or volume figures |
| 2 | cavuno.com/blog/ats-platforms-public-job-posting-apis, "11 ATS Platforms with Public Job Posting APIs [2026]" | Endpoints for 11 documented feeds, 5 undocumented ones and 8 gated ones; one example response per ATS; sync advice; each endpoint confirmed against one live employer on 29 Oct 2026 | Each feed tried once on one employer; nothing on dead boards, error or rate-limit rates, jobs per board or crawl time |
| 3 | developers.ashbyhq.com/docs/public-job-posting-api, "Ashby Job Postings API" | The official field reference for one ATS | One vendor only; no behaviour at volume |

## What our page will have that they don't

All of it is measured from our own job-index refresh, the daily job that re-reads every known board:

1. **Scale.** 30,928 candidate board addresses validated on 18 Nov across Greenhouse, Lever, Ashby, Recruitee and
   Personio (Workable's lane stopped on an HTTP 429 that day, so none of its 10,785 candidates was read), then 30,590
   boards re-checked on 19 Nov, Workable included. The top results each test one employer per ATS.
2. **Dead-address rates per ATS.** For example, 3,654 of 10,154 Greenhouse candidates answered "not a board". No
   ranking page publishes this. It decides how much of a crawl budget is wasted.
3. **Failures with their reasons.** Workable's 429 with `Retry-After: 84362` (about 23 hours) and Personio's lane
   stop (20 of 50 answers HTTP 403 or 429), each with the request rate that worked afterwards.
4. **Jobs per board and empty boards per ATS**, from the 395,365 jobs in the 18 Nov index.
5. **Pace.** Seconds per board per ATS from the log timestamps, which show what one machine can re-read in a day.
6. **Day over day.** Live boards and jobs per ATS on 18 and 19 Nov, plus two passes of 19 Nov about 2.4 hours apart.
7. **A downloadable CSV and the script** that rebuilds every number from the refresh's own report files.

What they have that ours will not repeat: endpoint lists for ATSs we do not crawl, and example payloads. Our page
names the endpoint it measured for each ATS and links the vendors' own docs instead of restating them.

## Limits to state on the page, so the originality claim stays honest

- Only two days of refresh reports exist (18 and 19 Nov 2026), so the page shows a day-over-day change, not a trend.
- Board addresses come from Common Crawl. Shares are of the addresses we found, not ATS market share.
- Workable stopped answering partway through the 19 Nov pass. Its numbers cover the boards it answered before the
  stop.
- BambooHR was read in the first 18 Nov run and then dropped, because its developer terms bar crawling. Its numbers
  are excluded everywhere.

## Alternatives considered

- `greenhouse lever ashby job board api scraping`: a web search (not Google) returned only Apify Store listings,
  product pages rather than articles, so it is a weaker match for a data page.
- `scraping ATS job boards rate limits`: the same search found no page that publishes rate-limit figures. It is
  a narrower query that the target page can still answer.
