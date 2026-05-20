(function () {
  var STORAGE_PREFIX = "easylearn-portal-a11y-";
  var dialog;
  var canvas;

  function getCanvas() {
    return document.querySelector(".canvas-body");
  }

  function loadPrefs() {
    canvas = getCanvas();
    if (!canvas) return;
    try {
      var keys = ["invert", "mono", "contrast-dark", "contrast-light", "sat-low", "sat-high", "links", "headings"];
      keys.forEach(function (k) {
        if (localStorage.getItem(STORAGE_PREFIX + k) === "1") {
          canvas.classList.add("el-a11y-board--" + k);
          var btn = document.querySelector('[data-a11y-toggle="' + k + '"]');
          if (btn) btn.setAttribute("aria-pressed", "true");
        }
      });
      var fs = localStorage.getItem(STORAGE_PREFIX + "font");
      var lh = localStorage.getItem(STORAGE_PREFIX + "lh");
      var tr = localStorage.getItem(STORAGE_PREFIX + "track");
      if (fs) {
        canvas.style.setProperty("--portal-a11y-font-pct", fs + "%");
        var i = document.getElementById("portal-a11y-font");
        if (i) {
          i.value = String(fs).replace(/%/g, "");
          syncSliderLabel("font", fs);
        }
      }
      if (lh) {
        canvas.style.setProperty("--portal-a11y-lh-pct", lh + "%");
        var i2 = document.getElementById("portal-a11y-lh");
        if (i2) {
          i2.value = String(lh).replace(/%/g, "");
          syncSliderLabel("lh", lh);
        }
      }
      if (tr !== null && tr !== "") {
        canvas.style.setProperty("--portal-a11y-track", tr + "px");
        var i3 = document.getElementById("portal-a11y-track");
        if (i3) {
          i3.value = tr;
          syncSliderLabel("track", tr);
        }
      }
    } catch (e) {
      /* ignore */
    }
  }

  function syncSliderLabel(kind, val) {
    var el = document.querySelector("[data-a11y-" + kind + "-val]");
    if (!el) return;
    if (kind === "track") el.textContent = val + "px";
    else el.textContent = val + (String(val).indexOf("%") === -1 ? "%" : "");
  }

  function openDialog() {
    dialog = document.getElementById("portal-accessibility-dialog");
    if (!dialog) return;
    if (typeof dialog.showModal === "function") {
      dialog.showModal();
    } else {
      dialog.setAttribute("open", "");
    }
    document.documentElement.classList.add("portal-a11y-open");
  }

  function closeDialog() {
    if (!dialog) dialog = document.getElementById("portal-accessibility-dialog");
    if (!dialog) return;
    if (typeof dialog.close === "function") {
      dialog.close();
    } else {
      dialog.removeAttribute("open");
    }
    document.documentElement.classList.remove("portal-a11y-open");
  }

  function toggleClass(name, pressed, btn) {
    canvas = getCanvas();
    if (!canvas) return;
    var cls = "el-a11y-board--" + name;
    if (pressed) {
      canvas.classList.add(cls);
      try {
        localStorage.setItem(STORAGE_PREFIX + name, "1");
      } catch (e) {
        /* ignore */
      }
    } else {
      canvas.classList.remove(cls);
      try {
        localStorage.removeItem(STORAGE_PREFIX + name);
      } catch (e) {
        /* ignore */
      }
    }
    btn.setAttribute("aria-pressed", pressed ? "true" : "false");
  }

  function resetAll() {
    canvas = getCanvas();
    if (!canvas) return;
    Array.from(canvas.classList).forEach(function (c) {
      if (c.indexOf("el-a11y-board--") === 0) canvas.classList.remove(c);
    });
    canvas.style.removeProperty("--portal-a11y-font-pct");
    canvas.style.removeProperty("--portal-a11y-lh-pct");
    canvas.style.removeProperty("--portal-a11y-track");
    canvas.style.setProperty("--portal-a11y-font-pct", "100%");
    canvas.style.setProperty("--portal-a11y-lh-pct", "100%");
    canvas.style.setProperty("--portal-a11y-track", "0px");
    document.querySelectorAll("[data-a11y-toggle]").forEach(function (b) {
      b.setAttribute("aria-pressed", "false");
    });
    var f = document.getElementById("portal-a11y-font");
    var l = document.getElementById("portal-a11y-lh");
    var t = document.getElementById("portal-a11y-track");
    if (f) {
      f.value = "100";
      syncSliderLabel("font", "100");
    }
    if (l) {
      l.value = "100";
      syncSliderLabel("lh", "100");
    }
    if (t) {
      t.value = "0";
      syncSliderLabel("track", "0");
    }
    try {
      Object.keys(localStorage).forEach(function (k) {
        if (k.indexOf(STORAGE_PREFIX) === 0) localStorage.removeItem(k);
      });
    } catch (e) {
      /* ignore */
    }
  }

  function init() {
    dialog = document.getElementById("portal-accessibility-dialog");
    if (!dialog) return;

    canvas = getCanvas();
    if (canvas && !canvas.style.getPropertyValue("--portal-a11y-font-pct")) {
      canvas.style.setProperty("--portal-a11y-font-pct", "100%");
      canvas.style.setProperty("--portal-a11y-lh-pct", "100%");
      canvas.style.setProperty("--portal-a11y-track", "0px");
    }

    loadPrefs();

    document.querySelectorAll("[data-portal-a11y-open]").forEach(function (btn) {
      btn.addEventListener("click", function (e) {
        e.preventDefault();
        openDialog();
      });
    });

    document.querySelectorAll("[data-portal-a11y-close]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        closeDialog();
      });
    });

    dialog.addEventListener("click", function (e) {
      if (e.target === dialog) closeDialog();
    });

    dialog.addEventListener("cancel", function () {
      document.documentElement.classList.remove("portal-a11y-open");
    });

    dialog.addEventListener("close", function () {
      document.documentElement.classList.remove("portal-a11y-open");
    });

    document.getElementById("portal-a11y-reset") &&
      document.getElementById("portal-a11y-reset").addEventListener("click", function () {
        resetAll();
      });

    document.querySelectorAll("[data-a11y-toggle]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var name = btn.getAttribute("data-a11y-toggle");
        var pressed = btn.getAttribute("aria-pressed") !== "true";
        toggleClass(name, pressed, btn);
      });
    });

    function bindRange(id, cssVar, storageKey, kind) {
      var input = document.getElementById(id);
      if (!input) return;
      input.addEventListener("input", function () {
        canvas = getCanvas();
        if (!canvas) return;
        var v = input.value;
        if (kind === "track") {
          canvas.style.setProperty(cssVar, v + "px");
          syncSliderLabel("track", v);
          try {
            localStorage.setItem(STORAGE_PREFIX + storageKey, v);
          } catch (e) {
            /* ignore */
          }
        } else {
          canvas.style.setProperty(cssVar, v + "%");
          syncSliderLabel(kind, v);
          try {
            localStorage.setItem(STORAGE_PREFIX + storageKey, v);
          } catch (e) {
            /* ignore */
          }
        }
      });
    }

    bindRange("portal-a11y-font", "--portal-a11y-font-pct", "font", "font");
    bindRange("portal-a11y-lh", "--portal-a11y-lh-pct", "lh", "lh");
    bindRange("portal-a11y-track", "--portal-a11y-track", "track", "track");

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && dialog && dialog.open) closeDialog();
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
