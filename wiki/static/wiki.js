// Site search, mobile menu toggle, keep the current page in view.
(function () {
  var side = document.querySelector(".side");
  var input = document.querySelector(".filter");
  var box = document.getElementById("search-results");
  var menu = document.querySelector(".menu");

  // --- search: search.js (window.WIKI_SEARCH) is loaded on first use -------------
  var data = null, loading = false, hits = [], sel = -1;

  function load() {
    if (data || loading) return;
    if (window.WIKI_SEARCH) { prep(); return; }
    loading = true;
    var s = document.createElement("script");
    s.src = input.dataset.index || "search.js";
    s.onload = function () { loading = false; prep(); run(); };
    s.onerror = function () { loading = false; };
    document.head.appendChild(s);
  }

  function prep() {
    data = (window.WIKI_SEARCH || []).map(function (e) {
      return { e: e, t: (e.t || "").toLowerCase(), w: (e.w || "").toLowerCase(), x: (e.x || "").toLowerCase() };
    });
  }

  function esc(s) {
    return s.replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; });
  }

  function mark(text, terms) {
    var out = esc(text);
    terms.forEach(function (term) {
      var re = new RegExp("(" + esc(term).replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + ")", "ig");
      out = out.replace(re, "<mark>$1</mark>");
    });
    return out;
  }

  function snippet(d, terms) {
    var text = d.e.x || "", low = d.x, at = -1;
    terms.some(function (term) { at = low.indexOf(term); return at >= 0; });
    if (at < 0 || d.t.indexOf(terms[0]) >= 0 && d.e.s) return d.e.s || text.slice(0, 120);
    var start = Math.max(0, at - 40);
    return (start ? "…" : "") + text.slice(start, at + 90) + "…";
  }

  function run() {
    var q = input.value.trim().toLowerCase();
    if (!q) { hide(); return; }
    if (!data) { load(); return; }
    var terms = q.split(/\s+/).filter(Boolean);
    hits = [];
    data.forEach(function (d) {
      var score = 0;
      for (var i = 0; i < terms.length; i++) {
        var term = terms[i], s = 0;
        if (d.t.indexOf(term) >= 0) s += d.t.indexOf(term) === 0 ? 16 : 10;
        if (d.w.indexOf(term) >= 0) s += 6;
        if (d.x.indexOf(term) >= 0) s += 1;
        if (!s) return;
        score += s;
      }
      hits.push({ d: d, score: score });
    });
    hits.sort(function (a, b) { return b.score - a.score; });
    hits = hits.slice(0, 12);
    sel = hits.length ? 0 : -1;
    if (!hits.length) {
      box.innerHTML = '<p class="none">' + esc(input.dataset.empty || "") + "</p>";
    } else {
      box.innerHTML = hits.map(function (h, i) {
        var e = h.d.e;
        var icon = e.i ? '<img src="' + esc(e.i) + '" alt="">' : '<span class="dot"></span>';
        return '<a class="hit" role="option" id="hit-' + i + '" href="' + esc(e.u) + '"' + (i === sel ? ' aria-selected="true"' : "") + ">" +
          icon + '<span><strong>' + mark(e.t, terms) + "</strong><em>" + esc(e.k || "") + "</em>" +
          "<small>" + mark(snippet(h.d, terms), terms) + "</small></span></a>";
      }).join("");
    }
    box.hidden = false;
    input.setAttribute("aria-expanded", "true");
  }

  function hide() {
    if (!box) return;
    box.hidden = true;
    input.setAttribute("aria-expanded", "false");
  }

  function move(step) {
    if (!hits.length) return;
    sel = (sel + step + hits.length) % hits.length;
    box.querySelectorAll(".hit").forEach(function (a, i) {
      if (i === sel) { a.setAttribute("aria-selected", "true"); a.scrollIntoView({ block: "nearest" }); }
      else a.removeAttribute("aria-selected");
    });
  }

  if (input && box) {
    input.addEventListener("focus", function () { load(); if (input.value.trim()) run(); });
    input.addEventListener("input", run);
    input.addEventListener("keydown", function (e) {
      if (e.key === "ArrowDown") { e.preventDefault(); move(1); }
      else if (e.key === "ArrowUp") { e.preventDefault(); move(-1); }
      else if (e.key === "Enter") {
        if (sel >= 0 && hits[sel]) location.href = hits[sel].d.e.u;
      } else if (e.key === "Escape") { hide(); input.blur(); }
    });
    document.addEventListener("click", function (e) {
      if (!e.target.closest || !e.target.closest(".search-wrap")) hide();
    });
    document.addEventListener("keydown", function (e) {
      var tag = (e.target.tagName || "").toLowerCase();
      var typing = tag === "input" || tag === "textarea" || e.target.isContentEditable;
      if ((e.key === "/" && !typing) || (e.key.toLowerCase() === "k" && (e.ctrlKey || e.metaKey))) {
        e.preventDefault();
        input.focus();
        input.select();
      }
    });
  }

  // --- catalog filters: table sections, kind / style / phase, sort, compact view --------
  function store(key, value) {
    try { if (value === undefined) return localStorage.getItem(key); localStorage.setItem(key, value); } catch (e) {}
    return null;
  }

  document.querySelectorAll(".catalog-view").forEach(function (view) {
    var bar = view.querySelector(".filters");
    if (!bar) return;
    bar.hidden = false;
    var cards = Array.prototype.slice.call(view.querySelectorAll(".card"));
    cards.forEach(function (c, i) { c.dataset.i = i; });
    var sortSel = bar.querySelector("[data-sort]");
    var viewBtn = bar.querySelector("[data-view]");
    var count = bar.querySelector(".fcount");

    function chosen(dim) {
      return Array.prototype.map.call(bar.querySelectorAll('[data-dim="' + dim + '"][aria-pressed="true"]'),
        function (b) { return b.dataset.val; });
    }

    function apply() {
      var pools = chosen("pool"), kinds = chosen("kind"), styles = chosen("style"), phases = chosen("phase");
      var shown = {}, total = {};
      cards.forEach(function (c) {
        total[c.getAttribute("href")] = 1;
        var sec = c.closest(".pool");
        var inPool = !pools.length || !sec || pools.indexOf(sec.dataset.pool) >= 0;
        var ok = (!kinds.length || kinds.indexOf(c.dataset.kind) >= 0) &&
          (!styles.length || styles.indexOf(c.dataset.style) >= 0) &&
          (!phases.length || (c.dataset.phase || "").split(" ").some(function (p) { return phases.indexOf(p) >= 0; }));
        c.hidden = !(ok && inPool);
        if (!c.hidden) shown[c.getAttribute("href")] = 1;
      });
      // A kind block or table section with nothing left to show disappears with its heading.
      view.querySelectorAll(".kind, .pool").forEach(function (box) {
        box.hidden = !box.querySelector(".card:not([hidden])");
      });
      var n = Object.keys(shown).length, all = Object.keys(total).length;
      count.textContent = n === all ? "" : (count.dataset.template || "").replace("{n}", n).replace("{total}", all);
    }

    function sort() {
      var how = sortSel ? sortSel.value : "";
      view.querySelectorAll(".cards").forEach(function (box) {
        var list = Array.prototype.slice.call(box.children);
        list.sort(function (a, b) {
          if (how === "name") return a.dataset.name.localeCompare(b.dataset.name);
          if (how === "price" || how === "-price") {
            var pa = a.dataset.price === "" ? null : +a.dataset.price, pb = b.dataset.price === "" ? null : +b.dataset.price;
            if (pa === null || pb === null) return (pa === null) - (pb === null);
            if (pa !== pb) return how === "price" ? pa - pb : pb - pa;
          }
          return a.dataset.i - b.dataset.i;
        });
        list.forEach(function (c) { box.appendChild(c); });
      });
    }

    function setView(list) {
      view.classList.toggle("list", list);
      viewBtn.setAttribute("aria-pressed", String(list));
    }

    bar.addEventListener("click", function (e) {
      var b = e.target.closest("button");
      if (!b) return;
      if (b.dataset.dim) b.setAttribute("aria-pressed", String(b.getAttribute("aria-pressed") !== "true"));
      else if (b.hasAttribute("data-toggle")) {
        b.setAttribute("aria-expanded", String(bar.classList.toggle("open")));
        return;
      } else if (b.hasAttribute("data-view")) { setView(!view.classList.contains("list")); store("wiki-view", view.classList.contains("list") ? "list" : "cards"); return; }
      else if (b.hasAttribute("data-clear")) {
        bar.querySelectorAll("[data-dim]").forEach(function (x) { x.setAttribute("aria-pressed", "false"); });
        if (sortSel) { sortSel.value = ""; sort(); }
      }
      apply();
    });
    if (sortSel) sortSel.addEventListener("change", sort);
    setView(store("wiki-view") === "list");
    apply();
  });

  // --- colour theme: system -> dark -> light ------------------------------------------
  var themeBtn = document.querySelector(".theme");
  if (themeBtn) {
    var modes = ["", "dark", "light"], labels = (themeBtn.dataset.labels || "").split("|");
    var showTheme = function () {
      var i = Math.max(0, modes.indexOf(document.documentElement.dataset.theme || ""));
      themeBtn.title = labels[i] || "";
      themeBtn.setAttribute("aria-label", labels[i] || "");
    };
    themeBtn.addEventListener("click", function () {
      var i = (Math.max(0, modes.indexOf(document.documentElement.dataset.theme || "")) + 1) % modes.length;
      if (modes[i]) document.documentElement.dataset.theme = modes[i];
      else delete document.documentElement.dataset.theme;
      store("wiki-theme", modes[i]);
      showTheme();
    });
    showTheme();
  }

  // --- mobile menu ------------------------------------------------------------------
  if (menu) {
    menu.addEventListener("click", function () {
      var open = document.body.classList.toggle("nav-open");
      menu.setAttribute("aria-expanded", String(open));
    });
  }
  var cur = side && side.querySelector('[aria-current="page"], [aria-current=page]');
  if (cur && cur.scrollIntoView) cur.scrollIntoView({ block: "nearest" });
})();
