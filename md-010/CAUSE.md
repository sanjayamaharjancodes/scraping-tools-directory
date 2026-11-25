# md-010: why ScrapeTools' Google impressions fell after 15 Nov 2026

Written 25 Nov 2026, 21:59 NPT (16:14 UTC). Evidence read between 21:32 and 21:58 NPT the same day; the raw reads are in
`md-010/gsc-reads.txt`. Search Console's Performance days are Pacific time (PT); every other time here is UTC unless marked.
Search Console's URL Inspection and Crawl stats display Nepal time (NPT, UTC+5:45); that is proven in section 3.4.

## 1. Answer

**The cause is on Google's side. Nothing on the site broke, and nothing the site changed reached Google before the drop.**
What disappeared is one kind of impression: our pages shown at positions 40 to 100 of Google's results, almost all
on desktop in the United States, for commercial queries such as "scraper api pricing". Those impressions never brought
a click: 0 clicks in 736 impressions from 24 Aug to 15 Nov. Top-10 impressions continued after the drop.

Two Google-side mechanisms fit the evidence, and the checks available here cannot separate them:

- **(a) Ranking.** The November 2026 core update ran from 10 Nov 18:06 to 24 Nov 14:03 UTC (Google's Search Status
  Dashboard). It may have moved our pages below position 100 for most of these queries. Against it: impressions did not
  fall in its first five days (12, 10, 16, 22 and 27 on 10-14 Nov PT, against an average of about 12 on 1-9 Nov), and
  the one query still measurable kept about its position (82.2 before, 86.5 after).
- **(b) Impression supply.** Results at positions 40-100 are rarely seen by people, so whoever was generating those
  impressions stopped. That could be automated rank checks, or a change in how Google serves or counts deep result
  pages. For it: the same thing happened from 17 to 30 Sep with no site change and no Google update. In that dip the
  main query kept its position and its impressions then came back (section 3.3). "scraper api pricing" also drew 1-4
  impressions on most days (8 once) at positions 60-90 for three months, which looks like repeated checks more than
  human demand.

Either way there is no site fault to fix. So, per the brief, the deliverable is this evidence plus the dated re-check
plan in section 5. No page was changed and no re-indexing was requested, because nothing was fixed.

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

Daily, whole site, PT: 12 Nov 16 (position 38.9), 13 Nov 22 (46.9), 14 Nov 27 (45.6), 15 Nov 20 (78.2), 16 Nov 4 (90.8),
17 Nov 1, 18 Nov 0, then 2, 1, 1, 0, 1 for 19-23 Nov, all at positions 1-6.5 from the 19th. Every one of the five main pages
stopped on the same days (per-page daily series in `gsc-reads.txt`). By country, the United States went from 159 to 8;
by device, desktop went from 197 to 9 and mobile from 16 to 1.

Queries (31 named before; 4 named after). Each of the top ones lost almost all its impressions:
"scraper api pricing" 35 to 2 (position 82.2, then 86.5), "scraperapi pricing" 18 to 0 (54.1), "scraper api cost" 14 to 1
(88.3, then 95), "bright data web scraper api pricing" 10 to 0 (75.2), "scrapingbee vs scraperapi" 8 to 1 (87, then 95).

## 3. Candidates tested

### 3.1 Site changes deployed around 14-16 Nov: not the cause

- **Builds (GitHub Pages, UTC):** 12 Nov 04:52 (`64b034a`, new page), 14 Nov 04:58 (`a32d222`, new page),
  15 Nov 16:07 (`f134f58`, the md-004 footer, About and free-tier edits), 16 Nov 13:41 (`83a7b98`, a note removed from the
  repository), 17 Nov 05:08 (`a5f9d67`, new page).
- **Head tags:** from the 12 Nov build to the 17 Nov build, the seven pages above changed no `<title>`, canonical, robots
  meta, `<h1>` or meta description. Their edits were a footer Contact link, a footer link to scaleturn.com, the About
  wording, two home-page cards and one body link (`git diff 64b034a a5f9d67`).
- **robots.txt** has one commit, `506ab21` of 25 Jul 2026. There are no redirects: `http://` and the github.io address both
  301 to the https page, and each page answers 200 at its own URL. No page in the set has a noindex or an X-Robots-Tag.
  Live check: section 4.
- **Google never held an edited copy.** The index copies date from 5 Nov (four pages) and 12 Nov (cost per 1,000). The
  calculator's crawled HTML (URL Inspection, "View crawled page") still says "an independent comparison site", wording
  replaced in the 5 Nov 15:37 UTC build. It lacks the 11 Nov nav links and the 15 Nov footer.
- **The md-004 deploy, 15 Nov 16:07 UTC (08:07 PT, the 15th):** this is the change closest to the drop. The 15 Nov PT day
  runs 08:00 UTC on the 15th to 08:00 UTC on the 16th, and its position fell to 78.2 from 45.6. But the md-004 version
  of these pages never reached Google's index:
  - URL Inspection on 25 Nov still shows the 5 Nov copies (12 Nov for cost per 1,000), so no later fetch was indexed;
  - Crawl stats' example list (80 examples; the report counts about 94 successful fetches in 90 days) has two 15 Nov fetches, at 12:19 and 14:57 UTC,
    both before the deploy, and none after it until `/` at 17 Nov 10:38 UTC, after the 16 Nov PT day had ended.

  An edit that never reached Google's index cannot have moved how Google ranked or served these pages.
- **Removals:** none in the last 6 months. **Manual actions:** none. **Security issues:** none.

