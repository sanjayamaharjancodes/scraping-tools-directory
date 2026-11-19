# ct-001: pages retired on 19 Nov 2026

## How the pages were measured

`python -I ct-001/audit_pages.py --exclude ats-job-posting-api-crawl-data.html` measured every HTML file in the
site root as it was before this change, at commit `82a424c` (16 files: 15 pages in the sitemap plus Google's
verification stub). Results are in `ct-001/page-audit.json`. Running it on a later commit measures the retired
pages with their notices and gives different numbers. To reproduce, check out `82a424c`'s pages and run it there.

- **Words:** words in `<main>`.
- **Facts:** distinct numbers in `<main>`, such as prices, credit counts and percentages. Dates and years are not
  counted.
- **Unique facts:** facts that appear on no other page.
- **Facts also on another page:** the share of a page's facts that the site already states elsewhere. This is the
  overlap that matters here: the pages restate the same vendor price lists.
- **Text overlap:** the share of the page's 5-word sequences found on any other page, the same shingles the
  content-autopilot gate uses. It is low everywhere because that gate already blocks duplicate prose.

| Page | Words | Facts | Unique facts | Facts also on another page | Text overlap with any page | Most text overlap | Inbound links |
|---|---:|---:|---:|---:|---:|---|---:|
| about.html | 491 | 0 | 0 | n/a | 1.6% | 0.8% methodology.html | 14 |
| cheapest-web-scraping-api.html | 1051 | 47 | 12 | 74.5% | 5.7% | 1.7% web-scraping-api-cost-per-1000-requests.html | 14 |
| disclosure.html | 280 | 0 | 0 | n/a | 3.6% | 1.4% methodology.html | 14 |
| googlef4530fde7f9bc941.html (verification stub) | 5 | 0 | 0 | n/a | 0.0% | | 0 |
| index.html | 1651 | 70 | 10 | 85.7% | 6.4% | 1.5% scraperapi-cost-calculator.html | 14 |
| methodology.html | 660 | 2 | 1 | 50.0% | 1.2% | 0.6% about.html | 14 |
| privacy.html | 244 | 0 | 0 | n/a | 0.4% | 0.4% about.html | 14 |
| scrapecreators-pricing.html | 909 | 24 | 8 | 66.7% | 2.5% | 1.5% serp-api-pricing-comparison.html | 3 |
| scraperapi-cost-calculator.html | 1578 | 52 | 11 | 78.8% | 6.9% | 2.6% scraperapi-vs-scrapingbee.html | 14 |
| **scraperapi-free-trial.html** | 1065 | 25 | 5 | 80.0% | 6.4% | 3.4% scraperapi-cost-calculator.html | 14 |
| scraperapi-vs-bright-data.html | 1045 | 40 | 9 | 77.5% | 5.5% | 2.5% scraperapi-free-trial.html | 14 |
| scraperapi-vs-scrapingbee.html | 1044 | 66 | 15 | 77.3% | 11.6% | 5.3% scrapingdog-vs-scrapingbee.html | 14 |
| **scrapingdog-vs-scrapingbee.html** | 948 | 43 | 7 | 83.7% | 8.8% | 5.9% scraperapi-vs-scrapingbee.html | 4 |
| serp-api-pricing-comparison.html | 933 | 54 | 28 | 48.1% | 2.4% | 1.4% scrapecreators-pricing.html | 1 |
| web-scraping-api-cost-per-1000-requests.html | 924 | 50 | 10 | 80.0% | 5.5% | 2.1% index.html | 14 |
| **web-scraping-apis-with-free-tier.html** | 1008 | 18 | 1 | 94.4% | 1.5% | 1.1% cheapest-web-scraping-api.html | 14 |

**Not candidates:**
- The home page, because it is the site's entry point and holds the main pricing table.
- The four trust pages (About, Methodology, Disclosure, Privacy), because reviewers and readers look for them.
- The verification stub, because Search Console needs it.

All pages are about the same length (909 to 1,651 words in `<main>`), so word count does not separate them. The
weakest pages are the ones that add the fewest facts the site does not already state.

## The three pages retired

| Page | Reason | Link from its notice to |
|---|---|---|
| web-scraping-apis-with-free-tier.html | 1 unique fact out of 18: 94.4% of its facts are on other pages, the most of any content page. Its free allowances are summarized on the cheapest-API page. | cheapest-web-scraping-api.html |
| scrapingdog-vs-scrapingbee.html | 7 unique facts out of 43 (83.7% elsewhere), and the highest single-page text overlap on the site (5.9%, with scraperapi-vs-scrapingbee.html, which also covers ScrapingBee). The home page compares the same two vendors' plans alongside ScraperAPI and Scrapfly. | index.html |
| scraperapi-free-trial.html | 5 unique facts out of 25 (80.0% elsewhere), and most text overlap with the calculator. The calculator works out the same credits per request type for any volume and describes the 7-day, 5,000-credit trial. | scraperapi-cost-calculator.html |

`web-scraping-api-cost-per-1000-requests.html` also has 80.0% of its facts on other pages, but 10 of its facts are
its own (per-1,000 prices at each volume), twice the free-trial page's 5. So it stays.

## What was changed (mirrors the content-autopilot's own retire step, and goes further)

- Each retired page gets `<meta name="robots" content="noindex, follow">` and a note box at the top of `<main>`
  linking the page above. The file and URL stay, so old links and bookmarks still work. Nothing else on the page
  changed.
- Removed from `sitemap.xml`, `llms.txt`, `data/pages.json` and the home page's "More guides" cards and "Where to go
  next" line. The new data page takes a card there.
- **Reversible:** delete the robots meta and the note box, then re-add the four index entries.

## Left for the manager

- **The shared navigation still links two retired pages** ("Free Tiers", "ScraperAPI free trial") on every page.
  That nav comes from the content-autopilot's page skeleton, and its gate compares each draft's nav with the
  skeleton. Changing it means changing the skeleton too, so it is left until the autopilot's next step is decided.
  The links still work, and the pages are noindex.
- **Other pages' body text still links a retired page in places**, for example the cheapest-API page's "free tier
  comparison". Those links work.
- **The content-autopilot's page registry still lists the three pages.** Before it resumes, mark them retired there,
  or its refresh rule (facts older than 30 days) could rewrite one and put it back in the sitemap.
- **Its publish step rebuilds three things this change edited by hand.** `publish.py` regenerates `llms.txt` and
  `data/pages.json` from the site's pages:
  - **llms.txt / pages.json:** it skips noindex pages, so the retired pages stay out and the new page is picked up.
    Its fixed "Data" section would drop the two crawl-data lines in `llms.txt`.
  - **Home-page cards:** it rebuilds the "More guides" block from its own registry, so the new page's card stays
    only if the page is registered there.
  Register the new page and keep those two lines before lifting STOP.
- Per the 19 Nov rule (every public page carries something only we have), none of the three was rewritten or merged
  into another page. Each points to an existing page.
