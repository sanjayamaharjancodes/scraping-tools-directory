"""Fails if a tool we run against our sites loads the GoatCounter counter (ct-005, 20 Nov 2026).

Usage:
    python -I ct-005/test_no_counter.py [--autopilot F:/Lab/assets/content-autopilot] [--no-browser]

Why: in November 2026 our own checks were counted among the sites' GoatCounter visitors. "Loads the counter" means a request for the GoatCounter script (gc.zgo.at/count.js) or its count endpoint
(<code>.goatcounter.com/count). Reads of GoatCounter's API (/api/v0/, by rx-001/reach_read.py) count no visit and
are allowed.

1. Discovery. Every script in ct-*/, rx-*/, md-*/, tools/ and scripts/ is classified by what it can reach: browser (starts Chrome,
   Playwright, Puppeteer or Lighthouse, or renders through content-autopilot's render.py), network (urllib,
   http.client, requests, fetch) or offline. Each browser or network tool must be listed in TOOLS with how the test
   drives it; one that is not listed fails the test. So rx-001/reach_read.py is driven once its branch is merged,
   and any tool added later is either driven here or flagged.
2. Python network tools run in this process with the network and process start replaced: every URL they request is
   recorded and answered 404, every process start or raw socket is recorded and refused. A counter request, a
   process start or no request at all (the harness did not reach the tool's network code) fails the tool.
3. Browser tools run against a local page that carries the live counter snippet, read byte for byte from this
   site's index.html and served from 127.0.0.1. A script on that page tells the test server whether the counter
   script loaded, failed to load (blocked) or was absent (stripped). "loaded", or no report, fails the tool. count.js
   never counts a page on 127.0.0.1 (its localhost rule), so running this test registers no visit.
4. Planted cases prove the test can fail: a Python tool that requests count.js, an unlisted browser tool, and plain
   headless Chrome with no blocking, which must report "loaded" (this one needs the internet).
Exit code 0 only when every tool passes and every planted case is caught.
"""
import argparse
import contextlib
import http.server
import importlib.util
import io
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CHROME = "C:/Program Files/Google/Chrome/Application/chrome.exe"
SCAN_DIRS = re.compile(r"^(?:ct-\d+|rx-\d+|md-\d+|tools|scripts)$")
SCAN_EXT = (".py", ".mjs", ".js", ".ps1")
SELF = "ct-005/test_no_counter.py"

# How each tool is driven. kind: python = in-process with the network replaced; render = content-autopilot's
# render.py on the fixture (run_gate.py's only browser path); node / python-browser = run as a process on the fixture.
TOOLS = {
    "ct-001/check_live.py": ("python", []),
    "ct-002/check_live.py": ("python", []),
    "ct-003/check_live.py": ("python", []),
    "ct-004/check_live.py": ("python", []),
    "ct-005/check_live.py": ("python", []),
    "rx-001/reach_read.py": ("python", []),
    "scripts/firecrawl_benchmark.py": ("python", ["robots"]),   # md-009: reaches Firecrawl and the panel sites, never ours
    "ct-001/run_gate.py": ("render", None),
    "ct-002/run_gate.py": ("render", None),
    "ct-003/run_gate.py": ("render", None),
    "ct-005/run_gate.py": ("render", None),
    "ct-004/consent_probe.mjs": ("node", ["--url", "{url}", "--wait", "4"]),
    "ct-005/lighthouse_run.py": ("python-browser", ["--url", "{url}", "--runs", "1"]),
}
# Python is classified by what it imports (anywhere in the file, function-level imports included), so a string
# such as 'fetch("data.json")' in a page check does not make a build script a network tool.
PY_NET = {"urllib.request", "http.client", "requests", "httpx", "aiohttp", "urllib3", "socket", "websocket",
          "websockets"}
