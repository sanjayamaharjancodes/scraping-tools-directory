"""After the branch is published: check the live site for ct-005.

Usage: python -I ct-005/check_live.py
Checks, each printed as PASS or FAIL:
- the new page answers 200, carries its own canonical URL, the AdSense loader in <head> and loads its data file;
- sitemap.xml lists the new page, and still lists the three earlier data pages;
- the published CSV and JSON answer 200 and are byte-identical to this repository's copies (line endings aside);
- llms.txt lists the page and both its data files; data/pages.json lists the page; the home page links it;
- each earlier data page links the new page;
- every page in the sitemap answers 200 and has the shared nav;
- ct-005/ is not served (the Pages build excludes it): a raw file and a rendered Markdown name both answer 404.
Exit code 0 only when every check passes. Standard library only. Read-only: GET requests to the site, no browser,
so nothing here runs the GoatCounter script (ct-005/test_no_counter.py checks that).
"""
import os
import re
import sys
import time
import urllib.error
import urllib.request

BASE = "https://scrapetools.scaleturn.com/"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = "job-posting-age.html"
DATA = ("data/job-posting-age-2026-11.csv", "data/job-posting-age-2026-11.json")
EARLIER_PAGES = ("ats-job-posting-api-crawl-data.html", "what-day-are-most-jobs-posted.html", "ai-job-titles.html")
LOADER = ('<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?'
          'client=ca-pub-5554189148912369" crossorigin="anonymous"></script>')


def get_once(path):
    req = urllib.request.Request(BASE + path, headers={"User-Agent": "Mozilla/5.0 (compatible; ct-005-live-check)",
                                                       "Cache-Control": "no-cache"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, b""
    except (urllib.error.URLError, OSError) as e:
        return None, str(e).encode()


def get(path):
    """One retry, 3 s later, on a 5xx or no response (GitHub Pages answered 503 once on 19 Nov)."""
    st, body = get_once(path)
    if st is None or st >= 500:
        time.sleep(3)
        st, body = get_once(path)
    return st, body


def main():
    results = []

    def check(name, ok, detail=""):
        results.append(ok)
        print(f"{'PASS' if ok else 'FAIL'} {name}{': ' + detail if detail else ''}")

    st, body = get(PAGE)
    html = body.decode("utf8", "replace")
    head = html[:html.find("</head>")] if "</head>" in html else ""
    check(f"{PAGE} answers 200", st == 200, str(st))
    check("canonical is the page's own URL", f'<link rel="canonical" href="{BASE}{PAGE}">' in html)
    check("the AdSense loader is in <head>, once", head.count(LOADER) == 1 and html.count(LOADER) == 1)
    check(f"{PAGE} loads its data from {DATA[1]}", f'fetch("{DATA[1]}")' in html)

    st, body = get("sitemap.xml")
    sm = body.decode("utf8", "replace")
    check("sitemap.xml answers 200", st == 200, str(st))
    for p in (PAGE,) + EARLIER_PAGES:
        check(f"sitemap lists {p}", f"<loc>{BASE}{p}</loc>" in sm)

    for rel in DATA:
        st, body = get(rel)
        local = open(os.path.join(ROOT, rel), "rb").read()
        same = body.replace(b"\r\n", b"\n") == local.replace(b"\r\n", b"\n")
        check(f"{rel} answers 200 and matches the repository", st == 200 and same, f"{st}, identical={same}")

    st, body = get("llms.txt")
    llms = body.decode("utf8", "replace")
    for rel in (PAGE,) + DATA:
        check(f"llms.txt lists {rel}", f"]({BASE}{rel})" in llms)
    st, body = get("data/pages.json")
    check("data/pages.json lists the page", f'"{BASE}{PAGE}"' in body.decode("utf8", "replace"), str(st))
    st, body = get("")
    check("home page links the new page", f'href="{PAGE}"' in body.decode("utf8", "replace"), str(st))
    for p in EARLIER_PAGES:
        st, body = get(p)
        check(f"{p} links the new page", f'href="{PAGE}"' in body.decode("utf8", "replace"), str(st))

    pages = sorted({u[len(BASE):] or "index.html" for u in re.findall(r"<loc>([^<]+)</loc>", sm)})
    bad = []
    for p in pages:
        st, body = get("" if p == "index.html" else p)
        if st != 200 or '<nav class="site-nav"' not in body.decode("utf8", "replace"):
            bad.append(f"{p} ({st})")
    check(f"every sitemap page answers 200 with the shared nav ({len(pages)} pages read)", not bad, "; ".join(bad))

    for rel in ("ct-005/build_data.py", "ct-005/PREMISE.html"):
        st, _ = get(rel)
        check(f"{rel} is not served (Pages build excludes ct-005/)", st == 404, str(st))
    print("ALL PASS" if all(results) else f"{results.count(False)} FAILED")
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
