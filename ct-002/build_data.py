"""Rebuild every number on what-day-are-most-jobs-posted.html from the job index that ATS Jobs Search built at
04:03 UTC on 19 Nov 2026 (the manifest and its six gzip shards).

The index files are not published here. The CSV and JSON written by this script carry every count the page uses,
plus each input file's SHA-256, so a run on a different index build is detected and refused.

Usage:
    python -I ct-002/build_data.py --index <dir with index-manifest.json and index-*.gz>
    python -I ct-002/build_data.py --index <dir> --check what-day-are-most-jobs-posted.html
    python -I ct-002/build_data.py --check what-day-are-most-jobs-posted.html      (no index: checks the page
                                                                                       against the committed JSON)

Writes (paths relative to the site root, the parent of ct-002/):
    data/job-posting-days-2026-11.csv    weekday counts and shares per group (the page's download)
    data/job-posting-days-2026-11.json   the same plus hour-of-day counts, the refresh-time table, method and hashes
    ct-002/facts.json                    the content-autopilot gate's facts file (each number traced to the files above)
With --check, it fails if any number visible on the page is not in the data, if a table cell does not hold its own
row's value, or if the chart data embedded in the page differs from the JSON.

Standard library only. Nothing is fetched from the network. Each shard is read and released in turn.
"""
import argparse
import collections
import csv
import datetime as dt
import gzip
import hashlib
import io
import json
import math
import os
import re
import sys

SITE = "https://scrapetools.scaleturn.com"
CSV_REL = "data/job-posting-days-2026-11.csv"
JSON_REL = "data/job-posting-days-2026-11.json"
PAGE = "what-day-are-most-jobs-posted.html"
TARGET_QUERY = "what day are most jobs posted"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The build the page measures. A different build (the Actor rebuilds the index daily) is refused, not silently used.
BUILT_AT = "2026-11-19T04:03:40.394Z"
EXPECTED_SHA256 = {
    "index-manifest.json": "4c302194d6386bdc305f804c78e82e2e75b3ff7fd7bbcaa370127cfec26e6c7e",
    "index-ashby-0.gz": "250ff59939e319f8b25e521b5fc4ef456d5af1d0e6ced94ac2b2d94a96c01c56",
    "index-greenhouse-0.gz": "8bbaac67b4e62e04f6e59fefe927e4501c746165001daec296d3636df004f9e7",
    "index-lever-0.gz": "51880d82b821dd182ab43dcd948b24797c025b034268ee8ec625ae2e898265dd",
    "index-personio-0.gz": "b7eb3e494a299ccdac055568a4fd2a62c014442897926712741dded64bffdaea",
    "index-recruitee-0.gz": "de78defc708dbb0cc2cad7ff1d68a06f4e73b1008bff1d3cd3ae3216b0097cd0",
    "index-workable-0.gz": "5c6a507c70a1b287d33a6d93ab4af88774e351621b174ffa06ec2553aa7eb1d3",
}

ATS_ORDER = ["greenhouse", "lever", "ashby", "recruitee", "personio", "workable"]
ATS_NAME = {"greenhouse": "Greenhouse", "lever": "Lever", "ashby": "Ashby", "recruitee": "Recruitee",
            "personio": "Personio", "workable": "Workable"}
# The vendor field each posting time comes from (the crawler's src/ats.js). Workable gives a date without a time.
POSTED_FIELD = {"greenhouse": "first_published", "lever": "createdAt", "ashby": "publishedAt",
                "recruitee": "published_at (else created_at)", "personio": "createdAt",
                "workable": "published_on (else created_at), a date without a time"}
DATE_ONLY = {"workable"}
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
DAY_KEYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

# ---------------------------------------------------------------- region from the location text
US_CODES = ("AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND "
            "OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY").split()
US_STATES = ("Alabama|Alaska|Arizona|Arkansas|California|Colorado|Connecticut|Delaware|Florida|Georgia|Hawaii|Idaho|"
             "Illinois|Indiana|Iowa|Kansas|Kentucky|Louisiana|Maine|Maryland|Massachusetts|Michigan|Minnesota|"
             "Mississippi|Missouri|Montana|Nebraska|Nevada|New Hampshire|New Jersey|New Mexico|New York|"
             "North Carolina|North Dakota|Ohio|Oklahoma|Oregon|Pennsylvania|Rhode Island|South Carolina|"
             "South Dakota|Tennessee|Texas|Utah|Vermont|Virginia|Washington|West Virginia|Wisconsin|Wyoming|"
             "District of Columbia")
