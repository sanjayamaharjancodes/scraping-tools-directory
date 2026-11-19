"""Rebuild every number on ats-job-posting-api-crawl-data.html from the job-index refresh's own report files.

The report files themselves are not published (one also holds BambooHR figures, which the page excludes). The CSV
and JSON written here carry every per-ATS count the page uses, plus each report file's SHA-256 hash.

Usage:
    python ct-001/build_data.py --evidence <dir with refresh-*.json / *.log> --crawler-src <crawler src dir>
    python ct-001/build_data.py ... --check ats-job-board-api-crawl-data.html

Writes (paths relative to the site root, the parent of ct-001/):
    data/ats-board-crawl-2026-11.csv    per-ATS numbers (the page's download)
    data/ats-board-crawl-2026-11.json   the same rows plus totals, stop reasons, method settings and input hashes
    ct-001/facts.json                   the content-autopilot gate's facts file (every number traced to the files above)
With --check, it then fails if any number visible on the page is not in the generated data.

Inputs are a fixed list of files, each recorded with its sha256, so a later run on changed files is detectable.
Standard library only. Nothing is fetched from the network.
"""
import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import os
import re
import sys

SITE = "https://scrapetools.scaleturn.com"
CSV_REL = "data/ats-board-crawl-2026-11.csv"
JSON_REL = "data/ats-board-crawl-2026-11.json"
TARGET_QUERY = "ats public job posting api"
ATS_ORDER = ["greenhouse", "lever", "ashby", "recruitee", "personio", "workable"]
ATS_NAME = {"greenhouse": "Greenhouse", "lever": "Lever", "ashby": "Ashby", "recruitee": "Recruitee",
            "personio": "Personio", "workable": "Workable"}
# BambooHR was read only in the first 18 Nov run and then removed from the crawler because its developer terms bar
# crawling. It is excluded from every figure.
EXCLUDED = {"bamboohr"}

FILES = {
    "first_refresh_18": "refresh-2026-11-18.json",            # all ATSs, 18 Nov 04:20-06:14 UTC
    "personio_a_18": "refresh-2026-11-18-personio.json",      # Personio first pass (several requests at a time)
    "personio_b_18": "refresh-2026-11-18-personio-2.json",    # Personio re-read of the failed boards, 1 a second
    "final_18": "refresh-2026-11-18-final.json",              # the index after 18 Nov (company names, page checks)
    "pass1_19_log": "refresh-2026-11-19.log",                 # 19 Nov, first pass (process ended before its report)
    "pass2_19_log": "refresh-2026-11-19-r2.log",              # 19 Nov, second pass
}
OPTIONAL = {"pass2_19_json": "refresh-2026-11-19.json"}       # the second pass's report, when it finished

LINE = re.compile(r"^(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d+Z) (.*)$")
PROGRESS = re.compile(r"^(\w+): (\d+) of (\d+) checked, (\d+) ok, (\d+) jobs$")
DONE = re.compile(r"^(\w+): done, (\d+) checked, (\d+) ok, (\d+) not boards, (\d+) failed, (\d+) jobs$")


def sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def ts(s):
    return dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=dt.timezone.utc)


def pct(part, whole):
    return round(100.0 * part / whole, 1) if whole else None


def r1(x):
    return round(x, 1) if x is not None else None


def parse_log(path):
    """The last run in a refresh log: start time, per-ATS progress points and done lines."""
    with open(path, encoding="utf-8") as f:
        lines = [ln.rstrip("\n") for ln in f]
    start_idx = max(i for i, ln in enumerate(lines) if re.search(r"Z Checking \d+ boards$", ln))
    m = LINE.match(lines[start_idx])
    run = {"start": m.group(1), "boards": int(re.search(r"Checking (\d+) boards", m.group(2)).group(1)),
           "progress": {}, "done": {}}
    for ln in lines[start_idx + 1:]:
        m = LINE.match(ln)
        if not m:
            continue
        t, msg = m.group(1), m.group(2)
        p = PROGRESS.match(msg)
        if p:
            run["progress"].setdefault(p.group(1), []).append(
                {"t": t, "checked": int(p.group(2)), "of": int(p.group(3)), "ok": int(p.group(4)), "jobs": int(p.group(5))})
        d = DONE.match(msg)
        if d:
            run["done"][d.group(1)] = {"t": t, "checked": int(d.group(2)), "ok": int(d.group(3)),
                                       "not_boards": int(d.group(4)), "failed": int(d.group(5)), "jobs": int(d.group(6))}
    return run


