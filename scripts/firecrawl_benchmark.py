"""ScrapeTools benchmark harness, first run: Firecrawl (md-009, 22 Nov 2026).

Runs the method on methodology.html against the fixed panel in data/benchmark-panel-2026-11.json: success rate,
median and 95th-percentile latency per successful request, and cost per 1,000 successful pages from the vendor's
published monthly prices. Standard library only.

Usage (from the repository root):
    python -I scripts/firecrawl_benchmark.py robots            # robots.txt verdict for every panel page (no key)
    python -I scripts/firecrawl_benchmark.py balance           # the account's remaining credits
    python -I scripts/firecrawl_benchmark.py smoke --page S01  # one request, with the credit counter before and after
    python -I scripts/firecrawl_benchmark.py run --rounds 5    # the benchmark; writes data/firecrawl-benchmark-<date>.*
    python -I scripts/firecrawl_benchmark.py summary <json>    # recompute the summary from a raw file
    python -I scripts/firecrawl_benchmark.py check <json> <page.html> [...]   # every Firecrawl figure on the pages
                                                               # must come from the raw file's summary

The API key is read from D:/Lab/secrets/firecrawl/.env (FIRECRAWL_API_KEY=...) or the FIRECRAWL_KEY_FILE path, and is
never printed or written anywhere else. Raw files hold status codes, timings, lengths, SHA-256 hashes and marker
results, never the pages' text.
"""
import argparse
import csv
import datetime
import hashlib
import html as htmlmod
import json
import math
import os
import re
import statistics
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser

sys.dont_write_bytecode = True
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PANEL = os.path.join(ROOT, "data", "benchmark-panel-2026-11.json")
KEY_FILE = os.environ.get("FIRECRAWL_KEY_FILE", "D:/Lab/secrets/firecrawl/.env")
API = "https://api.firecrawl.dev/v2"
UA = "ScrapeToolsBench/1.0 (+https://scrapetools.scaleturn.com/methodology.html)"
HARNESS_VERSION = "1.0"
MIN_START_GAP_S = 8.0
MIN_HOST_GAP_S = 10.0
CLIENT_TIMEOUT_S = 90


def out(*a):
    print(*a, flush=True)


def load_panel():
    raw = open(PANEL, "rb").read()
    return json.loads(raw.decode("utf-8")), hashlib.sha256(raw).hexdigest()


