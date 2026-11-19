"""ct-004 check: AdSense loader on every page of three sites, ads.txt, the scaleturn.com home page's data cards, the
privacy texts and the ScraperAPI affiliate links.

Usage:
    python -I ct-004/check_live.py                      # after the deploy: reads the live sites
    python -I ct-004/check_live.py --local \\
        --scaleturn <scaleturn-site dir> --gettingpaid <getting-paid-nepal dir>
                                                        # before it: reads the branch files instead

Checks, each printed as PASS or FAIL:
- every page answers 200 and loads the AdSense loader exactly once, inside <head>, byte for byte as scaleturn.com
  does (async, client=ca-pub-5554189148912369). Pages: ScrapeTools = every .html file in this repository except the
  Search Console file (the three noindex retired pages included) plus anything in its sitemap; Getting Paid Nepal and
  scaleturn.com = a fixed list plus anything in their sitemaps;
- https://scaleturn.com/ads.txt answers 200 and carries the publisher line;
- the scaleturn.com home page: its first section after the hero is #data, it links the three data reports, and every
  number in each data card appears on the report it links;
- the three privacy pages name AdSense, its cookie, the opt-outs and Google's EU consent requirement, and none says
  the site loads no ad code; Getting Paid Nepal's About page does not either;
- ScrapeTools: each page that carries the ScraperAPI affiliate link still does (fp_ref=sanjaya18), every affiliate
  link has rel="sponsored nofollow", an affiliate/scraperapi-<page> click event and an "Affiliate link" label.
Exit code 0 only when every check passes. Standard library only. Read-only: GET requests, or local files with --local.
"""
import argparse
import html as htmlmod
import os
import re
import sys
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOADER = ('<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?'
          'client=ca-pub-5554189148912369" crossorigin="anonymous"></script>')
ADS_LINE = "google.com, pub-5554189148912369, DIRECT, f08c47fec0942fa0"
AFFILIATE = "https://www.scraperapi.com/?fp_ref=sanjaya18"
SITES = {
    "scrapetools": "https://scrapetools.scaleturn.com/",
    "gettingpaid": "https://gettingpaid.scaleturn.com/",
    "scaleturn": "https://scaleturn.com/",
}
FIXED_PAGES = {
    "gettingpaid": ["", "about.html", "affiliate-disclosure.html", "bank-wire-transfer-nepal.html", "contact.html",
                    "payment-comparison-nepal.html", "payoneer-nepal-guide.html", "privacy-policy.html",
                    "tax-foreign-income-nepal.html", "terms.html", "upwork-fiverr-freelancers-nepal.html"],
    "scaleturn": ["", "game-assets.html", "ats-job-feed/", "about.html", "contact.html", "privacy.html"],
}
DATA_PAGES = ("ats-job-posting-api-crawl-data.html", "what-day-are-most-jobs-posted.html", "ai-job-titles.html")
# ScrapeTools pages that carry the affiliate link on 19 Nov 2026 (ct-004), and in which form.
AFFILIATE_PAGES = {"": "link", "scraperapi-cost-calculator.html": "link", "scraperapi-free-trial.html": "link",
                   "scraperapi-vs-bright-data.html": "link", "scraperapi-vs-scrapingbee.html": "link",
                   "web-scraping-apis-with-free-tier.html": "link", "cheapest-web-scraping-api.html": "widget",
                   "web-scraping-api-cost-per-1000-requests.html": "widget"}
PRIVACY = {"scrapetools": "privacy.html", "gettingpaid": "privacy-policy.html", "scaleturn": "privacy.html"}
PRIVACY_NEEDS = ("AdSense", "__gads", "Consent in the EEA, the UK and Switzerland",
                 "https://support.google.com/adsense/answer/13790256", "https://www.google.com/settings/ads",
                 "https://www.aboutads.info/choices/", "https://www.google.com/policies/privacy/partners/")
NO_ADS_CLAIMS = re.compile(r"loads? no advertising code|no page loads advertising code|sets? no advertising cookies|"
                           r"do(?:es)? not load any advertising code|shows no (?:display )?ads", re.I)
NUM = re.compile(r"\d[\d,]*(?:\.\d+)?%?")


class Reader:
    def __init__(self, local, dirs):
        self.local, self.dirs = local, dirs

    def get(self, site, path):
        """(status, text). Locally a missing file is 404."""
        if self.local:
            p = path if path and not path.endswith("/") else path + "index.html"
            f = os.path.join(self.dirs[site], *p.split("/"))
            if not os.path.isfile(f):
                return 404, ""
            with open(f, encoding="utf8") as fh:
                return 200, fh.read()
        url = SITES[site] + path
        st, body = self._once(url)
        if st is None or st >= 500:        # GitHub Pages answered 503 once on 19 Nov (ct-003): one retry
            time.sleep(3)
            st, body = self._once(url)
        return st, body.decode("utf8", "replace")

    @staticmethod
    def _once(url):
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; ct-004-live-check)",
                                                   "Cache-Control": "no-cache"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            return e.code, b""
        except (urllib.error.URLError, OSError) as e:
            return None, str(e).encode()


def text_of(html):
    html = re.sub(r"<(script|style)\b.*?</\1>", " ", html, flags=re.S | re.I)
    return re.sub(r"\s+", " ", htmlmod.unescape(re.sub(r"<[^>]+>", " ", html))).strip()


def sitemap_paths(rd, site):
    st, sm = rd.get(site, "sitemap.xml")
    return [loc[len(SITES[site]):] for loc in re.findall(r"<loc>([^<]+)</loc>", sm) if loc.startswith(SITES[site])]