def lane_stop_burst(points, done):
    """A stopped lane fails its remaining boards at once. Find the first progress point after which the next
    1,000 checks took under one second, and return (checked at that point, seconds from it to the done line)."""
    seq = points + ([{"t": done["t"], "checked": done["checked"]}] if done else [])
    for a, b in zip(seq, seq[1:]):
        if (ts(b["t"]) - ts(a["t"])).total_seconds() < 1.0 and b["checked"] - a["checked"] >= 100:
            return a["checked"], round((ts(done["t"]) - ts(a["t"])).total_seconds(), 1) if done else None
    return None, None


def summarize_pass(run):
    start = ts(run["start"])
    out = {}
    for ats in ATS_ORDER:
        d = run["done"].get(ats)
        pts = run["progress"].get(ats, [])
        if d:
            secs = (ts(d["t"]) - start).total_seconds()
            row = {"complete": True, "checked": d["checked"], "ok": d["ok"], "not_boards": d["not_boards"],
                   "failed": d["failed"], "no_public_page": d["checked"] - d["ok"] - d["not_boards"] - d["failed"],
                   "jobs": d["jobs"], "lane_seconds": round(secs, 1)}
            burst_at, burst_secs = lane_stop_burst(pts, d)
            if burst_at is not None:
                answered = d["ok"] + d["not_boards"]
                stop_t = ts(next(p["t"] for p in pts if p["checked"] == burst_at))
                row.update({"stopped": True, "answered_before_stop": answered,
                            "failed_at_once": d["checked"] - burst_at, "failed_at_once_seconds": burst_secs,
                            "seconds_to_stop": round((stop_t - start).total_seconds(), 1),
                            "seconds_per_board": round((stop_t - start).total_seconds() / answered, 2)})
            else:
                row.update({"stopped": False, "seconds_per_board": round(secs / d["checked"], 2)})
        elif pts:
            last = pts[-1]
            secs = (ts(last["t"]) - start).total_seconds()
            row = {"complete": False, "checked": last["checked"], "of": last["of"], "ok": last["ok"],
                   "jobs": last["jobs"], "lane_seconds": round(secs, 1),
                   "seconds_per_board": round(secs / last["checked"], 2), "stopped": False}
        else:
            row = {"complete": False}
        out[ats] = row
    return out


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def crawler_settings(src):
    """Lane limits and stop rules, read from the crawler's own source."""
    ats_js = open(os.path.join(src, "ats.js"), encoding="utf-8").read()
    http_js = open(os.path.join(src, "http.js"), encoding="utf-8").read()
    lanes = {}
    for ats in ATS_ORDER:
        m = re.search(r"^\s*'?" + ats + r"'?: \{ concurrency: (\d+)(?:, minIntervalMs: (\d+))? \}", ats_js, re.M)
        if not m:
            raise SystemExit(f"lane {ats} not found in ats.js")
        lanes[ats] = {"concurrency": int(m.group(1)),
                      "min_interval_ms": int(m.group(2)) if m.group(2) else None}
    const = {k: int(re.search(rf"const {k} = (\d+);", http_js).group(1))
             for k in ("STOP_WINDOW", "STOP_BLOCKED", "STOP_RETRY_AFTER_S")}
    # Board statuses, from the header comment of refresh.js ("//   miss   answered 404, 410 or 401, ...").
    refresh_js = open(os.path.join(src, "refresh.js"), encoding="utf-8").read()
    statuses, cur = {}, None
    for line in refresh_js.splitlines():
        m = re.match(r"^//\s{3}(new|ok|miss|gone|error|nopage)\s+(.*)$", line)
        if m:
            cur = m.group(1)
            statuses[cur] = m.group(2).strip()
        elif cur and re.match(r"^//\s{6,}\S", line):
            statuses[cur] += " " + line[2:].strip()
        elif not line.startswith("//"):
            break
    return {"lanes": lanes, "stop_window": const["STOP_WINDOW"], "stop_blocked": const["STOP_BLOCKED"],
            "stop_retry_after_s": const["STOP_RETRY_AFTER_S"], "board_statuses": statuses}


