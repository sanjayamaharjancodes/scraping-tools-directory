# md-010: why ScrapeTools' Google impressions fell after 15 Nov 2026

Written 25 Nov 2026, 22:04 NPT (16:19 UTC); first version 21:59 NPT. Evidence read between 21:31 and 21:58 NPT the
same day; the raw reads are in `md-010/gsc-reads.txt`. Search Console's Performance days are Pacific time (PT); every
other time here is UTC unless marked. URL Inspection and Crawl stats display Nepal time (NPT, UTC+5:45); section 3.4
proves it.

## 1. Answer

**No technical fault on the site (proven). The drop came from outside the site; which external mechanism caused it is
not settled.**

- **What fell.** Every page with impressions lost them on the same days, 15-16 Nov PT, in every position band. In 1-15 Nov:
  - deep positions (40-100), mostly US desktop, for queries such as "scraper api pricing";
  - at least 24 top-10 impressions from ten other countries (Brazil 6 at position 6.5, Ecuador 4, Colombia 4, India 3, and
    others; Nepal's 2 are left out as likely our own checks).

  After 16 Nov those ten countries show 0. The old pages' only later top-10 impressions are three on 21 Nov, all from one
  search at position 1 (consistent with a `site:` query). The only other top-10 impressions are on pages that had none
  before.
- **What it cost.** Nothing in visits: 0 clicks in 736 impressions from 24 Aug to 15 Nov, and 0 after.
- **What is proven.**
  - Robots.txt, the sitemap, canonicals, robots tags, status codes and redirects are as they should be (section 4).
  - All five main pages are still indexed.
  - Google's indexed copies of them date from 5 Nov (four pages) and 12 Nov (one page), and the 15 Nov deploy never
    reached the index (section 3.1).
- **Mechanism (a), favoured: a ranking change during Google's November 2026 core update**, which ran from 10 Nov 18:06 to
  24 Nov 14:03 UTC (Search Status Dashboard).
  - The drop falls inside the rollout and hit all pages, bands and countries at once.
  - Googlebot Smartphone fetched every page on 13 Nov, 14:02-14:05 UTC, at the 12 Nov build. It indexed two pages added
    by the content autopilot on 15 Nov. So a site-level content assessment could be part of (a). Nothing available here
    can test that.
  - Against (a): impressions did not fall in the update's first five days (12, 10, 16, 22 and 27 on 10-14 Nov PT, against
    an average of about 12 on 1-9 Nov). Also, "scraper api pricing", the one query still measurable, kept about its
    position (82.2 before, 86.5 on its last days).
- **Mechanism (b), weaker: deep-position impressions stopped being generated.** Results at positions 40-100 are rarely seen
  by people. That could be automated rank checks by a third party, or a change in how Google serves or counts deep result
  pages. It matches the deep band: "scraper api pricing" drew 1-4 impressions on most days (8 once) at positions 60-90 for
  three months. But (b) does not explain the lost top-10 impressions. The 17-30 Sep dip, its best precedent, was deep-only:
  the calculator kept 20 impressions at position 21.3 and the home page 15 at 14.7 (section 3.3).

Either way there is no site fault to fix. So, per the brief, the deliverable is this evidence plus the dated re-check plan
in section 5. No page was changed and no re-indexing was requested, because nothing was fixed. If (a) is confirmed,
the response is a content decision, which this maintenance task does not cover (no new content, no rewrites).

## 2. Before and after: the pages that carried the impressions

Search Console, Web search, 1-15 Nov PT (15 days) against 16-23 Nov PT (8 days). These seven pages are the only ones
with any impression from 24 Aug to 15 Nov (736 in total).

| page | impressions 1-15 Nov | position 1-15 Nov | impressions 16-23 Nov | position 16-23 Nov | in Google's index (URL Inspection, 25 Nov) |
|---|---|---|---|---|---|
| `/scraperapi-cost-calculator.html` | 109 | 58.7 | 3 | 68 | indexed; copy crawled 5 Nov 12:02 UTC |
| `/` | 77 | 51.9 | 4 | 68.3 | indexed; copy crawled 5 Nov 16:55 UTC |
| `/scraperapi-vs-scrapingbee.html` | 35 | 79.1 | 2 | 80.5 | indexed; copy crawled 5 Nov 12:00 UTC |
| `/scraperapi-vs-bright-data.html` | 21 | 59.9 | 0 | - | indexed; copy crawled 5 Nov 12:00 UTC |
| `/web-scraping-api-cost-per-1000-requests.html` | 20 | 92.3 | 3 | 65.3 | indexed; copy crawled 12 Nov 14:11 UTC |
| `/about.html` | 3 | 5.3 | 1 | 1 | (not inspected) |
| `/methodology.html` | 2 | 1.5 | 1 | 9 | (not inspected) |
| whole site | 213 | 57.2 | 10 | 44.7 | 9 indexed, 5 not (unchanged set, below) |

**Daily, whole site, PT:**
- 12 Nov 16 impressions (position 38.9), 13 Nov 22 (46.9), 14 Nov 27 (45.6), 15 Nov 20 (78.2), 16 Nov 4 (90.8), 17 Nov 1,
  18 Nov 0.
