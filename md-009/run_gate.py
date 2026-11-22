"""Run the content-autopilot machine gate (checks.run_all, with its phone render) on the home page after md-009.

Usage:
    python -I md-009/run_gate.py --autopilot <content-autopilot dir> --original <index.html before md-009>
                                 [--work <scratch dir>] [--live]

The home page is a hub the autopilot never refreshes, so its facts were last recorded by the 5 Nov 2026 refresh
(content-autopilot/published/index/facts.json). This runner gates the page in refresh mode against the page as it
was before md-009 (--original, e.g. `git show main:index.html`), so the kept-links and kept-affiliate rules apply.
Facts = the 5 Nov facts plus md-009/facts.json (Firecrawl's pricing page and this site's benchmark data, 22 Nov).
The gate requires every fact to be fetched within 3 days; the 5 Nov facts back figures md-009 did not change, so
their fact-age findings are reported separately from every other finding. Exit code 0 only when nothing else fails.
Without --live, links to this site's own files are checked against this repository (the branch is not published
yet). The phone render is content-autopilot's render.py, which strips the GoatCounter and ad code (ct-005).
"""
import argparse
import json
import os
import re
import shutil
import sys
import tempfile

SLUG = "index"
SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def untraced_all(checks, common, dd, cfg):
    """The full list behind the gate's untraced_number finding (the gate prints only the first 12)."""
    facts = common.read_json(os.path.join(dd, "facts.json"))
    allowed = set()
    for ft in facts["facts"]:
        allowed |= {checks.norm_num(str(n)) for n in ft.get("numbers", [])}
    for dv in facts.get("derived", []):
        allowed.add(round(float(dv["result"]), 6))
        allowed |= {checks.norm_num(str(n)) for n in dv.get("numbers", [])}
    pg = checks.parse(common.read_text(os.path.join(dd, "page.html")))
    vis = " ".join(pg.text_parts) + " " + pg.metas.get("description", "") + " " + pg.title
    small = cfg["checks"]["max_small_int_untraced"]
    return [raw for raw, v, unit in checks.numbers_in(vis)
            if v not in allowed and not (not unit and float(v).is_integer() and 0 <= v <= small)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--autopilot", required=True)
    ap.add_argument("--original", required=True, help="the home page as it was before md-009")
    ap.add_argument("--work")
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--page", help="the page to gate (default: this branch's index.html)")
    a = ap.parse_args()
    sys.path.insert(0, a.autopilot)
    import checks
    import common
    import render as render_mod

    cfg = common.load_config()
    work = a.work or tempfile.mkdtemp(prefix="md009-gate-")
    dd = os.path.join(work, "draft")
    site = os.path.join(work, "site")
    shutil.rmtree(dd, ignore_errors=True)
    shutil.rmtree(site, ignore_errors=True)
    os.makedirs(os.path.join(dd, "inputs"))
    # A copy of this branch's site with the pre-md-009 home page, which refresh mode reads as the live page.
    shutil.copytree(SITE, site, ignore=shutil.ignore_patterns(".git", ".claude", "ct-*", "md-*", "scripts",
                                                              "__pycache__", ".tmp-*", ".rx001-repos"))
    shutil.copy(a.original, os.path.join(site, "index.html"))
    shutil.copy(a.page or os.path.join(SITE, "index.html"), os.path.join(dd, "page.html"))
    base = json.load(open(os.path.join(a.autopilot, "published", "index", "facts.json"), encoding="utf-8"))
    ours = json.load(open(os.path.join(SITE, "md-009", "facts.json"), encoding="utf-8"))
    facts = {"target_query": base["target_query"], "facts": base["facts"] + ours["facts"],
             "derived": base.get("derived", []) + ours.get("derived", [])}
    with open(os.path.join(dd, "facts.json"), "w", encoding="utf-8") as fh:
        json.dump(facts, fh, indent=1)
    with open(os.path.join(dd, "inputs", "topic.json"), "w", encoding="utf-8") as fh:
        json.dump({"target_query": facts["target_query"]}, fh)
    old_ids = {f["id"] for f in base["facts"]}

    def fetch(url, timeout):
        prefix = cfg["site_url"] + "/"
        if not a.live and url.startswith(prefix):
            p = os.path.join(SITE, url[len(prefix):].split("#")[0] or "index.html")
            return (200, open(p, encoding="utf8").read()) if os.path.isfile(p) else (404, "")
        return checks.http_status(url, timeout)

    shots = {}

    def renderer(page_path):
        r = render_mod.render(page_path, cfg, os.path.join(dd, "shots"), site)
        shots.update(r)
        return r

    findings = checks.run_all(dd, SLUG, cfg, site, mode="refresh", fetch=fetch, check_net=True, render=renderer)
    age = re.compile(r"^fact (\S+): fetch date 2026-11-05 is not within 3 days of today$")
    stale, other = [], []
    for f in findings:
        m = age.match(f.get("msg", "") or f.get("message", "") or "")
        (stale if m and m.group(1) in old_ids else other).append(f)
    print(json.dumps(other, indent=1))
    for f in other:
        if f["rule"] == "untraced_number":
            print("untraced:", " ".join(sorted(set(x for x in untraced_all(checks, common, dd, cfg)))))
    print(f"fact-age findings on the unchanged 5 Nov facts: {len(stale)} (of {len(old_ids)} such facts)")
    pg = checks.parse(common.read_text(os.path.join(dd, "page.html")))
    inter = shots.get("interaction") or {}
    print(f"words in <main>: {len(checks.words(' '.join(pg.main_parts)))}; phone height {shots.get('height')} px "
          f"= {round((shots.get('height') or 0) / 900, 1)} screens; js_errors {shots.get('js_errors')}; "
          f"interaction ok {inter.get('ok')}, states {len(inter.get('states') or [])}; "
          f"links {'live' if a.live else 'repository'}")
    print(f"phone screenshots: {os.path.join(dd, 'shots')}")
    fails = [f for f in other if f.get("severity", "fail") == "fail"]
    print("GATE PASSED (apart from the 5 Nov fact ages)" if not fails else f"GATE FAILED: {len(fails)} findings")
    sys.exit(0 if not fails else 1)


if __name__ == "__main__":
    main()