def build(evidence, src):
    inputs = {}
    for key, name in FILES.items():
        p = os.path.join(evidence, name)
        if not os.path.exists(p):
            raise SystemExit(f"missing input {p}")
        inputs[key] = p
    for key, name in OPTIONAL.items():
        p = os.path.join(evidence, name)
        if os.path.exists(p):
            inputs[key] = p
    first = read_json(inputs["first_refresh_18"])
    pa, pb = read_json(inputs["personio_a_18"]), read_json(inputs["personio_b_18"])
    final = read_json(inputs["final_18"])
    pass1, pass2 = parse_log(inputs["pass1_19_log"]), parse_log(inputs["pass2_19_log"])
    p1, p2 = summarize_pass(pass1), summarize_pass(pass2)
    p2json = read_json(inputs["pass2_19_json"]) if "pass2_19_json" in inputs else None
    # The 19 Nov figures come from the second pass when it finished every ATS (its report exists and its log has a
    # done line for each); otherwise from the first pass, with Lever marked incomplete.
    primary_name = "pass2" if p2json and all(p2[a].get("complete") for a in ATS_ORDER) else "pass1"
    day19, other19 = (p2, p1) if primary_name == "pass2" else (p1, p2)

    stops18 = {s["lane"]: s["reason"] for s in first["refresh"]["stoppedLanes"]}
    stops18.update({s["lane"]: s["reason"] for s in pa["refresh"]["stoppedLanes"]})
    rows = []
    for ats in ATS_ORDER:
        r = {"ats": ATS_NAME[ats]}
        # 18 Nov: first validation of the candidates found in Common Crawl (a "not a board" answer means gone).
        if ats == "personio":
            a, b = pa["refresh"]["byAts"]["personio"], pb["refresh"]["byAts"]["personio"]
            cand, ok, gone, err = a["checked"], a["ok"] + b["ok"], a["gone"] + b["gone"], b["error"]
            r["personio_pass_a"] = {"checked": a["checked"], "ok": a["ok"], "gone": a["gone"], "error": a["error"],
                                    "seconds": pa["refresh"]["seconds"], "answered": a["ok"] + a["gone"]}
            r["personio_pass_b"] = {"checked": b["checked"], "ok": b["ok"], "gone": b["gone"], "error": b["error"],
                                    "seconds": pb["refresh"]["seconds"]}
        else:
            a = first["refresh"]["byAts"][ats]
            cand, ok, gone, err = a["checked"], a["ok"], a["gone"] + a["miss"], a["error"]
        read = ok + gone > 0   # Workable's lane stopped on 18 Nov before any board was read: no rate to report
        r.update({"candidates_18nov": cand, "live_18nov": ok, "not_a_board_18nov": gone, "failed_18nov": err,
                  "live_pct_18nov": pct(ok, cand) if read else None,
                  "not_a_board_pct_18nov": pct(gone, cand) if read else None,
                  "lane_stopped_18nov": stops18.get(ats, "")})
        # Index after 18 Nov (boards with a public page; jobs counted per board).
        ix = final["byAts"].get(ats)
        nopage = final["directoryStatus"].get(f"{ats}:nopage", 0)
        if ix:
            r.update({"index_boards_18nov": ix["boards"], "index_boards_with_jobs_18nov": ix["boardsWithJobs"],
                      "index_jobs_18nov": ix["jobs"], "jobs_per_board_18nov": r1(ix["jobs"] / ix["boards"]),
                      "jobs_per_board_with_jobs_18nov": r1(ix["jobs"] / ix["boardsWithJobs"]),
                      "empty_board_pct_18nov": pct(ix["boards"] - ix["boardsWithJobs"], ix["boards"]),
                      "no_public_page_18nov": nopage})
        # 19 Nov: re-check of every board not ruled out on 18 Nov.
        d = day19[ats]
        if d.get("checked"):
            r.update({"checked_19nov": d["checked"], "live_19nov": d["ok"], "jobs_19nov": d["jobs"],
                      "complete_19nov": "yes" if d.get("complete") else f"no ({d['checked']} of {d['of']})",
                      "seconds_per_board_19nov": d["seconds_per_board"], "lane_seconds_19nov": d["lane_seconds"],
                      "jobs_per_live_board_19nov": r1(d["jobs"] / d["ok"]) if d["ok"] else None})
            if d.get("complete"):
                # A stopped lane's share is taken over the boards that answered before the stop (below), not all.
                # live = in the index (job list and a working public board page); answered = the job API returned
                # a job list, whether or not the company's hosted board page still exists ("no public page").
                answered = d["ok"] + d["no_public_page"]
                r.update({"not_a_board_19nov": d["not_boards"], "failed_19nov": d["failed"],
                          "no_public_page_19nov": d["no_public_page"],
                          "answered_19nov": None if d.get("stopped") else answered,
                          "answered_pct_19nov": None if d.get("stopped") else pct(answered, d["checked"]),
                          "live_pct_19nov": None if d.get("stopped") else pct(d["ok"], d["checked"])})
            if d.get("stopped"):
                r.update({"answered_before_stop_19nov": d["answered_before_stop"],
                          "failed_at_once_19nov": d["failed_at_once"],
                          "failed_at_once_seconds_19nov": d["failed_at_once_seconds"],
                          "live_pct_of_answered_19nov": pct(d["ok"], d["answered_before_stop"]),
                          "not_a_board_pct_of_answered_19nov": pct(d["not_boards"], d["answered_before_stop"])})
            # Boards with and without jobs in the index the 19 Nov report built (only when that report exists).
            ix19 = (p2json or {}).get("byAts", {}).get(ats) if primary_name == "pass2" else None
            if ix19:
                r.update({"index_boards_19nov": ix19["boards"], "index_boards_with_jobs_19nov": ix19["boardsWithJobs"],
                          "empty_board_pct_19nov": pct(ix19["boards"] - ix19["boardsWithJobs"], ix19["boards"])})
            if ix and d.get("complete"):
                r.update({"boards_change_18_to_19nov": d["ok"] - ix["boards"],
                          "jobs_change_18_to_19nov": d["jobs"] - ix["jobs"],
                          "jobs_change_pct_18_to_19nov": round(100.0 * (d["jobs"] - ix["jobs"]) / ix["jobs"], 2)})
        o = other19[ats]
        if o.get("complete") and d.get("complete"):
            r.update({"jobs_19nov_other_pass": o["jobs"], "live_19nov_other_pass": o["ok"],
                      "jobs_diff_between_passes": d["jobs"] - o["jobs"]})
            if o.get("stopped"):
                r["answered_before_stop_19nov_other_pass"] = o["answered_before_stop"]
        rows.append(r)

    # Totals over the six ATSs in the table (BambooHR excluded).
    def tot(key):
        return sum(r.get(key) or 0 for r in rows)
    validated = [r for r in rows if r["ats"] != "Workable"]
    p1_start, p2_start = ts(pass1["start"]), ts(pass2["start"])
    summary = {
        "candidates_validated_18nov_five_ats": sum(r["candidates_18nov"] for r in validated),
        "live_18nov_five_ats": sum(r["live_18nov"] for r in validated),
        "not_a_board_18nov_five_ats": sum(r["not_a_board_18nov"] for r in validated),
        "not_a_board_pct_18nov_five_ats": pct(sum(r["not_a_board_18nov"] for r in validated),
                                              sum(r["candidates_18nov"] for r in validated)),
        "workable_candidates_18nov": rows[-1]["candidates_18nov"],
        "candidates_tried_18nov_six_ats": tot("candidates_18nov"),
        "index_boards_18nov": final["boards"], "index_boards_with_jobs_18nov": final["boardsWithJobs"],
        "index_jobs_18nov": final["jobs"], "index_built_18nov": final["builtAt"],
        "index_empty_board_pct_18nov": pct(final["boards"] - final["boardsWithJobs"], final["boards"]),
        "checked_19nov": pass2["boards"] if primary_name == "pass2" else pass1["boards"],
        # Day totals only when every ATS finished its 19 Nov pass.
        "live_19nov": tot("live_19nov") if all(day19[a].get("complete") for a in ATS_ORDER) else None,
        "jobs_19nov": tot("jobs_19nov") if all(day19[a].get("complete") for a in ATS_ORDER) else None,
        "primary_19nov_pass": primary_name,
        "pass1_19nov_start": pass1["start"], "pass2_19nov_start": pass2["start"],
        "hours_between_19nov_passes": round((p2_start - p1_start).total_seconds() / 3600, 1),
        "workable_retry_after_s_18nov": int(re.search(r"Retry-After (\d+)", stops18.get("workable", "x 0")).group(1)),
        "personio_stop_reason_18nov": stops18.get("personio", ""),
        "workable_stop_reason_18nov": stops18.get("workable", ""),
        "stopped_lanes_19nov_report": (p2json or {}).get("refresh", {}).get("stoppedLanes"),
        "pass2_19nov_report_seconds": (p2json or {}).get("seconds"),
    }
    summary["workable_retry_after_hours_18nov"] = round(summary["workable_retry_after_s_18nov"] / 3600, 1)
    # The 18 Nov stop happened after that run began (builtAt minus its duration), so its Retry-After ran out no
    # earlier than run start + Retry-After. The 19 Nov first pass started before that moment and was answered.
    run18_start = ts(first["builtAt"]) - dt.timedelta(seconds=first["seconds"])
    earliest_end = run18_start + dt.timedelta(seconds=summary["workable_retry_after_s_18nov"])
    summary["workable_18nov_run_start"] = run18_start.isoformat().replace("+00:00", "Z")
    summary["workable_18nov_retry_after_earliest_end"] = earliest_end.isoformat().replace("+00:00", "Z")
    summary["workable_answered_19nov_before_18nov_wait_ended"] = bool(p1_start < earliest_end
                                                                       and p1["workable"].get("ok", 0) > 0)
    stop19 = {s["lane"]: s["reason"] for s in (summary["stopped_lanes_19nov_report"] or [])}
    if "workable" in stop19:
        summary["workable_stop_reason_19nov"] = stop19["workable"]
        summary["workable_retry_after_s_19nov"] = int(re.search(r"Retry-After (\d+)", stop19["workable"]).group(1))
        summary["workable_retry_after_hours_19nov"] = round(summary["workable_retry_after_s_19nov"] / 3600, 1)
    if p2json:
        # Candidates still "new" after 19 Nov never answered at all (not even 404) in any pass.
        summary["recruitee_never_answered_19nov"] = p2json["directoryStatus"].get("recruitee:new", 0)
    done = [r for r in rows if r.get("answered_pct_19nov") is not None]
    if done:
        summary["answered_pct_19nov_min"] = min(r["answered_pct_19nov"] for r in done)
        summary["answered_pct_19nov_max"] = max(r["answered_pct_19nov"] for r in done)
        summary["rechecked_19nov_five_ats"] = sum(r["checked_19nov"] for r in done)
        summary["answered_19nov_five_ats"] = sum(r["answered_19nov"] for r in done)
        summary["answered_pct_19nov_five_ats"] = pct(summary["answered_19nov_five_ats"],
                                                     summary["rechecked_19nov_five_ats"])
    m = re.search(r"(\d+) of its last (\d+) answers", summary["personio_stop_reason_18nov"])
    summary["personio_stop_blocked_18nov"], summary["personio_stop_window_18nov"] = int(m.group(1)), int(m.group(2))
    pa_row = next(r for r in rows if r["ats"] == "Personio")
    summary["personio_pass_a_answered_18nov"] = pa_row["personio_pass_a"]["answered"]
    summary["personio_pass_a_seconds_18nov"] = pa_row["personio_pass_a"]["seconds"]
    summary["personio_pass_b_checked_18nov"] = pa_row["personio_pass_b"]["checked"]
    summary["personio_pass_b_errors_18nov"] = pa_row["personio_pass_b"]["error"]
    summary["personio_pass_b_hours_18nov"] = round(pa_row["personio_pass_b"]["seconds"] / 3600, 1)
    # That pass also looked up company names on the same one-a-second lane (counted only when a name was found),
    # so it made at least checked + names requests.
    summary["personio_pass_b_names_fetched_18nov"] = pb["refresh"]["namesFetched"]
    summary["personio_pass_b_requests_min_18nov"] = pb["refresh"]["checked"] + pb["refresh"]["namesFetched"]
    summary["personio_pass_b_seconds_per_request_18nov"] = round(
        pb["refresh"]["seconds"] / summary["personio_pass_b_requests_min_18nov"], 2)
    wk = next(r for r in rows if r["ats"] == "Workable")
    if wk.get("failed_at_once_19nov") is not None:
        # Failed checks outside the burst the log can time (progress lines come every 1,000 checks).
        summary["workable_failed_outside_timed_burst_19nov"] = wk["failed_19nov"] - wk["failed_at_once_19nov"]
    inputs_meta = {os.path.basename(p): sha256(p) for p in inputs.values()}
    return {"rows": rows, "summary": summary, "inputs_sha256": inputs_meta}


