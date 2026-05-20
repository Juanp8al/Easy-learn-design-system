(function () {
  var home = document.querySelector(".el-home");
  if (!home) return;

  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var STAGGER_MS = 130;

  function revealEl(el) {
    if (el) el.classList.add("is-visible");
  }

  function resetEl(el) {
    if (!el) return;
    el.classList.remove("is-visible");
    void el.offsetWidth;
  }

  function revealAll(nodes, force) {
    var list = Array.prototype.slice.call(nodes);
    list.forEach(function (el, i) {
      if (reduced) {
        revealEl(el);
        return;
      }
      var delayAttr = el.getAttribute("data-reveal-delay");
      var delay = (delayAttr !== null && delayAttr !== "" ? parseInt(delayAttr, 10) : i) * STAGGER_MS;
      if (force) {
        resetEl(el);
      }
      window.setTimeout(function () {
        revealEl(el);
      }, delay + (force ? 80 : 0));
    });
  }

  function revealInSection(section, force) {
    if (!section) return;
    revealAll(section.querySelectorAll(".el-reveal"), force);
  }

  /* Hero al cargar */
  var heroItems = home.querySelectorAll(".el-home-hero .el-reveal");
  if (reduced) {
    heroItems.forEach(revealEl);
  } else {
    window.setTimeout(function () {
      revealAll(heroItems, false);
    }, 120);
  }

  /* Secciones al entrar en viewport */
  var sections = home.querySelectorAll("[data-reveal-section]");
  if (sections.length && "IntersectionObserver" in window && !reduced) {
    var seen = new WeakSet();
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          var section = entry.target;
          if (seen.has(section)) return;
          seen.add(section);
          revealInSection(section, false);
        });
      },
      { root: null, rootMargin: "0px 0px -5% 0px", threshold: 0.08 }
    );
    sections.forEach(function (section) {
      io.observe(section);
    });
  } else {
    sections.forEach(function (section) {
      revealInSection(section, false);
    });
  }

  /* «Ver cómo funciona» → scroll + animación en #flujo */
  home.querySelectorAll('a[href="#flujo"]').forEach(function (link) {
    link.addEventListener("click", function (e) {
      var target = document.getElementById("flujo");
      if (!target) return;
      e.preventDefault();
      var topbar = document.querySelector(".sitio-topbar");
      var offset = topbar ? topbar.offsetHeight + 12 : 0;
      var y = target.getBoundingClientRect().top + window.scrollY - offset;

      if (reduced) {
        window.scrollTo(0, y);
        revealInSection(target, true);
        return;
      }

      window.scrollTo({ top: y, behavior: "smooth" });
      window.setTimeout(function () {
        revealInSection(target, true);
      }, 580);
    });
  });

  if (window.location.hash) {
    var hashEl = document.querySelector(window.location.hash);
    if (hashEl && hashEl.closest(".el-home")) {
      window.setTimeout(function () {
        revealInSection(hashEl, !reduced);
      }, reduced ? 0 : 400);
    }
  }
})();