US_CITIES = ("San Francisco|Los Angeles|NYC|Seattle|Chicago|Boston|Austin|Denver|Atlanta|Miami|Dallas|Houston|"
             "Philadelphia|Phoenix|San Diego|San Jose|Sunnyvale|Santa Clara|Palo Alto|Mountain View|Menlo Park|"
             "Redwood City|San Mateo|Oakland|Pittsburgh|Salt Lake City|Minneapolis|Detroit|Nashville|Raleigh|"
             "Bay Area|Silicon Valley")
EU_COUNTRIES = ("Germany|Deutschland|Netherlands|Nederland|Holland|United Kingdom|England|Scotland|Wales|"
                "Northern Ireland|Ireland|France|Spain|España|Espana|Italy|Italia|Portugal|Belgium|België|Belgique|"
                "Austria|Österreich|Switzerland|Schweiz|Suisse|Sweden|Sverige|Denmark|Danmark|Norway|Norge|Finland|"
                "Suomi|Poland|Polska|Czech Republic|Czechia|Slovakia|Hungary|Romania|Bulgaria|Greece|Croatia|"
                "Slovenia|Serbia|Estonia|Latvia|Lithuania|Luxembourg|Iceland|Malta|Cyprus|Ukraine|Bosnia|Albania|"
                "North Macedonia|Montenegro|Moldova|Europe|European Union")
EU_CITIES = ("Berlin|Munich|München|Hamburg|Cologne|Köln|Frankfurt|Stuttgart|Düsseldorf|Leipzig|Dresden|Hannover|"
             "Nuremberg|Nürnberg|Bremen|Essen|Dortmund|Vienna|Wien|Graz|Zurich|Zürich|Geneva|Genève|Basel|Bern|"
             "Amsterdam|Rotterdam|Utrecht|Eindhoven|The Hague|Den Haag|London|Manchester|Edinburgh|Glasgow|"
             "Bristol|Leeds|Dublin|Paris|Lyon|Marseille|Madrid|Barcelona|Milan|Milano|Rome|Roma|Lisbon|Lisboa|"
             "Porto|Brussels|Bruxelles|Antwerp|Stockholm|Gothenburg|Copenhagen|København|Oslo|Helsinki|Warsaw|"
             "Warszawa|Kraków|Krakow|Wrocław|Wroclaw|Prague|Praha|Budapest|Bucharest|Tallinn|Riga|Vilnius")
OTHER_PLACES = ("Canada|(?<!New )Mexico|México|Brazil|Brasil|Argentina|Chile|Colombia|Peru|India|China|Japan|"
                "Singapore|Australia|New Zealand|Philippines|Indonesia|Malaysia|Vietnam|Thailand|Korea|Taiwan|"
                "Hong Kong|Israel|United Arab Emirates|UAE|Dubai|Saudi Arabia|Qatar|Egypt|Nigeria|Kenya|"
                "South Africa|Pakistan|Bangladesh|Turkey|Türkiye|Morocco|Costa Rica|Uruguay|Puerto Rico|LATAM|"
                "APAC|Toronto|Vancouver|Montreal|Montréal|Bangalore|Bengaluru|Mumbai|Hyderabad|Sydney|Melbourne|"
                "Tokyo|Tel Aviv|São Paulo|Sao Paulo|Bogotá|Bogota|Manila")
RX_US_CODE = re.compile(r",\s*(?:" + "|".join(US_CODES) + r")(?=$|[\s,;)/|-])")      # "Boston, MA", case-sensitive
RX_US_WORD = re.compile(r"\b(?:US|USA|U\.S\.A?\.?)(?=$|[\s,;)/|-])")                   # "Remote - US", "USA"
RX_US_NAME = re.compile(r"\b(?:United States|" + US_STATES + "|" + US_CITIES + r")\b", re.I)
RX_EU = re.compile(r"\b(?:" + EU_COUNTRIES + "|" + EU_CITIES + r")\b|\b(?:UK|EU)\b", re.I)
RX_OTHER = re.compile(r"\b(?:" + OTHER_PLACES + r")\b", re.I)


def region(location):
    """'us', 'europe', or 'other' (no place we recognise, or places in more than one region)."""
    loc = location or ""
    us = bool(RX_US_CODE.search(loc) or RX_US_WORD.search(loc) or RX_US_NAME.search(loc))
    eu = bool(RX_EU.search(loc))
    oth = bool(RX_OTHER.search(loc))
    if us and not eu and not oth:
        return "us"
    if eu and not us and not oth:
        return "europe"
    return "other"


# ---------------------------------------------------------------- clocks (no tz database needed)
def _sunday(year, month, n):
    """n-th Sunday of the month (n=-1: the last)."""
    if n > 0:
        d = dt.date(year, month, 1)
        d += dt.timedelta(days=(6 - d.weekday()) % 7)
        return d + dt.timedelta(weeks=n - 1)
    d = dt.date(year + (month == 12), month % 12 + 1, 1) - dt.timedelta(days=1)
    return d - dt.timedelta(days=(d.weekday() - 6) % 7)