CSV_COLS = ["ats", "candidates_18nov", "live_18nov", "not_a_board_18nov", "failed_18nov", "live_pct_18nov",
            "not_a_board_pct_18nov", "lane_stopped_18nov", "index_boards_18nov", "index_boards_with_jobs_18nov",
            "index_jobs_18nov", "jobs_per_board_18nov", "jobs_per_board_with_jobs_18nov", "empty_board_pct_18nov",
            "no_public_page_18nov", "checked_19nov", "complete_19nov", "live_19nov", "not_a_board_19nov",
            "failed_19nov", "no_public_page_19nov", "answered_19nov", "answered_pct_19nov", "live_pct_19nov",
            "answered_before_stop_19nov",
            "live_pct_of_answered_19nov", "not_a_board_pct_of_answered_19nov", "failed_at_once_19nov",
            "failed_at_once_seconds_19nov",
            "index_boards_19nov", "index_boards_with_jobs_19nov", "empty_board_pct_19nov",
            "jobs_19nov", "jobs_per_live_board_19nov",
            "seconds_per_board_19nov", "lane_seconds_19nov", "boards_change_18_to_19nov", "jobs_change_18_to_19nov",
            "jobs_change_pct_18_to_19nov", "live_19nov_other_pass", "jobs_19nov_other_pass",
            "jobs_diff_between_passes", "answered_before_stop_19nov_other_pass"]


