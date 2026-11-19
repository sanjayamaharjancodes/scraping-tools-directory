"""After the branch is published: check the live site for ct-002.

Usage: python -I ct-002/check_live.py
Checks, each printed as PASS or FAIL:
- the new page answers 200 and carries its own canonical URL;
- sitemap.xml lists the new page and none of ct-001's three retired pages;
- the published CSV and JSON answer 200 and are byte-identical to this repository's copies (line endings aside);
- llms.txt lists the page and both data files, and still lists ct-001's two data files;
- the home page links the new page;
- no page in the sitemap, and no retired page, has a nav link to a retired page;
- ct-002/ is not served (the Pages build excludes it): a raw file and a rendered Markdown name both answer 404.
Exit code 0 only when every check passes. Standard library only. Read-only: GET requests to the site.
"""
import os
import re
import sys
import urllib.error
import urllib.request

BASE = "https://scrapetools.scaleturn.com/"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = "what-day-are-most-jobs-posted.html"
DATA = ("data/job-posting-days-2026-11.csv", "data/job-posting-days-2026-11.json")
CT001_DATA = ("data/ats-board-crawl-2026-11.csv", "data/ats-board-crawl-2026-11.json")
RETIRED = ("web-scraping-apis-with-free-tier.html", "scraperapi-free-trial.html", "scrapingdog-vs-scrapingbee.html")


def get(path):
    req = urllib.request.Request(BASE + path, headers={"User-Agent": "Mozilla/5.0 (compatible; ct-002-live-check)",
                                                       "Cache-Control": "no-cache"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, b""
    except (urllib.error.URLError, OSError) as e:
        return None, str(e).encode()


def nav(html):
    m = re.search(r'<nav class="site-nav".*?</nav>', html, re.S)
    return re.findall(r'href="([^"]+)"', m.group(0)) if m else None


def main():
    results = []

    def check(name, ok, detail=""):
        results.append(ok)
        print(f"{'PASS' if ok else 'FAIL'} {name}{': ' + detail if detail else ''}")

    st, body = get(PAGE)
    html = body.decode("utf8", "replace")
    check(f"{PAGE} answers 200", st == 200, str(st))
    check("canonical is the page's own URL", f'<link rel="canonical" href="{BASE}{PAGE}">' in html)
    check(f"{PAGE} loads its chart data from {DATA[1]}", f'fetch("{DATA[1]}")' in html)

    st, body = get("sitemap.xml")
    sm = body.decode("utf8", "replace")
    check("sitemap.xml answers 200", st == 200, str(st))
    check("sitemap lists the new page", f"<loc>{BASE}{PAGE}</loc>" in sm)
    for old in RETIRED:
        check(f"sitemap does not list {old}", f"<loc>{BASE}{old}</loc>" not in sm)

    for rel in DATA:
        st, body = get(rel)
        local = open(os.path.join(ROOT, rel), "rb").read()
        same = body.replace(b"\r\n", b"\n") == local.replace(b"\r\n", b"\n")
        check(f"{rel} answers 200 and matches the repository", st == 200 and same, f"{st}, identical={same}")

    st, body = get("llms.txt")
    llms = body.decode("utf8", "replace")
    for rel in (PAGE,) + DATA + CT001_DATA:
        check(f"llms.txt lists {rel}", f"]({BASE}{rel})" in llms)

    st, body = get("")
    check("home page links the new page", f'href="{PAGE}"' in body.decode("utf8", "replace"), str(st))

    pages = [u[len(BASE):] or "index.html" for u in re.findall(r"<loc>([^<]+)</loc>", sm)]
    bad = []
    for p in sorted(set(pages) | set(RETIRED)):
        st, body = get("" if p == "index.html" else p)
        links = nav(body.decode("utf8", "replace")) if st == 200 else None
        if links is None:
            bad.append(f"{p} ({st}, no nav)")
        elif set(links) & set(RETIRED):
            bad.append(f"{p} links {sorted(set(links) & set(RETIRED))}")
    check(f"no nav links a retired page ({len(set(pages) | set(RETIRED))} pages read)", not bad, "; ".join(bad))

    # Pages may render .md as .html, so probe both a raw file and the rendered name; both must be absent.
    for rel in ("ct-002/build_data.py", "ct-002/PREMISE.html"):
        st, _ = get(rel)
        check(f"{rel} is not served (Pages build excludes ct-002/)", st == 404, str(st))
    print("ALL PASS" if all(results) else f"{results.count(False)} FAILED")
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