### 3.2 The structured-data episode: not the cause (timing)

- Dataset markup first entered the repository in `cd7b6d4`, committed 19 Nov 04:13 UTC (18 Nov PT). That was after the
  drop, and on data pages that had never had an impression.
- The Datasets report (last update 24 Nov) shows 3 valid items, 0 invalid. The "Missing field license" issue shows
  validation Passed and 0 items.

### 3.3 Search Console, page by page: the site is still indexed; deep impressions stopped

- **URL Inspection, top five pages:** all "URL is on Google / Page is indexed"; crawl allowed; fetch successful; indexing
  allowed. The user-declared and Google-selected canonical are both the page itself.
- **Page indexing** (last update 16 Nov): 9 indexed, 5 "Discovered - currently not indexed". The five are
  cheapest-web-scraping-api, disclosure, privacy, scraperapi-free-trial and web-scraping-apis-with-free-tier, and the
  issue was first detected 18 Aug. None of them had an impression, so no page left the index at the drop.
- **Sitemaps:** read 19 Nov, Success, 15 pages.
- **Crawl stats:** "Host had no problems in the last 90 days". The only 404s were `/favicon.ico`, before 5 Nov.
- **September control, same property:** 3-16 Sep: 96 impressions at position 52.6; 17-30 Sep: 34 at 18.9; 1-14 Oct: 125 at
  36.2. "scraper api pricing" went 30, then 4, then 21 at positions 63.1, 64.3 and 67.8: the same position throughout,
  while its impressions fell 87% and came back.
  - Only one build ran between 14 Aug and 4 Nov: 30 Sep 13:18 UTC, a one-line README change.
  - The September 2026 spam update began 24 Sep 16:15 UTC, a week after that dip started.

  So this exact signature (deep impressions gone, top-10 impressions left, positions unchanged) has already happened
  once on this site with no cause on our side.

### 3.4 Google-side, with evidence

- **Search Status Dashboard** (`status.search.google.com/incidents.json`, read 25 Nov):
  - "November 2026 core update": 10 Nov 18:06 UTC to 24 Nov 14:03 UTC;
  - "December 2026 core update": began 24 Nov 15:02 UTC, still active;
  - "September 2026 spam update": 24 Sep to 8 Oct.
- **Data anomalies page** (support.google.com/webmasters/answer/6211453, read 25 Nov): the only November entry is a
  logging error in the *Generative AI* report for 9-11 Nov. It lists nothing for the Web search report on 15-16 Nov.
- **Time zones:** the calculator's index copy predates 5 Nov 15:37 UTC, and URL Inspection gives its crawl as "Nov 5,
  5:47:41 PM". That is 12:02 UTC read as NPT; read as PT it would be 6 Nov 01:47 UTC, after the replaced wording had gone
  live. So the display is NPT. Crawl stats shows the same time as URL Inspection for the 12 Nov crawl, so it uses NPT too.

### 3.5 Not tested, and why

- **Rank check:** a Google search for "scraper api credit cost" (position 15.5 before the drop) loaded page 1 without
  ScrapeTools. Page 2 returned Google's "unusual traffic" CAPTCHA. It was not solved and no further searches were made.
  Separating (a) from (b) directly needs that check (section 5).
- **Other properties as a control** (gettingpaid, makeyeti): these are out of scope in the brief, and the session's
  permission check refused opening their reports.

## 4. Live state, as it should be (`python -I md-010/check.py`)

For each of the seven pages in section 2:
- **robots.txt:** answers 200, matches this repository's copy and lets Googlebot fetch the page.
- **sitemap.xml:** answers 200 and lists the page.
- **The page:** answers 200 at its own URL with no redirect and no X-Robots-Tag; exactly one canonical, to itself; no
  robots meta tag.

Seven planted faults must each be caught (a blocking robots.txt, a missing sitemap entry, a redirect, an X-Robots-Tag
noindex, a noindex meta tag, a foreign canonical, two canonicals).

Run 25 Nov 2026 21:58:25-21:58:30 NPT: `19 of 19 passed`, `ALL PASS`, exit 0.

Three other pages carry `noindex, follow` on purpose since 19 Nov (ct-001 retired them): scraperapi-free-trial,
scrapingdog-vs-scrapingbee and web-scraping-apis-with-free-tier. None of them had an impression before the drop.

## 5. Re-check plan (dated)

1. **2 Dec 2026** (Search Console data to about 30 Nov). Steps:
   - Run `python -I md-010/check.py`.
   - Read the daily Web impressions for 24-30 Nov, plus the "scraper api pricing" daily series.
   - If impressions at positions above 40 are back near the old positions (calculator about 55, "scraper api pricing" about
     85), it was mechanism (b), as in September, and SAN-181 can close.
2. **When the December 2026 core update ends.** It began 24 Nov 15:02 UTC, and Google says rollouts take up to two weeks,
   so it should end by about 8 Dec. Check its end in `incidents.json`.
3. **About 15-16 Dec 2026** (a full week after that end). Compare the week after the end with 3-9 Nov, the last full week
   before the November update, by page and by query.
   - Deep impressions still about 0, pages still indexed and `check.py` still passing: treat it as a ranking change
     (mechanism a). Better content is then a content decision, outside maintenance.
   - `check.py` fails, or a page in section 2 leaves the index: that is a site fault. Fix it, then use Request indexing
     for each fixed URL.
4. **Optional discriminator, no automation:** someone in their own browser searches "scraperapi pricing" (position 54
   before) and reads results pages 5 and 6. If ScrapeTools is there, the ranking held and it was (b).