def fmt(v):
    return "" if v is None else str(v)


def write_outputs(data, root, settings):
    data = dict(data)
    data["method"] = settings
    data["about"] = ("Per-ATS results of the ScrapeTools job-index refresh, 18-19 Nov 2026. "
                     "Built by ct-001/build_data.py from the refresh's report files; BambooHR excluded.")
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(CSV_COLS)
    for r in data["rows"]:
        w.writerow([fmt(r.get(c)) for c in CSV_COLS])
    csv_text = buf.getvalue()
    with open(os.path.join(root, CSV_REL), "w", encoding="utf-8", newline="") as f:
        f.write(csv_text)
    with open(os.path.join(root, JSON_REL), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1)
        f.write("\n")
    # facts.json for the content-autopilot machine gate: one fact per CSV row, one per summary/method value.
    today = dt.date.today().isoformat()
    facts = []
    for r in data["rows"]:
        # "column=value; ..." rather than the raw CSV line: the gate reads "10785,0,0" as one number.
        cells = [(c, r.get(c)) for c in CSV_COLS[1:] if r.get(c) not in (None, "")]
        excerpt = f"{r['ats']}: " + "; ".join(f"{c}={v}" for c, v in cells)
        nums = sorted({str(abs(v)) for _, v in cells if isinstance(v, (int, float)) and not isinstance(v, bool)},
                      key=float)
        facts.append({"id": f"row-{r['ats'].lower()}", "claim": f"{r['ats']} per-ATS crawl figures (CSV row)",
                      "source_url": f"{SITE}/{CSV_REL}", "fetched": today, "excerpt": excerpt, "numbers": nums})
    flat = dict(data["summary"])
    for ats, lane in settings["lanes"].items():
        flat[f"lane_{ats}_concurrency"] = lane["concurrency"]
        if lane["min_interval_ms"]:
            flat[f"lane_{ats}_min_interval_ms"] = lane["min_interval_ms"]
    for k in ("stop_window", "stop_blocked", "stop_retry_after_s"):
        flat[k] = settings[k]
    for r in data["rows"]:
        for sub in ("personio_pass_a", "personio_pass_b"):
            for k, v in (r.get(sub) or {}).items():
                flat[f"{sub}_{k}"] = v
    for k, st in settings["board_statuses"].items():
        flat[f"board_status_{k}"] = st
    for k, v in flat.items():
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            facts.append({"id": k, "claim": k.replace("_", " "), "source_url": f"{SITE}/{JSON_REL}",
                          "fetched": today, "excerpt": f'"{k}": {v}', "numbers": [str(abs(v))]})
        elif isinstance(v, str) and re.search(r"\d", v):
            # Stop reasons, status rules and timestamps: their numbers (HTTP codes, crawl days) are traced too.
            nums = sorted({m.group(0) for m in re.finditer(r"\d+(?:\.\d+)?", v)}, key=float)
            facts.append({"id": k, "claim": k.replace("_", " "), "source_url": f"{SITE}/{JSON_REL}",
                          "fetched": today, "excerpt": f'"{k}": "{v}"', "numbers": nums})
    with open(os.path.join(root, "ct-001", "facts.json"), "w", encoding="utf-8") as f:
        json.dump({"target_query": TARGET_QUERY, "facts": facts}, f, indent=1)
        f.write("\n")
    return data