PY_BROWSER = {"playwright", "selenium", "pyppeteer", "webbrowser", "render"}     # render = content-autopilot's
RX_LAUNCHES = re.compile(r"chrome\.exe|chromium|lighthouse|--headless|\bnpx\b", re.I)
RX_JS_BROWSER = re.compile(r"chrome\.exe|chromium|playwright|puppeteer|lighthouse|--headless", re.I)
RX_JS_NETWORK = re.compile(r"\bfetch\(|https?\.(?:get|request)\(|node:https?\b|require\(['\"]https?['\"]\)|"
                           r"Invoke-WebRequest|Invoke-RestMethod|\bcurl\b")


def py_imports(text):
    import ast
    mods = set()
    for node in ast.walk(ast.parse(text)):
        if isinstance(node, ast.Import):
            mods |= {n.name for n in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module:
            mods.add(node.module)
            mods |= {f"{node.module}.{n.name}" for n in node.names}
    return mods


def classify(rel, text):
    if rel.endswith(".py"):
        mods = py_imports(text)
        top = {m.split(".")[0] for m in mods}
        if top & PY_BROWSER or ("subprocess" in top and RX_LAUNCHES.search(text)):
            return "browser"
        return "network" if mods & PY_NET else "offline"
    if RX_JS_BROWSER.search(text):
        return "browser"
    return "network" if RX_JS_NETWORK.search(text) else "offline"


def is_counter(url):
    u = urllib.parse.urlsplit(url if "//" in url else "https://" + url)
    host = (u.hostname or "").lower()
    if host == "zgo.at" or host.endswith(".zgo.at"):
        return True
    return (host == "goatcounter.com" or host.endswith(".goatcounter.com")) and u.path.startswith("/count")


# ---------------------------------------------------------------- 1. discovery
def discover(root):
    found = {}
    for d in sorted(os.listdir(root)):
        if not (SCAN_DIRS.match(d) and os.path.isdir(os.path.join(root, d))):
            continue
        for dirpath, dirnames, files in os.walk(os.path.join(root, d)):
            dirnames[:] = [x for x in dirnames if x not in ("__pycache__", "node_modules")]
            for f in files:
                if not f.endswith(SCAN_EXT):
                    continue
                rel = os.path.relpath(os.path.join(dirpath, f), root).replace(os.sep, "/")
                if rel == SELF:
                    continue
                text = open(os.path.join(dirpath, f), encoding="utf-8", errors="replace").read()
                found[rel] = classify(rel, text)
    return found


def check_discovery(found, tools):
    """Every browser or network tool must be listed; a listed browser tool must be driven as one."""
    bad = []
    for rel, kind in found.items():
        if kind == "offline":
            continue
        if rel not in tools:
            bad.append(f"{rel}: a {kind} tool that test_no_counter.py does not drive (add it to TOOLS)")
        elif kind == "browser" and tools[rel][0] == "python":
            bad.append(f"{rel}: starts a browser but is listed as a python network tool")
    return bad


# ---------------------------------------------------------------- 2. python network tools, in process
class _Out(io.StringIO):
    def reconfigure(self, **kw):
        pass


@contextlib.contextmanager
def no_network(rec):
    """Record and refuse every URL, process start and raw socket while the block runs."""
    saved = (urllib.request.urlopen, urllib.request.OpenerDirector.open, subprocess.Popen, os.system,
             socket.create_connection, socket.socket.connect)

    def fake_urlopen(req, *a, **k):
        url = req.full_url if isinstance(req, urllib.request.Request) else str(req)
        rec["urls"].append(url)
        raise urllib.error.HTTPError(url, 404, "refused by test_no_counter", {}, io.BytesIO(b""))

    def fake_open(self, req, *a, **k):
        return fake_urlopen(req)

    class FakePopen:
        def __init__(self, args, *a, **k):
            rec["spawn"].append(args if isinstance(args, str) else " ".join(map(str, args)))
            raise OSError("process start refused by test_no_counter")

    def fake_system(cmd):
        rec["spawn"].append(cmd)
        return 1

    def fake_conn(address, *a, **k):
        rec["sockets"].append(str(address))
        raise OSError("socket refused by test_no_counter")

    def fake_connect(self, address):
        rec["sockets"].append(str(address))
        raise OSError("socket refused by test_no_counter")

    urllib.request.urlopen, urllib.request.OpenerDirector.open = fake_urlopen, fake_open
    subprocess.Popen, os.system = FakePopen, fake_system
    socket.create_connection, socket.socket.connect = fake_conn, fake_connect
    try:
        yield
    finally:
        (urllib.request.urlopen, urllib.request.OpenerDirector.open, subprocess.Popen, os.system,
         socket.create_connection, socket.socket.connect) = saved


def run_python_tool(path, args, env=None):
    rec = {"urls": [], "spawn": [], "sockets": [], "exit": None}
    old_env = {k: os.environ.get(k) for k in (env or {})}
    os.environ.update(env or {})
    old_argv, old_path = sys.argv, list(sys.path)
    sys.argv = [path] + list(args)
    out = _Out()
    try:
        with no_network(rec), contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            spec = importlib.util.spec_from_file_location("tool_under_test", path)
            mod = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(mod)
                if hasattr(mod, "main"):
                    rec["exit"] = mod.main()
            except SystemExit as e:
                rec["exit"] = e.code
            except Exception as e:      # the tool may fail on 404s; what it requested is what matters
                rec["exit"] = f"{type(e).__name__}: {e}"[:160]
    finally:
        sys.argv, sys.path[:] = old_argv, old_path
        for k, v in old_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    return rec


def judge_python(rec):
    counter = [u for u in rec["urls"] if is_counter(u)]
    if counter:
        return False, f"requested the counter: {counter[:2]}"
    if rec["spawn"]:
        return False, f"tried to start a process: {rec['spawn'][:1]}"
    if rec["sockets"]:
        return False, f"opened a raw socket: {rec['sockets'][:1]}"
    if not rec["urls"]:
        return False, f"made no request, so the harness did not exercise it (exit {rec['exit']!r})"
    hosts = sorted({urllib.parse.urlsplit(u).hostname for u in rec["urls"]})
    return True, f"{len(rec['urls'])} requests to {', '.join(hosts)}; no counter, no process, no socket"


# ---------------------------------------------------------------- 3. browser tools, on a local fixture
def live_snippet():
    html = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    m1 = re.search(r"<script>window\.goatcounter = .*?</script>", html)
    m2 = re.search(r"<script data-goatcounter=[^>]*></script>", html)
    if not (m1 and m2):
        sys.exit("STOP: index.html has no GoatCounter snippet to copy into the fixture")
    return m1.group(0) + "\n" + m2.group(0)


REPORTER = """<script>
(function () {
  var s = document.querySelector('script[src*="gc.zgo.at"]'), sent = false;
  function rep(v) { if (sent) return; sent = true;
    new Image().src = "%(report)s?tool=%(tool)s&counter=" + v + "&t=" + Date.now(); }
  if (!s) { rep("absent"); return; }
  s.addEventListener("load", function () { rep("loaded"); });
  s.addEventListener("error", function () { rep("blocked"); });
  setTimeout(function () { rep(window.goatcounter && window.goatcounter.count ? "loaded" : "pending"); }, 5000);
})();
</script>"""


def fixture_html(tool, report_url, snippet):
    return ("<!DOCTYPE html>\n<html lang=\"en\"><head><meta charset=\"UTF-8\"><title>Counter fixture</title></head>"
            "<body><main><h1>Counter fixture</h1><p>A local page with the live GoatCounter snippet.</p></main>\n"
            + snippet + "\n" + REPORTER % {"report": report_url, "tool": tool} + "\n</body></html>\n")


class FixtureServer:
    def __init__(self, snippet):
        self.reports, self.snippet = [], snippet
        outer = self

        class H(http.server.BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def do_GET(self):
                u = urllib.parse.urlsplit(self.path)
                q = urllib.parse.parse_qs(u.query)
                if u.path == "/__report":
                    outer.reports.append((q.get("tool", ["?"])[0], q.get("counter", ["?"])[0]))
                    body, ctype = b"", "image/gif"
                elif u.path.startswith("/t/"):
                    tool = u.path.split("/")[2]
                    body = fixture_html(tool, outer.report_url, outer.snippet).encode()
                    ctype = "text/html; charset=utf-8"
                else:
                    self.send_response(404)
                    self.end_headers()
                    return
                self.send_response(200)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

        class Server(http.server.ThreadingHTTPServer):
            def handle_error(self, request, client_address):
                if not isinstance(sys.exc_info()[1], ConnectionError):   # a browser closing early is not an error
                    super().handle_error(request, client_address)

        self.srv = Server(("127.0.0.1", 0), H)
        self.base = f"http://127.0.0.1:{self.srv.server_address[1]}"
        self.report_url = self.base + "/__report"
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()

    def url(self, tool):
        return f"{self.base}/t/{tool}/"

    def verdicts(self, tool):
        return [v for t, v in self.reports if t == tool]

    def close(self):
        self.srv.shutdown()
        self.srv.server_close()


def judge_browser(states, expect_load=False):
    if not states:
        return False, "the page never reported: the tool did not load the fixture"
    if expect_load:
        return ("loaded" in states), f"reports {states}"
    if "loaded" in states:
        return False, f"the counter script loaded (reports {states})"
    return True, f"counter not loaded (reports {sorted(set(states))})"


def run_process(cmd, timeout=360):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=ROOT)
        return r.returncode, (r.stdout + r.stderr)[-300:]
    except (OSError, subprocess.TimeoutExpired) as e:
        return None, str(e)


def run_render(fx, autopilot, work):
    """run_gate.py's browser path: content-autopilot's render.render() on the fixture page."""
    sys.path.insert(0, autopilot)
    try:
        import common
        import render as render_mod
        page = os.path.join(work, "render-draft", "page.html")
        os.makedirs(os.path.dirname(page), exist_ok=True)
        with urllib.request.urlopen(fx.url("render"), timeout=10) as r:
            open(page, "w", encoding="utf-8").write(r.read().decode("utf-8"))
        site = os.path.join(work, "render-site")
        os.makedirs(site, exist_ok=True)
        res = render_mod.render(page, common.load_config(), os.path.join(work, "render-out"), site)
        return res.get("ok"), res.get("error")
    finally:
        sys.path.remove(autopilot)


def static_render_only(rel):
    """run_gate.py may reach a browser only through render_mod.render (tested above)."""
    text = open(os.path.join(ROOT, rel), encoding="utf-8").read()
    other = re.findall(r"chrome\.exe|chromium|playwright|puppeteer|lighthouse|--headless|subprocess", text, re.I)
    return not other, ("its only browser path is content-autopilot render.render" if not other
                       else f"also mentions {sorted(set(other))}")


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--autopilot", default="F:/Lab/assets/content-autopilot")
    ap.add_argument("--no-browser", action="store_true", help="skip the browser runs (discovery and Python only)")
    ap.add_argument("--root", help="another checkout of this site to scan and drive (default: this one), e.g. a "
                                   "branch that adds tools")
    a = ap.parse_args()
    global ROOT
    if a.root:
        ROOT = os.path.abspath(a.root)
        print(f"root: {ROOT}")
    results = []

    def report(name, ok, detail):
        results.append(ok)
        print(f"{'PASS' if ok else 'FAIL'} {name}: {detail}", flush=True)

    found = discover(ROOT)
    bad = check_discovery(found, TOOLS)
    counts = {k: sum(1 for v in found.values() if v == k) for k in ("browser", "network", "offline")}
    report("discovery", not bad, "; ".join(bad) if bad else
           f"{len(found)} scripts: {counts['browser']} browser, {counts['network']} network, {counts['offline']} "
           "offline; every browser and network tool is driven below")
    missing = [rel for rel in TOOLS if rel not in found]
    if missing:
        print(f"note: not in this checkout, not run: {', '.join(missing)}")

    # 2. python network tools
    for rel, (kind, args) in TOOLS.items():
        if kind == "python" and rel in found:
            env = {"REACH_ENV_FILE": os.path.join(ROOT, "no-such-secrets.env")}   # no secret is read
            rec = run_python_tool(os.path.join(ROOT, rel), args, env)
            ok, detail = judge_python(rec)
            report(rel, ok, detail)

    # 4a. planted: a python tool that requests count.js must be caught
    work = tempfile.mkdtemp(prefix="nocounter-", dir=os.path.join(ROOT, ".tmp-ct005")
                            if os.path.isdir(os.path.join(ROOT, ".tmp-ct005")) else None)
    planted = os.path.join(work, "planted_fetch.py")
    open(planted, "w", encoding="utf-8").write(
        "import urllib.request\n\ndef main():\n    urllib.request.urlopen('https://gc.zgo.at/count.js')\n")
    ok, detail = judge_python(run_python_tool(planted, []))
    report("planted: Python tool requesting count.js is caught", not ok, detail)
    # 4b. planted: an unlisted browser tool is caught by discovery
    fake_root = os.path.join(work, "root")
    os.makedirs(os.path.join(fake_root, "ct-999"))
    open(os.path.join(fake_root, "ct-999", "shot.py"), "w", encoding="utf-8").write(   # written, never run
        'import subprocess\nCHROME = "C:/Program Files/Google/Chrome/Application/chrome.exe"\n'
        'subprocess.run([CHROME, "--headless=new", "--screenshot", "https://scrapetools.scaleturn.com/"])\n')
    caught = check_discovery(discover(fake_root), TOOLS)
    report("planted: unlisted browser tool is caught", bool(caught), "; ".join(caught) or "not caught")

    if a.no_browser:
        print("browser runs skipped (--no-browser)")
    else:
        fx = FixtureServer(live_snippet())
        try:
            # 4c. control: headless Chrome with no blocking must load the counter, or the test cannot fail
            run_process([CHROME, "--headless=new", "--disable-gpu", "--no-first-run",
                         f"--user-data-dir={os.path.join(work, 'control-profile')}", "--virtual-time-budget=8000",
                         "--dump-dom", fx.url("control")], timeout=90)
            time.sleep(1)
            ok, detail = judge_browser(fx.verdicts("control"), expect_load=True)
            report("planted: plain headless Chrome loads the counter (control)", ok,
                   detail + ("" if ok else "; without this the browser checks prove nothing (internet needed)"))

            for rel, (kind, args) in TOOLS.items():
                if rel not in found or kind in ("python",):
                    continue
                tool = re.sub(r"[^a-z0-9]+", "-", rel.lower())
                if kind == "render":
                    s_ok, s_detail = static_render_only(rel)
                    report(rel, s_ok, s_detail)
                    continue
                url = fx.url(tool)
                argv = [x.replace("{url}", url) for x in args]
                cmd = (["node", os.path.join(ROOT, rel)] if kind == "node"
                       else [sys.executable, "-I", os.path.join(ROOT, rel)]) + argv
                rc, tail = run_process(cmd)
                time.sleep(1)
                ok, detail = judge_browser(fx.verdicts(tool))
                report(rel, ok, f"{detail}; exit {rc}" + ("" if ok else f"; {tail!r}"))

            if any(k == "render" and r in found for r, (k, _) in TOOLS.items()):
                r_ok, r_err = run_render(fx, a.autopilot, work)
                time.sleep(1)
                ok, detail = judge_browser(fx.verdicts("render"))
                report("content-autopilot render.render (run_gate.py's browser path)", ok and bool(r_ok),
                       detail + ("" if r_ok else f"; render error {r_err}"))
        finally:
            fx.close()
    shutil.rmtree(work, ignore_errors=True)
    failed = results.count(False)
    print(f"{len(results) - failed} of {len(results)} passed")
    print("ALL PASS" if not failed else f"{failed} FAILED")
    sys.exit(0 if not failed else 1)


if __name__ == "__main__":
    main()