def api_key():
    for line in open(KEY_FILE, encoding="utf-8"):
        if line.startswith("FIRECRAWL_API_KEY="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("no FIRECRAWL_API_KEY line in the key file")


# ------------------------------------------------------------------ robots
def robots_verdicts(panel):
    """RFC 9309: 2xx parse it; 4xx other than 401/403 = no rules; 401/403, 5xx or unreachable = disallow all."""
    cache, rows = {}, []
    for p in panel["pages"]:
        parts = urllib.parse.urlsplit(p["url"])
        base = f"{parts.scheme}://{parts.netloc}"
        if base not in cache:
            status, text = None, ""
            try:
                req = urllib.request.Request(base + "/robots.txt", headers={"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=30) as r:
                    status, text = r.status, r.read().decode("utf-8", "replace")
            except urllib.error.HTTPError as e:
                status = e.code
            except Exception as e:  # unreachable
                status = "error: " + type(e).__name__
            rp = urllib.robotparser.RobotFileParser()
            if isinstance(status, int) and 200 <= status < 300:
                rp.parse(text.splitlines())
                mode = "parsed"
            elif isinstance(status, int) and 400 <= status < 500 and status not in (401, 403):
                rp.parse([])
                mode = "no rules"
            else:
                rp.parse(["User-agent: *", "Disallow: /"])
                mode = "disallow all"
            delay = None
            m = re.findall(r"(?im)^\s*crawl-delay\s*:\s*([0-9.]+)", text)
            if m:
                delay = max(float(x) for x in m)
            cache[base] = (rp, status, mode, delay)
        rp, status, mode, delay = cache[base]
        rows.append({"id": p["id"], "url": p["url"], "robots_status": status, "robots_mode": mode,
                     "allowed_star": rp.can_fetch("*", p["url"]),
                     "allowed_firecrawlagent": rp.can_fetch("FirecrawlAgent", p["url"]),
                     "crawl_delay_s": delay})
    return rows


def cmd_robots(a):
    panel, _ = load_panel()
    rows = robots_verdicts(panel)
    for r in rows:
        out(f"{r['id']} {'ALLOWED' if r['allowed_star'] and r['allowed_firecrawlagent'] else 'DISALLOWED'} "
            f"robots={r['robots_status']} ({r['robots_mode']}) crawl-delay={r['crawl_delay_s']} {r['url']}")
    bad = [r for r in rows if not (r["allowed_star"] and r["allowed_firecrawlagent"])]
    out(f"{len(rows) - len(bad)} of {len(rows)} pages allowed")
    return 1 if bad else 0


# ------------------------------------------------------------------ content checks
def norm(text):
    return re.sub(r"\s+", " ", re.sub(r"[*_`]", "", text or "")).strip()


def html_text(body):
    body = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", body or "")
    return htmlmod.unescape(re.sub(r"<[^>]+>", " ", body))


def judge(text, page, block_phrases):
    t = norm(text)
    found = []
    for m in page["markers"]:
        if isinstance(m, dict):
            found.append(bool(re.search(m["re"], t)))
        else:
            found.append(norm(m) in t)
    blocked = [b for b in block_phrases if b in t]
    return all(found), found, blocked


# ------------------------------------------------------------------ requests
def http_json(method, url, key, body=None, timeout=CLIENT_TIMEOUT_S):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Authorization": "Bearer " + key, "Content-Type": "application/json",
                                          "User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
        try:
            return e.code, json.loads(raw)
        except ValueError:
            return e.code, {"error": raw[:300]}


def balance(key):
    st, js = http_json("GET", API + "/team/credit-usage", key, timeout=30)
    if st != 200 or not js.get("success"):
        raise SystemExit(f"credit-usage read failed: HTTP {st}")
    d = js["data"]
    return {"remaining": d.get("remainingCredits"), "plan": d.get("planCredits"),
            "period_start": d.get("billingPeriodStart"), "period_end": d.get("billingPeriodEnd"),
            "read_utc": now()}


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")[:-4] + "Z"


def firecrawl_request(page, panel, key):
    cfg = panel["vendors"]["firecrawl"]["request"]
    body = dict(cfg, url=page["url"])
    started = now()
    t0 = time.perf_counter()
    rec = {"vendor": "firecrawl", "id": page["id"], "category": page["category"], "url": page["url"],
           "started_utc": started}
    try:
        st, js = http_json("POST", API + "/scrape", key, body)
        rec["latency_ms"] = round((time.perf_counter() - t0) * 1000)
        rec["api_status"] = st
        data = js.get("data") or {}
        meta = data.get("metadata") or {}
        md = data.get("markdown") or ""
        rec["api_success"] = bool(js.get("success"))
        rec["target_status"] = meta.get("statusCode")
        rec["error"] = (meta.get("error") or js.get("error") or js.get("code") or None)
        if isinstance(rec["error"], str):
            rec["error"] = rec["error"][:200]
        rec["credits_reported"] = meta.get("creditsUsed")
        rec["proxy_used"] = meta.get("proxyUsed")
        rec["cache_state"] = meta.get("cacheState")
        rec["warning"] = (data.get("warning") or None) and str(data.get("warning"))[:200]
        rec["metadata_keys"] = sorted(k for k in meta.keys() if not re.match(r"^(og|twitter|article|fb|al)[:_A-Z]", k))[:40]
        rec["chars"] = len(md)
        rec["sha256"] = hashlib.sha256(md.encode("utf-8")).hexdigest() if md else None
        ok, found, blocked = judge(md, page, panel["block_phrases"])
        rec["markers_found"] = found
        rec["block_phrases"] = blocked
        if st == 429:
            rec["fault"] = "api_429"
        rec["success"] = bool(st == 200 and rec["api_success"] and ok and not blocked)
        rec["reason"] = "ok" if rec["success"] else (
            f"api_{st}" if st != 200 else "api_success_false" if not rec["api_success"] else
            "block_page" if blocked else "marker_missing")
    except (TimeoutError, OSError) as e:
        rec["latency_ms"] = round((time.perf_counter() - t0) * 1000)
        timeout = "timed out" in str(e).lower() or isinstance(e, TimeoutError)
        rec.update({"api_status": None, "api_success": False, "success": False,
                    "reason": "client_timeout" if timeout else "network_error",
                    "error": type(e).__name__ + ": " + str(e)[:150]})
        if not timeout:
            rec["fault"] = "network_error"
    return rec


def direct_request(page, panel):
    rec = {"vendor": "direct-control", "id": page["id"], "category": page["category"], "url": page["url"],
           "started_utc": now()}
    t0 = time.perf_counter()
    try:
        req = urllib.request.Request(page["url"], headers={"User-Agent": UA, "Accept": "text/html"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                st, body = r.status, r.read()
        except urllib.error.HTTPError as e:
            st, body = e.code, e.read()
        rec["latency_ms"] = round((time.perf_counter() - t0) * 1000)
        text = html_text(body.decode("utf-8", "replace"))
        ok, found, blocked = judge(text, page, panel["block_phrases"])
        rec.update({"target_status": st, "chars": len(body), "sha256": hashlib.sha256(body).hexdigest(),
                    "markers_found": found, "block_phrases": blocked,
                    "success": bool(ok and not blocked and 200 <= st < 300)})
        rec["reason"] = "ok" if rec["success"] else ("block_page" if blocked else
                                                     f"status_{st}" if not 200 <= st < 300 else "marker_missing")
    except Exception as e:
        rec.update({"latency_ms": round((time.perf_counter() - t0) * 1000), "success": False,
                    "reason": "network_error", "error": type(e).__name__})
    return rec


def round_order(pages):
    """Interleave by host, the same order every round."""
    hosts = {}
    for p in pages:
        hosts.setdefault(urllib.parse.urlsplit(p["url"]).netloc, []).append(p)
    order, queues = [], [list(v) for v in hosts.values()]
    while any(queues):
        for q in queues:
            if q:
                order.append(q.pop(0))
    return order


class Pacer:
    def __init__(self, delays):
        self.delays, self.last_start, self.last_host = delays, 0.0, {}

    def wait(self, url):
        host = urllib.parse.urlsplit(url).netloc
        gap_host = max(MIN_HOST_GAP_S, self.delays.get(host) or 0)
        t = time.monotonic()
        need = max(self.last_start + MIN_START_GAP_S, self.last_host.get(host, -1e9) + gap_host) - t
        if need > 0:
            time.sleep(need)
        t = time.monotonic()
        self.last_start, self.last_host[host] = t, t


# ------------------------------------------------------------------ summary
def pctl(values, q):
    """Nearest-rank percentile."""
    v = sorted(values)
    return v[max(0, math.ceil(q * len(v)) - 1)] if v else None


def summarize(raw):
    reqs = [r for r in raw["requests"] if r["vendor"] == "firecrawl"]
    panel_ids = {p["id"]: p for p in raw["panel"]["pages"]}

    def block(rs):
        succ = [r for r in rs if r["success"]]
        lat = [r["latency_ms"] for r in succ]
        return {"requests": len(rs), "successes": len(succ),
                "success_rate_pct": round(100 * len(succ) / len(rs), 1) if rs else None,
                "latency_n": len(lat),
                "median_latency_ms": round(statistics.median(lat)) if lat else None,
                "p95_latency_ms": pctl(lat, 0.95)}

    general = [r for r in reqs if r["category"] in ("static", "js")]
    s = {"all": block(reqs), "general": block(general)}
    for c in ("static", "js", "protected"):
        s[c] = block([r for r in reqs if r["category"] == c])
    s["per_page"] = {}
    for pid in panel_ids:
        rs = [r for r in reqs if r["id"] == pid]
        reasons = sorted({r["reason"] for r in rs if not r["success"]})
        s["per_page"][pid] = dict(block(rs), failure_reasons=reasons)
    ctrl = [r for r in raw["requests"] if r["vendor"] == "direct-control"]
    s["control"] = {"requests": len(ctrl), "successes": sum(1 for r in ctrl if r["success"]),
                    "by_category": {c: f"{sum(1 for r in ctrl if r['category'] == c and r['success'])} of "
                                       f"{sum(1 for r in ctrl if r['category'] == c)}"
                                    for c in ("static", "js", "protected")}}
    faults = [r for r in reqs if r.get("fault")]
    s["faults"] = len(faults)
    b0, b1 = raw.get("balance_before") or {}, raw.get("balance_after") or {}
    used = (b0.get("remaining") - b1.get("remaining")) if b0.get("remaining") is not None and \
        b1.get("remaining") is not None else None
    s["credits"] = {"before": b0.get("remaining"), "after": b1.get("remaining"), "used": used,
                    "requests_sent": len(reqs),
                    "reported_sum": sum(r.get("credits_reported") or 0 for r in reqs) if any(
                        r.get("credits_reported") is not None for r in reqs) else None}
    plans = raw["panel"]["vendors"]["firecrawl"]["pricing"]["plans"]
    succ_all = s["all"]["successes"]
    succ_gen = s["general"]["successes"]
    cost = {}
    for p in plans:
        if not p["monthly_usd"]:
            continue
        per_credit = p["monthly_usd"] / p["credits"]
        row = {"usd_per_credit": per_credit}
        if used is not None and succ_all:
            row["per_1000_successful_all_usd"] = round(used / succ_all * 1000 * per_credit, 2)
        # General panel: one credit per request sent (the billing rule, checked against the counter in R3).
        if succ_gen:
            n_gen = s["general"]["requests"]
            row["per_1000_successful_general_usd"] = round(n_gen / succ_gen * 1000 * per_credit, 2)
        cost[p["name"]] = row
    s["cost_per_1000_successful_pages"] = cost
    s["ruling_inputs"] = {
        "R2_general_success_pct": s["general"]["success_rate_pct"], "R2_threshold_pct": 90,
        "R3_credits_used": used, "R3_requests_sent": len(reqs),
        "R4_faults": len(faults), "R4_limit": math.ceil(0.05 * len(reqs)) if reqs else None}
    return s


# ------------------------------------------------------------------ commands
def cmd_balance(a):
    b = balance(api_key())
    out(json.dumps(b, indent=1))
    return 0


def cmd_smoke(a):
    panel, _ = load_panel()
    page = next(p for p in panel["pages"] if p["id"] == a.page)
    key = api_key()
    b0 = balance(key)
    rec = firecrawl_request(page, panel, key)
    time.sleep(20)
    b1 = balance(key)
    out(json.dumps({"request": rec, "remaining_before": b0["remaining"], "remaining_after": b1["remaining"]},
                   indent=1))
    return 0


def write_outputs(prefix, raw):
    tmp = prefix + ".json.partial"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(raw, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    return tmp


CSV_COLS = ["run_date", "vendor", "round", "seq", "id", "category", "url", "started_utc", "latency_ms",
            "api_status", "target_status", "chars", "sha256", "markers_found", "block_phrases", "success", "reason",
            "credits_reported", "proxy_used", "error"]


def cmd_run(a):
    panel, panel_sha = load_panel()
    date = datetime.date.today().isoformat()
    prefix = os.path.join(ROOT, "data", f"firecrawl-benchmark-{date}")
    if os.path.exists(prefix + ".json") and not a.overwrite:
        raise SystemExit(f"{prefix}.json exists; pass --overwrite to replace it")
    rob = robots_verdicts(panel)
    if any(not (r["allowed_star"] and r["allowed_firecrawlagent"]) for r in rob):
        raise SystemExit("a panel page is disallowed by robots.txt; the run did not start")
    delays = {urllib.parse.urlsplit(r["url"]).netloc: r["crawl_delay_s"] for r in rob}
    key = api_key()
    raw = {"schema": 1, "run_date": date, "harness": f"scripts/firecrawl_benchmark.py {HARNESS_VERSION}",
           "panel_file": "data/benchmark-panel-2026-11.json", "panel_sha256": panel_sha, "panel": panel,
           "rounds": a.rounds, "robots": rob, "balance_before": balance(key), "requests": []}
    pacer = Pacer(delays)
    order = round_order(panel["pages"])
    out(f"run {date}: {len(order)} pages x {a.rounds} rounds; credits before {raw['balance_before']['remaining']}")
    # Control: one direct request per page, before the vendor rounds.
    for i, p in enumerate(order, 1):
        pacer.wait(p["url"])
        rec = direct_request(p, panel)
        rec.update({"round": 0, "seq": i})
        raw["requests"].append(rec)
        out(f"control {p['id']} {rec.get('target_status')} {rec['reason']} {rec['latency_ms']} ms")
    write_outputs(prefix, raw)
    stopped = None
    for rnd in range(1, a.rounds + 1):
        for i, p in enumerate(order, 1):
            pacer.wait(p["url"])
            rec = firecrawl_request(p, panel, key)
            rec.update({"round": rnd, "seq": i})
            raw["requests"].append(rec)
            out(f"r{rnd} {p['id']} api={rec.get('api_status')} target={rec.get('target_status')} "
                f"{rec['reason']} {rec['latency_ms']} ms credits={rec.get('credits_reported')}")
            write_outputs(prefix, raw)
            if rec.get("fault") == "api_429":
                stopped = f"API 429 at round {rnd}, page {p['id']}"
                break
        if stopped:
            break
    raw["stopped"] = stopped
    time.sleep(30)  # let the credit counter settle
    raw["balance_after"] = balance(key)
    raw["summary"] = summarize(raw)
    with open(prefix + ".json", "w", encoding="utf-8", newline="\n") as fh:
        json.dump(raw, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    os.remove(prefix + ".json.partial")
    with open(prefix + ".csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=CSV_COLS, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        for r in raw["requests"]:
            row = dict(r, run_date=date)
            row["markers_found"] = "|".join("yes" if x else "no" for x in r.get("markers_found") or [])
            row["block_phrases"] = "|".join(r.get("block_phrases") or [])
            w.writerow(row)
    out(json.dumps(raw["summary"], indent=1))
    return 0


def cmd_summary(a):
    raw = json.load(open(a.raw, encoding="utf-8"))
    s = summarize(raw)
    out(json.dumps(s, indent=1))
    if raw.get("summary") is not None and raw["summary"] != s:
        out("MISMATCH: the stored summary differs from the recomputed one")
        return 1
    return 0


def figures(summary):
    """Every figure a page may print about this run, as the strings it would print."""
    f = set()

    def add_num(x):
        if x is None:
            return
        if isinstance(x, float) and x.is_integer():
            x = int(x)
        f.add(f"{x:,}" if isinstance(x, int) else f"{x}")
        if isinstance(x, float):
            f.add(f"{x:,.1f}")
            f.add(f"{x:,.2f}")

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k.endswith("_ms") and isinstance(v, (int, float)):
                    add_num(v)
                    add_num(round(v / 1000, 1))
                    add_num(round(v / 1000, 2))
                else:
                    walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
        elif isinstance(o, bool):
            return
        elif isinstance(o, (int, float)):
            add_num(o)
    walk(summary)
    return f


def cmd_check(a):
    """Each element marked data-bench="..." on the pages must print a figure from the raw file's summary."""
    raw = json.load(open(a.raw, encoding="utf-8"))
    s = summarize(raw)
    if raw.get("summary") != s:
        out("FAIL stored summary differs from the recomputed one")
        return 1
    allowed = figures(s)
    bad, n = 0, 0
    for page in a.pages:
        text = open(page, encoding="utf-8").read()
        for m in re.finditer(r'data-bench="([^"]+)"[^>]*>(.*?)</', text, re.S):
            path, shown = m.group(1), re.sub(r"<[^>]+>", "", m.group(2))
            node = s
            for part in path.split("."):
                node = node.get(part) if isinstance(node, dict) else None
            nums = re.findall(r"[0-9][0-9,]*(?:\.[0-9]+)?", shown)
            n += 1
            if node is None or not nums or any(x not in allowed for x in nums) or \
                    not any(x in figures({"v": node} if not isinstance(node, dict) else node) for x in nums):
                bad += 1
                out(f"FAIL {os.path.basename(page)}: data-bench={path!r} shows {shown.strip()!r}; summary has {node!r}")
    out(f"{n} marked figures checked, {bad} failed")
    return 1 if bad or not n else 0


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("robots")
    sub.add_parser("balance")
    sp = sub.add_parser("smoke")
    sp.add_argument("--page", default="S01")
    sp = sub.add_parser("run")
    sp.add_argument("--rounds", type=int, default=5)
    sp.add_argument("--overwrite", action="store_true")
    sp = sub.add_parser("summary")
    sp.add_argument("raw")
    sp = sub.add_parser("check")
    sp.add_argument("raw")
    sp.add_argument("pages", nargs="+")
    a = ap.parse_args()
    return {"robots": cmd_robots, "balance": cmd_balance, "smoke": cmd_smoke, "run": cmd_run,
            "summary": cmd_summary, "check": cmd_check}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