def _utc(d, hour):
    return dt.datetime(d.year, d.month, d.day, hour, tzinfo=dt.timezone.utc).timestamp()


def us_eastern_offset_h(ts):
    """US Eastern: UTC-4 from the 2nd Sunday of March 07:00 UTC to the 1st Sunday of November 06:00 UTC, else UTC-5
    (the US rule since 2007)."""
    y = dt.datetime.fromtimestamp(ts, dt.timezone.utc).year
    return -4 if _utc(_sunday(y, 3, 2), 7) <= ts < _utc(_sunday(y, 11, 1), 6) else -5


def central_europe_offset_h(ts):
    """Central European time: UTC+2 from the last Sunday of March to the last Sunday of October, 01:00 UTC both
    (the EU rule), else UTC+1."""
    y = dt.datetime.fromtimestamp(ts, dt.timezone.utc).year
    return 2 if _utc(_sunday(y, 3, -1), 1) <= ts < _utc(_sunday(y, 10, -1), 1) else 1


CLOCKS = {"utc": lambda ts: 0, "us_eastern": us_eastern_offset_h, "central_europe": central_europe_offset_h}
CLOCK_NAME = {"utc": "UTC", "us_eastern": "US Eastern time", "central_europe": "Central European time"}


def local(ts, clock, date_only):
    """(local date, local hour or None). A date-only posting keeps its own date and has no hour."""
    if date_only:
        return dt.datetime.fromtimestamp(ts, dt.timezone.utc).date(), None
    t = dt.datetime.fromtimestamp(ts + 3600 * CLOCKS[clock](ts), dt.timezone.utc)
    return t.date(), t.hour


# ---------------------------------------------------------------- inputs
def sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def verify_inputs(index_dir):
    got = {}
    for name, want in EXPECTED_SHA256.items():
        p = os.path.join(index_dir, name)
        if not os.path.exists(p):
            sys.exit(f"STOP: {p} is missing. The page measures the index built at {BUILT_AT}.")
        got[name] = sha256(p)
        if got[name] != want:
            sys.exit(f"STOP: {name} has SHA-256 {got[name]}, not the {BUILT_AT} build's {want}. The Actor rebuilds "
                     "its index daily; point --index at the snapshot of that build, or re-measure the page.")
    man = json.load(open(os.path.join(index_dir, "index-manifest.json"), encoding="utf-8"))
    if man.get("builtAt") != BUILT_AT:
        sys.exit(f"STOP: manifest builtAt {man.get('builtAt')} is not {BUILT_AT}.")
    return man, got


def read_jobs(index_dir, man):
    """Yield (ats, board_key, title, location, posted_sec) for every job, one shard at a time."""
    for s in man["shards"]:
        with gzip.open(os.path.join(index_dir, s["key"] + ".gz")) as fh:
            shard = json.loads(fh.read())
        if shard.get("v") != 1:
            sys.exit(f"STOP: shard {s['key']} has version {shard.get('v')}, expected 1")
        ats = shard["ats"]
        for b, job_id, title, location, remote, posted in shard["jobs"]:
            yield ats, (ats, b), title or "", location or "", posted
        del shard


# ---------------------------------------------------------------- measuring
def pct(part, whole, nd=1):
    return round(100.0 * part / whole, nd) if whole else None


def closure_adjusted(by_date, start, build_day):
    """A snapshot holds only the jobs still open, so a Monday's jobs, older than that week's Friday's, have had more
    time to close. Estimate the closure rate from the data: log(jobs on a date) = weekday level - rate x age, fitted
    by least squares over Monday-Friday dates with one level per weekday, so the rate comes from how the same
    weekday's count falls from week to week. Then weight each date's jobs by exp(rate x age) and recompute the
    weekday shares. The rate also absorbs any trend in posting volume over the four weeks."""
    pts = [(i % 7, (build_day - start).days - i, math.log(c)) for i, c in enumerate(by_date) if c > 0 and i % 7 < 5]
    num = den = 0.0
    for wd in range(5):
        q = [p for p in pts if p[0] == wd]
        ma, my = sum(p[1] for p in q) / len(q), sum(p[2] for p in q) / len(q)
        num += sum((p[1] - ma) * (p[2] - my) for p in q)
        den += sum((p[1] - ma) ** 2 for p in q)
    rate = -num / den
    adj = [0.0] * 7
    for i, c in enumerate(by_date):
        adj[i % 7] += c * math.exp(rate * ((build_day - start).days - i))
    s = sum(adj)
    out = {"closure_rate_per_day_pct": round(100 * (1 - math.exp(-rate)), 2),
           "same_weekday_decline_per_week_pct": round(100 * (1 - math.exp(-7 * rate)), 1)}
    for i, k in enumerate(DAY_KEYS):
        out[f"{k}_adj_pct"] = round(100 * adj[i] / s, 1)
    out["mon_wed_adj_pct"] = round(100 * sum(adj[:3]) / s, 1)
    out["weekend_adj_pct"] = round(100 * (adj[5] + adj[6]) / s, 1)
    top = max(range(7), key=lambda i: adj[i])
    out["top_day_adj"] = DAYS[top]
    out["top_day_adj_pct"] = out[f"{DAY_KEYS[top]}_adj_pct"]
    others = [out[f"{DAY_KEYS[i]}_adj_pct"] for i in range(5) if i != top]
    out["other_weekdays_adj_min_pct"], out["other_weekdays_adj_max_pct"] = min(others), max(others)
    return out


