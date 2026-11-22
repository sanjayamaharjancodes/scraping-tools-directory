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

## 2. Result

(Filled in after the run.)