- 19-23 Nov: 2, 1, 1, 0, 1, all at positions 1-6.5.

Every one of the five main pages stopped on the same days (per-page daily series in `gsc-reads.txt`). The 16-23 Nov
figures for `/`, the calculator and cost per 1,000 include one impression each on 21 Nov, at positions 5, 10 and 4. On
that day the site total was 1 impression at position 1, so all three came from one search.

**By country**, 1-15 Nov against 16-23 Nov: the United States 159 to 8; Germany 10 to 1; Brazil, Ecuador, Colombia, India,
Switzerland, Malaysia, South Africa, Peru, the Netherlands and Singapore 24 (all at average positions 2-10) to 0.
**By device:** desktop 197 to 9, mobile 16 to 1.

**Queries** (31 named before; 4 named after). Each of the top ones lost almost all its impressions:

| query | impressions 1-15 Nov | position | impressions 16-23 Nov | position |
|---|---|---|---|---|
| "scraper api pricing" | 35 | 82.2 | 2 | 86.5 |
| "scraperapi pricing" | 18 | 54.1 | 0 | - |
| "scraper api cost" | 14 | 88.3 | 1 | 95 |
| "bright data web scraper api pricing" | 10 | 75.2 | 0 | - |
| "scrapingbee vs scraperapi" | 8 | 87 | 1 | 95 |

## 3. Candidates tested

### 3.1 Site changes deployed around 14-16 Nov: no technical fault, and the deploy nearest the drop was never indexed

- **Builds (GitHub Pages, UTC):**
  - 12 Nov 04:52, `64b034a`: new page;
  - 14 Nov 04:58, `a32d222`: new page;
  - 15 Nov 16:07, `f134f58`: the md-004 footer, About and free-tier edits;
  - 16 Nov 13:41, `83a7b98`: a note removed from the repository;
  - 17 Nov 05:08, `a5f9d67`: new page.
- **Head tags.** From the 12 Nov build to the 17 Nov build, the seven pages above changed no `<title>`, canonical, robots
  meta, `<h1>` or meta description (`git diff 64b034a a5f9d67`). Their edits were:
  - a footer Contact link and a footer link to scaleturn.com;
  - the About wording;
  - two home-page cards and one body link.
- **robots.txt and redirects.** robots.txt has one commit, `506ab21` of 25 Jul 2026. `http://` and the github.io address
  both 301 to the https page, and each page answers 200 at its own URL. No page in the set has a noindex or an
  X-Robots-Tag. The live check is in section 4.
- **Google's indexed copies.**
  - They date from 5 Nov (four pages) and 12 Nov (cost per 1,000).
  - The calculator's crawled HTML (URL Inspection, "View crawled page") still says "an independent comparison site". That
    wording was replaced in the 5 Nov 15:37 UTC build.
  - The copy also lacks the 11 Nov nav links and the 15 Nov footer.
- **The md-004 deploy, 15 Nov 16:07 UTC (08:07 PT, the 15th).** This is the change closest to the drop. The 15 Nov PT day
  runs from 08:00 UTC on the 15th to 08:00 UTC on the 16th, and that day's position fell to 78.2 from 45.6. But the md-004
  version of these pages never reached Google's index:
  - URL Inspection on 25 Nov still shows the 5 Nov copies (12 Nov for cost per 1,000), so no later fetch was indexed.
  - Crawl stats' example list has two 15 Nov fetches, at 12:19 and 14:57 UTC, both before the deploy, and none after it
    until `/` at 17 Nov 10:38 UTC, after the 16 Nov PT day had ended. The list holds 80 examples, of about 94 successful
    fetches the report counts in 90 days.
- **What did reach Google before the drop (untested, part of mechanism a).**
  - The 13 Nov smartphone sweep fetched every page at the 12 Nov build. That build had the 9-12 Nov changes:
    - autopilot pages for cost per 1,000 and ScrapeCreators pricing;
    - an autopilot refresh of ScraperAPI vs Bright Data;
    - the 11 Nov nav links and free-tier refresh.
  - The 15 Nov fetches indexed two autopilot pages: scrapecreators-pricing and scrapingdog-vs-scrapingbee.
  - Whether Google's site-level assessment used them cannot be tested from here.
- **Removals:** none in the last 6 months. **Manual actions:** none. **Security issues:** none.

### 3.2 The structured-data episode: not the cause (timing)

- Dataset markup first entered the repository in `cd7b6d4`, committed 19 Nov 04:13 UTC (18 Nov PT). That was after the
  drop, and on data pages that had never had an impression.
- The Datasets report (last update 24 Nov) shows 3 valid items and 0 invalid. Its "Missing field license" issue shows
  validation Passed and 0 items.

### 3.3 Search Console, page by page: the pages are still indexed; their impressions stopped

- **URL Inspection, top five pages:**
  - all show "URL is on Google / Page is indexed";
  - crawl allowed, fetch successful, indexing allowed;
  - the user-declared and the Google-selected canonical are both the page itself.