def build(index_dir):
    man, hashes = verify_inputs(index_dir)
    built = dt.datetime.fromisoformat(BUILT_AT.replace("Z", "+00:00"))
    # Four full weeks, Monday to Sunday, ending on the last Sunday before the build day.
    end = built.date() - dt.timedelta(days=(built.date().weekday() + 1) % 7 or 7)
    start = end - dt.timedelta(days=27)
    assert start.weekday() == 0 and end.weekday() == 6, (start, end)

    # Pass 1: count every job, then drop copies: the same title, location and posting time on two boards of one
    # ATS (one employer's jobs mirrored on several boards). A board's own repeats are kept.
    total = collections.Counter()
    no_date = collections.Counter()
    per_key = {}
    rows = []
    for ats, board, title, location, posted in read_jobs(index_dir, man):
        total[ats] += 1
        if not posted:
            no_date[ats] += 1
            continue
        k = (ats, title.strip().lower(), location.strip().lower(), posted)
        bc = per_key.setdefault(k, collections.Counter())
        bc[board] += 1
        rows.append((ats, board, location, posted, k))
    keep_board = {k: min(bc, key=lambda b: (-bc[b], b)) for k, bc in per_key.items() if len(bc) > 1}
    jobs = [(ats, board, location, posted) for ats, board, location, posted, k in rows
            if k not in keep_board or keep_board[k] == board]
    copies = collections.Counter(r[0] for r in rows) - collections.Counter(j[0] for j in jobs)
    del rows, per_key

    # Groups: (id, label, ATSs, region filter, clock, window only)
    groups = [("all", "All six ATSs", ATS_ORDER, None, "utc", True)]
    groups += [(a, ATS_NAME[a], [a], None, "utc", True) for a in ATS_ORDER]
    groups += [("us", "Jobs located in the US", ATS_ORDER, "us", "us_eastern", True),
               ("europe", "Jobs located in Europe", ATS_ORDER, "europe", "central_europe", True),
               ("all_open", "All open jobs, any posting date", ATS_ORDER, None, "utc", False)]

    reg_count = collections.Counter()
    reg_count_window = collections.Counter()
    out_groups, out_hours, by_date_all = {}, {}, {}
    hour_ts = []      # (UTC minute of day) of every timed job in the window, for the refresh table
    for gid, label, atss, reg, clock, windowed in groups:
        wd = [0] * 7
        by_date = [0] * 28
        board_jobs = collections.defaultdict(lambda: [0] * 7)
        hours = [[0] * 24 for _ in range(7)]
        timed = 0
        for ats, board, location, posted in jobs:
            if ats not in atss:
                continue
            r = region(location) if (reg or gid == "all") else None
            if gid == "all":
                reg_count[r] += 1
            if reg and r != reg:
                continue
            d, h = local(posted, clock, ats in DATE_ONLY)
            if windowed and not (start <= d <= end):
                continue
            if gid == "all":
                reg_count_window[r] += 1
            w = d.weekday()
            wd[w] += 1
            if windowed:
                by_date[(d - start).days] += 1
            board_jobs[board][w] += 1
            if h is not None:
                hours[w][h] += 1
                timed += 1
                if gid == "all":
                    t = dt.datetime.fromtimestamp(posted, dt.timezone.utc)
                    hour_ts.append(t.hour * 60 + t.minute)
        n = sum(wd)
        nb = len(board_jobs)
        bw = [0.0] * 7
        for counts in board_jobs.values():
            s = sum(counts)
            for i in range(7):
                bw[i] += counts[i] / s
        g = {"label": label, "clock": CLOCK_NAME[clock] + (" (Workable: its own date)" if "workable" in atss else ""),
             "window": f"{start.isoformat()} to {end.isoformat()}" if windowed else "all open jobs",
             "jobs": n, "boards": nb}
        for i, k in enumerate(DAY_KEYS):
            g[f"{k}_jobs"] = wd[i]
        for i, k in enumerate(DAY_KEYS):
            g[f"{k}_pct"] = pct(wd[i], n)
        for i, k in enumerate(DAY_KEYS):
            g[f"{k}_board_pct"] = round(100.0 * bw[i] / nb, 1) if nb else None
        g["mon_wed_pct"] = pct(sum(wd[:3]), n)
        g["mon_thu_pct"] = pct(sum(wd[:4]), n)
        g["weekend_pct"] = pct(wd[5] + wd[6], n)
        g["weekend_board_pct"] = round(100.0 * (bw[5] + bw[6]) / nb, 1) if nb else None
        top = max(range(7), key=lambda i: wd[i])
        g["top_day"] = DAYS[top]
        g["top_day_pct"] = g[f"{DAY_KEYS[top]}_pct"]
        btop = max(range(7), key=lambda i: bw[i])
        g["top_day_boards"] = DAYS[btop]
        out_groups[gid] = g
        if windowed:
            by_date_all[gid] = by_date
            g.update(closure_adjusted(by_date, start, built.date()))
        if timed:
            by_hour = [sum(hours[w][h] for w in range(7)) for h in range(24)]
            ph = max(range(24), key=lambda h: by_hour[h])
            weekday_hours = [sum(hours[w][h] for w in range(5)) for h in range(24)]
            out_hours[gid] = {
                "label": label, "clock": CLOCK_NAME[clock], "timed_jobs": timed,
                "by_weekday_hour": hours, "hour_pct": [pct(x, timed) for x in by_hour],
                "peak_hour": ph, "peak_hour_pct": pct(by_hour[ph], timed),
                "share_9_to_17_pct": pct(sum(by_hour[9:17]), timed),
                "share_0_to_6_pct": pct(sum(by_hour[0:6]), timed),
                "busiest_three_hours_start": max(range(22), key=lambda h: sum(by_hour[h:h + 3])),
                "weekday_peak_hour": max(range(24), key=lambda h: weekday_hours[h]),
            }
            b3 = out_hours[gid]["busiest_three_hours_start"]
            out_hours[gid]["busiest_three_hours_pct"] = pct(sum(by_hour[b3:b3 + 3]), timed)

    # Refresh time: one daily refresh at hour H (UTC) picks up each job posted since the last one. Mean wait from
    # posting to that refresh, and the share picked up within 6 hours, over every timed job of the window.
    refresh = []
    m = len(hour_ts)
    for H in range(24):
        waits = [((H * 60 - t) % 1440) / 60 for t in hour_ts]
        refresh.append({"hour_utc": H, "mean_wait_h": round(sum(waits) / m, 1),
                        "within_6h_pct": pct(sum(1 for w in waits if w <= 6), m)})
    best = min(refresh, key=lambda r: (r["mean_wait_h"], r["hour_utc"]))
    worst = max(refresh, key=lambda r: (r["mean_wait_h"], -r["hour_utc"]))

    timed_ats = [a for a in ATS_ORDER if a not in DATE_ONLY]
    summary = {
        "index_built_at": BUILT_AT, "window_start": start.isoformat(), "window_end": end.isoformat(),
        "window_days": 28, "window_weeks": 4,
        "index_boards": man["boards"], "index_jobs": man["jobs"],
        "jobs_counted": sum(total.values()), "jobs_without_date": sum(no_date.values()),
        "jobs_dated": sum(total.values()) - sum(no_date.values()),
        "copies_dropped": sum(copies.values()), "jobs_after_copies": len(jobs),
        "window_jobs": out_groups["all"]["jobs"], "window_boards": out_groups["all"]["boards"],
        "window_share_of_open_pct": pct(out_groups["all"]["jobs"], len(jobs)),
        "window_timed_jobs": out_hours["all"]["timed_jobs"],
        "region_us_jobs": reg_count["us"], "region_europe_jobs": reg_count["europe"],
        "region_other_jobs": reg_count["other"],
        "region_us_pct": pct(reg_count["us"], len(jobs)), "region_europe_pct": pct(reg_count["europe"], len(jobs)),
        "region_other_pct": pct(reg_count["other"], len(jobs)),
        "window_region_us_jobs": reg_count_window["us"], "window_region_europe_jobs": reg_count_window["europe"],
        "refresh_best_hour_utc": best["hour_utc"], "refresh_best_mean_wait_h": best["mean_wait_h"],
        "refresh_best_within_6h_pct": best["within_6h_pct"],
        "refresh_worst_hour_utc": worst["hour_utc"], "refresh_worst_mean_wait_h": worst["mean_wait_h"],
        "refresh_worst_within_6h_pct": worst["within_6h_pct"],
        "refresh_at_index_build_hour_utc": 4,
        "refresh_at_index_build_mean_wait_h": refresh[4]["mean_wait_h"],
        "refresh_at_index_build_within_6h_pct": refresh[4]["within_6h_pct"],
    }
    for a in ATS_ORDER:
        summary[f"copies_dropped_{a}"] = copies[a]
        summary[f"jobs_without_date_{a}"] = no_date[a]
    data = {
        "title": "What day are most jobs posted: posting day and hour of open jobs on company job boards",
        "source": "The job index of ATS Jobs Search (Apify Actor scaleturn/ats-jobs-search), built "
                  f"{BUILT_AT}: {man['boards']} company job boards on six applicant tracking systems.",
        "method": {
            "window": f"Jobs whose posting date, on the group's clock, falls from Monday {start.isoformat()} to "
                      f"Sunday {end.isoformat()}: four full weeks, so every weekday is counted four times.",
            "posting_time": POSTED_FIELD,
            "date_only": "Workable gives a date without a time: its jobs count for weekdays on their own date, "
                         "and not for hours.",
            "copies": "A job with the same title, location and posting time on two or more boards of one ATS is "
                      "counted once, on the board that lists it most often.",
            "board_weighted": "Each board's jobs in the group share one vote, split by weekday, so a board that "
                              "posts hundreds of jobs counts as much as a board that posts one.",
            "closure_adjusted": "The snapshot holds only jobs still open, and older dates have lost more. The "
                                "daily closure rate is fitted from how each weekday's count falls from week to "
                                "week (least squares on the log of Monday-Friday daily counts, one level per "
                                "weekday); each date's jobs are then weighted by exp(rate x age in days) before "
                                "the weekday shares are taken. The rate also absorbs any trend in posting volume.",
            "region": "From the job's location text: US when it names the US, a US state (name or two-letter code "
                      f"after a comma) or one of {len(US_CITIES.split('|'))} large US cities, and no other region; "
                      f"Europe when it names a European country or one of {len(EU_CITIES.split('|'))} large "
                      "European cities (the lists are in ct-002/build_data.py), and no other region; else other "
                      "or unknown.",
            "clocks": "UTC for all groups except: US-located jobs in US Eastern time (UTC-4 until "
                      f"{_sunday(end.year, 11, 1).isoformat()} 06:00 UTC, UTC-5 after), Europe-located jobs in "
                      f"Central European time (UTC+2 until {_sunday(end.year, 10, -1).isoformat()} 01:00 UTC, "
                      "UTC+1 after).",
            "refresh": "For one refresh a day at a given UTC hour: the mean wait from a job's posting minute to the "
                       "next refresh, and the share of jobs picked up within 6 hours, over every timed job of the "
                       "four weeks.",
        },
        "summary": summary,
        "rows": [dict(id=gid, **g) for gid, g in out_groups.items()],
        "hours": out_hours,
        "by_date": {"dates": [(start + dt.timedelta(days=i)).isoformat() for i in range(28)], **by_date_all},
        "refresh_by_hour_utc": refresh,
        "inputs_sha256": hashes,
    }
    data["widget"] = widget_data(data)
    return data