# ---------------------------------------------------------------- --check: every number on the page is in the data

MONTH = r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*"
NUM = re.compile(r"(?<![\w.#/-])(\d[\d,]*(?:\.\d+)?)%?(?![\w-]*\d)")


def visible_text(html):
    html = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", " ", html, flags=re.S | re.I)
    m = re.search(r"<main\b.*?</main>", html, re.S | re.I)
    body = m.group(0) if m else html
    head = " ".join(re.findall(r"<title>(.*?)</title>", html, re.S) +
                    re.findall(r'<meta name="description" content="([^"]*)"', html))
    text = re.sub(r"<[^>]+>", " ", body) + " " + head
    return re.sub(r"&[a-z]+;|&#\d+;", " ", text)


def page_numbers(text):
    t = re.sub(r"\b\d{1,2} " + MONTH + r"(?: \d{4})?\b", " ", text)       # 18 Nov, 19 Nov 2026
    t = re.sub(r"\b" + MONTH + r" \d{1,2},? \d{4}\b", " ", t)
    t = re.sub(r"\b\d{4}-\d\d-\d\d(?:T[\d:.]+Z)?\b", " ", t)
    t = re.sub(r"\b\d\d:\d\d(?::\d\d)?\b", " ", t)                          # 00:16 UTC
    t = re.sub(r"\b20[2-3]\d\b", " ", t)
    return [m.group(1) for m in NUM.finditer(t)]


