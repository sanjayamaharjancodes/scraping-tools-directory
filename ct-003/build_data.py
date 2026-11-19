"""Rebuild every number on ai-job-titles.html from the job index that ATS Jobs Search built at 04:03 UTC on
19 Nov 2026 (the manifest and its six gzip shards): which job titles name AI or machine learning, how often, on how
many company boards, and in which role groups, seniority and regions.

The index files are not published here. The CSV and JSON written by this script carry every count the page uses,
plus each input file's SHA-256 (checked by ct-002/build_data.py's verify_inputs: a different build is refused).

Usage:
    python -I ct-003/build_data.py --index <dir with index-manifest.json and index-*.gz>
    python -I ct-003/build_data.py --index <dir> --check ai-job-titles.html
    python -I ct-003/build_data.py --index <dir> --audit          (print sample titles per role group)
    python -I ct-003/build_data.py --check ai-job-titles.html     (no index: checks the page against the committed JSON)
    python -I ct-003/build_data.py --refresh-facts                (no index: re-dates facts.json from the committed JSON)

Writes (paths relative to the site root, the parent of ct-003/):
    data/ai-job-titles-2026-11.csv    one row per AI-named role name posted by 2 or more boards (the page's download)
    data/ai-job-titles-2026-11.json   the same rows plus every table on the page, the rules, method and hashes
    ct-003/facts.json                 the content-autopilot gate's facts file (each number traced to the files above)

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
import re
import sys

SITE = "https://scrapetools.scaleturn.com"
CSV_REL = "data/ai-job-titles-2026-11.csv"
JSON_REL = "data/ai-job-titles-2026-11.json"
PAGE = "ai-job-titles.html"
TARGET_QUERY = "ai job titles"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# The same build as ct-002's page: its verify_inputs refuses any other build by SHA-256, and its region() reads the
# location text. Loaded from the file, so both pages use one definition.
_spec = importlib.util.spec_from_file_location("ct002_build", os.path.join(ROOT, "ct-002", "build_data.py"))
ct002 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ct002)
BUILT_AT = ct002.BUILT_AT
ATS_ORDER = ct002.ATS_ORDER
ATS_NAME = ct002.ATS_NAME
region = ct002.region

# ---------------------------------------------------------------- what counts as a title that names AI
# Short forms are matched case-sensitively and must not touch a Latin letter or digit ("AI/ML" and "生成AI" match,
# "Mail" and "OpenAI" do not). Long forms are matched in any case.
SHORT_TERMS = ["AI", "A.I.", "ML", "LLM", "LLMs", "KI", "NLP"]
RX_SHORT = re.compile(r"(?<![A-Za-z0-9])(A\.I\.|AI|ML|LLMs|LLM|KI|NLP)(?![A-Za-z0-9])")
LONG_TERMS = ["machine learning", "artificial intelligence", "künstliche intelligenz", "deep learning", "genai",
              "gen ai", "generative ai", "computer vision", "natural language processing", "large language model",
              "mlops", "llmops", "aiops", "agentic", "prompt engineer"]
RX_LONG = re.compile(r"machine[- ]learning|artificial[- ]intelligence|künstlichen? intelligenz|deep[- ]learning|"
                     r"gen[- ]?ai|generative[- ]ai|computer[- ]vision|natural[- ]language[- ]processing|"
                     r"large[- ]language[- ]models?|mlops|llmops|aiops|agentic|prompt[- ]engineer", re.I)
# In a title written all in capitals, "AI" can be a word of another language (Italian "AI PIANI": "to the floors").
# There a short form counts only at the start or end of the title or of one of its parts, or next to one of these
# English words.
CAPS_NEIGHBOURS = {"ENGINEER", "ENGINEERING", "ENGINEERS", "PLATFORM", "SOLUTIONS", "SOLUTION", "SPECIALIST",
                   "DEVELOPER", "RESEARCH", "RESEARCHER", "SCIENTIST", "MANAGER", "PRODUCT", "DATA", "JUNIOR",
                   "SENIOR", "VP", "HEAD", "LEAD", "CONSULTANT", "ARCHITECT", "TRAINER", "CONTINUOUS"}


def long_term(m):
    t = re.sub(r"[- ]+", " ", m.group(0).lower())
    t = {"künstlichen intelligenz": "künstliche intelligenz", "large language models": "large language model"}.get(t, t)
    return "genai" if t == "genai" else t


def all_caps(title):
    latin = re.findall(r"[A-Za-z]", title)
    return len(latin) >= 3 and not any(c.islower() for c in latin)


RX_LAW = re.compile(r"\bJ\.?D\.?\b|\blaw\b|\blegal\b|\bcounsel\b|\battorney\b|\blawyer\b|\btax\b|\bsteuer", re.I)


def ai_terms(title):
    """The AI terms a title names (empty list: it names none)."""
    terms = [long_term(m) for m in RX_LONG.finditer(title)]
    caps = all_caps(title)
    law = bool(RX_LAW.search(title))
    for m in RX_SHORT.finditer(title):
        if law and m.group(0) == "LLM":           # in a legal title, LLM is the Master of Laws degree
            continue
        if caps:
            before = re.findall(r"[A-Za-z]+", title[:m.start()])
            after = re.findall(r"[A-Za-z]+", title[m.end():])
            gap_b = title[:m.start()].rstrip()
            gap_a = title[m.end():].lstrip()
            edge_b = not gap_b or gap_b[-1] in "-–—|,:/(（[【&"
            edge_a = not gap_a or gap_a[0] in "-–—|,:/)）]】&"
            near = (before[-1] if before else "") in CAPS_NEIGHBOURS or (after[0] if after else "") in CAPS_NEIGHBOURS
            if not (edge_b or edge_a or near):
                continue
        terms.append(m.group(0))
    return terms


# ---------------------------------------------------------------- title parts and role names
RX_PARTS = re.compile(r"\s[-–—|]\s|\s[-–—]|[-–—]\s|,\s|\s@\s|:\s|[()\[\]（）【】｜]")
RX_GENDER = re.compile(r"\b(?:[mwfdxh]\s*/\s*[mwfdxh](?:\s*/\s*[mwfdxh])?|all genders?|alle geschlechter|"
                       r"gn\*?|w\*m\*d|m\*w\*d)\b", re.I)
SENIORITY_WORD = r"(?:senior|sr\.?|staff|principal|lead|junior|jr\.?|founding|mid[- ]level|mid|entry[- ]level|" \
                 r"distinguished|expert)"
# "Senior AI Engineer", "Senior / Staff AI Engineer", "Sr. ML Engineer": the leading seniority words go
SENIORITY_PREFIX = re.compile(r"^" + SENIORITY_WORD + r"(?:\s*/\s*|\s+|$)", re.I)
LEVEL_SUFFIX = re.compile(r"\s+(?:i{1,3}|iv|v|[1-5]|level\s*[1-5])$", re.I)


def role_display(part):
    """One title part as a role name: gender tags, leading seniority words and trailing levels removed, slashes
    closed up ("AI / ML" is "AI/ML"); "" when the part is only seniority words (as in "Senior / Staff")."""
    x = RX_GENDER.sub(" ", part)
    x = re.sub(r"[\s ]+", " ", x.replace("‐", "-"))
    x = re.sub(r"\s*/\s*", "/", x).strip(" -–—,.;:*/")
    prev = None
    while prev != x:
        prev = x
        x = SENIORITY_PREFIX.sub("", x)
        x = LEVEL_SUFFIX.sub("", x).strip(" -–—,.;:*/")
    return x


# Abbreviations read as their full form in role keys, so "ML Engineer" and "Machine Learning Engineer" are one title.
# A slash joins words without being read ("AI/ML" stays as written).
CANON = [(re.compile(r"(?<![\w/.])a\.i\.(?![\w/])"), "ai"),
         (re.compile(r"(?<![\w/])artificial intelligence(?![\w/])"), "ai"),
         (re.compile(r"(?<![\w/])ml ops(?![\w/])"), "mlops"),
         (re.compile(r"(?<![\w/])ml(?![\w/])"), "machine learning"),
         (re.compile(r"(?<![\w/])gen ?ai(?![\w/])"), "generative ai")]


def norm_part(part):
    """The case-insensitive key of a role name: hyphens read as spaces, abbreviations as their full form."""
    k = re.sub(r"\s+", " ", role_display(part).replace("-", " ")).strip().lower()
    for rx, full in CANON:
        k = rx.sub(full, k)
    return k


def title_parts(title):
    """The parts of a title that hold a role name (parts that are only seniority words are dropped)."""
    return [p.strip() for p in RX_PARTS.split(title) if p and p.strip() and norm_part(p)]


# ---------------------------------------------------------------- role groups (first rule that matches wins)
GROUPS = [
    ("training", "AI training and data work",
     r"\bAI[- ]?trainers?\b|\btrainers? network\b|\bAI[- ]?tutors?\b|annotat|\bdata contributors?\b|"
     r"\b(?:research|recording|training|voice|conversation|video) contributors?\b|\bAI training\b(?! (?:infra|platform|"
     r"system|cluster|compute|framework|engineer|runtime|stack|data platform))|\bAI (?:speech )?testers?\b|"
     r"\bspeech tester\b|evaluators? for AI|\bresearch participants?\b|\bstudy participants?\b|"
     r"\brecord(?:ing)? videos?\b|\bdata collection operator\b|\bteleoperator\b|\brobot trainer\b|"
     r"\bAI data (?:specialist|quality|annotator|associate)|\bKI-Tester\b|\braters?\b"),
    ("leadership", "Leadership and founders",
     r"\bhead\b|\bdirector\b|\bVP\b|\bvice president\b|\bchief\b(?! of staff)|\bC[TEFOI]O\b|\bCCO\b|"
     r"\bco-?founder\b|\bfounder\b(?!'?s)|\bgeschäftsführ"),
    ("research", "Research",
     r"\bresearch(?:er)?s?\b|(?<!data )\bscientists?\b|\bPhD\b"),
    ("customer", "Customer-facing and consulting",
     r"forward[- ]deployed|\bsolutions? (?:engineer|architect|consultant|specialist)|\bdeployment strategist\b|"
     r"\bdeployment (?:lead|manager|specialist)\b|\bdelivery (?:lead|manager)\b|"
     r"\bsales engineer\b|\bcustomer engineer\b|\bpre-?sales\b|\bconsult(?:ant|ing)\b|\bimplementation\b|"
     r"\btechnical account\b|\bcustomer success\b|\badvisor\b|\bberater\b|\bapplied AI architect\b"),
    ("product", "Product and design",
     r"\bproduct (?:manager|owner|lead|management|director|designer|marketing)\b|\bdesigner\b|\bUX\b|"
     r"\bprogram(?:me)? manager\b|\bproject manager\b|\bprojektmanager"),
    ("engineering", "Engineering",
     r"\bengineer(?:s|ing)?\b|\bdeveloper\b|\bentwickler|\bingenieur|\barchitect\b|\bSWE\b|\bSDE\b|"
     r"\bprogrammer\b|\bdevops\b|\bmlops\b|\bllmops\b|\bmember of (?:technical|product) staff\b|\bhacker\b|"
     r"\bcoder\b|\bbuilder\b"),
    ("data", "Data science and analytics",
     r"\bdata scien|\banalyst\b|\banalytics\b|\bdatenanalyst"),
    ("gtm", "Sales, marketing and content",
     r"\baccount (?:executive|manager|director)\b|\bsales\b|\bmarketing\b|\bbusiness development\b|\bgrowth\b|"
     r"\bpartnerships?\b|\bGTM\b|\bgo-to-market\b|\bcontent\b|\bcopywriter\b|\beditor\b|\bSEO\b|\bvertrieb"),
    ("governance", "Governance, policy and safety",
     r"\bgovernance\b|\bpolicy\b|\bethic|\bsafety\b|\bcompliance\b|\brisk\b|\blegal\b|\bcounsel\b|\btrust\b|"
     r"\bregulat"),
]
GROUP_RX = [(gid, label, re.compile(rx, re.I)) for gid, label, rx in GROUPS]
GROUP_LABEL = {gid: label for gid, label, _ in GROUPS}
GROUP_LABEL["other"] = "Other roles"
GROUP_ORDER = [g for g, _, _ in GROUPS] + ["other"]


def group_of(title):
    for gid, _, rx in GROUP_RX:
        if rx.search(title):
            return gid
    return "other"


# ---------------------------------------------------------------- seniority words in a title
RX_SENIOR = re.compile(r"\b(?:senior|sr\.?|staff|principal|lead|distinguished|head of|director|VP|vice president|"
                       r"chief|founding)\b", re.I)
RX_JUNIOR = re.compile(r"\b(?:junior|jr\.?|intern|interns|internship|graduate|grad|entry[- ]level|trainee|apprentice|"
                       r"apprenticeship|werkstudent(?:in)?|working student|praktikum|praktikant(?:in)?|co-?op|"
                       r"new grad|stagiaire|student|ausbildung|berufseinsteiger|einsteiger|alternance|stage)\b", re.I)
RX_NOT_SENIORITY = re.compile(r"member of (?:technical|product) staff|chief of staff|staffing|lead generation", re.I)


def seniority(title):
    t = RX_NOT_SENIORITY.sub(" ", title)
    if RX_JUNIOR.search(t):
        return "junior"
    if RX_SENIOR.search(t):
        return "senior"
    return "neither"


# ---------------------------------------------------------------- titles that career guides name (see PREMISE.md)
# Each is matched against every part of every open title (not only AI-named ones), after norm_part().
# The guides' own wording; abbreviations are read as above, so "AI/ML" stays distinct but "ML Engineer" is
# "Machine Learning Engineer". Two variants only where a guide gives the title in two forms.
GUIDE_TITLES = [
    ("AI Engineer", ["ai engineer"]),
    ("Machine Learning Engineer", ["machine learning engineer"]),
    ("Applied AI Engineer", ["applied ai engineer"]),
    ("AI Software Engineer", ["ai software engineer"]),
    ("LLM Engineer", ["llm engineer"]),
    ("Generative AI Engineer", ["generative ai engineer"]),
    ("Agentic AI Engineer", ["agentic ai engineer"]),
    ("Agent Engineer", ["agent engineer"]),
    ("Prompt Engineer", ["prompt engineer"]),
    ("RAG Engineer", ["rag engineer"]),
    ("Context Engineer", ["context engineer"]),
    ("AI Platform Engineer", ["ai platform engineer"]),
    ("AI Infrastructure Engineer", ["ai infrastructure engineer"]),
    ("AI Systems Engineer", ["ai systems engineer"]),
    ("AI Reliability Engineer", ["ai reliability engineer"]),
    ("MLOps Engineer", ["mlops engineer"]),
    ("LLMOps Engineer", ["llmops engineer"]),
    ("Evals Engineer", ["evals engineer"]),
    ("AI Evaluator", ["ai evaluator"]),
    ("AI Red Teamer", ["ai red teamer"]),
    ("AI Safety Engineer", ["ai safety engineer"]),
    ("AI Alignment Engineer", ["ai alignment engineer"]),
    ("Research Engineer", ["research engineer"]),
    ("Research Scientist", ["research scientist"]),
    ("AI Research Scientist", ["ai research scientist"]),
    ("AI Researcher", ["ai researcher"]),
    ("Computer Vision Engineer", ["computer vision engineer"]),
    ("Computer Vision Scientist", ["computer vision scientist"]),
    ("Data Scientist", ["data scientist"]),
    ("Robotics Engineer", ["robotics engineer"]),
    ("Forward Deployed Engineer", ["forward deployed engineer"]),
    ("AI Forward Deployed Engineer", ["ai forward deployed engineer", "forward deployed ai engineer"]),
    ("AI Solutions Architect", ["ai solutions architect", "ai solution architect"]),
    ("Applied AI Solution Architect", ["applied ai solution architect", "applied ai solutions architect"]),
    ("AI Architect", ["ai architect"]),
    ("AI Product Manager", ["ai product manager"]),
    ("AI Consultant", ["ai consultant"]),
    ("AI Strategist", ["ai strategist"]),
    ("AI Governance Specialist", ["ai governance specialist"]),
    ("AI Ethics Specialist", ["ai ethics specialist"]),
    ("AI Ethicist", ["ai ethicist"]),
    ("AI Trainer", ["ai trainer"]),
    ("Data Annotator", ["data annotator"]),
    ("LLM Specialist", ["llm specialist"]),
    ("Machine Learning Platform Specialist", ["machine learning platform specialist"]),
    ("Head of AI", ["head of ai"]),
    ("Chief AI Officer", ["chief ai officer"]),
]
GUIDE_LOOKUP = {}
for _i, (_name, _vars) in enumerate(GUIDE_TITLES):
    for _v in _vars:
        GUIDE_LOOKUP[_v] = _i


# ---------------------------------------------------------------- reading the index
def read_jobs(index_dir, man):
    """Yield (ats, board_index, board_name, title, location, posted_sec) for every job, one shard at a time."""
    for s in man["shards"]:
        with gzip.open(os.path.join(index_dir, s["key"] + ".gz")) as fh:
            shard = json.loads(fh.read())
        if shard.get("v") != 1:
            sys.exit(f"STOP: shard {s['key']} has version {shard.get('v')}, expected 1")
        ats = shard["ats"]
        names = [b[1] or b[0] for b in shard["boards"]]       # a board without a company name: its token
        for b, job_id, title, location, remote, posted in shard["jobs"]:
            yield ats, b, names[b], (title or "").strip(), (location or "").strip(), posted
        del shard


def pct(part, whole, nd=1):
    return round(100.0 * part / whole, nd) if whole else None


def display_name(forms):
    """The most common original spelling of a role name (ties: alphabetical), for the CSV and the page."""
    return min(forms.items(), key=lambda kv: (-kv[1], kv[0]))[0]


def build(index_dir, audit=False):
    man, hashes = ct002.verify_inputs(index_dir)
    # Copies: the same title, location and posting time on two boards of one ATS count once, on the board that
    # lists it most often (the rule of ct-002's page; jobs without a posting time are all kept).
    rows, per_key = [], {}
    read = collections.Counter()
    for ats, b, bname, title, location, posted in read_jobs(index_dir, man):
        read[ats] += 1
        k = (ats, title.lower(), location.lower(), posted) if posted else None
        if k:
            per_key.setdefault(k, collections.Counter())[(ats, b)] += 1
        rows.append((ats, b, bname, title, location, k))
    keep = {k: min(bc, key=lambda x: (-bc[x], x)) for k, bc in per_key.items() if len(bc) > 1}
    jobs = [(ats, b, bname, title, location) for ats, b, bname, title, location, k in rows
            if k is None or k not in keep or keep[k] == (ats, b)]
    copies = read - collections.Counter(j[0] for j in jobs)
    del rows, per_key

    n_all = collections.Counter()
    boards_all = collections.defaultdict(set)
    n_ai = collections.Counter()
    boards_ai = collections.defaultdict(set)
    sen_all, sen_ai, sen_ai_nt = collections.Counter(), collections.Counter(), collections.Counter()
    reg_all, reg_ai, reg_ai_nt = collections.Counter(), collections.Counter(), collections.Counter()
    terms = collections.Counter()
    terms_ats = collections.defaultdict(collections.Counter)
    caps_dropped = 0
    in_role = in_suffix = 0
    grp_n, grp_boards = collections.Counter(), collections.defaultdict(set)
    grp_board_n = collections.defaultdict(collections.Counter)
    grp_sen = collections.defaultdict(collections.Counter)
    grp_reg = collections.defaultdict(collections.Counter)
    board_ai_n = collections.Counter()
    board_grp = collections.defaultdict(collections.Counter)
    roles = {}             # role key -> {"forms", "boards", "listings", "group", "us", "europe", "other", ...}
    suffix_roles = {}
    guide_n, guide_boards = collections.Counter(), collections.defaultdict(set)
    guide_ai = collections.Counter()
    fde = collections.Counter()
    fde_boards = set()
    samples = collections.defaultdict(list)

    for ats, b, bname, title, location in jobs:
        board = (ats, b)
        n_all[ats] += 1
        boards_all[ats].add(board)
        s = seniority(title)
        r = region(location)
        sen_all[s] += 1
        reg_all[r] += 1
        parts = title_parts(title)
        normed = [norm_part(p) for p in parts]
        tl = ai_terms(title)
        if not tl and RX_SHORT.search(title):
            caps_dropped += 1
        # titles that guides name, over every open job, matched on the role name (the first part, as in the list)
        gi = GUIDE_LOOKUP.get(normed[0]) if normed else None
        if gi is not None:
            guide_n[gi] += 1
            guide_boards[gi].add(board)
            if tl:
                guide_ai[gi] += 1
        if re.search(r"forward[- ]deployed", title, re.I):
            fde["listings"] += 1
            fde_boards.add(board)
            fde["ai_named"] += bool(tl)
            fde[r] += 1
        if not tl:
            continue
        n_ai[ats] += 1
        boards_ai[ats].add(board)
        sen_ai[s] += 1
        reg_ai[r] += 1
        for t in set(tl):
            key = t if t in SHORT_TERMS else t.lower()
            terms[key] += 1
            terms_ats[key][ats] += 1
        g = group_of(title)
        if g != "training":
            sen_ai_nt[s] += 1
            reg_ai_nt[r] += 1
        grp_n[g] += 1
        grp_boards[g].add(board)
        grp_board_n[g][board] += 1
        grp_sen[g][s] += 1
        grp_reg[g][r] += 1
        board_ai_n[(ats, bname, b)] += 1
        board_grp[(ats, bname, b)][g] += 1
        if audit and len(samples[g]) < 400:
            samples[g].append(title)
        # the role name: the first part of the title that names AI; if that is not the first part, the AI term is
        # a suffix (team, product or project) and the role is the first part
        first_ai = next((i for i, p in enumerate(parts) if ai_terms(p)), None)
        if first_ai == 0:
            in_role += 1
            key, store = normed[0], roles
        else:
            in_suffix += 1
            key, store = (normed[0] if normed else title.lower()), suffix_roles
        if not key:
            continue
        e = store.setdefault(key, {"forms": collections.Counter(), "boards": set(), "listings": 0,
                                   "groups": collections.Counter(), "us": 0, "europe": 0, "other": 0,
                                   "junior": 0, "senior": 0, "ats": collections.Counter()})
        e["forms"][role_display(parts[0]) if parts else title] += 1
        if audit and len(e.setdefault("examples", [])) < 6:
            e["examples"].append(title)
        e["boards"].add(board)
        e["listings"] += 1
        e["groups"][g] += 1
        e[r] += 1
        e["ats"][ats] += 1
        if s in ("junior", "senior"):
            e[s] += 1

    if audit:
        for g in GROUP_ORDER:
            sm = samples[g]
            step = max(1, len(sm) // 25)
            print(f"== {g} ({grp_n[g]} listings): " + " || ".join(sm[::step][:25]))
        oth = collections.Counter(t for t in samples["other"])
        print("== other, most common:", oth.most_common(40))
        for store, name in ((roles, "role"), (suffix_roles, "suffix")):
            short = [(k, e) for k, e in store.items() if len(e["boards"]) >= 3 and len(k.split()) <= 2
                     and (ai_terms(k.upper()) or SENIORITY_PREFIX.match(k + " ") or k in ("manager", "director"))]
            for k, e in sorted(short, key=lambda kv: -len(kv[1]["boards"]))[:12]:
                print(f"== {name} key {k!r} ({len(e['boards'])} boards): " + " || ".join(e["examples"]))

    total = sum(n_all.values())
    total_ai = sum(n_ai.values())
    nb_all = sum(len(v) for v in boards_all.values())
    nb_ai = sum(len(v) for v in boards_ai.values())

    def role_rows(store, kind):
        out = []
        for key, e in store.items():
            nb = len(e["boards"])
            if nb < 2:
                continue
            out.append({"kind": kind, "title": display_name(e["forms"]), "key": key,
                        "group": GROUP_LABEL[display_name(e["groups"])], "boards": nb, "listings": e["listings"],
                        "us": e["us"], "europe": e["europe"], "other_region": e["other"],
                        "junior_word": e["junior"], "senior_word": e["senior"],
                        "top_ats": ATS_NAME[display_name(e["ats"])]})
        out.sort(key=lambda r: (-r["boards"], -r["listings"], r["key"]))
        for i, r in enumerate(out, 1):
            r["rank"] = i
        return out

    role_list = role_rows(roles, "ai_in_role_name")
    suffix_list = role_rows(suffix_roles, "ai_in_suffix")

    ats_rows = []
    for a in ATS_ORDER:
        ats_rows.append({"id": a, "ats": ATS_NAME[a], "listings": n_all[a], "ai_listings": n_ai[a],
                         "ai_pct": pct(n_ai[a], n_all[a]), "boards": len(boards_all[a]),
                         "ai_boards": len(boards_ai[a]), "ai_boards_pct": pct(len(boards_ai[a]), len(boards_all[a]))})

    grp_rows = []
    for g in GROUP_ORDER:
        top_board = max(grp_board_n[g].values()) if grp_board_n[g] else 0
        grp_rows.append({"id": g, "group": GROUP_LABEL[g], "listings": grp_n[g], "listings_pct": pct(grp_n[g], total_ai),
                         "boards": len(grp_boards[g]), "boards_pct": pct(len(grp_boards[g]), nb_ai),
                         "top_board_listings": top_board, "top_board_pct": pct(top_board, grp_n[g]),
                         "junior_pct": pct(grp_sen[g]["junior"], grp_n[g]),
                         "senior_pct": pct(grp_sen[g]["senior"], grp_n[g]),
                         "us_pct": pct(grp_reg[g]["us"], grp_n[g]), "europe_pct": pct(grp_reg[g]["europe"], grp_n[g])})

    top_boards = []
    for (ats, bname, b), c in sorted(board_ai_n.items(), key=lambda kv: (-kv[1], kv[0]))[:10]:
        mg, mc = min(board_grp[(ats, bname, b)].items(), key=lambda kv: (-kv[1], kv[0]))
        top_boards.append({"board": bname, "ats": ATS_NAME[ats], "ai_listings": c, "ai_listings_pct": pct(c, total_ai),
                           "main_group": GROUP_LABEL[mg], "main_group_pct": pct(mc, c)})
    top5 = sum(x["ai_listings"] for x in top_boards[:5])

    guide_rows = []
    for i, (name, variants) in enumerate(GUIDE_TITLES):
        guide_rows.append({"id": f"guide-{i:02d}", "title": name, "variants": "; ".join(variants),
                           "boards": len(guide_boards[i]), "listings": guide_n[i],
                           "ai_named_pct": pct(guide_ai[i], guide_n[i]),
                           **{f"{a}_boards": sum(1 for x in guide_boards[i] if x[0] == a) for a in ATS_ORDER}})

    def sen_block(c):
        n = sum(c.values())
        return {"listings": n, "junior_pct": pct(c["junior"], n), "senior_pct": pct(c["senior"], n),
                "neither_pct": pct(c["neither"], n), "junior": c["junior"], "senior": c["senior"]}

    def reg_block(c):
        n = sum(c.values())
        return {"listings": n, "us_pct": pct(c["us"], n), "europe_pct": pct(c["europe"], n),
                "other_pct": pct(c["other"], n), "us": c["us"], "europe": c["europe"], "other": c["other"]}

    by_key = {r["key"]: r for r in role_list}
    ai_eng = by_key.get("ai engineer", {})
    ml_eng = by_key.get("machine learning engineer", {})
    summary = {
        "index_built_at": BUILT_AT, "index_boards": man["boards"], "index_jobs": man["jobs"],
        "index_boards_with_jobs": man["boardsWithJobs"],
        "jobs_read": sum(read.values()), "copies_dropped": sum(copies.values()), "listings": total,
        "boards_with_listings": nb_all,
        "ai_listings": total_ai, "ai_listings_pct": pct(total_ai, total, 2), "ai_boards": nb_ai,
        "ai_boards_pct": pct(nb_ai, nb_all),
        "ai_in_role_name": in_role, "ai_in_role_name_pct": pct(in_role, total_ai),
        "ai_in_suffix": in_suffix, "ai_in_suffix_pct": pct(in_suffix, total_ai),
        "role_names_2plus_boards": len(role_list), "suffix_roles_2plus_boards": len(suffix_list),
        "guide_titles_counted": len(GUIDE_TITLES),
        "short_form_titles_dropped": caps_dropped,      # all-capitals or Master of Laws rule
        "top5_boards_ai_listings": top5, "top5_boards_ai_pct": pct(top5, total_ai),
        "training_listings_pct": pct(grp_n["training"], total_ai),
        "training_boards": len(grp_boards["training"]),
        "training_boards_pct": pct(len(grp_boards["training"]), nb_ai),
        "ai_excl_training_listings": total_ai - grp_n["training"],
        "ai_excl_training_pct": pct(total_ai - grp_n["training"], total, 2),
        "fde_listings": fde["listings"], "fde_boards": len(fde_boards),
        "fde_ai_named": fde["ai_named"], "fde_ai_named_pct": pct(fde["ai_named"], fde["listings"]),
        "fde_us_pct": pct(fde["us"], fde["listings"]), "fde_europe_pct": pct(fde["europe"], fde["listings"]),
        "ai_engineer_boards": ai_eng.get("boards"), "ai_engineer_listings": ai_eng.get("listings"),
        "ml_engineer_boards": ml_eng.get("boards"), "ml_engineer_listings": ml_eng.get("listings"),
        "ai_share_us_jobs_pct": pct(reg_ai["us"], reg_all["us"]),
        "ai_share_europe_jobs_pct": pct(reg_ai["europe"], reg_all["europe"]),
        "ai_share_other_jobs_pct": pct(reg_ai["other"], reg_all["other"]),
    }
    for a in ATS_ORDER:
        summary[f"copies_dropped_{a}"] = copies[a]

    data = {
        "title": "AI job titles: which titles that name AI or machine learning employers post, counted on company "
                 "job boards",
        "source": "The job index of ATS Jobs Search (Apify Actor scaleturn/ats-jobs-search), built "
                  f"{BUILT_AT}: {man['boards']} company job boards on six applicant tracking systems.",
        "method": {
            "ai_named": "A title names AI when it contains one of these terms. Case-sensitive, not touching a Latin "
                        "letter or digit: " + ", ".join(SHORT_TERMS) + ". Any case: " + ", ".join(LONG_TERMS) +
                        ". In a title written all in capitals, a short form counts only at the start or end of the "
                        "title or of one of its parts, or next to an English job word. In a title that names law, "
                        "a legal role or tax, LLM is the Master of Laws degree and does not count.",
            "role_name": "Titles are split into parts at spaced dashes, bars, commas, colons, @ and brackets; a part "
                         "that is only seniority words (as in 'Senior / Staff') is skipped. The role name is the "
                         "first part with gender tags, leading seniority words (Senior, Sr., Staff, Principal, Lead, "
                         "Junior, Jr., Founding, Mid-level, Entry-level, Distinguished, Expert) and trailing levels "
                         "(I-V, 1-5) removed and slashes closed up, read case-insensitively with hyphens as spaces "
                         "and abbreviations as their full form (ML: machine learning; A.I. and artificial "
                         "intelligence: AI; GenAI: generative AI; a slash pair such as AI/ML stays as written). "
                         "When the first part names AI, the AI term is in the role name; otherwise it is in a suffix "
                         "(a team, product or project) and the first part is the role.",
            "groups": {gid: {"label": label, "rule": rx} for gid, label, rx in GROUPS},
            "groups_order": "A title gets the first group whose rule matches anywhere in it; titles that match none "
                            "are Other roles.",
            "seniority": "Junior when the title has a junior, intern, student or graduate word; else senior when it "
                         "has Senior, Sr., Staff, Principal, Lead, Distinguished, Head of, Director, VP, Chief or "
                         "Founding ('Member of Technical Staff' and 'Chief of Staff' are not seniority).",
            "guide_titles": "Titles that career guides and essays list, each matched against the role name (the "
                            "first part, normalized as above) of every open title, AI-named or not; the variants "
                            "matched are listed with each.",
            "copies": "A job with the same title, location and posting time on two or more boards of one ATS is "
                      "counted once, on the board that lists it most often (as on the posting-day page).",
            "region": "From the location text, with ct-002/build_data.py's rule: US, Europe, or other (another region, "
                      "several regions, or no place recognised).",
            "boards": "Boards, not companies: a company can run more than one board.",
        },
        "summary": summary,
        "terms": [{"term": t, "listings": c, **{a: terms_ats[t][a] for a in ATS_ORDER}}
                  for t, c in sorted(terms.items(), key=lambda kv: (-kv[1], kv[0]))],
        "ats": ats_rows,
        "groups": grp_rows,
        "seniority": {"all": sen_block(sen_all), "ai": sen_block(sen_ai), "ai_excl_training": sen_block(sen_ai_nt)},
        "region": {"all": reg_block(reg_all), "ai": reg_block(reg_ai), "ai_excl_training": reg_block(reg_ai_nt)},
        "top_boards": top_boards,
        "guide_titles": guide_rows,
        "rows": role_list + suffix_list,
        "inputs_sha256": hashes,
    }
    return data


# ---------------------------------------------------------------- outputs
CSV_COLS = ["kind", "rank", "title", "group", "boards", "listings", "us", "europe", "other_region", "junior_word",
            "senior_word", "top_ats"]


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
    for r in data["rows"]:
        d = {k: r[k] for k in CSV_COLS if k not in ("kind", "group", "top_ats")}
        facts.append(_fact(f"{r['kind']}-{r['rank']}", f"{r['title']}: boards and listings (CSV row)", c, today, d))
    for r in data["ats"]:
        facts.append(_fact(f"ats-{r['id']}", f"{r['ats']}: AI-named titles", j, today, r))
    for r in data["groups"]:
        facts.append(_fact(f"group-{r['id']}", f"{r['group']}: AI-named listings", j, today, r))
    for k, blk in data["seniority"].items():
        facts.append(_fact(f"seniority-{k}", f"seniority words, {k}", j, today, blk))
    for k, blk in data["region"].items():
        facts.append(_fact(f"region-{k}", f"region, {k}", j, today, blk))
    for i, r in enumerate(data["top_boards"], 1):
        facts.append(_fact(f"board-{i}", f"board {i} by AI-named listings: {r['board']}", j, today, r))
    for r in data["guide_titles"]:
        d = {k: v for k, v in r.items() if k != "variants"}
        facts.append(_fact(r["id"], f"{r['title']}: boards and listings", j, today, d))
    for r in data["terms"]:
        facts.append(_fact(f"term-{r['term']}", f"listings naming {r['term']}", j, today, r))
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
            for v in x.values():
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


# Table caption prefix -> (rows source, row key column, {column label: field})
TABLES = {
    "Most common AI job titles": ("rows", "Title", {"Boards": "boards", "Listings": "listings"}),
    "Titles the career guides list": ("guide_titles", "Title", {"Boards": "boards", "Listings": "listings"}),
    "AI-named listings by role group": ("groups", "Group", {"Listings": "listings", "Share": "listings_pct",
                                                            "Boards": "boards", "Largest board": "top_board_pct"}),
    "Share of titles that name AI, by ATS": ("ats", "ATS", {"Listings": "listings", "AI-named": "ai_listings",
                                                           "Share": "ai_pct", "Boards with one": "ai_boards_pct"}),
}
ROW_NAME = {"rows": "title", "guide_titles": "title", "groups": "group", "ats": "ats"}


def check_tables(page, data):
    html = open(page, encoding="utf-8").read()
    bad, seen = [], 0
    for cap, body in re.findall(r"<caption>(.*?)</caption>.*?<tbody>(.*?)</tbody>", html, re.S):
        key = next((k for k in TABLES if cap.startswith(k)), None)
        if not key:
            continue
        src, rowcol, cols = TABLES[key]
        pool = [r for r in data[src] if src != "rows" or r["kind"] == "ai_in_role_name"]
        for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", body, re.S):
            cells = {k: re.sub(r"<[^>]+>", "", v).strip()
                     for k, v in re.findall(r'<t[dh] data-label="([^"]+)"[^>]*>(.*?)</t[dh]>', tr, re.S)}
            name = cells.get(rowcol, "")
            row = next((r for r in pool if r[ROW_NAME[src]] == name), None)
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
    return [] if f'fetch("{JSON_REL}")' in html else [f"the page does not fetch {JSON_REL}"]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", help="directory with index-manifest.json and the index-*.gz shards of the "
                                    f"{BUILT_AT} build; without it, --check uses the committed {JSON_REL}")
    ap.add_argument("--check", help="page to verify: every visible number must come from the data")
    ap.add_argument("--audit", action="store_true", help="with --index: print sample titles of each role group")
    ap.add_argument("--refresh-facts", action="store_true",
                    help="without --index: rewrite ct-003/facts.json from the committed JSON with today's date")
    a = ap.parse_args()
    if a.index:
        data = build(a.index, audit=a.audit)
        write_outputs(data)
        s = data["summary"]
        print(f"index {BUILT_AT}: {s['jobs_read']} jobs read, {s['copies_dropped']} copies dropped, {s['listings']} "
              f"listings on {s['boards_with_listings']} boards; AI-named {s['ai_listings']} ({s['ai_listings_pct']}%) "
              f"on {s['ai_boards']} boards")
        print(f"wrote {CSV_REL}, {JSON_REL}, ct-003/facts.json")
    elif a.check or a.refresh_facts:
        data = json.load(open(os.path.join(ROOT, JSON_REL), encoding="utf-8"))
        print(f"no --index: using the committed {JSON_REL} (index {data['summary']['index_built_at']})")
        if a.refresh_facts:
            write_facts(data)
            print("wrote ct-003/facts.json with today's date")
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
        print("WIDGET CHECK PASS: the lookup loads the JSON" if not wbad else "WIDGET CHECK FAIL: " + "; ".join(wbad))
        if bad or tbad or not seen or wbad:
            sys.exit(1)


if __name__ == "__main__":
    main()
