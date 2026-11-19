"""Rebuild every number on job-posting-age.html from the job index that ATS Jobs Search built at 04:03 UTC on
19 Nov 2026 (the manifest and its six gzip shards): how long before the build each open job was posted, by ATS,
region, seniority and role group, how many open postings are talent pools, and how many jobs posted in each earlier
week are still open.

The index files are not published here. The CSV and JSON written by this script carry every count the page uses,
plus each input file's SHA-256 (checked by ct-002/build_data.py's verify_inputs: a different build is refused).

Usage:
    python -I ct-005/build_data.py --index <dir with index-manifest.json and index-*.gz>
    python -I ct-005/build_data.py --index <dir> --check job-posting-age.html
    python -I ct-005/build_data.py --index <dir> --audit        (sample titles per role group, week-0 boards)
    python -I ct-005/build_data.py --check job-posting-age.html (no index: checks the page against the committed JSON)
    python -I ct-005/build_data.py --refresh-facts              (no index: re-dates facts.json from the committed JSON)

Writes (paths relative to the site root, the parent of ct-005/):
    data/job-posting-age-2026-11.csv    one row per group: listings, boards, median age, shares older than 7 to 730 days
    data/job-posting-age-2026-11.json   the same plus age bands, weekly cohorts, talent pools, the age-check widget's
                                        percentiles, the rules, method and hashes
    ct-005/facts.json                   the content-autopilot gate's facts file (each number traced to the files above)

Age = the build time minus the posting time the vendor's feed gives (Greenhouse first_published, Lever createdAt,
Ashby publishedAt, Recruitee published_at, Personio createdAt, Workable published_on, a date without a time).
Standard library only. Nothing is fetched from the network. Each shard is read and released in turn.
"""
import argparse
import collections
import csv
import datetime as dt
import gzip
import importlib.util
import io
import json
import os
import random
import re
import sys

SITE = "https://scrapetools.scaleturn.com"
CSV_REL = "data/job-posting-age-2026-11.csv"
JSON_REL = "data/job-posting-age-2026-11.json"
PAGE = "job-posting-age.html"
TARGET_QUERY = "should i apply to a job posted 30 days ago"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# The same build as the ct-002 and ct-003 pages: ct-002's verify_inputs refuses any other build by SHA-256, its
# region() reads the location text, and ct-003's seniority() reads seniority words. Loaded from the files, so the
# pages share one definition of each.
sys.dont_write_bytecode = True


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, rel))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ct002 = _load("ct002_build", "ct-002/build_data.py")
ct003 = _load("ct003_build", "ct-003/build_data.py")
BUILT_AT = ct002.BUILT_AT
BUILT_TS = dt.datetime.fromisoformat(BUILT_AT.replace("Z", "+00:00")).timestamp()
ATS_ORDER = ct002.ATS_ORDER
ATS_NAME = ct002.ATS_NAME
POSTED_FIELD = ct002.POSTED_FIELD
region = ct002.region
seniority = ct003.seniority

THRESHOLDS = [7, 14, 30, 60, 90, 180, 365, 730]          # "older than N days" = posted N or more days before the build
# Day ranges [from, to): months here are 30, 60, 90 and 180 days, a year 365.
BANDS = [(0, 7, "Under 1 week"), (7, 14, "1 to 2 weeks"), (14, 30, "2 weeks to 30 days"),
         (30, 60, "30 days to 2 months"), (60, 90, "2 to 3 months"), (90, 180, "3 to 6 months"),
         (180, 365, "6 to 12 months"), (365, 730, "1 to 2 years"), (730, None, "2 years or more")]
COHORT_WEEKS = [0, 1, 2, 3, 4, 6, 8, 13, 26, 52]
# A posting time before 2000 is not a real posting date (84 Greenhouse jobs carry 0, 1 Jan 1970): treated as missing.
VALID_FROM = dt.datetime(2000, 1, 1, tzinfo=dt.timezone.utc).timestamp()
# Boards with 50 or more open listings and none posted 14 or more days before the build: they re-post their
# listings (an aggregator re-posting daily, for example) or posted them all at once. Their dates need not mark when
# a job opened, so the weekly cohorts leave them out; every other figure keeps them, because a job seeker sees those
# dates.
REPOST_MIN_LISTINGS, REPOST_MAX_AGE = 50, 14

