"""Run the content-autopilot machine gate (checks.run_all, including its phone render) on ai-job-titles.

Usage:
    python -I ct-003/run_gate.py --autopilot <content-autopilot dir> [--work <scratch dir>] [--live]

The gate compares the page's nav and footer with the autopilot's templates/page-skeleton.html; this page keeps the
current nav, so the autopilot's main checkout works. Without --live, the page's facts (which cite this site's data
files) are checked against the files in this repository, so the gate can run before the branch is published. With
--live, every source URL is fetched from the web, as the gate normally does. Exit code 0 only when the gate has no
"fail" finding.
"""
import argparse
import json
import os
import shutil
import sys
import tempfile

SLUG = "ai-job-titles"
SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--autopilot", required=True, help="content-autopilot directory (checks.py, render.py)")
    ap.add_argument("--work", help="scratch directory for the draft copy and phone screenshots")
    ap.add_argument("--live", action="store_true", help="fetch this site's data files from the web too")
    a = ap.parse_args()
    sys.path.insert(0, a.autopilot)
    import checks
    import common
    import render as render_mod

    cfg = common.load_config()
    work = a.work or tempfile.mkdtemp(prefix="ct003-gate-")
    dd = os.path.join(work, "draft")
    shutil.rmtree(dd, ignore_errors=True)
    os.makedirs(os.path.join(dd, "inputs"))
    # The data files stay in the site's data/ folder: a draft's own data/ folder is read as vendor files.
    shutil.copy(os.path.join(SITE, SLUG + ".html"), os.path.join(dd, "page.html"))
    shutil.copy(os.path.join(SITE, "ct-003", "facts.json"), os.path.join(dd, "facts.json"))
    with open(os.path.join(dd, "inputs", "topic.json"), "w", encoding="utf8") as fh:
        json.dump({"target_query": json.load(open(os.path.join(dd, "facts.json"), encoding="utf8"))["target_query"]}, fh)

    def fetch(url, timeout):
        prefix = cfg["site_url"] + "/"
        if not a.live and url.startswith(prefix):
            p = os.path.join(SITE, url[len(prefix):])
            return (200, open(p, encoding="utf8").read()) if os.path.exists(p) else (404, "")
        return checks.http_status(url, timeout)

    shots = {}

    def renderer(page_path):
        r = render_mod.render(page_path, cfg, os.path.join(dd, "shots"), SITE)
        shots.update(r)
        return r

    findings = checks.run_all(dd, SLUG, cfg, SITE, mode="new", fetch=fetch, check_net=True, render=renderer)
    pg = checks.parse(common.read_text(os.path.join(dd, "page.html")))
    print(json.dumps(findings, indent=1))
    inter = shots.get("interaction") or {}
    print(f"words in <main>: {len(checks.words(' '.join(pg.main_parts)))}; phone height {shots.get('height')} px "
          f"= {round((shots.get('height') or 0) / 900, 1)} screens; js_errors {shots.get('js_errors')}; "
          f"interaction ok {inter.get('ok')}, states {len(inter.get('states') or [])}; "
          f"sources {'live' if a.live else 'repository'}")
    for s in (inter.get("states") or [])[:4]:
        print("  state:", s.get("control"), "|", s.get("value"), "|", " / ".join(s.get("results") or [])[:200])
    print(f"phone screenshots: {os.path.join(dd, 'shots')}")
    ok = checks.passed(findings)
    print("GATE PASSED" if ok else "GATE FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