- **Page indexing** (last update 16 Nov): 9 indexed, 5 "Discovered - currently not indexed". The five are
  cheapest-web-scraping-api, disclosure, privacy, scraperapi-free-trial and web-scraping-apis-with-free-tier. That issue was
  first detected 18 Aug, and none of the five ever had an impression, so no page left the index at the drop.
- **Sitemaps:** read 19 Nov, Success, 15 pages.
- **Crawl stats:** "Host had no problems in the last 90 days". The only 404s were `/favicon.ico`, before 5 Nov.
- **September control, same property:**
  - Totals: 3-16 Sep, 96 impressions at position 52.6; 17-30 Sep, 34 at 18.9; 1-14 Oct, 125 at 36.2.
  - "scraper api pricing" went 30, then 4, then 21, at positions 63.1, 64.3 and 67.8.
  - Only one build ran between 14 Aug and 4 Nov: 30 Sep 13:18 UTC, a one-line README change. The September 2026 spam update
    began 24 Sep 16:15 UTC, a week after the dip started.

  So deep impressions have vanished and returned once before with no cause on our side. **That dip differs from
  November's**, though: the calculator (20 at 21.3) and the home page (15 at 14.7) kept their shallower impressions, while
  in November they kept 3 and 4, at about position 68.

### 3.4 Google-side, with evidence

- **Search Status Dashboard** (`status.search.google.com/incidents.json`, read 25 Nov):
  - "November 2026 core update": 10 Nov 18:06 UTC to 24 Nov 14:03 UTC;
  - "December 2026 core update": began 24 Nov 15:02 UTC, still active;
  - "September 2026 spam update": 24 Sep to 8 Oct.
- **Data anomalies page** (support.google.com/webmasters/answer/6211453, read 25 Nov): the only November entry is a
  logging error in the *Generative AI* report for 9-11 Nov. It lists nothing for the Web search report on 15-16 Nov.
- **Time zones.** URL Inspection gives the calculator's crawl as "Nov 5, 5:47:41 PM", and its index copy predates 5 Nov
  15:37 UTC.
  - Read as NPT, that crawl was 12:02 UTC, which fits.
  - Read as PT, it would be 6 Nov 01:47 UTC, after the replaced wording had gone live.

  So the display is NPT. Crawl stats shows the same time as URL Inspection for the 12 Nov crawl, so it uses NPT too.

### 3.5 Not tested, and why

- **Rank check.** A Google search for "scraper api credit cost" (position 15.5 before the drop) loaded page 1 without
  ScrapeTools. Page 2 returned Google's "unusual traffic" CAPTCHA; it was not solved and no further searches were made.
  This check is what would separate (a) from (b) directly (section 5).
- **Other properties as a control** (gettingpaid, makeyeti). The brief puts them out of scope, and the session's
  permission check refused opening their reports.

## 4. Live state, as it should be (`python -I md-010/check.py`)

For each of the seven pages in section 2:
- **robots.txt** answers 200, matches this repository's copy and lets Googlebot fetch the page.
- **sitemap.xml** answers 200 and lists the page.
- **The page** answers 200 at its own URL, with no redirect and no X-Robots-Tag. It has exactly one canonical, pointing to
  itself, and no robots meta tag.

Seven planted faults must each be caught: a blocking robots.txt, a missing sitemap entry, a redirect, an X-Robots-Tag
noindex, a noindex meta tag, a canonical to another page, and two canonicals.

Run 25 Nov 2026 21:58:25-21:58:30 NPT: `19 of 19 passed`, `ALL PASS`, exit 0.

Three other pages have carried `noindex, follow` on purpose since 19 Nov (ct-001 retired them): scraperapi-free-trial,
scrapingdog-vs-scrapingbee and web-scraping-apis-with-free-tier. None of them had an impression before the drop.

## 5. Re-check plan (dated)

1. **2 Dec 2026** (Search Console data to about 30 Nov).
   - Run `python -I md-010/check.py`.
   - Read daily Web impressions for 24-30 Nov, by page and by country, plus the "scraper api pricing" daily series.
   - **Both bands back near their old levels** (deep: calculator about 55, "scraper api pricing" about 85; top-10: the
     non-US countries): the update's swing has reversed; record it and keep watching.
   - **Only the deep band back:** (b) explains that band, and the top-10 loss stays open.
   - **Neither band back:** wait for step 3.
2. **When the December 2026 core update ends.** It began 24 Nov 15:02 UTC, and Google says rollouts take up to two weeks,
   so it should end by about 8 Dec. Its end is recorded in `incidents.json`.
3. **About 15-16 Dec 2026**, a full week after that end. Compare that week with 3-9 Nov, the last full week before the
   November update, by page, query and country.
   - **Still about 0, the pages still indexed and `check.py` still passing:** record mechanism (a) as the working cause.
     Whether to answer it with content work is a decision for Sanjay and the manager, not maintenance.
   - **`check.py` fails, or a page in section 2 leaves the index:** that is a site fault. Fix it, then use Request indexing
     for each fixed URL.
4. **Optional discriminator, done by hand.** Someone searches "scraperapi pricing" (position 54 before) in their own
   browser and reads results pages 5 and 6. If ScrapeTools is there, the deep ranking held.
