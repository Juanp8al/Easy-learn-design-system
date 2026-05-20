(function () {
  var MIN_MS = 650;
  var overlay;
  var labelEl;

  function qs(sel, root) {
    return (root || document).querySelector(sel);
  }

  function qsa(sel, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(sel));
  }

  function show(kind) {
    if (!overlay) return;
    overlay.removeAttribute("hidden");
    overlay.setAttribute("aria-hidden", "false");
    document.documentElement.classList.add("el-form-loader-active");
    document.body.classList.add("el-form-loader-active");
    qsa("[data-el-loader-panel]").forEach(function (panel) {
      var match = panel.getAttribute("data-el-loader-panel") === kind;
      panel.hidden = !match;
    });
    if (labelEl) {
      labelEl.textContent =
        kind === "book"
          ? "Cargando…"
          : kind === "typewriter"
            ? "Publicando…"
            : "Procesando…";
    }
  }

  function hide() {
    if (!overlay) return;
    overlay.setAttribute("hidden", "");
    overlay.setAttribute("aria-hidden", "true");
    document.documentElement.classList.remove("el-form-loader-active");
    document.body.classList.remove("el-form-loader-active");
  }

  function init() {
    overlay = document.getElementById("el-form-loader-overlay");
    if (!overlay) return;
    labelEl = document.getElementById("el-form-loader-overlay-label");
    window.addEventListener("pageshow", hide);
  }

  function resolveLoader(form) {
    if (form.getAttribute("data-el-loader-ignore") === "true") return null;
    var explicit = form.getAttribute("data-el-loader");
    if (explicit === "book" || explicit === "server" || explicit === "typewriter") {
      return explicit;
    }
    if (document.body.classList.contains("easylearn-admin-loader")) {
      var method = (form.getAttribute("method") || "get").toLowerCase();
      if (method !== "post") return null;
      if (form.closest("#header") || form.closest(".skip-loader")) return null;
      return "server";
    }
    return null;
  }

  document.addEventListener(
    "submit",
    function (e) {
      var form = e.target;
      if (!form || form.nodeName !== "FORM") return;
      var loader = resolveLoader(form);
      if (!loader) return;
      if (typeof form.checkValidity === "function" && !form.checkValidity()) return;

      var draftBtn = e.submitter && e.submitter.getAttribute("name") === "save_draft";
      if (draftBtn && form.getAttribute("data-el-loader-draft") === "skip") return;

      e.preventDefault();
      show(loader);
      var t0 = Date.now();
      window.setTimeout(function () {
        var elapsed = Date.now() - t0;
        var wait = Math.max(0, MIN_MS - elapsed);
        window.setTimeout(function () {
          if (typeof HTMLFormElement === "undefined" || !HTMLFormElement.prototype.submit) {
            hide();
            return;
          }
          try {
            HTMLFormElement.prototype.submit.call(form);
          } catch (err) {
            hide();
          }
        }, wait);
      }, 0);
    },
    true
  );

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