def widget_data(data):
    """The compact block embedded in the page for its chart. --check requires the page's copy to equal this."""
    return {
        "days": [d[:3] for d in DAYS],
        "groups": {gid: {"label": h["label"], "clock": h["clock"], "jobs": h["timed_jobs"],
                         "wh": h["by_weekday_hour"]} for gid, h in data["hours"].items() if gid != "all_open"},
        "refresh": [[r["hour_utc"], r["mean_wait_h"], r["within_6h_pct"]] for r in data["refresh_by_hour_utc"]],
    }


# ---------------------------------------------------------------- outputs
CSV_COLS = (["id", "label", "clock", "window", "jobs", "boards"] + [f"{k}_jobs" for k in DAY_KEYS]
            + [f"{k}_pct" for k in DAY_KEYS] + [f"{k}_board_pct" for k in DAY_KEYS]
            + ["mon_wed_pct", "mon_thu_pct", "weekend_pct", "weekend_board_pct", "top_day", "top_day_pct",
               "top_day_boards"]
            + [f"{k}_adj_pct" for k in DAY_KEYS]
            + ["mon_wed_adj_pct", "weekend_adj_pct", "top_day_adj", "top_day_adj_pct", "other_weekdays_adj_min_pct",
               "other_weekdays_adj_max_pct", "closure_rate_per_day_pct", "same_weekday_decline_per_week_pct"])


