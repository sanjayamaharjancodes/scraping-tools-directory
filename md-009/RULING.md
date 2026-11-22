# md-009 ruling: does Firecrawl earn a place in the ScrapeTools comparison?

## 1. Pre-registration (committed 22 Nov 2026, before the first keyed request)

- **Why this test exists.** Firecrawl's growth team (Juan, 26 Oct and 21 Nov 2026) asked to be added to the site's
  comparison and offered free credits. We did not take those credits; the test used the public free plan (1,000 credits a
  month, no card) on an account that already existed (created 25 Aug 2026).
- **Panel, settings, pacing and rule:** `data/benchmark-panel-2026-11.json` (19 pages: 13 static, 4 JavaScript, 2
  bot-protected; 5 rounds; success = the page's own text markers, taken from a normal browser view). The rule is in
  its `ruling_rule` field and is repeated here:
  - **R1 eligibility:** it sells its own API on published monthly credit plans that state the credits a request uses.
  - **R2 reliability:** at least 90% of requests to the general panel (static and JavaScript pages) succeed.
  - **R3 billing:** the account's own credit counter shows at most 1 credit per request sent for the run.
  - **R4 valid run:** harness faults (API 429, our own network errors) under 5% of requests, else no ruling.
  - **Not a criterion:** price rank. The protected pair is reported but not ruled on (two pages are too few).
- **Harness:** `scripts/firecrawl_benchmark.py` (standard library; key read from `D:/Lab/secrets/firecrawl/.env`).
- **Robots:** all 19 pages allowed for `*` and `FirecrawlAgent` (`python -I scripts/firecrawl_benchmark.py robots`,
  22 Nov 2026). Crawl-delays honoured: Hacker News 30 s, GOV.UK 10 s, Wikipedia 5 s, web-scraping.dev 2 s.
- **Firecrawl terms** (firecrawl.dev/terms-of-service, dated 7 Oct 2026): no clause restricts publishing benchmarks.
  Clause 5.d.1 bars commercial use "except as expressly authorized by Firecrawl"; Firecrawl's growth team invited this
  test for the comparison in writing (26 Oct, 21 Nov).
- **Comparison page note.** The email names "Best Web Scraping APIs 2026: 8 Tools Compared". That title was the home
  page until 5 Nov 2026 (commit f857e04); since then `index.html` compares four credit-plan vendors by monthly cost,
  and the eight-vendor table is on `cheapest-web-scraping-api.html`.

## 2. Result (run 22 Nov 2026, 05:41-05:57 UTC)

Raw files: `data/firecrawl-benchmark-2026-11-22.csv` and `.json` (the JSON embeds the panel, its SHA-256, the robots
verdicts, the credit counter before and after, and the summary; `summary` recomputes it identically). After the run
the billing-period dates were dropped from the two counter reads (account details, not results) and the summary
gained `max_latency_ms`; the requests are unchanged. Nearest-rank p95 of 10 or 15 values is the slowest one, so
the small groups show the slowest request instead.

| Group | Requests | Succeeded | Median (successful) | 95th percentile, or slowest where n < 20 |
|---|---|---|---|---|
| Static pages (13) | 65 | 65 (100%) | 2.26 s | 2.98 s (n 65) |
| JavaScript pages (4) | 20 | 15 (75%) | 1.78 s | slowest 2.66 s (n 15) |
| **General panel (17)** | **85** | **80 (94.1%)** | **2.22 s** | **2.97 s (n 80)** |
| Bot-protected practice pages (2) | 10 | 10 (100%) | 1.64 s | slowest 4.34 s (n 10) |
| All | 95 | 90 (94.7%) | 2.17 s | 3.03 s (n 90) |

- **Failures:** all 5 are `J03` (quotes.toscrape.com/js-delayed), whose quotes appear 10 s after load: Firecrawl
  returned the page shell (262 characters) without them at its default settings (no `waitFor`). Every other page
  succeeded in every round.
- **Proxy:** all 95 requests report `proxyUsed: basic`; `auto` never escalated, the two Cloudflare challenge pages
  included. No request reported `concurrencyLimited`.
- **Credits:** counter 1,024 before, 929 after: 95 credits for 95 requests; every response reported `creditsUsed: 1`,
  the 5 failed ones included (a document came back, which the billing docs say is billed). Plus 1 smoke request
  (S01, before the run, 1,025 to 1,024). Free plan used: 96 of 1,000 credits this period.
- **Cost per 1,000 successful pages** (credits used / successes x plan price per credit, monthly list prices):
  Hobby $4.04, Standard $1.05, Growth $0.85, Scale $0.80 on the general panel (all 95: $4.01, $1.05, $0.84, $0.79).
- **Control (one plain GET per page):** static 12 of 13, JavaScript 0 of 4, protected 0 of 2 (403 "Just a
  moment..."). The static miss, S01, is an artifact of the control, not of the page: its marker "A Light in the
  Attic" is in the HTML only in `title`/`alt` attributes (the visible link text is truncated to "A Light in the
  ..."), and the control's text extraction drops attributes. Firecrawl's Markdown keeps that text. The marker was
  chosen from the HTML rather than a browser view; the panel stays as frozen.

## 3. Ruling: YES

| Rule | Needed | Measured | |
|---|---|---|---|
| R1 eligibility | own API, monthly credit plans, credits per request published | yes: 1 credit per page, plans $19-$749/mo (pricing page, 22 Nov) | pass |
| R2 reliability | >= 90% of 85 general-panel requests | 94.1% (80) | pass |
| R3 billing | <= 1 credit per request | 95 credits / 95 requests | pass |
| R4 valid run | faults < 5% | 0 faults, no 429 | valid |

Firecrawl goes into the home page comparison (index.html) and the nine-vendor table on
cheapest-web-scraping-api.html, labelled as the one entry we tested; the other vendors stay "from vendor pages".
Price rank was not a criterion: for plain pages Firecrawl is the most expensive of the five credit-plan vendors at
100,000 ($99) and 1,000,000 ($749) a month.

## 4. Pages changed and checks (22 Nov 2026)

Changed: index.html (Firecrawl row with a Tested pill, widget data, results section, Firecrawl in the text lines),
cheapest-web-scraping-api.html (vendor-table row, corrected "eight"/"four"/"no benchmark" lines), methodology.html
(first results live for one vendor), and one-line truth fixes on about.html, scraperapi-free-trial.html and
scraperapi-vs-bright-data.html; llms.txt, data/pages.json, sitemap.xml, .github/README.md, style.css
(.tier-pill.tested). data/vendors.json is unchanged, so the vendors.json widgets on other pages still show four
vendors; the cheapest page's widget line says "four of these vendors".

| Check | Command | Result |
|---|---|---|
| Summary recomputes | `python -I scripts/firecrawl_benchmark.py summary data/firecrawl-benchmark-2026-11-22.json` | exit 0 |
| Figures trace to the raw file | `... check data/firecrawl-benchmark-2026-11-22.json index.html methodology.html` | index 2, methodology 22 marked figures, 0 failed; 2 planted errors caught (after the rework) |
| Widget unchanged for the other four | node diff of `best()` before/after, 212 volumes x rendering on/off | 1,696 cases, 0 differ |
| Machine gate, cheapest page | `python -I md-009/run_gate.py --autopilot F:/Lab/assets/content-autopilot --slug cheapest-web-scraping-api --original <main copy>` | passed apart from 18 fact-age findings on its 8 Nov facts; 8,984 px (original 8,965), under the 10-screen cap |
| Machine gate, home page | same, `--original <main copy of index.html>` | after the rework: the same 2 findings as main and no worse: "22 numbers on the page not in facts.json" (identical list on main, all in the More-guides cards) and too_long 12.2 screens, 10,982 px (main 11,001 px). Plus 54 fact-age findings on the 5 Nov facts. |
| AdSense loader and affiliate links | `python -I ct-004/check_live.py --local --scrapetools . --scaleturn F:/Lab/assets/scaleturn-site --gettingpaid F:/Lab/assets/getting-paid-nepal` | 64 of 64, ALL PASS |
| Our tools count no visit | `python -I ct-005/test_no_counter.py` (now scans scripts/ and md-*/) | 18 of 18, ALL PASS |
| Links | every href on the six changed pages | 149 local targets exist; 31 external links all 200 |
| Render | phone (gate render, 412 px) and desktop (1,536 px viewport, local copy without counter/ad code) | no overflow, no JS errors; widget interaction ok |

The gate's "claimed testing" rule (checks.py BANNED) predates any real test; the pages state the test in the
site's third-person voice ("ScrapeTools ran", "ScrapeTools test") and the claims trace to the raw file.

## 5. Originality gate (22 Nov 2026)

- **Query** "best web scraping api 2026" (Google, en/US, 22 Nov). Top 3 organic: tinyfish.ai/blog/best-web-scraping-tools,
  scrapingdog.com/blog/best-web-scraping-apis/, a Reddit r/developer thread. Reddit could not be read (plain fetch 403;
  the Chrome extension refuses reddit.com), so #4, zackproser.com/blog/best-web-scraping-api-2026, took its place.
- **Inputs** All four pages went through one text extractor (`<main>`/`<article>`, scripts stripped); the rivals' word
  counts match a browser view of their articles. Files in the job's temp folder (not the repo), labels drawn at random
  each time, the mapping kept outside the reviewer's folder.

**Counting run (attempt 3, blind).** A separate headless Claude (`claude -p --tools Read --strict-mcp-config
--setting-sources project --no-session-persistence`) started in a neutral folder outside any repository, as in
ct-003/ct-005. Labels: X ours, Z ScrapingDog, Y tinyfish.ai, W zackproser.com. Prompt, verbatim:

> Four web pages that rank on Google for "best web scraping api 2026" were saved as plain text (page furniture and scripts stripped; tables flattened with " | "). They are the files page-W.txt, page-X.txt, page-Y.txt and page-Z.txt in the current folder. Read all four with the Read tool and nothing else.
>
> Rank the four pages from most original (1) to least original (4), using your own judgment of what originality means for a page like this. Then rank them the same way for usefulness to someone choosing a web scraping API, and for trustworthiness. Reply with a table (page | originality | usefulness | trust) and one or two sentences per page on its originality, under 300 words. No ties.

| Page | Originality | Usefulness | Trust |
|---|---|---|---|
| ScrapeTools home page (this branch, after the fix below) | **1** | **1** | **1** |
| ScrapingDog blog (vendor's own benchmark) | 2 | 3 | 4 |
| tinyfish.ai blog | 3 | 2 | 3 |
| zackproser.com (#4, in place of Reddit) | 4 | 4 | 2 |

Its reason for first place: cost per volume worked out across five vendors with credits per request, a test planned
in advance with raw CSV and JSON published, and plain statements of what it does not cover.

**Earlier runs (do not count as blind).** Two Agent-tool subagents, started from this session, also ranked our page
1st on every criterion. The second said its context carried this branch's git snapshot (commit messages naming
Firecrawl), so neither run was blind; the first one's prompt also defined originality in terms that favour a
disclosed method and discount a vendor's self-test. The first prompt asked for ranks on originality ("information a
reader could not get from the vendors' own pages or from other round-ups — first-hand measurements, data the author
produced, a disclosed method, analysis that goes beyond restating marketing claims ... Self-reported tests by an
interested party count, but less than a test whose method and data are disclosed"), usefulness and trust; the
second asked for originality only, judged by the reviewer's own meaning. Both were run before attempt 3.

- **Defect found by attempt 1, fixed before attempt 3.** The cost sentence cited the counter's 95 credits but gave the
  85-request figure ($4.04 on Hobby, versus $4.01 over all 95). It now names its basis: 85 credits, 80 passes.
  Re-checked: 24 figures traced; gate unchanged apart from height 15.0 screens.
- **Weakness named for ours** Narrow: five credit-plan vendors priced from their own pages, one tested, once, mostly
  on practice sites, at that vendor's request. The page says all of this.
- **Checked by hand, not by a script:** the methodology page's figures (19 pages: 13, 4, 2; 8 s and 10 s pacing;
  90%, 1 credit) match data/benchmark-panel-2026-11.json, and "published here in July 2026" matches the page's first
  commit (506ab21, 25 Jul 2026).

## 6. Rework (manager, 22 Nov 2026): full results on methodology.html, compact summary on the home page

- The results table, its footnote, the failures paragraph and the cost paragraph moved from index.html to
  methodology.html's first-run section (anchor `#firecrawl-results`); methodology renders at 6,251 px on a phone with
  no overflow or JS errors.
- index.html keeps a compact Tested summary in the short answer (80 of 85, traced, linking to the full results), the
  Firecrawl table row (Tested pill; anchor `#firecrawl-test`, so the cheapest page's links still land on it) and the
  widget entry. Removed from index: the results section, Firecrawl's vendor summary, its out-of-credit bullet, the
  mixed-workload and tie sentences, the rendered-price sentence, the extra free-offer clause, the change-log line and
  the billing-docs source link.
- To end no taller than main with a table row and a widget entry added, existing content was recast with the same
  facts and links: the short answer's three "lowest list price" bullets became one sentence, the "Where the lowest
  list price changes hands" heading and six bullets became one paragraph, and the "These four are the credit-plan
  vendors..." paragraph was folded into the ScrapeOps paragraph ("Other credit-plan vendors exist and were not
  checked."). The widget footer went back to its original wording.
- Checks after the rework: figure check index 2 + methodology 22, 0 failed, plants caught; gate as in section 4;
  `ct-004/check_live.py --local` 64 of 64; `ct-005/test_no_counter.py` 18 of 18.
