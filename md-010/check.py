"""md-010 live check: robots.txt, sitemap, canonical and robots tags of the pages that carried Google impressions.

Usage: python -I md-010/check.py
The page set is every page with a Google Search impression from 24 Aug to 15 Nov 2026 (Search Console, read
25 Nov 2026; md-010/CAUSE.md): the home page, the calculator, both ScraperAPI comparisons, cost per 1,000,
about and methodology. Expected state, as CAUSE.md states it:
- robots.txt answers 200, matches this repository's copy (line endings aside) and lets Googlebot fetch each page;
- sitemap.xml answers 200, parses as XML and lists each page's URL exactly;
- each page answers 200 at its own URL with no redirect and no X-Robots-Tag header;
- each page has exactly one <link rel="canonical">, pointing to its own URL;
- each page has no robots meta tag (name="robots" or name="googlebot").
Planted cases run first, offline: a blocking robots.txt, a sitemap missing a page, a redirect, an X-Robots-Tag
noindex, a noindex meta tag, a canonical to another URL and two canonicals. Each must fail, or the check could not.
Exit code 0 only when every live check passes and every planted case is caught. Standard library only; GET
requests, no browser, so the GoatCounter script never runs (ct-005/test_no_counter.py drives this file).
"""
import os
import sys
import time
import urllib.error
import urllib.request
import urllib.robotparser
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

BASE = "https://scrapetools.scaleturn.com/"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = ("", "scraperapi-cost-calculator.html", "scraperapi-vs-scrapingbee.html", "scraperapi-vs-bright-data.html",
         "web-scraping-api-cost-per-1000-requests.html", "about.html", "methodology.html")
UA = "Mozilla/5.0 (compatible; md-010-live-check)"
SITEMAP_NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"


def get_once(path):
    req = urllib.request.Request(BASE + path, headers={"User-Agent": UA, "Cache-Control": "no-cache"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.geturl(), dict(r.headers.items()), r.read()
    except urllib.error.HTTPError as e:
        return e.code, BASE + path, {}, b""
    except (urllib.error.URLError, OSError) as e:
        return None, BASE + path, {}, str(e).encode()


def get(path):
    """One retry, 3 s later, on a 5xx or no response (GitHub Pages answered 503 once on 19 Nov)."""
    got = get_once(path)
    if got[0] is None or got[0] >= 500:
        time.sleep(3)
        got = get_once(path)
    return got


class HeadTags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.canonicals, self.robots_meta = [], []

    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v or "") for k, v in attrs}
        if tag == "link" and "canonical" in a.get("rel", "").lower().split():
            self.canonicals.append(a.get("href", ""))
        if tag == "meta" and a.get("name", "").lower() in ("robots", "googlebot"):
            self.robots_meta.append(f'{a.get("name")}="{a.get("content", "")}"')


# ------------------------------------------------------------------ rules, shared by live and planted inputs
def robots_problems(text, repo_text):
    probs = []
    if text.replace("\r\n", "\n").strip() != repo_text.replace("\r\n", "\n").strip():
        probs.append("differs from the repository's robots.txt")
    rp = urllib.robotparser.RobotFileParser()
    rp.parse(text.splitlines())
    blocked = [p or "/" for p in PAGES if not rp.can_fetch("Googlebot", BASE + p)]
    if blocked:
        probs.append(f"Googlebot blocked from {blocked}")
    if f"Sitemap: {BASE}sitemap.xml" not in text:
        probs.append("no Sitemap line for the sitemap")
    return probs


def sitemap_problems(xml_bytes):
    try:
        locs = {e.text.strip() for e in ET.fromstring(xml_bytes).iter(SITEMAP_NS + "loc") if e.text}
    except ET.ParseError as e:
        return [f"not valid XML ({e})"]
    missing = [BASE + p for p in PAGES if BASE + p not in locs]
    return [f"missing {missing}"] if missing else []


