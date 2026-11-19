"""Lighthouse runs that never count as a visit and never fetch an ad (ct-005, 20 Nov 2026).

Usage:
    python -I ct-005/lighthouse_run.py --url https://scrapetools.scaleturn.com/ [--url ...] [--runs 3]
                                       [--form-factor mobile|desktop] [--out <dir>]

Prints, per URL, the Performance score of each run and their median. With --out, each run's JSON report is kept.

Why a runner: in November 2026 our own checks were counted among the sites' GoatCounter visitors. A Lighthouse run
loads the page like a visitor, so it loads the GoatCounter script (gc.zgo.at/count.js) and, on the live sites, the
AdSense loader's ad requests too. This runner starts its own headless Chrome on a throwaway profile with a
host-resolver allowlist: only the hosts of the URLs under test, the AdSense loader host (pagead2.googlesyndication.com,
so the page loads as visitors get it) and Google Fonts resolve. Every other name, gc.zgo.at and *.goatcounter.com
among them, fails to resolve, so the counter script never loads and no ad is requested (ct-004 found that URL
patterns alone miss cross-site ad frames). Lighthouse's own --blocked-url-patterns blocks the counter as a second
layer. Lighthouse then attaches to that Chrome by its debugging port, so no flag passes through a shell.

Lighthouse 12.6.1 (the version ct-004 measured with) is run through npx; it is in the local npx cache.
Scores exclude ad fill, as ct-004's did. ct-005/test_no_counter.py runs this script against a local page that
carries the live counter snippet and fails if the counter loads.
"""
import argparse
import json
import os
import shutil
import socket
import statistics
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request

CHROME = "C:/Program Files/Google/Chrome/Application/chrome.exe"
LIGHTHOUSE = "lighthouse@12.6.1"
ALLOWED_EXTRA = ("pagead2.googlesyndication.com", "fonts.googleapis.com", "fonts.gstatic.com")
# The GoatCounter script and its count endpoint. API reads (/api/v0/) are not visits and are not run by browsers here.
COUNTER_PATTERNS = ("*gc.zgo.at*", "*zgo.at/count*", "*goatcounter.com/count*")


def resolver_rules(urls):
    hosts = sorted({urllib.parse.urlsplit(u).hostname for u in urls} | set(ALLOWED_EXTRA))
    return "MAP * ~NOTFOUND , " + " , ".join(f"EXCLUDE {h}" for h in hosts)


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def start_chrome(urls, profile):
    port = free_port()
    cmd = [CHROME, "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
           f"--user-data-dir={profile}", f"--remote-debugging-port={port}",
           f"--host-resolver-rules={resolver_rules(urls)}", "about:blank"]
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(100):                       # up to 10 s for the debugging port
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/json/version", timeout=1):
                return proc, port
        except OSError:
            time.sleep(0.1)
    proc.kill()
    raise RuntimeError("Chrome did not open its debugging port")


def npx():
    path = shutil.which("npx.cmd") or shutil.which("npx")
    if not path:
        raise RuntimeError("npx not found (Node.js is needed for Lighthouse)")
    return path


def run_once(url, port, form_factor, out_json):
    cmd = [npx(), "--yes", LIGHTHOUSE, url, f"--port={port}", "--output=json", f"--output-path={out_json}",
           "--only-categories=performance", f"--form-factor={form_factor}", "--quiet"]
    if form_factor == "desktop":
        cmd.append("--preset=desktop")
    cmd += [f"--blocked-url-patterns={p}" for p in COUNTER_PATTERNS]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if r.returncode != 0 or not os.path.exists(out_json):
        raise RuntimeError(f"lighthouse exit {r.returncode}: {(r.stderr or r.stdout)[-400:]}")
    with open(out_json, encoding="utf-8") as f:
        rep = json.load(f)
    score = rep["categories"]["performance"]["score"]
    items = rep.get("audits", {}).get("network-requests", {}).get("details", {}).get("items", [])
    # Lighthouse lists the attempt too; a blocked one has statusCode -1 (no response). Only an answered one leaked.
    leaked = [i.get("url") for i in items if ("zgo.at" in i.get("url", "") or "goatcounter.com/count" in
                                               i.get("url", "")) and (i.get("statusCode") or -1) > 0]
    return (round(score * 100) if score is not None else None), leaked


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", action="append", required=True)
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--form-factor", choices=("mobile", "desktop"), default="mobile")
    ap.add_argument("--out", help="directory to keep each run's JSON report")
    a = ap.parse_args()
    work = tempfile.mkdtemp(prefix="lh-run-")
    out = a.out or work
    os.makedirs(out, exist_ok=True)
    proc, port = start_chrome(a.url, os.path.join(work, "profile"))
    failed = False
    try:
        for i, url in enumerate(a.url):
            scores = []
            for n in range(a.runs):
                s, leaked = run_once(url, port, a.form_factor, os.path.join(out, f"lh-{i}-{n}.json"))
                scores.append(s)
                if leaked:
                    failed = True
                    print(f"FAIL {url}: counter requests in the report: {leaked}")
            ok = [s for s in scores if s is not None]
            med = statistics.median(ok) if ok else None
            print(f"{url}: performance {scores}, median {med} ({a.form_factor}; counter and ad hosts unresolved)")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
        shutil.rmtree(os.path.join(work, "profile"), ignore_errors=True)
        if not a.out:
            shutil.rmtree(work, ignore_errors=True)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
