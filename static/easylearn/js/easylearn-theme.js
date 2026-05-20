(function () {
  var STORAGE_KEY = "easylearn-theme";

  function getStored() {
    try {
      return localStorage.getItem(STORAGE_KEY);
    } catch (e) {
      return null;
    }
  }

  function resolveTheme() {
    var stored = getStored();
    if (stored === "dark" || stored === "light") return stored;
    return "light";
  }

  function syncToggles(theme) {
    var isDark = theme === "dark";

    document.querySelectorAll("[data-theme-toggle]").forEach(function (btn) {
      btn.classList.toggle("is-dark", isDark);
      btn.setAttribute("aria-pressed", isDark ? "true" : "false");
      btn.setAttribute(
        "aria-label",
        isDark ? "Activar modo claro" : "Activar modo oscuro"
      );
      btn.setAttribute("title", isDark ? "Modo oscuro activo" : "Modo claro activo");

      var icon = btn.querySelector("[data-theme-icon]");
      if (icon) {
        icon.className =
          "fa-solid " +
          (isDark ? "fa-moon" : "fa-sun") +
          " el-theme-btn__icon";
      }
    });

    document.querySelectorAll("[data-theme-value]").forEach(function (btn) {
      var active = btn.getAttribute("data-theme-value") === theme;
      btn.classList.toggle("is-active", active);
      btn.setAttribute("aria-pressed", active ? "true" : "false");
    });
  }

  function applyTheme(theme) {
    var root = document.documentElement;
    root.setAttribute("data-theme", theme);
    root.style.colorScheme = theme === "dark" ? "dark" : "light";
    syncToggles(theme);
  }

  function setTheme(theme) {
    if (theme !== "light" && theme !== "dark") return;
    try {
      localStorage.setItem(STORAGE_KEY, theme);
    } catch (e) {
      /* ignore */
    }
    applyTheme(theme);
  }

  function toggleTheme() {
    setTheme(resolveTheme() === "dark" ? "light" : "dark");
  }

  function init() {
    applyTheme(resolveTheme());

    document.addEventListener("click", function (e) {
      if (e.target.closest("[data-theme-toggle]")) {
        e.preventDefault();
        toggleTheme();
        return;
      }

      var btn = e.target.closest("[data-theme-value]");
      if (!btn) return;
      e.preventDefault();
      setTheme(btn.getAttribute("data-theme-value"));
    });
  }

  window.EasyLearnTheme = {
    get: resolveTheme,
    set: setTheme,
    toggle: toggleTheme,
    apply: applyTheme,
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
