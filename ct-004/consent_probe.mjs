// Does Google's EU consent message (AdSense Privacy & messaging) show on a page? ct-004, 19 Nov 2026.
//
// Usage:
//   node ct-004/consent_probe.mjs --url https://scaleturn.com/ [--local <site dir>] [--shot out.png] [--wait 25]
//
// Opens the URL with ?fc=alwaysshow&fctype=gdpr, Google's documented preview of the published European regulations
// message (https://support.google.com/adsense/answer/10924669; https://developers.google.com/funding-choices/fc-api-docs),
// which ignores the visitor's region. Then it waits for the message (.fc-consent-root) and prints one JSON line.
// Exit code 0 when the message showed, 1 when it did not, 2 on an error.
//
// Safety: no ad can load and no visit is counted. Headless Chrome runs on a throwaway profile (never Sanjay's
// Chrome). Every request is paused: the AdSense loader scripts (pagead2.googlesyndication.com/pagead/js/ and
// /pagead/managed/js/), the consent host (fundingchoicesmessages.google.com) and Google's font and static hosts go
// through. Any other request to an ad, ad-quality or analytics host (doubleclick, googlesyndication, googleadservices,
// adtrafficquality, google-analytics, googletagmanager, GoatCounter) is failed before it leaves, and listed.
//
// --local <dir>: requests to the URL's own host are answered from <dir> (the branch's files) instead of the web, so
// a page can be checked at its real origin before it is deployed. Nothing else changes.
import { spawn } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const CHROME = "C:/Program Files/Google/Chrome/Application/chrome.exe";
const ALLOW = [
  /^https:\/\/pagead2\.googlesyndication\.com\/pagead\/(?:js|managed\/js)\//,
  /^https:\/\/fundingchoicesmessages\.google\.com\//,
  /^https:\/\/(?:fonts\.googleapis\.com|fonts\.gstatic\.com|www\.gstatic\.com)\//,
];
const AD_HOST = /(?:^|\.)(?:doubleclick\.net|googlesyndication\.com|googleadservices\.com|adtrafficquality\.google|google-analytics\.com|googletagmanager\.com|goatcounter\.com|zgo\.at|adservice\.google\.[a-z.]+)$/;
const TYPES = { ".html": "text/html; charset=utf-8", ".css": "text/css", ".js": "text/javascript", ".json": "application/json",
  ".csv": "text/csv", ".ico": "image/x-icon", ".png": "image/png", ".svg": "image/svg+xml", ".txt": "text/plain", ".xml": "application/xml" };

function args(argv) {
  const a = { wait: 25 };
  for (let i = 0; i < argv.length; i += 2) a[argv[i].replace(/^--/, "")] = argv[i + 1];
  if (!a.url) throw new Error("--url is required");
  a.wait = Number(a.wait);
  return a;
}

function decide(u, a, target) {
  const url = new URL(u);
  if (ALLOW.some((rx) => rx.test(u))) return "allow";
  if (AD_HOST.test(url.hostname)) return "block";
  if (a.local && url.hostname === target.hostname) return "local";
  return "allow";
}

function localFile(dir, u) {
  let p = decodeURIComponent(new URL(u).pathname);
  if (p.endsWith("/")) p += "index.html";
  const f = path.join(dir, ...p.split("/").filter(Boolean));
  if (!path.resolve(f).startsWith(path.resolve(dir)) || !fs.existsSync(f) || !fs.statSync(f).isFile()) return null;
  return { body: fs.readFileSync(f), type: TYPES[path.extname(f).toLowerCase()] || "application/octet-stream" };
}