def allowed_values(data):
    vals = set()

    def walk(x):
        if isinstance(x, bool):
            return
        if isinstance(x, (int, float)):
            vals.add(round(float(abs(x)), 6))
        elif isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
        elif isinstance(x, str):
            for m in re.finditer(r"\d+(?:\.\d+)?", x):
                vals.add(round(float(m.group(0)), 6))
    walk({k: v for k, v in data.items() if k != "inputs_sha256"})
    # HTTP statuses named in the crawler's status rules (src/refresh.js header) and the success code.
    vals |= {200.0, 401.0, 404.0, 410.0, 403.0, 429.0}
    return vals


def check_page(page, data):
    text = visible_text(open(page, encoding="utf-8").read())
    allowed = allowed_values(data)
    bad = []
    for raw in page_numbers(text):
        v = round(float(raw.replace(",", "")), 6)
        if v in allowed or (v.is_integer() and 0 <= v <= 12):
            continue
        bad.append(raw)
    return sorted(set(bad), key=lambda s: float(s.replace(",", "")))


# Each table cell must hold its own row's value, not just any value from the data. Caption prefix -> {column label:
# data key}; a per-ATS override covers Workable, whose first check and stop are on 19 Nov.
TABLES = {
    "First check of each board address": {
        "Addresses": "candidates_18nov", "Not a board": "not_a_board_18nov", "Share": "not_a_board_pct_18nov"},
    "Re-check of known boards": {
        "Job list returned": "answered_pct_19nov", "Jobs per board": "jobs_per_live_board_19nov",
        "No jobs": "empty_board_pct_19nov", "Seconds per board": "seconds_per_board_19nov"},
}
OVERRIDES = {("First check of each board address", "Workable"): {
    "Not a board": "not_a_board_19nov", "Share": "not_a_board_pct_of_answered_19nov"},
    ("Re-check of known boards", "Workable"): {"Job list returned": "live_pct_of_answered_19nov"}}