# ---------------------------------------------------------------- talent pools and general applications
# A posting that collects applications for no single vacancy. Matched on the whole title, in any case.
POOL_RX = re.compile(
    r"general application|open application|spontaneous application|unsolicited application|speculative application|"
    r"initiativbewerbung|blindbewerbung|open sollicitatie|candidature spontan|candidatura espont|"
    r"talent (?:pool|community|network)|future (?:opportunit|role|opening|position|vacanc)|"
    r"don.?t see (?:a|the|your|what)|didn.?t find|not listed|can.?t find (?:a|the|your)|"
    r"general interest|expression of interest|join our team(?: anyway)?$|always hiring", re.I)

# ---------------------------------------------------------------- role groups (first rule that matches wins)
# (id, label, words in any case, short forms that count only in capitals: "IT" matches, "it" and "Ai" do not)
GROUPS = [
    ("pool", "Talent pools and general applications", POOL_RX.pattern, None),
    ("health", "Healthcare and care",
     r"\b(?:nurse|nursing|nurse practitioner|physician|doctor|clinical|clinician|medical|therapist|therapy|"
     r"physiotherap\w*|pharmac\w*|dental|dentist|hygienist|caregiv\w*|care (?:assistant|worker|aide|giver|manager|"
     r"coordinator)|personal care|home health|hospice|psychologist|psychiatr\w*|veterinar\w*|pflege\w*|arzt|ärzt\w*|"
     r"midwife|paramedic|radiograph\w*|behaviou?r(?:al)? (?:technician|therapist|analyst)|dietitian|nutritionist|"
     r"gyn\w*|endocrinolog\w*|oncolog\w*|cardiolog\w*|dermatolog\w*|patholog\w*|surgeon|surgical|social worker|"
     r"audiolog\w*|optometr\w*|phlebotom\w*|patient|direct support professional|telehealth|counsell?or|"
     r"medizinisch\w*|praxisassist\w*|child development)\b",
     r"\b(?:RN|LPN|LVN|CNA|FNP|PMHNP|LCSW|BCBA|RBT|DSP|HHA|MD|DO|NP)\b"),
    ("sales", "Sales and business development",
     r"\bsales\b|account executive|account manager|account director|account management|business development|"
     r"business developer|partnerships?\b|alliances?\b|key account|vertrieb|commercial (?:manager|director|lead)|"
     r"channel (?:manager|partner)|territory (?:manager|representative)|client partner|partner manager|"
     r"deal desk|value consultant|canvasser|értékesítő",
     r"\b(?:SDR|BDR|AE)\b"),
    ("support", "Customer support and success",
     r"customer (?:support|service|success|care|experience|onboarding|activation)|support (?:specialist|agent|"
     r"representative|engineer|associate)|client (?:success|services|support|care)|technical support|help ?desk|"
     r"call cent(?:er|re)|kundenservice|kundenbetreuer|onboarding|implementation (?:specialist|consultant|manager)",
     None),
    ("marketing", "Marketing and content",
     r"marketing|content|copywriter|social media|\bcommunications?\b|public relations|\bbrand\b|"
     r"\bgrowth\b|community manager|demand gen\w*|user acquisition|event (?:marketer|manager|management|"
     r"coordinator)|campaign",
     r"\b(?:SEO|PR|CRM)\b"),
    ("product", "Product and design",
     r"product (?:manager|owner|lead|director|management|designer)|\bdesign(?:er)?\b|user research|"
     r"creative director|art director|illustrator|animator",
     r"\b(?:UX|UI)\b"),
    ("software", "Software and IT",
     r"software|developer|entwickler|programmer|devops|devsecops|secops|site reliability|full[- ]?stack|"
     r"front[- ]?end|back[- ]?end|\b(?:ios|android|mobile|web|cloud|platform|infrastructure|security|network|"
     r"systems?|qa|test|automation|embedded|firmware|solutions?|integration|release|react|python|java|golang|rust|"
     r"ruby|kotlin|swift|php|salesforce|sap) engineer|engineering manager|sysadmin|system administrator|cyber|"
     r"informatik\w*|architect\w*|forward deployed|member of technical staff|release manager|"
     r"security (?:manager|analyst|engineer|architect|operations)",
     r"\b(?:SRE|QA|IT|SOC)\b"),
    ("data", "Data and AI",
     r"\bdata\b|analytics|machine learning|business intelligence|statistic\w*",
     r"\b(?:ML|AI|BI)\b"),
    ("engineering", "Other engineering and technical",
     r"engineer|ingenieur|technician|techniker|mechanic|electrician|electrical|mechanical|manufacturing|"
     r"maintenance|scientist|\bresearch(?:er)?\b|laborator\w*|chemist|biolog\w*|quality", None),
    ("finance", "Finance and accounting",
     r"financ\w*|accountant|accounting|accounts? (?:payable|receivable)|controller|controlling|fp&a|bookkeep\w*|"
     r"payroll|\btax\b|treasury|\baudit\w*|buchhalt\w*|steuer\w*|actuar\w*|underwrit\w*|"
     r"risk (?:analyst|manager|officer)|\bcredit\b|\bloan\b|mortgage", r"\bSOX\b"),
    ("people", "People and recruiting",
     r"recruit\w*|talent acquisition|human resources|people (?:partner|operations|team|manager|lead)|"
     r"personal(?:referent|sachbearbeiter|leit|entwickl|betreu|management)\w*|sourcer|total rewards|"
     r"compensation|talent (?:partner|management|development)|learning (?:and|&) development|employee experience|"
     r"\bhiring\b",
     r"\b(?:HR|L&D|HRBP)\b"),
    ("legal", "Legal and compliance",
     r"legal|lawyer|attorney|counsel\b|paralegal|compliance|jurist\w*|rechtsanwalt\w*|privacy|litigation|"
     r"regulatory|contracts? (?:manager|specialist|administrator|negotiator)", None),
    ("operations", "Operations and logistics",
     r"operations?\b|logistic\w*|warehouse|supply chain|procurement|purchas\w*|\bbuyer\b|driver|courier|"
     r"fulfil\w*|lager\w*|fahrer|dispatch\w*|inventory|project manager|program manager|programme manager|"
     r"office manager|administrat\w*|assistant|coordinator|chief of staff|facilit\w*|planner|scheduler|"
     r"vendor (?:manager|lead)|delivery manager|material handler|sourcing", None),
    ("education", "Education and teaching",
     r"teacher|teaching|tutor|instructor|lecturer|professor|educator|pädagog\w*|erzieher\w*|lehrer\w*|lehrkraft|"
     r"\bkita\b|faculty|\bschool\b", None),
    ("frontline", "Hospitality, retail and trades",
     r"retail|\bstore\b|\bshop\b|restaurant|\bchef\b|\bcook\b|kitchen|barista|\bserver\b|bartender|waiter|waitress|"
     r"\bhost(?:ess)?\b|housekeep\w*|cleaner|cashier|sales associate|verkäufer\w*|\bkoch\b|köchin|hotel|"
     r"front desk|receptionist|security officer|carpenter|plumber|welder|installer", None),
]
GROUP_RX = [(gid, label, re.compile(ci, re.I), re.compile(cs) if cs else None) for gid, label, ci, cs in GROUPS]
GROUP_LABEL = {gid: label for gid, label, _, _ in GROUPS}
GROUP_LABEL["other"] = "Other roles"
GROUP_ORDER = [g for g, _, _, _ in GROUPS] + ["other"]


