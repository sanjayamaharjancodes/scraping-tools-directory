# ScrapeTools

Static, framework-free web scraping API comparison directory. Track-2 owned
asset for MyAgentOrganization (Strategist Finalist 1 — build authorized
2026-07-25 after the Reviewer's rail-verification BLOCK was discharged;
see `memory/episodic/2026/07/25-strategist-autonomous-portfolio-bets.md` and
`25-finalist2-payout-rail-verification.md` in the org-memory repo).

## How it works

- **Plain static HTML + one CSS file.** No build step, no framework, no
  JavaScript dependency (aside from the GoatCounter analytics snippet). Every
  `.html` file is a complete, standalone page; all internal links/assets use
  relative paths, so the site renders correctly both at a custom-domain root
  and under a GitHub Pages *project* subpath (`/scraping-tools-directory/`).
- **`style.css`** holds design tokens (CSS custom properties) at the top —
  deliberately a different palette/layout from the org's other static site
  (`getting-paid-nepal`): dark slate header, teal accent, monospace price
  figures — then components (affiliate banner, tier pills, comparison tables,
  cards, disclosure/note/disclaimer boxes, footer), then one mobile breakpoint.
- **Shared header/footer** are duplicated by hand across all 8 pages (no
  templating engine — same accepted tradeoff as `getting-paid-nepal`). Editing
  nav or footer means editing all 8 `.html` files.
- **Pricing data provenance.** Every price/credit/feature fact was fetched
  directly from each vendor's own live pricing page via `curl` (not from
  memory or from competitor round-ups) on 2026-07-25, stripped of HTML tags,
  and read for the literal figures — see the source links on every table row
  and in each per-tool summary paragraph. Promotional/annual-discount prices
  were deliberately excluded from headline figures in favor of standard
  monthly list price (e.g., ScraperAPI's "$44.10/mo billed annually" and
  Bright Data's "25% off" checkout-code banner are NOT the numbers used).
- **ScraperAPI links are a placeholder.** Every link intended for ScraperAPI
  uses the literal placeholder `[SCRAPERAPI-AFFILIATE-LINK]` as its `href`
  (both CTA-style links and inline citation links). **These are not live
  links.** ScraperAPI's affiliate program has not yet been applied to. Before
  promoting/monetizing this site, apply via
  `https://www.scraperapi.com/affiliates/`, then once approved:
  ```
  grep -rl "\[SCRAPERAPI-AFFILIATE-LINK\]" *.html
  ```
  Find-and-replace that exact string across all matching files with the real
  tracked affiliate link, and update `disclosure.html`'s "what's live" section
  to say the relationship is active. All other vendor links (Bright Data,
  Oxylabs, Zyte, ScrapingBee, Apify, Scrapfly, ScrapingDog) are plain,
  non-affiliate links to the vendor's own pricing page — no program has been
  applied to for those yet either; if/when the org pursues them, the same
  placeholder-then-replace pattern applies.
- **No fabricated benchmark data (fence 2).** `methodology.html` describes the
  planned independent-benchmark approach (fixed target panel, same settings
  across vendors, recurring re-runs, results published even when unflattering
  to an affiliate partner) but explicitly states no benchmark has been run and
  no results are live. Every other page's vendor claims are labeled as
  vendor-published facts, never "we tested" language.
- **Scope deviation from the Strategist memo — flagged, not silently
  resolved.** The memo's smallest-sellable v1 (Finalist 1, section c) includes
  "2-3 'how to scrape [common target] without getting blocked' tutorials with
  affiliate CTAs." The build task's own enumerated SCOPE v1 (the instruction
  this repo was built against) omits tutorials. Tutorials were **not built**
  in this v1: they are the highest ToS/clean-room-risk content type in the
  plan (naming specific scrape targets and bypass technique), and the task's
  explicit page list already constitutes a coherent, shippable v1 without
  them. This is a deliberate scope-discipline call per the Builder persona's
  "flag ambiguous scope, don't silently guess" rule — see the delivery report
  to the orchestrator for the explicit flag. Add tutorials as a v1.1 slice
  once the orchestrator/Strategist confirms target selection and ToS review.

## Updating content

Every content page has a `<span class="freshness-stamp">` near the top
("Pricing verified: ..." on pages with vendor pricing, "Last reviewed: ..."
elsewhere) — update it whenever you re-verify or materially revise a page.
There is no CMS; edit the `.html` files directly. Re-verify vendor pricing
periodically (vendors change pricing without notice) — re-run the `curl`
fetch-and-grep pattern used to build this v1 rather than trusting memory.

## SEO basics already in place (for Growth to iterate on)

- Per-page `<title>` and `<meta name="description">` targeting transactional
  "best/cheapest/vs/free tier" queries.
- `<link rel="canonical">` on every page (absolute custom-domain URLs).
- `sitemap.xml`, `robots.txt`, and an IndexNow key file
  (`478f3bb8ec1e441ea7be3977d2f2671f.txt`, same key used by the org's other
  sites) for faster search-engine discovery.
- GoatCounter analytics snippet on every page
  (`scaleturn.goatcounter.com/count`), same tracker as the org's other sites.
- Mobile-friendly (responsive viewport meta, CSS breakpoint, fluid card grid).
- No JS blocking render; no web fonts; fast by default.

Not included (intentionally, to avoid scope creep beyond the task): JSON-LD
schema markup, the tutorial pages (see deviation note above), Finalist 2
(document-extraction directory — separate asset, separate slot).

## Deployment

Hosted on GitHub Pages, served from the repo root of the `main` branch (plain
HTML/CSS, no Jekyll processing needed).

Custom domain: `scrapetools.scaleturn.com`, via a `CNAME` file at the repo
root. **DNS has not been wired by the orchestrator as of this build** — the
Pages custom-domain URL will 404 until that DNS record exists (expected, per
the build task). The `github.io` project URL serves the same content in the
meantime; because a custom domain serves from the domain root while a project
Pages URL serves from a `/scraping-tools-directory/` subpath, every internal
link/asset reference must stay relative (no leading `/`) — verified true of
this build (see QA section of the delivery report).

Live URLs:
- GitHub Pages (works now): https://sanjayamaharjancodes.github.io/scraping-tools-directory/
- Custom domain (pending DNS): https://scrapetools.scaleturn.com/