def page_list(rd, site):
    if site == "scrapetools":
        fixed = ["" if f == "index.html" else f for f in sorted(os.listdir(ROOT))
                 if f.endswith(".html") and not f.startswith("google")]
    else:
        fixed = FIXED_PAGES[site]
    return fixed + [p for p in sitemap_paths(rd, site) if p not in fixed]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--local", action="store_true", help="read the branch files instead of the live sites")
    ap.add_argument("--scrapetools", default=ROOT)
    ap.add_argument("--scaleturn", default="F:/Lab/assets/scaleturn-site")
    ap.add_argument("--gettingpaid", default="F:/Lab/assets/getting-paid-nepal")
    a = ap.parse_args()
    rd = Reader(a.local, {"scrapetools": a.scrapetools, "scaleturn": a.scaleturn, "gettingpaid": a.gettingpaid})
    results = []

    def check(name, ok, detail=""):
        results.append(ok)
        print(f"{'PASS' if ok else 'FAIL'} {name}{': ' + detail if detail else ''}")

    pages = {}
    for site in SITES:
        for path in page_list(rd, site):
            st, html = rd.get(site, path)
            pages[(site, path)] = html
            head = html[:html.find("</head>")] if "</head>" in html else ""
            live = re.sub(r"<!--.*?-->", "", head, flags=re.S)
            n_all = html.count(LOADER)
            ok = st == 200 and n_all == 1 and live.count(LOADER) == 1
            check(f"{SITES[site]}{path} answers 200 and loads the AdSense loader once, in <head>", ok,
                  "" if ok else f"status {st}, {n_all} in page, {live.count(LOADER)} live in <head>")

    if a.local:
        f = os.path.join(a.scaleturn, "ads.txt")
        st, ads = (200, open(f, encoding="utf8").read()) if os.path.isfile(f) else (404, "")
    else:
        st, ads = rd.get("scaleturn", "ads.txt")
    check("scaleturn.com/ads.txt answers 200 and carries the publisher line", st == 200 and ADS_LINE in ads, str(st))

    home = pages[("scaleturn", "")]
    hero_end = home.find("</section>", home.find('class="hero"'))
    first = re.search(r"<section\b[^>]*>", home[hero_end:]) if hero_end > 0 else None
    check("scaleturn.com: the first section after the hero is the data section (#data)",
          bool(first) and 'id="data"' in first.group(0), first.group(0) if first else "no hero")
    m = re.search(r'<section id="data">(.*?)</section>', home, re.S)
    data = m.group(1) if m else ""
    for page in DATA_PAGES:
        url = SITES["scrapetools"] + page
        check(f"scaleturn.com home links {url} from its data section", f'href="{url}"' in data)
    for card in re.findall(r'<article class="card data-card">(.*?)</article>', data, re.S):
        link = re.search(r'href="https://scrapetools\.scaleturn\.com/([^"]+\.html)"', card)
        report = link.group(1) if link else "?"
        st, rep = rd.get("scrapetools", report) if link else (None, "")
        have = set(NUM.findall(text_of(rep)))
        missing = sorted(set(NUM.findall(text_of(card))) - have)
        check(f"every number in the home card for {report} is on that report", st == 200 and not missing,
              f"status {st}, not on the report: {missing}" if missing or st != 200 else "")

    for site, path in PRIVACY.items():
        html = pages.get((site, path)) or rd.get(site, path)[1]
        lacking = [x for x in PRIVACY_NEEDS if x not in html]
        claim = NO_ADS_CLAIMS.search(text_of(html))
        check(f"{SITES[site]}{path} names AdSense, its cookie, the opt-outs and Google's EU consent requirement, "
              "and claims no ad-free site", not lacking and not claim,
              f"lacks {lacking}" if lacking else (f'says "{claim.group(0)}"' if claim else ""))
    about = pages.get(("gettingpaid", "about.html"), "")
    claim = NO_ADS_CLAIMS.search(text_of(about))
    check("gettingpaid.scaleturn.com/about.html claims no ad-free site", not claim, claim.group(0) if claim else "")

    for path, form in AFFILIATE_PAGES.items():
        html = pages.get(("scrapetools", path), "")
        attr = "href" if form == "link" else "data-affiliate-url"
        check(f"{SITES['scrapetools']}{path} keeps its ScraperAPI affiliate link ({form}, fp_ref=sanjaya18)",
              f'{attr}="{AFFILIATE}"' in html)
    for (site, path), html in pages.items():
        if site != "scrapetools":
            continue
        for tag in re.findall(r"<a\b[^>]*fp_ref=[^>]*>", html):
            rel = re.search(r'rel="([^"]*)"', tag)
            ev = re.search(r'data-goatcounter-click="([^"]*)"', tag)
            ok = (f'href="{AFFILIATE}"' in tag and rel and {"sponsored", "nofollow"} <= set(rel.group(1).split())
                  and ev and re.fullmatch(r"affiliate/scraperapi-[a-z0-9-]+", ev.group(1))
                  and "Affiliate link" in text_of(html))
            check(f"{SITES[site]}{path}: affiliate link has the tag, rel sponsored nofollow, its click event and "
                  "an \"Affiliate link\" label", bool(ok), tag[:160] if not ok else "")

    failed = results.count(False)
    print(f"{len(results) - failed} of {len(results)} checks passed ({'local branch files' if a.local else 'live sites'})")
    print("ALL PASS" if not failed else f"{failed} FAILED")
    sys.exit(0 if not failed else 1)


if __name__ == "__main__":
    main()
