(function () {
  "use strict";

  function ready(fn) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn);
    } else {
      fn();
    }
  }

  ready(function () {
    var dialog = document.getElementById("portal-password-dialog");
    var form = document.getElementById("portal-password-form");
    if (!dialog || !form) return;

    var steps = dialog.querySelectorAll("[data-password-step]");
    var initial = parseInt(form.getAttribute("data-initial-step") || "1", 10);

    function showStep(n) {
      steps.forEach(function (el) {
        var step = parseInt(el.getAttribute("data-password-step"), 10);
        el.hidden = step !== n;
      });
      var active = dialog.querySelector('[data-password-step="' + n + '"]');
      if (active) {
        var focusable = active.querySelector("input, button, select, textarea");
        if (focusable) focusable.focus();
      }
    }

    function openDialog(step) {
      showStep(step || 1);
      if (typeof dialog.showModal === "function") {
        dialog.showModal();
      } else {
        dialog.setAttribute("open", "");
      }
    }

    function closeDialog() {
      if (dialog.open && typeof dialog.close === "function") {
        dialog.close();
      } else {
        dialog.removeAttribute("open");
      }
      showStep(1);
      form.reset();
    }

    document.querySelectorAll("[data-portal-password-open]").forEach(function (btn) {
      btn.addEventListener("click", function (e) {
        e.preventDefault();
        openDialog(1);
      });
    });

    dialog.querySelectorAll("[data-portal-password-close]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        closeDialog();
      });
    });

    dialog.querySelectorAll("[data-password-next]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var next = parseInt(btn.getAttribute("data-password-next"), 10);
        if (next === 3) {
          var oldInput = form.querySelector('[name="old_password"]');
          if (oldInput && !oldInput.value.trim()) {
            oldInput.focus();
            return;
          }
        }
        showStep(next);
      });
    });

    dialog.querySelectorAll("[data-password-back]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        showStep(parseInt(btn.getAttribute("data-password-back"), 10));
      });
    });

    /* No cerrar con clic fuera del cuadro ni con Escape; solo Atrás / Volver */
    dialog.addEventListener("cancel", function (e) {
      e.preventDefault();
    });

    if (dialog.hasAttribute("data-open-on-load") || initial > 1) {
      openDialog(initial);
    }
  });
})();
