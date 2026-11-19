"""After the branch is published: check the live site for ct-003.

Usage: python -I ct-003/check_live.py
Checks, each printed as PASS or FAIL:
- the new page answers 200, carries its own canonical URL and loads its data file;
- sitemap.xml lists the new page, and still lists the two earlier data pages;
- the published CSV and JSON answer 200 and are byte-identical to this repository's copies (line endings aside);
- llms.txt lists the page and both its data files, and still lists the earlier data pages' four files;
- data/pages.json lists the page; the home page links it;
- every page in the sitemap answers 200 and has the shared nav;
- ct-003/ is not served (the Pages build excludes it): a raw file and a rendered Markdown name both answer 404.
Exit code 0 only when every check passes. Standard library only. Read-only: GET requests to the site.
"""
import os
import re
import sys
import urllib.error
import urllib.request

BASE = "https://scrapetools.scaleturn.com/"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = "ai-job-titles.html"
DATA = ("data/ai-job-titles-2026-11.csv", "data/ai-job-titles-2026-11.json")
EARLIER_PAGES = ("ats-job-posting-api-crawl-data.html", "what-day-are-most-jobs-posted.html")
EARLIER_DATA = ("data/ats-board-crawl-2026-11.csv", "data/ats-board-crawl-2026-11.json",
                "data/job-posting-days-2026-11.csv", "data/job-posting-days-2026-11.json")


def get(path):
    req = urllib.request.Request(BASE + path, headers={"User-Agent": "Mozilla/5.0 (compatible; ct-003-live-check)",
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
    check(f"{PAGE} loads its explorer data from {DATA[1]}", f'fetch("{DATA[1]}")' in html)

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
    for rel in (PAGE,) + DATA + EARLIER_DATA:
        check(f"llms.txt lists {rel}", f"]({BASE}{rel})" in llms)

    st, body = get("data/pages.json")
    check("data/pages.json lists the page", f'"{BASE}{PAGE}"' in body.decode("utf8", "replace"), str(st))
    st, body = get("")
    check("home page links the new page", f'href="{PAGE}"' in body.decode("utf8", "replace"), str(st))

    pages = sorted({u[len(BASE):] or "index.html" for u in re.findall(r"<loc>([^<]+)</loc>", sm)})
    bad = []
    for p in pages:
        st, body = get("" if p == "index.html" else p)
        if st != 200 or '<nav class="site-nav"' not in body.decode("utf8", "replace"):
            bad.append(f"{p} ({st})")
    check(f"every sitemap page answers 200 with the shared nav ({len(pages)} pages read)", not bad, "; ".join(bad))

    # Pages may render .md as .html, so probe both a raw file and the rendered name; both must be absent.
    for rel in ("ct-003/build_data.py", "ct-003/PREMISE.html"):
        st, _ = get(rel)
        check(f"{rel} is not served (Pages build excludes ct-003/)", st == 404, str(st))
    print("ALL PASS" if all(results) else f"{results.count(False)} FAILED")
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
