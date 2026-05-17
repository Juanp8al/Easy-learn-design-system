/**
 * EasyLearn shell — navegación por hash entre vistas del boceto (RF-03, RF-04).
 * Las vistas principales se renderizan en el servidor (sin fetch de parciales).
 */
(function () {
  var routes = {
    dashboard: "view-dashboard",
    cursos: "view-cursos",
    curso: "view-curso",
    semana: "view-semana",
    tareas: "view-tareas",
    calificaciones: "view-calificaciones",
    calendario: "view-calendario",
    mensajes: "view-mensajes",
  };

  var titles = {
    dashboard: "EasyLearn · Inicio",
    cursos: "EasyLearn · Mis cursos",
    curso: "EasyLearn · Curso",
    semana: "EasyLearn · Semana",
    tareas: "EasyLearn · Entrega",
    calificaciones: "EasyLearn · Calificaciones",
    calendario: "EasyLearn · Calendario",
    mensajes: "EasyLearn · Mensajes",
  };

  function renderBreadcrumbs(route) {
    var el = document.getElementById("bread-nav");
    if (!el) return;
    function crumb(label, r) {
      if (r) return '<button type="button" data-goto="' + r + '">' + label + "</button>";
      return "<span>" + label + "</span>";
    }

    switch (route) {
      case "dashboard":
        el.innerHTML = crumb("Inicio", null);
        break;
      case "cursos":
        el.innerHTML = crumb("Inicio", "dashboard") + ' <span class="sep">›</span> ' + crumb("Mis cursos", null);
        break;
      case "curso":
        el.innerHTML =
          crumb("Inicio", "dashboard") +
          ' <span class="sep">›</span> ' +
          crumb("Mis cursos", "cursos") +
          ' <span class="sep">›</span> ' +
          crumb("Curso", null);
        break;
      case "semana":
        el.innerHTML =
          crumb("Inicio", "dashboard") +
          ' <span class="sep">›</span> ' +
          crumb("Mis cursos", "cursos") +
          ' <span class="sep">›</span> ' +
          crumb("Curso", "curso") +
          ' <span class="sep">›</span> ' +
          crumb("Semana", null);
        break;
      case "tareas":
        el.innerHTML =
          crumb("Inicio", "dashboard") +
          ' <span class="sep">›</span> ' +
          crumb("Mis cursos", "cursos") +
          ' <span class="sep">›</span> ' +
          crumb("Curso", "curso") +
          ' <span class="sep">›</span> ' +
          crumb("Semana", "semana") +
          ' <span class="sep">›</span> ' +
          "<span>Entrega</span>";
        break;
      case "calificaciones":
        el.innerHTML = crumb("Inicio", "dashboard") + ' <span class="sep">›</span> ' + crumb("Calificaciones", null);
        break;
      case "calendario":
        el.innerHTML = crumb("Inicio", "dashboard") + ' <span class="sep">›</span> ' + crumb("Calendario", null);
        break;
      case "mensajes":
        el.innerHTML = crumb("Inicio", "dashboard") + ' <span class="sep">›</span> ' + crumb("Mensajes", null);
        break;
      default:
        el.innerHTML = "";
    }
  }

  function setVisibleView(selector, targetId) {
    document.querySelectorAll(selector).forEach(function (v) {
      var visible = v.id === targetId;
      v.classList.toggle("is-visible", visible);
      v.setAttribute("aria-hidden", visible ? "false" : "true");
    });

    var target = document.getElementById(targetId);
    if (!target) return;
    target.setAttribute("tabindex", "-1");
    window.setTimeout(function () {
      try {
        target.focus({ preventScroll: true });
      } catch (_) {
        target.focus();
      }
    }, 0);
  }

  function go(route) {
    if (!routes[route]) return;
    var targetId = routes[route];
    setVisibleView(".view", targetId);
    document.querySelectorAll(".sidebar__link[data-route]").forEach(function (link) {
      var r = link.getAttribute("data-route");
      var active = r === route || (r === "cursos" && (route === "curso" || route === "semana"));
      link.classList.toggle("is-active", active);
      if (active) link.setAttribute("aria-current", "page");
      else link.removeAttribute("aria-current");
    });
    renderBreadcrumbs(route);
    document.title = titles[route] || "EasyLearn";
    if (route === "calificaciones") syncGradesActivities();
    try {
      history.replaceState(null, "", "#" + route);
    } catch (_) {}

    if (route === "tareas") {
      window.setTimeout(function () {
        var node = document.getElementById("task-countdown-label");
        if (node) node.textContent = "Calculado al conectar calendario del servidor";
      }, 120);
    }
  }

  function renderDashboardMiniCal() {
    var root = document.getElementById("cal-mayo-2026");
    if (!root || root.childNodes.length) return;
    var weeks = [
      [null, null, null, null, 1, 2, 3],
      [4, 5, 6, 7, 8, 9, 10],
      [11, 12, 13, 14, 15, 16, 17],
      [18, 19, 20, 21, 22, 23, 24],
      [25, 26, 27, 28, 29, 30, 31],
    ];
    var now = new Date();
    var todayInGrid =
      now.getFullYear() === 2026 && now.getMonth() === 4 ? now.getDate() : null;
    weeks.flat().forEach(function (d) {
      var el = document.createElement("div");
      el.className = "mc-day";
      if (d === null) {
        el.classList.add("is-empty");
        el.innerHTML = "&nbsp;";
      } else {
        el.textContent = String(d);
        if (todayInGrid !== null && d === todayInGrid) el.classList.add("is-today");
      }
      root.appendChild(el);
    });
  }

  function getHeaderSearchNeedle() {
    var inp = document.querySelector("#header-search-q");
    return inp ? inp.value.trim().toLowerCase() : "";
  }

  function syncGradesActivities(needleLower) {
    var gradesView = document.getElementById("view-calificaciones");
    if (!gradesView || !gradesView.classList.contains("is-visible")) return;
    if (needleLower === undefined) needleLower = getHeaderSearchNeedle();
    var gTb = gradesView.querySelector("#grades-detail-table tbody");
    if (!gTb) return;
    gTb.querySelectorAll("tr").forEach(function (tr) {
      var d = tr.getAttribute("data-search") || tr.textContent;
      tr.style.display = needleLower === "" || d.toLowerCase().indexOf(needleLower) !== -1 ? "" : "none";
    });
  }

  function runSearch(q) {
    var needle = (q || "").trim().toLowerCase();
    var dashTb = document.querySelector("#dash-activity-table tbody");
    if (dashTb) {
      dashTb.querySelectorAll("tr").forEach(function (tr) {
        var d = tr.getAttribute("data-search") || tr.textContent;
        tr.style.display = needle === "" || d.toLowerCase().indexOf(needle) !== -1 ? "" : "none";
      });
    }
    syncGradesActivities(needle);
    var catInput = document.getElementById("cat-search-course");
    if (catInput && document.getElementById("view-cursos") && document.getElementById("view-cursos").classList.contains("is-visible")) {
      filterCourseCatalog(needle);
    }
  }

  function filterCourseCatalog(needle) {
    var root = document.getElementById("course-catalog-root");
    if (!root) return;
    var cards = root.querySelectorAll(".course-catalog-card");
    cards.forEach(function (card) {
      var t = (card.getAttribute("data-catalog-scope") || "") + " " + card.textContent;
      card.style.display = needle === "" || t.toLowerCase().indexOf(needle) !== -1 ? "" : "none";
    });
    var rows = root.querySelectorAll(".course-summary-table tbody tr");
    rows.forEach(function (tr) {
      tr.style.display = needle === "" || tr.textContent.toLowerCase().indexOf(needle) !== -1 ? "" : "none";
    });
  }

  function initApp() {
    var isSearchPage = document.body.getAttribute("data-easylearn-page") === "search";
    var rolePage = document.body.getAttribute("data-easylearn-page");

    if (rolePage === "admin" || rolePage === "teacher") {
      var shell = document.querySelector(".app-shell");
      var collapseBtn = document.querySelector(".sidebar__collapse");
      if (shell && collapseBtn) {
        collapseBtn.addEventListener("click", function () {
          var collapsed = shell.classList.toggle("is-sidebar-collapsed");
          collapseBtn.setAttribute("aria-expanded", collapsed ? "false" : "true");
          collapseBtn.setAttribute("aria-label", collapsed ? "Expandir menú lateral" : "Contraer menú lateral");
          collapseBtn.setAttribute("title", collapsed ? "Expandir" : "Contraer");
        });
      }
      var profileRoot = document.querySelector(".header-profile");
      var profileTrigger = document.querySelector(".header-profile__trigger");
      var profileMenu = document.getElementById("header-profile-menu");
      if (profileRoot && profileTrigger && profileMenu) {
        function setProfileMenuOpen(open) {
          profileRoot.classList.toggle("header-profile--open", open);
          profileTrigger.setAttribute("aria-expanded", open ? "true" : "false");
          profileMenu.hidden = !open;
        }
        profileTrigger.addEventListener("click", function (e) {
          e.stopPropagation();
          setProfileMenuOpen(!profileRoot.classList.contains("header-profile--open"));
        });
        document.addEventListener("click", function (e) {
          if (!profileRoot.contains(e.target)) setProfileMenuOpen(false);
        });
        document.addEventListener("keydown", function (e) {
          if (e.key !== "Escape") return;
          if (!profileRoot.classList.contains("header-profile--open")) return;
          setProfileMenuOpen(false);
          profileTrigger.focus();
        });
      }

      function filterRoleDashboardRows(needleRaw) {
        var n = needleRaw === undefined || needleRaw === null ? "" : String(needleRaw).trim().toLowerCase();
        document.querySelectorAll(".canvas-body table tbody tr").forEach(function (tr) {
          if (tr.hasAttribute("data-search-skip")) {
            tr.style.display = "";
            return;
          }
          var firstTd = tr.querySelector("td");
          if (firstTd && firstTd.getAttribute("colspan")) {
            tr.style.display = "";
            return;
          }
          var ds = tr.getAttribute("data-search");
          var t = ds != null && ds !== "" ? ds : tr.textContent;
          tr.style.display = n === "" || t.toLowerCase().indexOf(n) !== -1 ? "" : "none";
        });
      }

      var qInputRole = document.querySelector("#header-search-q");
      if (qInputRole) {
        qInputRole.addEventListener("input", function () {
          filterRoleDashboardRows(qInputRole.value);
        });
        filterRoleDashboardRows(qInputRole.value);
      }

      if (rolePage === "teacher") {
        var teacherRoutes = {
          dashboard: "view-teacher-dashboard",
          cursos: "view-teacher-cursos",
          entregas: "view-teacher-entregas",
          foros: "view-teacher-foros",
          "historial-calificaciones": "view-teacher-rendimiento",
          rendimiento: "view-teacher-rendimiento",
        };
        var teacherTitles = {
          dashboard: "EasyLearn · Panel docente",
          cursos: "EasyLearn · Mis cursos",
          entregas: "EasyLearn · Entregas",
          foros: "EasyLearn · Foros y avisos",
          "historial-calificaciones": "EasyLearn · Historial de calificaciones",
          rendimiento: "EasyLearn · Historial de calificaciones",
        };

        function teacherCanonicalRoute(route) {
          return route === "rendimiento" ? "historial-calificaciones" : route;
        }

        function teacherCrumbLabel(route) {
          if (route === "cursos") return "Mis cursos";
          if (route === "entregas") return "Entregas";
          if (route === "foros") return "Foros y avisos";
          if (route === "historial-calificaciones" || route === "rendimiento") {
            return "Historial de calificaciones";
          }
          return route;
        }

        function renderTeacherBreadcrumbs(route) {
          var el = document.getElementById("bread-nav");
          if (!el) return;
          function crumb(label, r) {
            if (r) return '<button type="button" data-goto="' + r + '">' + label + "</button>";
            return "<span>" + label + "</span>";
          }
          if (route === "dashboard") {
            el.innerHTML = crumb("Inicio", null);
            return;
          }
          el.innerHTML =
            crumb("Inicio", "dashboard") +
            ' <span class="sep">›</span> ' +
            crumb(teacherCrumbLabel(route), null);
        }

        function goTeacher(route) {
          if (!teacherRoutes[route]) route = "dashboard";
          var targetId = teacherRoutes[route];
          var canonical = teacherCanonicalRoute(route);
          setVisibleView(".canvas-body .view", targetId);
          document.querySelectorAll(".sidebar__link[data-route]").forEach(function (link) {
            var r = link.getAttribute("data-route");
            var active = r === canonical;
            link.classList.toggle("is-active", active);
            if (active) link.setAttribute("aria-current", "page");
            else link.removeAttribute("aria-current");
          });
          renderTeacherBreadcrumbs(route);
          document.title = teacherTitles[route] || teacherTitles.dashboard;
          try {
            history.replaceState(null, "", "#" + canonical);
          } catch (_) {}
        }

        var canvasTeacher = document.querySelector(".canvas-body");
        if (canvasTeacher) {
          canvasTeacher.addEventListener("click", function (e) {
            var tgt = e.target.closest("[data-goto]");
            if (!tgt) return;
            var r = tgt.getAttribute("data-goto");
            if (teacherRoutes[r]) {
              e.preventDefault();
              goTeacher(r);
            }
          });
        }

        document.querySelectorAll(".sidebar__link[data-route]").forEach(function (btn) {
          btn.addEventListener("click", function () {
            goTeacher(btn.getAttribute("data-route"));
          });
        });

        window.addEventListener("hashchange", function () {
          if (document.body.getAttribute("data-easylearn-page") !== "teacher") return;
          var h = (location.hash || "").replace(/^#/, "");
          if (h === "rendimiento") h = "historial-calificaciones";
          if (teacherRoutes[h]) goTeacher(h);
        });

        var hInit = (location.hash || "").replace(/^#/, "");
        if (hInit === "rendimiento") hInit = "historial-calificaciones";
        if (teacherRoutes[hInit]) goTeacher(hInit);
        else goTeacher("dashboard");
      }

      return;
    }

    renderDashboardMiniCal();

    var canvas = document.querySelector(".canvas-body");
    if (canvas) {
      canvas.addEventListener("click", function (e) {
        var tgt = e.target.closest("[data-goto]");
        if (!tgt || tgt.closest(".course-tabs")) return;
        var r = tgt.getAttribute("data-goto");
        if (routes[r]) {
          e.preventDefault();
          go(r);
        }
      });
    }

    document.querySelectorAll(".sidebar__link[data-route]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        go(btn.getAttribute("data-route"));
      });
    });

    window.addEventListener("hashchange", function () {
      if (document.body.getAttribute("data-easylearn-page") === "search") return;
      var h = (location.hash || "").replace(/^#/, "");
      if (routes[h]) go(h);
    });

    var shell = document.querySelector(".app-shell");
    var collapseBtn = document.querySelector(".sidebar__collapse");
    if (shell && collapseBtn) {
      collapseBtn.addEventListener("click", function () {
        var collapsed = shell.classList.toggle("is-sidebar-collapsed");
        collapseBtn.setAttribute("aria-expanded", collapsed ? "false" : "true");
        collapseBtn.setAttribute("aria-label", collapsed ? "Expandir menú lateral" : "Contraer menú lateral");
        collapseBtn.setAttribute("title", collapsed ? "Expandir" : "Contraer");
      });
    }

    var profileRoot = document.querySelector(".header-profile");
    var profileTrigger = document.querySelector(".header-profile__trigger");
    var profileMenu = document.getElementById("header-profile-menu");
    if (profileRoot && profileTrigger && profileMenu) {
      function setProfileMenuOpen(open) {
        profileRoot.classList.toggle("header-profile--open", open);
        profileTrigger.setAttribute("aria-expanded", open ? "true" : "false");
        profileMenu.hidden = !open;
      }

      profileTrigger.addEventListener("click", function (e) {
        e.stopPropagation();
        setProfileMenuOpen(!profileRoot.classList.contains("header-profile--open"));
      });

      document.addEventListener("click", function (e) {
        if (!profileRoot.contains(e.target)) setProfileMenuOpen(false);
      });

      document.addEventListener("keydown", function (e) {
        if (e.key !== "Escape") return;
        if (!profileRoot.classList.contains("header-profile--open")) return;
        setProfileMenuOpen(false);
        profileTrigger.focus();
      });
    }

    document.querySelectorAll(".course-tab").forEach(function (tab) {
      tab.addEventListener("click", function (ev) {
        var goRoute = tab.getAttribute("data-goto");
        if (goRoute && routes[goRoute]) {
          ev.preventDefault();
          go(goRoute);
          return;
        }
        if (tab.disabled) return;
        var id = tab.getAttribute("data-coursetab");
        if (!id) return;
        var host = tab.closest("#view-curso");
        if (!host) return;
        host.querySelectorAll(".course-tab").forEach(function (t) {
          t.classList.toggle("is-on", t === tab);
        });
        host.querySelectorAll(".course-pane.cv-pane").forEach(function (p) {
          var show = p.id === "pane-" + id;
          p.classList.toggle("is-on", show);
          p.classList.toggle("hidden", !show);
        });
      });
    });

    var qInput = document.querySelector("#header-search-q");
    if (qInput) {
      qInput.addEventListener("input", function () {
        runSearch(qInput.value);
      });
    }

    var catSearch = document.getElementById("cat-search-course");
    if (catSearch) {
      catSearch.addEventListener("input", function () {
        filterCourseCatalog(catSearch.value.trim().toLowerCase());
      });
    }

    var uploadZone = document.getElementById("upload-zone");
    var fakeFile = document.getElementById("fake-file-input");
    var fb = document.getElementById("file-feedback");
    var btnPick = document.getElementById("btn-pick-file");
    var btnSubmit = document.getElementById("btn-submit-task");
    var preChecks = document.querySelectorAll(".pre-check");
    var stateTag = document.getElementById("delivery-state-tag");

    function validateSubmitReady() {
      var fileOk = uploadZone && uploadZone.classList.contains("is-filled");
      var allChecks = Array.from(preChecks).every(function (c) {
        return c.checked;
      });
      if (btnSubmit) btnSubmit.disabled = !(fileOk && allChecks);
    }

    if (btnPick && fakeFile) {
      btnPick.addEventListener("click", function () {
        fakeFile.click();
      });
    }

    if (fakeFile) {
      fakeFile.addEventListener("change", function () {
        if (!fakeFile.files || !fakeFile.files[0]) return;
        var f = fakeFile.files[0];
        if (uploadZone) {
          uploadZone.classList.add("is-filled");
          uploadZone.innerHTML =
            '<p style="margin:0"><strong>Archivo listo:</strong> ' +
            escapeHtml(f.name) +
            " (" +
            kb(f.size) +
            ") — <small>validación local (demo)</small></p>";
        }
        if (fb) {
          fb.className = "alert-zone alert-ok";
          fb.textContent = "Archivo cargado. Revisa checklist antes de entregar.";
        }
        validateSubmitReady();
      });
    }

    function escapeHtml(s) {
      return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;");
    }

    function kb(n) {
      return Math.max(1, Math.round(n / 102)) / 10 + " MB";
    }

    preChecks.forEach(function (c) {
      c.addEventListener("change", validateSubmitReady);
    });

    var bd = document.getElementById("btn-draft");
    if (bd && fb) {
      bd.addEventListener("click", function () {
        fb.className = "alert-zone alert-ok";
        fb.textContent = "Borrador guardado (simulación).";
      });
    }

    if (btnSubmit && fb && stateTag) {
      btnSubmit.addEventListener("click", function () {
        if (btnSubmit.disabled) return;
        btnSubmit.disabled = true;
        stateTag.textContent = "Entregado · En revisión";
        stateTag.className = "pill pill--muted large";
        fb.className = "alert-zone alert-ok";
        fb.textContent = "Registro simulado. La entrega real se conectará al backend de actividades.";
      });
    }

    validateSubmitReady();

    var catRoot = document.getElementById("course-catalog-root");
    var catView = document.getElementById("cat-view-mode");
    var catGridWrap = catRoot ? catRoot.querySelector(".course-catalog-grid-wrap") : null;
    var catResumen = document.getElementById("course-catalog-resumen");

    function applyCourseCatalogView() {
      if (!catRoot || !catView) return;
      var mode = catView.value;
      var isResumen = mode === "resumen";
      if (!/^(tarjeta|lista|resumen)$/.test(mode)) mode = "tarjeta";
      catRoot.className = "course-catalog-root course-catalog-root--" + mode;
      if (catGridWrap) catGridWrap.toggleAttribute("hidden", isResumen);
      if (catResumen) {
        catResumen.toggleAttribute("hidden", !isResumen);
        catResumen.setAttribute("aria-hidden", isResumen ? "false" : "true");
      }
    }

    if (catView) {
      var savedCatalogView = null;
      try {
        savedCatalogView = localStorage.getItem("easylearn:catalog-view");
      } catch (e) {}
      if (savedCatalogView && /^(tarjeta|lista|resumen)$/.test(savedCatalogView)) catView.value = savedCatalogView;
      catView.addEventListener("change", function () {
        applyCourseCatalogView();
        try {
          localStorage.setItem("easylearn:catalog-view", catView.value);
        } catch (e2) {}
      });
      applyCourseCatalogView();
    }

    var hash = (location.hash || "").replace(/^#/, "");
    if (isSearchPage) {
      document.querySelectorAll(".sidebar__link").forEach(function (link) {
        link.classList.remove("is-active");
        link.removeAttribute("aria-current");
      });
      var sl = document.getElementById("sidebar-link-search");
      if (sl) {
        sl.classList.add("is-active");
        sl.setAttribute("aria-current", "page");
      }
      document.title = "Resultados de búsqueda — EasyLearn";
    } else {
      go(routes[hash] ? hash : "dashboard");
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initApp);
  } else {
    initApp();
  }
})();
