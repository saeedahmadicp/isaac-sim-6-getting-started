(function () {
  "use strict";
  var KEY = "isaacsim61-done";
  function load() { try { return JSON.parse(localStorage.getItem(KEY) || "{}"); } catch (e) { return {}; } }
  function save(d) { try { localStorage.setItem(KEY, JSON.stringify(d)); } catch (e) { /* private mode */ } }

  // ---- lesson progress -------------------------------------------------------------------
  var LESSONS = Array.prototype.map.call(document.querySelectorAll(".tick"), function (t) { return t.dataset.slug; });
  function paint() {
    var d = load(), n = 0;
    document.querySelectorAll(".tick").forEach(function (t) {
      var ok = !!d[t.dataset.slug]; t.classList.toggle("ok", ok); if (ok) n++;
    });
    var bar = document.getElementById("pbar"), txt = document.getElementById("ptext");
    if (bar) bar.style.width = (LESSONS.length ? 100 * n / LESSONS.length : 0) + "%";
    if (txt) txt.textContent = n + " / " + LESSONS.length + " lessons";
    document.querySelectorAll(".done input").forEach(function (c) { c.checked = !!d[c.dataset.slug]; });
  }
  document.querySelectorAll(".done input").forEach(function (c) {
    c.addEventListener("change", function () { var d = load(); d[c.dataset.slug] = c.checked; save(d); paint(); });
  });
  paint();

  // ---- copy buttons on code blocks ---------------------------------------------------------
  document.querySelectorAll("article pre").forEach(function (pre) {
    if (pre.closest(".linenodiv")) return;
    var host = pre.closest(".hltable") || pre;
    if (host.querySelector(":scope > .copy")) return;
    var b = document.createElement("button"); b.className = "copy"; b.type = "button"; b.textContent = "copy";
    b.addEventListener("click", function () {
      var code = (pre.closest(".hltable") ? pre.closest(".hltable").querySelector("td.code pre") : pre).innerText;
      (navigator.clipboard ? navigator.clipboard.writeText(code) : Promise.reject()).then(function () {
        b.textContent = "copied"; setTimeout(function () { b.textContent = "copy"; }, 1200);
      }).catch(function () { b.textContent = "select + Ctrl+C"; });
    });
    host.appendChild(b);
  });

  // ---- "on this page" highlight -------------------------------------------------------------
  var tocLinks = document.querySelectorAll(".toc a");
  if (tocLinks.length && "IntersectionObserver" in window) {
    var map = {}; tocLinks.forEach(function (a) { map[a.getAttribute("href").slice(1)] = a; });
    var obs = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (e.isIntersecting && map[e.target.id]) {
          tocLinks.forEach(function (a) { a.classList.remove("on"); }); map[e.target.id].classList.add("on");
        }
      });
    }, { rootMargin: "0px 0px -75% 0px" });
    document.querySelectorAll("article h2[id], article h3[id]").forEach(function (h) { obs.observe(h); });
  }

  // ---- search -------------------------------------------------------------------------------
  var q = document.getElementById("q"), box = document.getElementById("results"), index = null, sel = -1;
  function esc(s) { return s.replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function getIndex(cb) {
    if (index) return cb(index);
    fetch("static/search-index.json").then(function (r) { return r.json(); })
      .then(function (j) { index = j.pages; cb(index); }).catch(function () { index = []; cb(index); });
  }
  function run() {
    var term = q.value.trim().toLowerCase();
    if (term.length < 2) { box.style.display = "none"; return; }
    getIndex(function (pages) {
      var words = term.split(/\s+/), hits = [];
      pages.forEach(function (p) {
        var t = p.text.toLowerCase(), title = p.title.toLowerCase(), score = 0, at = -1;
        for (var i = 0; i < words.length; i++) {
          var w = words[i], k = t.indexOf(w);
          if (k < 0 && title.indexOf(w) < 0) { score = 0; break; }
          score += (title.indexOf(w) >= 0 ? 10 : 0) + (t.split(w).length - 1);
          if (at < 0) at = k;
        }
        if (score) hits.push({ p: p, s: score, at: at });
      });
      hits.sort(function (a, b) { return b.s - a.s; });
      sel = -1;
      box.innerHTML = hits.slice(0, 8).map(function (h) {
        var start = Math.max(0, h.at - 50), snip = h.p.text.slice(start, start + 140);
        var re = new RegExp("(" + words.map(function (w) { return w.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); }).join("|") + ")", "gi");
        return '<a href="' + h.p.slug + '.html">' + esc(h.p.title) + "<small>…" +
          esc(snip).replace(re, "<mark>$1</mark>") + "…</small></a>";
      }).join("") || '<a><small>No results</small></a>';
      box.style.display = "block";
    });
  }
  if (q) {
    q.addEventListener("input", run);
    q.addEventListener("keydown", function (e) {
      var items = box.querySelectorAll("a[href]");
      if (e.key === "ArrowDown" || e.key === "ArrowUp") {
        e.preventDefault(); sel = Math.max(0, Math.min(items.length - 1, sel + (e.key === "ArrowDown" ? 1 : -1)));
        items.forEach(function (a, i) { a.classList.toggle("sel", i === sel); });
      } else if (e.key === "Enter" && items[Math.max(sel, 0)]) { location.href = items[Math.max(sel, 0)].href; }
      else if (e.key === "Escape") { box.style.display = "none"; q.blur(); }
    });
    document.addEventListener("click", function (e) { if (!e.target.closest(".search")) box.style.display = "none"; });
  }
  document.addEventListener("keydown", function (e) {
    if (e.target.matches("input,textarea")) return;
    if (e.key === "/") { e.preventDefault(); q && q.focus(); }
    var pn = { ArrowLeft: ".pn .prev", ArrowRight: ".pn .next" }[e.key];
    if (pn && e.altKey) { var a = document.querySelector(pn); if (a) location.href = a.href; }
  });
  // close the mobile nav after navigating
  document.querySelectorAll(".side a").forEach(function (a) {
    a.addEventListener("click", function () { document.body.classList.remove("nav-open"); });
  });
})();