def check_tables(page, data):
    html = open(page, encoding="utf-8").read()
    rows = {r["ats"]: r for r in data["rows"]}
    bad, seen = [], 0
    for cap, body in re.findall(r"<caption>(.*?)</caption>.*?<tbody>(.*?)</tbody>", html, re.S):
        spec = next((v for k, v in TABLES.items() if cap.startswith(k)), None)
        if not spec:
            continue
        key = next(k for k in TABLES if cap.startswith(k))
        for tr in re.findall(r"<tr>(.*?)</tr>", body, re.S):
            cells = dict(re.findall(r'<t[dh] data-label="([^"]+)"[^>]*>(.*?)</t[dh]>', tr, re.S))
            ats = re.sub(r"[^A-Za-z]", "", cells.get("ATS", ""))   # "Workable*" (footnote mark) -> "Workable"
            for label, field in {**spec, **OVERRIDES.get((key, ats), {})}.items():
                m = re.search(r"-?\d[\d,]*(?:\.\d+)?", re.sub(r"<[^>]+>", "", cells.get(label, "")))
                want = rows[ats].get(field)
                got = float(m.group(0).replace(",", "")) if m else None
                seen += 1
                if want is None or got is None or abs(got - float(want)) > 1e-9:
                    bad.append(f"{key} / {ats} / {label}: page {got}, data {field}={want}")
    return bad, seen


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--evidence", required=True, help="directory holding the refresh reports and logs")
    ap.add_argument("--crawler-src", required=True, help="the crawler's src/ directory (lane limits, stop rules)")
    ap.add_argument("--check", help="page to verify: every visible number must come from the generated data")
    args = ap.parse_args()
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data = write_outputs(build(args.evidence, args.crawler_src), root, crawler_settings(args.crawler_src))
    s = data["summary"]
    print(f"rows {len(data['rows'])}; 19 Nov figures from {s['primary_19nov_pass']}; inputs: "
          + ", ".join(sorted(data["inputs_sha256"])))
    print(f"wrote {CSV_REL}, {JSON_REL}, ct-001/facts.json")
    if args.check:
        bad = check_page(args.check, data)
        if bad:
            print(f"CHECK FAIL: {len(bad)} numbers on {os.path.basename(args.check)} are not in the data: "
                  + ", ".join(bad))
            sys.exit(1)
        print(f"CHECK PASS: every number on {os.path.basename(args.check)} is in the generated data")
        tbad, seen = check_tables(args.check, data)
        if tbad or not seen:
            print(f"TABLE CHECK FAIL ({seen} cells): " + ("; ".join(tbad) or "no table cells found"))
            sys.exit(1)
        print(f"TABLE CHECK PASS: {seen} table cells match their own row and column in the data")


if __name__ == "__main__":
    main()
