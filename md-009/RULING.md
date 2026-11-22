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
