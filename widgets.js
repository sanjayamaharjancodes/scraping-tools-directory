/* ScrapeTools cost-by-volume widget. No dependencies. Driven entirely by data/vendors.json.
   Optional: data-unit-label="Searches per month" data-unit-noun="searches" (default: basic requests).
   Mount: <div class="vcw" data-src="data/vendors.json" data-default="100000"
               data-affiliate-url="https://..." data-affiliate-vendor="scraperapi"></div>
   Order of the bars is by computed cost only; the affiliate card never changes it. */
(function () {
  "use strict";

  var nf = new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 });
  var usd = function (n) {
    return "$" + new Intl.NumberFormat("en-US", { minimumFractionDigits: n < 100 && n % 1 ? 2 : 0, maximumFractionDigits: 2 }).format(n);
  };
  var MIN = 1000, MAX = 10000000, STEPS = 200;

  function sliderToVolume(v) {
    var raw = Math.pow(10, Math.log10(MIN) + (Math.log10(MAX) - Math.log10(MIN)) * v / STEPS);
    var mag = Math.pow(10, Math.floor(Math.log10(raw)) - 1);   // two significant digits
    return Math.max(MIN, Math.min(MAX, Math.round(raw / mag) * mag));
  }
  function volumeToSlider(n) {
    return Math.round(STEPS * (Math.log10(n) - Math.log10(MIN)) / (Math.log10(MAX) - Math.log10(MIN)));
  }

  /* Cheapest published way to cover `volume` basic requests/month. Returns null when no
     published self-serve option covers it. Never extrapolates beyond published tiers. */
  function costFor(vendor, volume) {
    var best = null;
    function offer(cost, label) { if (best === null || cost < best.cost) { best = { cost: cost, label: label }; } }
    if (vendor.free_included && volume <= vendor.free_included) { offer(0, "Free tier"); }
    (vendor.tiers || []).forEach(function (t) { if (t.included >= volume) { offer(t.monthly_usd, t.name + " plan"); } });
    if (typeof vendor.payg_per_1000_usd === "number") { offer(volume / 1000 * vendor.payg_per_1000_usd, "Pay as you go"); }
    return best;
  }

  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) { e.className = cls; }
    if (text !== undefined) { e.textContent = text; }
    return e;
  }

  function mount(root) {
    var src = root.getAttribute("data-src") || "data/vendors.json";
    var start = Number(root.getAttribute("data-default")) || 100000;
    root.setAttribute("aria-busy", "true");
    fetch(src).then(function (r) {
      if (!r.ok) { throw new Error("HTTP " + r.status); }
      return r.json();
    }).then(function (data) {
      build(root, data, start);
    }).catch(function () {
      root.textContent = "The cost widget could not load its data. The tables on this page show the same published prices.";
    }).then(function () { root.removeAttribute("aria-busy"); });
  }

  function build(root, data, start) {
    root.textContent = "";
    var vendors = (data.vendors || []).filter(function (v) { return v.comparable !== false; });
    var skipped = (data.vendors || []).filter(function (v) { return v.comparable === false; });

    var head = el("div", "vcw-head");
    var label = el("label", "vcw-label");
    var unitLabel = root.getAttribute("data-unit-label") || "Basic requests per month (no JavaScript rendering)";
    var noun = root.getAttribute("data-unit-noun") || "basic requests";
    label.appendChild(el("span", "", unitLabel));
    var out = el("output", "vcw-volume", nf.format(start));
    out.setAttribute("aria-live", "off");
    var slider = el("input", "vcw-slider");
    slider.type = "range"; slider.min = "0"; slider.max = String(STEPS); slider.step = "1";
    slider.value = String(volumeToSlider(start));
    label.appendChild(out);
    head.appendChild(label);
    head.appendChild(slider);
    root.appendChild(head);

    var summary = el("p", "vcw-summary");
    summary.setAttribute("aria-live", "polite");
    root.appendChild(summary);

    var list = el("ul", "vcw-list");
    var rows = {};
    vendors.forEach(function (v) {
      var li = el("li", "vcw-row");
      var top = el("div", "vcw-rowtop");
      top.appendChild(el("span", "vcw-name", v.name));
      var cost = el("span", "vcw-cost", "");
      top.appendChild(cost);
      var track = el("div", "vcw-track");
      var bar = el("div", "vcw-bar");
      track.appendChild(bar);
      var meta = el("div", "vcw-meta");
      var plan = el("span", "vcw-plan", "");
      meta.appendChild(plan);
      var srcA = el("a", "", "source, checked " + v.verified);
      srcA.href = v.source_url; srcA.target = "_blank"; srcA.rel = "noopener";
      meta.appendChild(srcA);
      li.appendChild(top); li.appendChild(track); li.appendChild(meta);
      if (v.note) { li.appendChild(el("div", "vcw-note", v.note)); }
      list.appendChild(li);
      rows[v.id] = { li: li, cost: cost, bar: bar, plan: plan, vendor: v };
    });
    root.appendChild(list);

    if (skipped.length) {
      var sk = el("p", "vcw-skipped");
      sk.textContent = "Not shown because the vendor publishes no per-request figure we could verify: " +
        skipped.map(function (v) { return v.name; }).join(", ") + ".";
      root.appendChild(sk);
    }
    root.appendChild(el("p", "vcw-foot", "List prices in USD, billed monthly, before any annual discount. " +
      "Bars are ordered by cost, lowest first; ties keep alphabetical order."));

    var card = null, cardText = null, cardLink = null;
    var affUrl = root.getAttribute("data-affiliate-url");
    var affVendor = root.getAttribute("data-affiliate-vendor");
    if (affUrl && affVendor) {
      card = el("aside", "affiliate-card");
      card.appendChild(el("span", "affiliate-card-label", "Affiliate link"));
      cardText = el("p", "affiliate-card-text", "");
      card.appendChild(cardText);
      cardLink = el("a", "btn", "See ScraperAPI plans");
      cardLink.href = affUrl; cardLink.target = "_blank"; cardLink.rel = "sponsored nofollow noopener";
      cardLink.setAttribute("data-goatcounter-click", "affiliate/scraperapi-widget");
      cardLink.setAttribute("data-goatcounter-title", "ScraperAPI affiliate card (widget)");
      card.appendChild(cardLink);
      card.appendChild(el("p", "affiliate-card-fine",
        "We may earn a commission if you sign up through this link, at no cost to you. It does not change the order above."));
      root.appendChild(card);
    }

    function update() {
      var vol = sliderToVolume(Number(slider.value));
      out.textContent = nf.format(vol);
      var results = Object.keys(rows).map(function (id) {
        return { id: id, r: costFor(rows[id].vendor, vol) };
      });
      var max = 0;
      results.forEach(function (x) { if (x.r && x.r.cost > max) { max = x.r.cost; } });
      results.sort(function (a, b) {
        if (!a.r && !b.r) { return rows[a.id].vendor.name.localeCompare(rows[b.id].vendor.name); }
        if (!a.r) { return 1; }
        if (!b.r) { return -1; }
        return a.r.cost - b.r.cost || rows[a.id].vendor.name.localeCompare(rows[b.id].vendor.name);
      });
      results.forEach(function (x, i) {
        var row = rows[x.id];
        row.li.style.order = String(i);
        if (x.r) {
          row.cost.textContent = x.r.cost === 0 ? "$0" : usd(x.r.cost) + "/mo";
          row.plan.textContent = x.r.label;
          row.bar.style.transform = "scaleX(" + (max ? Math.max(0.02, x.r.cost / max) : 0.02) + ")";
          row.bar.classList.remove("vcw-none");
        } else {
          row.cost.textContent = "No published plan";
          row.plan.textContent = "Needs a custom quote above the published tiers";
          row.bar.style.transform = "scaleX(1)";
          row.bar.classList.add("vcw-none");
        }
      });
      var first = results.filter(function (x) { return x.r; })[0];
      summary.textContent = first
        ? "At " + nf.format(vol) + " " + noun + " a month, the lowest published list price is " +
          rows[first.id].vendor.name + " at " + (first.r.cost === 0 ? "$0 (" : usd(first.r.cost) + "/month (") + first.r.label + ")."
        : "No vendor in this list publishes a plan that covers " + nf.format(vol) + " " + noun + " a month.";
      if (card) {
        var av = rows[affVendor], ar = av && costFor(av.vendor, vol);
        card.hidden = !ar;
        if (ar) {
          cardText.textContent = "For " + nf.format(vol) + " " + noun + " a month, ScraperAPI's published list price is " +
            (ar.cost === 0 ? "$0 (" : usd(ar.cost) + " a month (") + ar.label + ").";
        }
      }
    }
    slider.addEventListener("input", update);
    update();
  }

  document.querySelectorAll(".vcw").forEach(mount);
}());
