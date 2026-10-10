// Sidebar filter, mobile menu toggle, keep the current page in view.
(function () {
  var side = document.querySelector(".side");
  var input = document.querySelector(".filter");
  var menu = document.querySelector(".menu");
  if (input && side) {
    input.addEventListener("input", function () {
      var q = input.value.trim().toLowerCase();
      if (q) document.body.classList.add("nav-open");
      side.querySelectorAll(".group").forEach(function (g) {
        var any = false;
        g.querySelectorAll("a").forEach(function (a) {
          var hit = !q || a.textContent.toLowerCase().indexOf(q) >= 0;
          a.hidden = !hit;
          any = any || hit;
        });
        g.hidden = !any;
      });
    });
    input.addEventListener("keydown", function (e) {
      if (e.key !== "Enter") return;
      var first = side.querySelector("a:not([hidden])");
      if (first) location.href = first.href;
    });
  }
  if (menu) {
    menu.addEventListener("click", function () {
      var open = document.body.classList.toggle("nav-open");
      menu.setAttribute("aria-expanded", String(open));
    });
  }
  var cur = side && side.querySelector('[aria-current="page"]');
  if (cur && cur.scrollIntoView) cur.scrollIntoView({ block: "nearest" });
})();