async function main() {
  const a = args(process.argv.slice(2));
  const target = new URL(a.url);
  target.searchParams.set("fc", "alwaysshow");
  target.searchParams.set("fctype", "gdpr");
  const profile = fs.mkdtempSync(path.join(process.env.CT004_TMP || os.tmpdir(), "consent-probe-"));
  const chrome = spawn(CHROME, ["--headless=new", `--user-data-dir=${profile}`, "--remote-debugging-port=0",
    "--no-first-run", "--no-default-browser-check", "--disable-extensions", "--window-size=1280,900", "about:blank"],
  { stdio: ["ignore", "ignore", "pipe"] });
  const out = { url: target.href, local: a.local || null, consent_shown: false, tcfapi: false, text: "",
    loader_requests: 0, consent_requests: [], blocked: [], local_served: 0, local_missing: [] };
  try {
    const wsBrowser = await new Promise((res, rej) => {
      let buf = "";
      const t = setTimeout(() => rej(new Error("Chrome did not start")), 20000);
      chrome.stderr.on("data", (d) => {
        buf += d;
        const m = buf.match(/DevTools listening on (ws:\/\/\S+)/);
        if (m) { clearTimeout(t); res(m[1]); }
      });
    });
    const port = new URL(wsBrowser).port;
    const pages = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
    const ws = new WebSocket(pages.find((p) => p.type === "page").webSocketDebuggerUrl);
    await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
    let id = 0;
    const pending = new Map();
    const send = (method, params = {}) => new Promise((res, rej) => {
      const i = ++id;
      pending.set(i, { res, rej });
      ws.send(JSON.stringify({ id: i, method, params }));
    });
    ws.onmessage = async (ev) => {
      const m = JSON.parse(ev.data);
      if (m.id && pending.has(m.id)) {
        const { res, rej } = pending.get(m.id);
        pending.delete(m.id);
        return m.error ? rej(new Error(JSON.stringify(m.error))) : res(m.result);
      }
      if (m.method !== "Fetch.requestPaused") return;
      const { requestId, request } = m.params;
      const how = decide(request.url, a, target);
      if (/^https:\/\/pagead2\.googlesyndication\.com\/pagead\//.test(request.url) && how === "allow") out.loader_requests++;
      if (request.url.startsWith("https://fundingchoicesmessages.google.com/")) out.consent_requests.push(request.url.slice(0, 120));
      try {
        if (how === "block") {
          out.blocked.push(request.url.slice(0, 120));
          await send("Fetch.failRequest", { requestId, errorReason: "BlockedByClient" });
        } else if (how === "local") {
          const f = localFile(a.local, request.url);
          if (f) out.local_served++; else out.local_missing.push(new URL(request.url).pathname);
          await send("Fetch.fulfillRequest", f
            ? { requestId, responseCode: 200, responseHeaders: [{ name: "Content-Type", value: f.type }], body: f.body.toString("base64") }
            : { requestId, responseCode: 404, responseHeaders: [{ name: "Content-Type", value: "text/plain" }], body: "" });
        } else {
          await send("Fetch.continueRequest", { requestId });
        }
      } catch { /* the page navigated away from this request */ }
    };
    const ver = await send("Browser.getVersion");
    await send("Emulation.setUserAgentOverride", { userAgent: ver.userAgent.replace("HeadlessChrome", "Chrome") });
    await send("Fetch.enable", { patterns: [{ urlPattern: "*", requestStage: "Request" }] });
    await send("Page.enable");
    await send("Runtime.enable");
    await send("Page.navigate", { url: target.href });
    const probe = `(() => { const r = document.querySelector('.fc-consent-root');
      return JSON.stringify({ shown: !!(r && r.innerText.trim()), text: r ? r.innerText.replace(/\\s+/g, ' ').trim().slice(0, 300) : '',
        tcf: typeof window.__tcfapi === 'function' }); })()`;
    const end = Date.now() + a.wait * 1000;
    while (Date.now() < end) {
      await new Promise((r) => setTimeout(r, 1000));
      let r;
      try {
        r = JSON.parse((await send("Runtime.evaluate", { expression: probe, returnByValue: true })).result.value);
      } catch { continue; }                                  // the page is still loading
      out.tcfapi = r.tcf;
      if (r.shown) { out.consent_shown = true; out.text = r.text; break; }
    }
    if (out.consent_shown) await new Promise((r) => setTimeout(r, 1500));
    if (a.shot) {
      const shot = await send("Page.captureScreenshot", { format: "png" });
      fs.writeFileSync(a.shot, Buffer.from(shot.data, "base64"));
    }
    ws.close();
  } finally {
    const exited = new Promise((r) => { chrome.once("exit", r); setTimeout(r, 10000); });
    chrome.kill();
    await exited;
    // Windows can hold the profile's files a moment after Chrome exits: removal is best effort.
    try { fs.rmSync(profile, { recursive: true, force: true, maxRetries: 10, retryDelay: 500 }); } catch {
      console.error(`note: could not remove the throwaway profile ${profile}`);
    }
  }
  console.log(JSON.stringify(out));
  process.exit(out.consent_shown ? 0 : 1);
}

main().catch((e) => { console.error(`consent_probe error: ${e.message}`); process.exit(2); });
