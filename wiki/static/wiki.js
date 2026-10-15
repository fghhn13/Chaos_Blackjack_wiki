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