def page_problems(path, status, final_url, headers, body):
    url = BASE + path
    probs = []
    if status != 200:
        probs.append(f"HTTP {status}")
    if final_url != url:
        probs.append(f"redirected to {final_url}")
    xrt = {k.lower(): v for k, v in headers.items()}.get("x-robots-tag")
    if xrt is not None:
        probs.append(f"X-Robots-Tag: {xrt}")
    tags = HeadTags()
    tags.feed(body.decode("utf8", "replace"))
    if tags.canonicals != [url]:
        probs.append(f"canonical {tags.canonicals} (want exactly [{url}])")
    if tags.robots_meta:
        probs.append(f"robots meta {tags.robots_meta}")
    return probs


# ------------------------------------------------------------------ planted cases (offline)
def planted(repo_robots):
    good_html = f'<html><head><link rel="canonical" href="{BASE}about.html"></head><body></body></html>'.encode()
    good_sitemap = ('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                    + "".join(f"<url><loc>{BASE}{p}</loc></url>" for p in PAGES) + "</urlset>").encode()
    cases = {
        "robots.txt blocking everything": robots_problems("User-agent: *\nDisallow: /\n", "User-agent: *\nDisallow: /\n"),
        "sitemap missing the calculator": sitemap_problems(good_sitemap.replace(
            f"<url><loc>{BASE}scraperapi-cost-calculator.html</loc></url>".encode(), b"")),
        "page redirected": page_problems("about.html", 200, BASE + "index.html", {}, good_html),
        "X-Robots-Tag noindex": page_problems("about.html", 200, BASE + "about.html",
                                              {"X-Robots-Tag": "noindex"}, good_html),
        "noindex meta tag": page_problems("about.html", 200, BASE + "about.html", {}, good_html.replace(
            b"</head>", b'<meta name="robots" content="noindex"></head>')),
        "canonical to another page": page_problems("about.html", 200, BASE + "about.html", {}, good_html.replace(
            b"about.html", b"index.html")),
        "two canonicals": page_problems("about.html", 200, BASE + "about.html", {}, good_html.replace(
            b"</head>", f'<link rel="canonical" href="{BASE}about.html"></head>'.encode())),
    }
    controls = {
        "repo robots.txt": robots_problems(repo_robots, repo_robots),
        "complete sitemap": sitemap_problems(good_sitemap),
        "clean page": page_problems("about.html", 200, BASE + "about.html", {}, good_html),
    }
    return cases, controls


def main():
    results = []

    def check(name, ok, detail=""):
        results.append(ok)
        print(f"{'PASS' if ok else 'FAIL'} {name}{': ' + detail if detail else ''}")

    with open(os.path.join(ROOT, "robots.txt"), encoding="utf8") as f:
        repo_robots = f.read()

    cases, controls = planted(repo_robots)
    for name, probs in cases.items():
        check(f"planted case caught: {name}", bool(probs), "; ".join(probs) if probs else "NOT caught")
    for name, probs in controls.items():
        check(f"control passes: {name}", not probs, "; ".join(probs))

    st, _, _, body = get("robots.txt")
    probs = [f"HTTP {st}"] if st != 200 else robots_problems(body.decode("utf8", "replace"), repo_robots)
    check("live robots.txt", not probs, "; ".join(probs) or "200, matches the repository, Googlebot may fetch all 7 pages")

    st, _, _, body = get("sitemap.xml")
    probs = [f"HTTP {st}"] if st != 200 else sitemap_problems(body)
    check("live sitemap.xml", not probs, "; ".join(probs) or "200, valid XML, lists all 7 pages")

    for p in PAGES:
        st, final, headers, body = get(p)
        probs = page_problems(p, st, final, headers, body)
        check(f"live /{p}", not probs, "; ".join(probs) or "200, no redirect, no X-Robots-Tag, one self canonical, "
                                                           "no robots meta")

    failed = results.count(False)
    print(f"{len(results) - failed} of {len(results)} passed")
    print("ALL PASS" if not failed else f"{failed} FAILED")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    sys.exit(main())