def group_of(title):
    for gid, _, ci, cs in GROUP_RX:
        if ci.search(title) or (cs and cs.search(title)):
            return gid
    return "other"


# ---------------------------------------------------------------- reading the index
def read_jobs(index_dir, man):
    """Yield (ats, board_index, board_name, title, location, posted_sec) for every job, one shard at a time."""
    for s in man["shards"]:
        with gzip.open(os.path.join(index_dir, s["key"] + ".gz")) as fh:
            shard = json.loads(fh.read())
        if shard.get("v") != 1:
            sys.exit(f"STOP: shard {s['key']} has version {shard.get('v')}, expected 1")
        ats = shard["ats"]
        names = [b[1] or b[0] for b in shard["boards"]]
        for b, job_id, title, location, remote, posted in shard["jobs"]:
            yield ats, b, names[b], (title or "").strip(), (location or "").strip(), posted
        del shard


def pct(part, whole, nd=1):
    return round(100.0 * part / whole, nd) if whole else None


def median(xs):
    n = len(xs)
    return (xs[n // 2] + xs[(n - 1) // 2]) / 2 if n else None


def quantile(xs, q):
    """xs sorted; nearest-rank on (n - 1), as the widget reads its percentiles."""
    return xs[round(q * (len(xs) - 1))] if xs else None


def r1(x):
    return None if x is None else round(x, 1)


def stats(ages, boards):
    """ages: sorted ages in days; boards: {board: [ages]} for the same listings."""
    n = len(ages)
    row = {"listings": n, "boards": len(boards), "median_days": r1(median(ages)),
           "p25_days": r1(quantile(ages, 0.25)), "p75_days": r1(quantile(ages, 0.75))}
    i = 0
    for t in THRESHOLDS:
        while i < n and ages[i] < t:
            i += 1
        row[f"older_{t}d_pct"] = pct(n - i, n)
        row[f"older_{t}d"] = n - i
    bmed = sorted(median(sorted(v)) for v in boards.values())
    row["board_median_days"] = r1(median(bmed))
    row["boards_median_over_30d_pct"] = pct(sum(1 for m in bmed if m >= 30), len(bmed))
    return row


def build(index_dir, audit=False):
    man, hashes = ct002.verify_inputs(index_dir)
    # Copies: the same title, location and posting time on two boards of one ATS count once, on the board that
    # lists it most often (the rule of the ct-002 and ct-003 pages).
    rows, per_key = [], {}
    read = collections.Counter()
    no_time = collections.Counter()
    for ats, b, bname, title, location, posted in read_jobs(index_dir, man):
        read[ats] += 1
        if posted is None or posted < VALID_FROM:
            no_time[ats] += 1
            continue
        k = (ats, title.lower(), location.lower(), posted)
        per_key.setdefault(k, collections.Counter())[(ats, b)] += 1
        rows.append((ats, b, bname, title, location, posted, k))
    keep = {k: min(bc, key=lambda x: (-bc[x], x)) for k, bc in per_key.items() if len(bc) > 1}
    jobs = [(ats, b, bname, title, location, max(0.0, (BUILT_TS - posted) / 86400.0))
            for ats, b, bname, title, location, posted, k in rows if k not in keep or keep[k] == (ats, b)]
    copies = read - no_time - collections.Counter(j[0] for j in jobs)
    del rows, per_key
    b_n, b_max = collections.Counter(), collections.defaultdict(float)
    for ats, b, bname, title, location, age in jobs:
        b_n[(ats, b)] += 1
        b_max[(ats, b)] = max(b_max[(ats, b)], age)
    reposting = {k for k, n in b_n.items() if n >= REPOST_MIN_LISTINGS and b_max[k] < REPOST_MAX_AGE}

    seg_ages = collections.defaultdict(list)
    seg_boards = collections.defaultdict(lambda: collections.defaultdict(list))
    weeks = collections.defaultdict(collections.Counter)          # segment -> week of age -> open listings
    week_boards = collections.defaultdict(set)
    over_year_boards = collections.Counter()
    samples = collections.defaultdict(list)
    rnd = random.Random(20261119)
    for ats, b, bname, title, location, age in jobs:
        board = (ats, b)
        g = group_of(title)
        segs = ["all", "ats-" + ats, "region-" + region(location), "seniority-" + seniority(title), "group-" + g,
                "kind-" + ("pool" if g == "pool" else "vacancy")]
        for s in segs:
            seg_ages[s].append(age)
            seg_boards[s][board].append(age)
        wk = int(age // 7)
        weeks["all_boards"][wk] += 1
        if board not in reposting:
            weeks["all"][wk] += 1
            weeks["ats-" + ats][wk] += 1
            if g != "pool":
                weeks["vacancy"][wk] += 1
        if wk == 0:
            week_boards[ats].add(board)
        if age >= 365:
            over_year_boards[board] += 1
        if audit and rnd.random() < 0.02:
            samples[g].append(title)

    segments = []
    order = (["all"] + [f"ats-{a}" for a in ATS_ORDER] + ["region-us", "region-europe", "region-other"] +
             ["seniority-junior", "seniority-neither", "seniority-senior"] + [f"group-{g}" for g in GROUP_ORDER] +
             ["kind-vacancy", "kind-pool"])
    labels = {"all": "All open jobs", "region-us": "Located in the US", "region-europe": "Located in Europe",
              "region-other": "Other or unclear location", "seniority-junior": "Junior, intern or student word",
              "seniority-neither": "No seniority word", "seniority-senior": "Senior, lead or higher word",
              "kind-vacancy": "Specific vacancies", "kind-pool": "Talent pools and general applications"}
    for a in ATS_ORDER:
        labels[f"ats-{a}"] = ATS_NAME[a]
    for g in GROUP_ORDER:
        labels[f"group-{g}"] = GROUP_LABEL[g]
    for sid in order:
        ages = sorted(seg_ages.get(sid, []))
        if not ages:
            continue
        row = {"id": sid, "label": labels[sid], "kind": sid.split("-")[0]}
        row.update(stats(ages, seg_boards[sid]))
        row["share_pct"] = pct(len(ages), len(seg_ages["all"]))
        if sid.startswith("ats-"):
            row["posted_field"] = POSTED_FIELD[sid[4:]]
        row["quantiles"] = [r1(quantile(ages, i / 100)) for i in range(101)]
        segments.append(row)
    seg = {r["id"]: r for r in segments}

    all_ages = sorted(seg_ages["all"])
    n_all = len(all_ages)
    bands = []
    for lo, hi, label in BANDS:
        c = sum(1 for x in all_ages if x >= lo and (hi is None or x < hi))
        bands.append({"band": label, "from_days": lo, "to_days": hi, "listings": c, "share_pct": pct(c, n_all)})

    cohorts = []
    for k in COHORT_WEEKS:
        row = {"week": k, "label": "Last 7 days" if k == 0 else f"{k} week{'s' if k > 1 else ''} earlier",
               "from_days": 7 * k, "to_days": 7 * k + 7, "open": weeks["all"][k],
               "per_100_pct": pct(weeks["all"][k], weeks["all"][0]),
               "vacancies_open": weeks["vacancy"][k], "vacancies_per_100_pct": pct(weeks["vacancy"][k], weeks["vacancy"][0]),
               "open_incl_reposting": weeks["all_boards"][k],
               "per_100_incl_reposting_pct": pct(weeks["all_boards"][k], weeks["all_boards"][0])}
        for a in ATS_ORDER:
            row[f"{a}_per_100_pct"] = pct(weeks["ats-" + a][k], weeks["ats-" + a][0])
        cohorts.append(row)
    half_week = next((c["week"] for c in cohorts if c["per_100_pct"] is not None and c["per_100_pct"] < 50), None)

    tot_year = sum(over_year_boards.values())
    cum, half_boards = 0, 0
    for _, c in over_year_boards.most_common():
        cum += c
        half_boards += 1
        if cum * 2 >= tot_year:
            break
    board_name = {(ats, b): bname for ats, b, bname, _, _, _ in jobs}
    top_year = [{"rank": i, "board": board_name[k], "ats": ATS_NAME[k[0]], "listings_over_year": c,
                 "listings": b_n[k], "share_of_over_year_pct": pct(c, tot_year)}
                for i, (k, c) in enumerate(over_year_boards.most_common(10), 1)]
    pool, vac = seg["kind-pool"], seg["kind-vacancy"]
    summary = {
        "index_built_at": BUILT_AT,
        "jobs_in_index": man["jobs"], "boards_in_index": man["boards"],
        "jobs_read": sum(read.values()), "jobs_without_posting_time": sum(no_time.values()),
        "reposting_boards": len(reposting), "reposting_listings": sum(b_n[k] for k in reposting),
        "reposting_min_listings": REPOST_MIN_LISTINGS, "reposting_max_age_days": REPOST_MAX_AGE,
        "copies_dropped": sum(copies.values()), "listings": n_all, "boards_with_listings": seg["all"]["boards"],
        "median_age_days": seg["all"]["median_days"],
        "older_30d_pct": seg["all"]["older_30d_pct"], "older_30d": seg["all"]["older_30d"],
        "younger_30d_pct": round(100 - seg["all"]["older_30d_pct"], 1),
        "older_90d_pct": seg["all"]["older_90d_pct"], "older_365d_pct": seg["all"]["older_365d_pct"],
        "older_365d": seg["all"]["older_365d"], "older_730d_pct": seg["all"]["older_730d_pct"],
        "board_median_days": seg["all"]["board_median_days"],
        "boards_median_over_30d_pct": seg["all"]["boards_median_over_30d_pct"],
        "pool_listings": pool["listings"], "pool_pct": pct(pool["listings"], n_all, 2),
        "pool_median_days": pool["median_days"], "pool_boards": pool["boards"],
        "pool_share_of_over_year_pct": pct(pool["older_365d"], seg["all"]["older_365d"]),
        "vacancy_median_days": vac["median_days"], "vacancy_older_30d_pct": vac["older_30d_pct"],
        "vacancy_older_365d_pct": vac["older_365d_pct"],
        "over_year_boards": len(over_year_boards), "over_year_half_boards": half_boards,
        "over_year_half_boards_pct": pct(half_boards, len(over_year_boards)),
        "over_year_half_boards_of_all_pct": pct(half_boards, seg["all"]["boards"]),
        "over_year_top3_listings": sum(r["listings_over_year"] for r in top_year[:3]),
        "over_year_top3_pct": pct(sum(r["listings_over_year"] for r in top_year[:3]), tot_year),
        "cohort_half_week": half_week,
        "week0_open": weeks["all"][0], "week4_open": weeks["all"][4],
        "week4_per_100": pct(weeks["all"][4], weeks["all"][0]),
    }
    for a in ATS_ORDER:
        summary[f"jobs_read_{a}"] = read[a]
        summary[f"copies_dropped_{a}"] = copies[a]
        summary[f"week0_boards_{a}"] = len(week_boards[a])

    data = {
        "title": "Age of open job postings on company job boards, November 2026",
        "page": f"{SITE}/{PAGE}",
        "method": {
            "source": f"The ATS Jobs Search job index built at {BUILT_AT} from employers' public job feeds on "
                      "Greenhouse, Lever, Ashby, Recruitee, Personio and Workable.",
            "age": "Days from the posting time in the vendor's feed to the index build. Posting time fields: " +
                   "; ".join(f"{ATS_NAME[a]} {POSTED_FIELD[a]}" for a in ATS_ORDER) +
                   " (Workable gives a date without a time, read as 00:00 UTC).",
            "older_than": "Older than N days = posted N or more days before the build.",
            "snapshot": "Every figure describes the jobs open at the build. Postings that opened and closed before "
                        "it are not in the index, so long-lived postings are over-represented compared with all "
                        "postings ever made: these are ages of open postings, not how long postings stay up.",
            "cohorts": "Open listings by week of posting, each week against the last 7 days. If employers posted the "
                       "same number of jobs every week, the ratio would be the share of postings still up that many "
                       "weeks after they went up. Changes in how many jobs were posted each week move it too.",
            "copies": "A job with the same title, location and posting time on two or more boards of one ATS is "
                      "counted once, on the board that lists it most often (as on the posting-day page).",
            "invalid_times": "A posting time before 1 Jan 2000 (a zero timestamp) is treated as missing and the job "
                             "is left out.",
            "reposting_boards": f"Boards with {REPOST_MIN_LISTINGS} or more open listings, none posted "
                                f"{REPOST_MAX_AGE} or more days before the build (re-posted or posted all at once), "
                                "are left out of the weekly cohorts only; the cohorts with them are kept as "
                                "open_incl_reposting.",
            "pools": "A talent pool or general application: the title matches " + POOL_RX.pattern,
            "groups": "Role groups come from keyword rules on the whole title; the first rule that matches wins. "
                      "Short forms (AI, HR, IT, PR, RN...) count only in capitals.",
            "seniority": "Seniority words from ct-003/build_data.py's rule (senior, staff, lead, head, director...; "
                         "junior, intern, student, graduate, trainee...).",
            "region": "From the location text, with ct-002/build_data.py's rule: US, Europe, or other.",
            "board_weighted": "board_median_days is the median over boards of each board's median listing age, so "
                              "each board counts once.",
            "rules": {gid: {"any_case": ci, "capitals_only": cs} for gid, _, ci, cs in GROUPS},
        },
        "summary": summary,
        "bands": bands,
        "cohorts": cohorts,
        "over_year_top_boards": top_year,
        "segments": segments,
        "inputs_sha256": hashes,
    }
    if audit:
        for g in GROUP_ORDER:
            print(f"\n== {GROUP_LABEL[g]} ({seg.get('group-' + g, {}).get('listings')})")
            for t in samples[g][:60 if g == "other" else 20]:
                print("   ", t)
        print("\nweek-0 boards per ATS:", {a: len(week_boards[a]) for a in ATS_ORDER})
    return data


# ---------------------------------------------------------------- outputs
CSV_COLS = (["id", "label", "listings", "boards", "median_days", "p25_days", "p75_days"] +
            [f"older_{t}d_pct" for t in THRESHOLDS] + ["board_median_days", "boards_median_over_30d_pct"])


def write_outputs(data):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=CSV_COLS, lineterminator="\n")
    w.writeheader()
    for r in data["segments"]:
        w.writerow({c: r.get(c) for c in CSV_COLS})
    with open(os.path.join(ROOT, CSV_REL), "w", encoding="utf-8", newline="") as f:
        f.write(buf.getvalue())
    with open(os.path.join(ROOT, JSON_REL), "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
        f.write("\n")
    write_facts(data)


def num_key(s):
    return float(s), s


def _nums(d):
    return sorted({str(abs(v)) for v in d.values() if isinstance(v, (int, float)) and not isinstance(v, bool)},
                  key=num_key)


def _fact(fid, claim, url, today, d):
    excerpt = "; ".join(f"{k}={v}" for k, v in d.items() if v is not None and v != "")
    return {"id": fid, "claim": claim, "source_url": url, "fetched": today, "excerpt": excerpt, "numbers": _nums(d)}


def write_facts(data, today=None):
    today = today or dt.date.today().isoformat()
    j, c = f"{SITE}/{JSON_REL}", f"{SITE}/{CSV_REL}"
    facts = []
    for r in data["segments"]:
        d = {k: r[k] for k in CSV_COLS if k not in ("id", "label")}
        facts.append(_fact(f"seg-{r['id']}", f"{r['label']}: age of open listings (CSV row)", c, today, d))
    for i, r in enumerate(data["bands"]):
        facts.append(_fact(f"band-{i}", f"open listings posted {r['band']} before the build", j, today,
                           {k: v for k, v in r.items() if k != "band"}))
    for r in data["cohorts"]:
        facts.append(_fact(f"cohort-{r['week']}", f"listings posted {r['label']} still open", j, today,
                           {k: v for k, v in r.items() if k != "label"}))
    for r in data["over_year_top_boards"]:
        facts.append(_fact(f"over-year-board-{r['rank']}", f"{r['board']}: listings a year old or more", j, today,
                           {k: v for k, v in r.items() if k not in ("board", "ats")}))
    for k, v in data["summary"].items():
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            facts.append({"id": k, "claim": k.replace("_", " "), "source_url": j, "fetched": today,
                          "excerpt": f'"{k}": {v}', "numbers": [str(abs(v))]})
    with open(os.path.join(HERE, "facts.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"target_query": TARGET_QUERY, "facts": facts}, f, indent=1, ensure_ascii=False)
        f.write("\n")


# ---------------------------------------------------------------- --check
def allowed_values(data):
    vals = set()

    def walk(x):
        if isinstance(x, bool):
            return
        if isinstance(x, (int, float)):
            vals.add(round(float(abs(x)), 6))
        elif isinstance(x, dict):
            for k, v in x.items():
                if k != "quantiles":        # the widget's percentiles: 101 values a group, no page number cites them
                    walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk({k: v for k, v in data.items() if k not in ("inputs_sha256", "method")})
    return vals


def check_page(page, data):
    text = ct002.visible_text(open(page, encoding="utf-8").read())
    allowed = allowed_values(data)
    bad = []
    for raw in ct002.page_numbers(text):
        v = round(float(raw.replace(",", "")), 6)
        if v in allowed or (v.is_integer() and 0 <= v <= 12):
            continue
        bad.append(raw)
    return sorted(set(bad), key=lambda s: float(s.replace(",", "")))


# Table caption prefix -> (rows source, row key column, row key field, {column label: field})
TABLES = {
    "Open jobs by how long ago they were posted": ("bands", "Posted", "band",
                                                   {"Listings": "listings", "Share": "share_pct"}),
    "Age of open listings by ATS": ("segments", "ATS", "label",
                                    {"Listings": "listings", "Median age": "median_days",
                                     "30+ days": "older_30d_pct", "1+ year": "older_365d_pct"}),
    "Age of open listings by role group": ("segments", "Group", "label",
                                           {"Listings": "listings", "Median age": "median_days",
                                            "90+ days": "older_90d_pct"}),
    "Jobs still open, by week posted": ("cohorts", "Posted", "label",
                                        {"Still open": "open", "Per 100": "per_100_pct"}),
}


def check_tables(page, data):
    html = open(page, encoding="utf-8").read()
    bad, seen = [], 0
    for cap, body in re.findall(r"<caption>(.*?)</caption>.*?<tbody>(.*?)</tbody>", html, re.S):
        key = next((k for k in TABLES if cap.startswith(k)), None)
        if not key:
            continue
        src, rowcol, rowfield, cols = TABLES[key]
        for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", body, re.S):
            cells = {k: re.sub(r"<[^>]+>", "", v).strip()
                     for k, v in re.findall(r'<t[dh] data-label="([^"]+)"[^>]*>(.*?)</t[dh]>', tr, re.S)}
            name = cells.get(rowcol, "")
            row = next((r for r in data[src] if r[rowfield] == name), None)
            if not row:
                bad.append(f"{key}: unknown row {name!r}")
                continue
            for label, field in cols.items():
                if label not in cells:
                    bad.append(f"{key} / {name} / {label}: column missing")
                    continue
                seen += 1
                m = re.search(r"\d[\d,]*(?:\.\d+)?", cells[label])
                got = float(m.group(0).replace(",", "")) if m else None
                want = row.get(field)
                if want is None or got is None or abs(got - float(want)) > 1e-9:
                    bad.append(f"{key} / {name} / {label}: page {got}, data {field}={want}")
    return bad, seen


def check_widget(page, data):
    html = open(page, encoding="utf-8").read()
    bad = [] if f'fetch("{JSON_REL}")' in html else [f"the page does not fetch {JSON_REL}"]
    for r in data["segments"]:
        q = r["quantiles"]
        if len(q) != 101 or any(q[i] > q[i + 1] for i in range(100)) or q[50] is None:
            bad.append(f"{r['id']}: quantiles are not 101 sorted values")
        elif abs(q[50] - r["median_days"]) > max(0.15, 0.002 * r["median_days"]) and r["listings"] % 2:
            bad.append(f"{r['id']}: the widget's 50th percentile {q[50]} is not the median {r['median_days']}")
    return bad


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", help="directory with index-manifest.json and the index-*.gz shards of the "
                                    f"{BUILT_AT} build; without it, --check uses the committed {JSON_REL}")
    ap.add_argument("--check", help="page to verify: every visible number must come from the data")
    ap.add_argument("--audit", action="store_true", help="with --index: print sample titles of each role group")
    ap.add_argument("--refresh-facts", action="store_true",
                    help="without --index: rewrite ct-005/facts.json from the committed JSON with today's date")
    a = ap.parse_args()
    if a.index:
        data = build(a.index, audit=a.audit)
        write_outputs(data)
        s = data["summary"]
        print(f"index {BUILT_AT}: {s['jobs_read']} jobs read, {s['jobs_without_posting_time']} without a posting "
              f"time, {s['copies_dropped']} copies dropped, {s['listings']} listings on {s['boards_with_listings']} "
              f"boards; median age {s['median_age_days']} days, {s['older_30d_pct']}% older than 30 days")
        print(f"wrote {CSV_REL}, {JSON_REL}, ct-005/facts.json")
    elif a.check or a.refresh_facts:
        data = json.load(open(os.path.join(ROOT, JSON_REL), encoding="utf-8"))
        print(f"no --index: using the committed {JSON_REL} (index {data['summary']['index_built_at']})")
        if a.refresh_facts:
            write_facts(data)
            print("wrote ct-005/facts.json with today's date")
    else:
        ap.error("give --index, --check, --refresh-facts or a combination")
    if a.check:
        bad = check_page(a.check, data)
        tbad, seen = check_tables(a.check, data)
        wbad = check_widget(a.check, data)
        print(("CHECK PASS: every number on the page is in the data" if not bad else
               f"CHECK FAIL: {len(bad)} numbers on the page are not in the data: " + ", ".join(bad)))
        print((f"TABLE CHECK PASS: {seen} table cells match their own row and column" if seen and not tbad else
               f"TABLE CHECK FAIL ({seen} cells): " + ("; ".join(tbad) or "no table cells found")))
        print("WIDGET CHECK PASS: the age check loads the JSON and its percentiles are sound" if not wbad else
              "WIDGET CHECK FAIL: " + "; ".join(wbad))
        if bad or tbad or not seen or wbad:
            sys.exit(1)


if __name__ == "__main__":
    main()