def write_outputs(data):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=CSV_COLS, lineterminator="\n")
    w.writeheader()
    for r in data["rows"]:
        w.writerow({c: r.get(c) for c in CSV_COLS})
    with open(os.path.join(ROOT, CSV_REL), "w", encoding="utf-8", newline="") as f:
        f.write(buf.getvalue())
    with open(os.path.join(ROOT, JSON_REL), "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
        f.write("\n")
    write_facts(data)


def write_facts(data, today=None):
    today = today or dt.date.today().isoformat()
    facts = []
    for r in data["rows"]:
        cells = [(c, r.get(c)) for c in CSV_COLS[1:] if r.get(c) not in (None, "")]
        excerpt = f"{r['id']}: " + "; ".join(f"{c}={v}" for c, v in cells)
        nums = sorted({str(abs(v)) for _, v in cells if isinstance(v, (int, float)) and not isinstance(v, bool)},
                      key=float)
        facts.append({"id": f"row-{r['id']}", "claim": f"{r['label']}: jobs posted per weekday (CSV row)",
                      "source_url": f"{SITE}/{CSV_REL}", "fetched": today, "excerpt": excerpt, "numbers": nums})
    for gid, h in data["hours"].items():
        flat = {k: v for k, v in h.items() if isinstance(v, (int, float)) and not isinstance(v, bool)}
        flat.update({f"hour_{i:02d}_pct": v for i, v in enumerate(h["hour_pct"])})
        excerpt = f'"hours" / "{gid}": ' + "; ".join(f"{k}={v}" for k, v in flat.items())
        nums = sorted({str(abs(v)) for v in flat.values() if v is not None}, key=float)
        facts.append({"id": f"hours-{gid}", "claim": f"{h['label']}: posting hour ({h['clock']})",
                      "source_url": f"{SITE}/{JSON_REL}", "fetched": today, "excerpt": excerpt, "numbers": nums})
    for r in data["refresh_by_hour_utc"]:
        facts.append({"id": f"refresh-{r['hour_utc']:02d}", "claim": f"daily refresh at {r['hour_utc']:02d}:00 UTC",
                      "source_url": f"{SITE}/{JSON_REL}", "fetched": today,
                      "excerpt": f'"hour_utc": {r["hour_utc"]}, "mean_wait_h": {r["mean_wait_h"]}, '
                                 f'"within_6h_pct": {r["within_6h_pct"]}',
                      "numbers": sorted({str(r["hour_utc"]), str(r["mean_wait_h"]), str(r["within_6h_pct"])},
                                        key=float)})
    for k, v in data["summary"].items():
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            facts.append({"id": k, "claim": k.replace("_", " "), "source_url": f"{SITE}/{JSON_REL}",
                          "fetched": today, "excerpt": f'"{k}": {v}', "numbers": [str(abs(v))]})
    with open(os.path.join(ROOT, "ct-002", "facts.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"target_query": TARGET_QUERY, "facts": facts}, f, indent=1, ensure_ascii=False)
        f.write("\n")


# ---------------------------------------------------------------- --check
MONTH = r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*"
NUM = re.compile(r"(?<![\w.#/-])(\d[\d,]*(?:\.\d+)?)%?(?![\w-]*\d)")


def visible_text(html):
    html = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", " ", html, flags=re.S | re.I)
    m = re.search(r"<main\b.*?</main>", html, re.S | re.I)
    body = m.group(0) if m else html
    head = " ".join(re.findall(r"<title>(.*?)</title>", html, re.S) +
                    re.findall(r'<meta name="description" content="([^"]*)"', html))
    return re.sub(r"&[a-z]+;|&#\d+;", " ", re.sub(r"<[^>]+>", " ", body) + " " + head)


def page_numbers(text):
    t = re.sub(r"\b\d{1,2} " + MONTH + r"(?: \d{4})?\b", " ", text)
    t = re.sub(r"\b" + MONTH + r" \d{1,2},? \d{4}\b", " ", t)
    t = re.sub(r"\b\d{4}-\d\d-\d\d(?:T[\d:.]+Z)?\b", " ", t)
    t = re.sub(r"\b(\d\d):00\b", r"\1", t)                       # 17:00 UTC is the hour 17
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
    walk({k: v for k, v in data.items() if k not in ("inputs_sha256", "widget")})
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


# Table caption prefix -> {column label: row field}. Each cell must hold its own row's value.
TABLES = {
    "Jobs posted on each weekday": "weekday",
    "Posting day by ATS": {"Jobs": "jobs", "Top day": "top_day_pct", "Mon-Thu": "mon_thu_pct",
                           "Weekend": "weekend_pct"},
}


def check_tables(page, data):
    html = open(page, encoding="utf-8").read()
    rows = {r["id"]: r for r in data["rows"]}
    bad, seen = [], 0
    for cap, body in re.findall(r"<caption>(.*?)</caption>.*?<tbody>(.*?)</tbody>", html, re.S):
        key = next((k for k in TABLES if cap.startswith(k)), None)
        if not key:
            continue
        for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", body, re.S):
            cells = {k: re.sub(r"<[^>]+>", "", v).strip()
                     for k, v in re.findall(r'<t[dh] data-label="([^"]+)"[^>]*>(.*?)</t[dh]>', tr, re.S)}
            if TABLES[key] == "weekday":
                # columns: one per group id (data-label is the group label); rows: weekdays
                day = cells.get("Day", "")
                if day not in DAYS:
                    bad.append(f"{key}: unknown row {day!r}")
                    continue
                spec = {lab: (gid, f"{DAY_KEYS[DAYS.index(day)]}_{fld}") for lab, (gid, fld) in WEEKDAY_COLS.items()}
            else:
                gid = next((r["id"] for r in data["rows"] if r["label"] == cells.get("ATS")), None)
                if not gid:
                    bad.append(f"{key}: unknown row {cells.get('ATS')!r}")
                    continue
                spec = {lab: (gid, fld) for lab, fld in TABLES[key].items()}
            for label, (gid, field) in spec.items():
                if label not in cells:
                    bad.append(f"{key} / {label}: column missing")
                    continue
                m = re.search(r"\d[\d,]*(?:\.\d+)?", cells[label])
                want = rows[gid].get(field)
                got = float(m.group(0).replace(",", "")) if m else None
                seen += 1
                if want is None or got is None or abs(got - float(want)) > 1e-9:
                    bad.append(f"{key} / {cells.get('Day') or cells.get('ATS')} / {label}: page {got}, "
                               f"data {gid}.{field}={want}")
                if field == "top_day_pct" and rows[gid]["top_day"] not in cells[label]:
                    bad.append(f"{key} / {gid}: top day on page {cells[label]!r}, data {rows[gid]['top_day']}")
    return bad, seen


# Weekday table columns: data-label -> (group id, field suffix)
WEEKDAY_COLS = {"Jobs": ("all", "jobs"), "Share": ("all", "pct"), "Each board once": ("all", "board_pct"),
                "US jobs, Eastern": ("us", "pct"), "All open jobs": ("all_open", "pct")}


def check_widget(page, data):
    html = open(page, encoding="utf-8").read()
    m = re.search(r'<script type="application/json" id="posting-data">(.*?)</script>', html, re.S)
    if not m:
        return ["no <script id=\"posting-data\"> block"]
    return [] if json.loads(m.group(1)) == data["widget"] else ["the page's chart data differs from the JSON"]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", help="directory with index-manifest.json and the index-*.gz shards of the "
                                    f"{BUILT_AT} build; without it, --check uses the committed {JSON_REL}")
    ap.add_argument("--check", help="page to verify: every visible number must come from the data")
    a = ap.parse_args()
    if a.index:
        data = build(a.index)
        write_outputs(data)
        s = data["summary"]
        print(f"index {BUILT_AT}: {s['jobs_counted']} jobs read, {s['jobs_without_date']} without a date, "
              f"{s['copies_dropped']} copies dropped; window {s['window_start']} to {s['window_end']}: "
              f"{s['window_jobs']} jobs on {s['window_boards']} boards")
        print(f"wrote {CSV_REL}, {JSON_REL}, ct-002/facts.json")
    elif a.check:
        data = json.load(open(os.path.join(ROOT, JSON_REL), encoding="utf-8"))
        if data.get("widget") != widget_data(data):
            sys.exit("STOP: the committed JSON's widget block does not match its own hours")
        print(f"no --index: checking against the committed {JSON_REL}")
    else:
        ap.error("give --index, --check or both")
    if a.check:
        bad = check_page(a.check, data)
        tbad, seen = check_tables(a.check, data)
        wbad = check_widget(a.check, data)
        print(("CHECK PASS: every number on the page is in the data" if not bad else
               f"CHECK FAIL: {len(bad)} numbers on the page are not in the data: " + ", ".join(bad)))
        print((f"TABLE CHECK PASS: {seen} table cells match their own row and column" if seen and not tbad else
               f"TABLE CHECK FAIL ({seen} cells): " + ("; ".join(tbad) or "no table cells found")))
        print("WIDGET CHECK PASS: the chart data equals the JSON" if not wbad else "WIDGET CHECK FAIL: " + wbad[0])
        if bad or tbad or not seen or wbad:
            sys.exit(1)


if __name__ == "__main__":
    main()
