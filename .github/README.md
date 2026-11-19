# ScrapeTools

Source of https://scrapetools.scaleturn.com/, a web scraping API pricing comparison published by Scaleturn
(https://scaleturn.com/).

This README lives in `.github/` so the Pages build does not publish it; GitHub still shows it on the repository page.

## How it works

- **Plain static HTML.** No build step and no framework. Every `.html` file is a complete page; internal links and
  assets use relative paths.
- **Styles and widgets.** `style.css` holds design tokens, then components, then one mobile breakpoint.
  `widgets.css` and `widgets.js` add the answer box, the cost-by-volume widget and the affiliate card. The widgets read
  `data/vendors.json`, which records each vendor's plans, credits per request, the source URL and the date it was
  checked.
- **How pages are produced.** Pages are drafted with AI tools and checked against vendor sources by an automated
  reviewer, and every footer says so. Some pages are refreshed by hand.
- **Sources.** Every price, credit count and free-tier term comes from the vendor's own pricing page, docs or help
  center, with a link and a verification date. Where a vendor does not publish a detail, the page says so.
  Promotional and annual-discount prices are not used as headline figures.
- **Affiliate links.** ScraperAPI links carrying `fp_ref` are referral links, marked `rel="sponsored"`. The
  relationship is named on `disclosure.html`, and a banner at the top of every vendor page says a commission may be
  earned through its vendor links and links to that disclosure. Other vendor links are plain.
- **No benchmark results yet.** `methodology.html` describes the planned benchmark and says none has been run. Pages
  report vendor-published facts, never "we tested".
- **One first-hand data page.** `ats-job-posting-api-crawl-data.html` reports our own job-index refresh (18-19 Nov
  2026). Every figure on it comes from `data/ats-board-crawl-2026-11.{csv,json}`. `ct-001/build_data.py` rebuilds
  those files from the refresh's report files, and its `--check` mode fails on any number on the page that is not
  in them. That page has no affiliate links, so it carries no affiliate banner. `ct-001/` is kept out of the Pages
  build by `_config.yml`.
- **Retired pages.** Three pages are `noindex` and out of the sitemap since 19 Nov 2026. Their URLs still work and
  link to a current page; `ct-001/RETIRED.md` lists them and how to reverse it.

## Updating content

- Each content page has a `<span class="freshness-stamp">` ("Pricing verified: …" or "Last reviewed: …"). Update it,
  and the page's `lastmod` in `sitemap.xml`, whenever you re-verify or materially revise the page.
- Re-fetch the vendor page for every figure you change. Do not work from memory or from other round-ups.

## SEO basics

- `<title>`, `<meta name="description">` and `<link rel="canonical">` on every page.
- `sitemap.xml` with `lastmod`, `robots.txt`, and an IndexNow key file.
- Responsive tables (`stack-table` in `widgets.css`); no web fonts.

## Deployment

GitHub Pages serves the repository root of `main`, at the custom domain in `CNAME` (`scrapetools.scaleturn.com`).
Keep internal links relative.

## Tools

- [ScraperAPI cost calculator](https://scrapetools.scaleturn.com/scraperapi-cost-calculator.html): monthly requests and request type to credits and the smallest plan.
- [ScraperAPI free trial](https://scrapetools.scaleturn.com/scraperapi-free-trial.html): what 5,000 trial credits buy per request type.
- [Cost per 1,000 requests](https://scrapetools.scaleturn.com/web-scraping-api-cost-per-1000-requests.html): published plans as a per-1,000 price.
