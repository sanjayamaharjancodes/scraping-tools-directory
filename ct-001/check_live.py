"""After the branch is published: check the live site for ct-001.

Usage: python ct-001/check_live.py
Checks, each printed as PASS or FAIL:
- the new page answers 200 and carries its own canonical URL;
- sitemap.xml lists the new page and none of the three retired pages;
- the published CSV and JSON answer 200 and are byte-identical to this repository's copies;
- each retired page answers 200, is noindex, and links its replacement;
- ct-001/ is not served (the Pages build excludes it): a raw file and a rendered Markdown name both answer 404.
Exit code 0 only when every check passes. Standard library only.
"""
import os
import re
import sys
import urllib.error
import urllib.request

BASE = "https://scrapetools.scaleturn.com/"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = "ats-job-posting-api-crawl-data.html"
RETIRED = {"web-scraping-apis-with-free-tier.html": "cheapest-web-scraping-api.html",
           "scraperapi-free-trial.html": "scraperapi-cost-calculator.html",
           "scrapingdog-vs-scrapingbee.html": "index.html"}


def get(path):
    req = urllib.request.Request(BASE + path, headers={"User-Agent": "Mozilla/5.0 (compatible; ct-001-live-check)",
                                                       "Cache-Control": "no-cache"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, b""
    except (urllib.error.URLError, OSError) as e:
        return None, str(e).encode()


def main():
    results = []

    def check(name, ok, detail=""):
        results.append(ok)
        print(f"{'PASS' if ok else 'FAIL'} {name}{': ' + detail if detail else ''}")

    st, body = get(PAGE)
    html = body.decode("utf8", "replace")
    check(f"{PAGE} answers 200", st == 200, str(st))
    check("canonical is the page's own URL", f'<link rel="canonical" href="{BASE}{PAGE}">' in html)
    st, body = get("sitemap.xml")
    sm = body.decode("utf8", "replace")
    check("sitemap.xml answers 200", st == 200, str(st))
    check("sitemap lists the new page", f"<loc>{BASE}{PAGE}</loc>" in sm)
    for old in RETIRED:
        check(f"sitemap no longer lists {old}", f"<loc>{BASE}{old}</loc>" not in sm)
    for rel in ("data/ats-board-crawl-2026-11.csv", "data/ats-board-crawl-2026-11.json"):
        st, body = get(rel)
        local = open(os.path.join(ROOT, rel), "rb").read()
        same = body.replace(b"\r\n", b"\n") == local.replace(b"\r\n", b"\n")
        check(f"{rel} answers 200 and matches the repository", st == 200 and same, f"{st}, identical={same}")
    for old, new in RETIRED.items():
        st, body = get(old)
        h = body.decode("utf8", "replace")
        check(f"{old} answers 200, noindex, links {new}",
              st == 200 and bool(re.search(r'<meta name="robots" content="noindex', h)) and f'href="{new}"' in h,
              str(st))
    # Pages may render .md as .html, so probe both a raw file and the rendered name; both must be absent.
    for rel in ("ct-001/build_data.py", "ct-001/PREMISE.html"):
        st, _ = get(rel)
        check(f"{rel} is not served (Pages build excludes ct-001/)", st == 404, str(st))
    print("ALL PASS" if all(results) else f"{results.count(False)} FAILED")
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
