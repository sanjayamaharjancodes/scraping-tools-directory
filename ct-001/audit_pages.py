"""Measure every HTML page of the site: words, facts, unique facts and overlap with the other pages.

Usage: python ct-001/audit_pages.py [--exclude page.html ...]   (run from anywhere; reads the site root)
Prints a Markdown table and writes ct-001/page-audit.json.

- words: words in <main> (the whole <body> when a page has no <main>), scripts and styles removed.
- facts: distinct numbers in that text (prices, counts, percentages), dates and bare years removed.
- unique facts: facts that appear on no other page of the site.
- overlap: the share of the page's 5-word sequences that also appear on at least one other page, and the single
  page it overlaps most (same 5-word shingles the content-autopilot gate uses for duplicate content).
Standard library only.
"""
import argparse
import json
import os
import re

MONTH = r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*"
NUM = re.compile(r"(?<![\w.#/-])(\$?\d[\d,]*(?:\.\d+)?%?)(?![\w-]*\d)")
K = 5


def main_text(html):
    html = re.sub(r"<(script|style|noscript)\b[^>]*>.*?</\1>", " ", html, flags=re.S | re.I)
    m = re.search(r"<main\b.*?</main>", html, re.S | re.I) or re.search(r"<body\b.*?</body>", html, re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", m.group(0) if m else html)
    text = re.sub(r"&nbsp;|&#160;", " ", text)
    return re.sub(r"&[a-z]+;|&#\d+;", "", text)


def numbers(text):
    t = re.sub(r"\b\d{1,2},? " + MONTH + r",? \d{4}\b", " ", text)
    t = re.sub(r"\b" + MONTH + r" \d{1,2},? \d{4}\b", " ", t)
    t = re.sub(r"\b\d{4}-\d\d-\d\d\b", " ", t)
    t = re.sub(r"\b" + MONTH + r" \d{4}\b", " ", t)
    t = re.sub(r"\b20[2-3]\d\b", " ", t)
    return {m.group(1).replace(",", "") for m in NUM.finditer(t)}


def words(text):
    return re.findall(r"[a-z0-9]+(?:'[a-z]+)?", text.lower())


def shingles(ws):
    return {" ".join(ws[i:i + K]) for i in range(len(ws) - K + 1)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exclude", nargs="*", default=[], help="pages to leave out (e.g. a page added by this task)")
    args = ap.parse_args()
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sitemap = open(os.path.join(root, "sitemap.xml"), encoding="utf-8").read()
    pages = sorted(f for f in os.listdir(root) if f.endswith(".html") and f not in args.exclude)
    raw = {p: open(os.path.join(root, p), encoding="utf-8").read() for p in pages}
    info = {}
    for p in pages:
        txt = main_text(raw[p])
        ws = words(txt)
        info[p] = {"words": len(ws), "facts": numbers(txt), "sh": shingles(ws),
                   "noindex": bool(re.search(r'<meta name="robots"[^>]*noindex', raw[p], re.I)),
                   "in_sitemap": ("/" + (p if p != "index.html" else "")) + "</loc>" in sitemap.replace(
                       "https://scrapetools.scaleturn.com", ""),
                   "inbound": sum(1 for q in pages if q != p and re.search(r'href="' + re.escape(p) + r'(?:#[^"]*)?"', raw[q]))}
    rows = []
    for p in pages:
        me = info[p]
        others_f = set().union(*(info[q]["facts"] for q in pages if q != p))
        others_s = set().union(*(info[q]["sh"] for q in pages if q != p))
        uniq = me["facts"] - others_f
        best, best_c = "", 0.0
        for q in pages:
            if q == p or not me["sh"]:
                continue
            c = len(me["sh"] & info[q]["sh"]) / len(me["sh"])
            if c > best_c:
                best, best_c = q, c
        rows.append({"page": p, "words": me["words"], "facts": len(me["facts"]), "unique_facts": len(uniq),
                     "facts_elsewhere_pct": round(100 * (len(me["facts"]) - len(uniq)) / len(me["facts"]), 1)
                     if me["facts"] else None,
                     "overlap_any_pct": round(100 * len(me["sh"] & others_s) / len(me["sh"]), 1) if me["sh"] else 0.0,
                     "max_overlap_pct": round(100 * best_c, 1), "max_overlap_with": best,
                     "inbound_links": me["inbound"], "in_sitemap": me["in_sitemap"], "noindex": me["noindex"]})
    with open(os.path.join(root, "ct-001", "page-audit.json"), "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=1)
        f.write("\n")
    print("| Page | Words | Facts | Unique facts | Facts also on another page | Text overlap with any page "
          "| Most text overlap | Inbound links | Sitemap |")
    print("|---|---:|---:|---:|---:|---:|---|---:|---|")
    for r in rows:
        fe = "n/a" if r["facts_elsewhere_pct"] is None else f"{r['facts_elsewhere_pct']}%"
        print(f"| {r['page']} | {r['words']} | {r['facts']} | {r['unique_facts']} | {fe} | {r['overlap_any_pct']}% | "
              f"{r['max_overlap_pct']}% {r['max_overlap_with']} | {r['inbound_links']} | "
              f"{'yes' if r['in_sitemap'] else 'no'}{' (noindex)' if r['noindex'] else ''} |")


if __name__ == "__main__":
    main()
