/**
 * EasyLearn shell — navegación por hash entre vistas del boceto (RF-03, RF-04).
 * Las vistas principales se renderizan en el servidor (sin fetch de parciales).
 */
(function () {
  var routes = {
    dashboard: "view-dashboard",
    cursos: "view-cursos",
    calificaciones: "view-calificaciones",
    calendario: "view-calendario",
    repaso: "view-repaso",
  };

  var titles = {
    dashboard: "EasyLearn · Inicio",
    cursos: "EasyLearn · Mis cursos",
    calificaciones: "EasyLearn · Calificaciones",
    calendario: "EasyLearn · Calendario",
    repaso: "EasyLearn · Repaso",
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
        window.location.replace("/aula/");
        return;
      case "calificaciones":
        el.innerHTML = crumb("Inicio", "dashboard") + ' <span class="sep">›</span> ' + crumb("Calificaciones", null);
        break;
      case "calendario":
        el.innerHTML = crumb("Inicio", "dashboard") + ' <span class="sep">›</span> ' + crumb("Calendario", null);
        break;
      case "repaso":
        el.innerHTML = crumb("Inicio", "dashboard") + ' <span class="sep">›</span> ' + crumb("Repaso", null);
        break;
      default:
        el.innerHTML = "";
    }
  }

  function portalDashboardUrl() {
    var brand = document.querySelector(".sidebar__brand-link[href]");
    if (brand && brand.getAttribute("href")) {
      return brand.getAttribute("href").split("#")[0];
    }
    return "/dashboard";
  }

  /** Si el enlace del menú apunta a otra página del portal, dejar navegación nativa. */
  function sidebarLinkUsesFullNavigation(link, viewId) {
    if (!link || link.tagName !== "A") return false;
    var href = link.getAttribute("href") || "";
    if (!href || href.indexOf("#") < 0) return false;
    if (href.indexOf("/aula") >= 0) return true;
    if (viewId && !document.getElementById(viewId)) return true;
    return false;
  }

  function go(route) {
    if (!routes[route]) return;
    var targetId = routes[route];
    if (!document.getElementById(targetId)) {
      window.location.assign(portalDashboardUrl() + "#" + route);
      return;
    }
    document.querySelectorAll(".view").forEach(function (v) {
      v.classList.toggle("is-visible", v.id === targetId);
    });
    document.querySelectorAll(".sidebar__link[data-route]").forEach(function (link) {
      var r = link.getAttribute("data-route");
      var active = r === route;
      link.classList.toggle("is-active", active);
      if (active) link.setAttribute("aria-current", "page");
      else link.removeAttribute("aria-current");
    });
    renderBreadcrumbs(route);
    document.title = titles[route] || "EasyLearn";
    if (route === "calificaciones") syncGradesActivities();
    if (route === "calendario") renderPortalMonthCal();
    try {
      history.replaceState(null, "", "#" + route);
    } catch (_) {}

  }

  var portalCalMonthNames = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
  ];
  var portalCalState = null;

  function loadPortalCalEvents() {
    var el = document.getElementById("portal-cal-events-data");
    if (!el) return [];
    try {
      return JSON.parse(el.textContent || "[]");
    } catch (_) {
      return [];
    }
  }

  function portalCalDayTone(dayEvents) {
    if (!dayEvents.length) return "";
    if (dayEvents.some(function (e) { return e.state === "overdue"; })) return "danger";
    if (dayEvents.some(function (e) { return e.state === "pending"; })) return "warn";
    if (dayEvents.some(function (e) {
      return e.state === "submitted" || e.state === "graded";
    })) return "ok";
    return "draft";
  }

  function portalCalEventsByDate(events) {
    var map = {};
    events.forEach(function (ev) {
      if (!map[ev.date]) map[ev.date] = [];
      map[ev.date].push(ev);
    });
    return map;
  }

  function initPortalMonthCalendar() {
    var root = document.getElementById("portal-month-cal");
    if (!root || root.dataset.inited === "1") return;
    root.dataset.inited = "1";
    var events = loadPortalCalEvents();
    portalCalState = {
      events: events,
      byDate: portalCalEventsByDate(events),
      viewYear: parseInt(root.getAttribute("data-year"), 10) || new Date().getFullYear(),
      viewMonth: parseInt(root.getAttribute("data-month"), 10) || new Date().getMonth() + 1,
      todayYear: parseInt(root.getAttribute("data-today-year"), 10) || new Date().getFullYear(),
      todayMonth: parseInt(root.getAttribute("data-today-month"), 10) || new Date().getMonth() + 1,
      todayDay: parseInt(root.getAttribute("data-today-day"), 10) || new Date().getDate(),
      selectedDate: null,
    };
    var prev = document.getElementById("portal-cal-prev");
    var next = document.getElementById("portal-cal-next");
    var todayBtn = document.getElementById("portal-cal-today");
    var showAll = document.getElementById("portal-cal-show-all");
    if (prev) {
      prev.addEventListener("click", function () {
        portalCalState.viewMonth -= 1;
        if (portalCalState.viewMonth < 1) {
          portalCalState.viewMonth = 12;
          portalCalState.viewYear -= 1;
        }
        renderPortalMonthCal();
      });
    }
    if (next) {
      next.addEventListener("click", function () {
        portalCalState.viewMonth += 1;
        if (portalCalState.viewMonth > 12) {
          portalCalState.viewMonth = 1;
          portalCalState.viewYear += 1;
        }
        renderPortalMonthCal();
      });
    }
    if (todayBtn) {
      todayBtn.addEventListener("click", function () {
        portalCalState.viewYear = portalCalState.todayYear;
        portalCalState.viewMonth = portalCalState.todayMonth;
        portalCalState.selectedDate =
          portalCalIso(portalCalState.todayYear, portalCalState.todayMonth, portalCalState.todayDay);
        renderPortalMonthCal();
      });
    }
    if (showAll) {
      showAll.addEventListener("click", function () {
        portalCalState.selectedDate = null;
        renderPortalMonthCal();
      });
    }
    renderPortalMonthCal();
  }

  function portalCalIso(y, m, d) {
    return y + "-" + String(m).padStart(2, "0") + "-" + String(d).padStart(2, "0");
  }

  function renderPortalMonthCal() {
    if (!portalCalState) initPortalMonthCalendar();
    if (!portalCalState) return;
    var root = document.getElementById("portal-month-cal");
    var grid = document.getElementById("portal-month-cal-grid");
    var label = document.getElementById("portal-cal-month-label");
    var listTitle = document.getElementById("portal-cal-list-title");
    var showAll = document.getElementById("portal-cal-show-all");
    if (!root || !grid) return;
    var y = portalCalState.viewYear;
    var m = portalCalState.viewMonth;
    if (label) {
      label.textContent = portalCalMonthNames[m - 1] + " " + y;
    }
    var first = new Date(y, m - 1, 1);
    var daysInMonth = new Date(y, m, 0).getDate();
    var startPad = (first.getDay() + 6) % 7;
    grid.innerHTML = "";
    var i;
    for (i = 0; i < startPad; i++) {
      var empty = document.createElement("div");
      empty.className = "mc-day is-empty";
      empty.innerHTML = "&nbsp;";
      grid.appendChild(empty);
    }
    for (i = 1; i <= daysInMonth; i++) {
      var iso = portalCalIso(y, m, i);
      var dayEvents = portalCalState.byDate[iso] || [];
      var cell = document.createElement("button");
      cell.type = "button";
      cell.className = "mc-day";
      cell.textContent = String(i);
      cell.setAttribute("data-date", iso);
      cell.setAttribute("aria-label", i + " de " + portalCalMonthNames[m - 1]);
      if (
        y === portalCalState.todayYear &&
        m === portalCalState.todayMonth &&
        i === portalCalState.todayDay
      ) {
        cell.classList.add("is-today");
      }
      if (dayEvents.length) {
        cell.classList.add("has-event");
        var tone = portalCalDayTone(dayEvents);
        if (tone) cell.classList.add("mc-day--tone-" + tone);
        cell.setAttribute(
          "aria-label",
          i + " de " + portalCalMonthNames[m - 1] + ", " + dayEvents.length + " entrega(s)"
        );
      }
      if (portalCalState.selectedDate === iso) {
        cell.classList.add("is-selected");
        cell.setAttribute("aria-pressed", "true");
      } else {
        cell.setAttribute("aria-pressed", "false");
      }
      cell.addEventListener("click", function () {
        var dateKey = cell.getAttribute("data-date");
        portalCalState.selectedDate =
          portalCalState.selectedDate === dateKey ? null : dateKey;
        renderPortalMonthCal();
      });
      grid.appendChild(cell);
    }
    while (grid.children.length % 7 !== 0) {
      var pad = document.createElement("div");
      pad.className = "mc-day is-empty";
      pad.innerHTML = "&nbsp;";
      grid.appendChild(pad);
    }
    filterPortalCalTable();
    if (listTitle) {
      if (portalCalState.selectedDate) {
        var parts = portalCalState.selectedDate.split("-");
        listTitle.textContent =
          "Entregas del " +
          parseInt(parts[2], 10) +
          " " +
          portalCalMonthNames[parseInt(parts[1], 10) - 1] +
          " " +
          parts[0];
      } else {
        listTitle.textContent = "Próximas entregas";
      }
    }
    if (showAll) showAll.hidden = !portalCalState.selectedDate;
  }

  function filterPortalCalTable(needleLower) {
    var tbody = document.querySelector("#portal-cal-events-table tbody");
    if (!tbody) return;
    if (needleLower === undefined) needleLower = getHeaderSearchNeedle();
    var selected = portalCalState ? portalCalState.selectedDate : null;
    tbody.querySelectorAll("tr").forEach(function (tr) {
      if (tr.classList.contains("portal-cal-empty-row")) return;
      var dateKey = tr.getAttribute("data-date") || "";
      var search = tr.getAttribute("data-search") || tr.textContent;
      var matchDay = !selected || dateKey === selected;
      var matchSearch =
        needleLower === "" || search.toLowerCase().indexOf(needleLower) !== -1;
      tr.style.display = matchDay && matchSearch ? "" : "none";
    });
  }

  function syncCalendarEvents(needleLower) {
    filterPortalCalTable(needleLower);
  }

  function renderDashboardMiniCal() {
    var root = document.getElementById("dash-mini-cal");
    if (!root || root.childNodes.length) return;
    var year = parseInt(root.getAttribute("data-year"), 10) || new Date().getFullYear();
    var month = parseInt(root.getAttribute("data-month"), 10) || new Date().getMonth() + 1;
    var today = parseInt(root.getAttribute("data-today"), 10) || new Date().getDate();
    var dueDays = [];
    try {
      dueDays = JSON.parse(root.getAttribute("data-due-days") || "[]");
    } catch (_) {}
    var first = new Date(year, month - 1, 1);
    var daysInMonth = new Date(year, month, 0).getDate();
    var startPad = (first.getDay() + 6) % 7;
    var cells = [];
    var i;
    for (i = 0; i < startPad; i++) cells.push(null);
    for (i = 1; i <= daysInMonth; i++) cells.push(i);
    while (cells.length % 7 !== 0) cells.push(null);
    cells.forEach(function (d) {
      var el = document.createElement("div");
      el.className = "mc-day";
      if (d === null) {
        el.classList.add("is-empty");
        el.innerHTML = "&nbsp;";
      } else {
        el.textContent = String(d);
        if (d === today) el.classList.add("is-today");
        if (dueDays.indexOf(d) !== -1) el.classList.add("has-event");
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
    var gTb = gradesView.querySelector("#grades-activity-table tbody");
    if (!gTb) return;
    gTb.querySelectorAll("tr").forEach(function (tr) {
      var d = tr.getAttribute("data-search") || tr.textContent;
      tr.style.display = needleLower === "" || d.toLowerCase().indexOf(needleLower) !== -1 ? "" : "none";
    });
  }

  function runSearch(q) {
    var needle = (q || "").trim().toLowerCase();
    var visibleView = document.querySelector(".canvas-body .view.is-visible");
    var dashTb = visibleView
      ? visibleView.querySelector("#dash-activity-table tbody")
      : document.querySelector("#dash-activity-table tbody");
    if (dashTb) {
      dashTb.querySelectorAll("tr").forEach(function (tr) {
        var d = tr.getAttribute("data-search") || tr.textContent;
        tr.style.display = needle === "" || d.toLowerCase().indexOf(needle) !== -1 ? "" : "none";
      });
    }
    syncGradesActivities(needle);
    syncCalendarEvents(needle);
    document.querySelectorAll(".repaso-course-card").forEach(function (card) {
      var t = card.getAttribute("data-search") || card.textContent;
      card.style.display = needle === "" || t.toLowerCase().indexOf(needle) !== -1 ? "" : "none";
    });
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

  function initActivitySubmitPage() {
    var form = document.getElementById("activity-submit-form");
    if (!form) return;

    var uploadZone = document.getElementById("upload-zone");
    var zoneEmpty = document.getElementById("upload-zone-empty");
    var zoneFilled = document.getElementById("upload-zone-filled");
    var fileInput = document.getElementById("submission-file");
    var btnPick = document.getElementById("btn-pick-file");
    var btnChange = document.getElementById("btn-change-file");
    var btnRemove = document.getElementById("btn-remove-file");
    var btnSubmit = document.getElementById("btn-submit-activity");
    var fb = document.getElementById("file-feedback");
    var fileNameEl = document.getElementById("upload-zone-filename");
    var fileMetaEl = document.getElementById("upload-zone-filemeta");
    var fileDownload = document.getElementById("upload-zone-download");
    var clearFileField = document.getElementById("clear-file-field");
    var comment = document.getElementById("submission-comment");
    var preChecks = form.querySelectorAll(".submit-check");
    var requiresFile = form.getAttribute("data-requires-file") === "1";
    var hadServerFile = !!(form.getAttribute("data-existing-file") || "").trim();
    var hasServerFile = hadServerFile;

    function escapeHtml(s) {
      return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;");
    }

    function basename(path) {
      var p = String(path || "");
      var i = Math.max(p.lastIndexOf("/"), p.lastIndexOf("\\"));
      return i >= 0 ? p.slice(i + 1) : p;
    }

    function formatSize(bytes) {
      if (!bytes && bytes !== 0) return "";
      if (bytes < 1024) return bytes + " B";
      if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
      return (bytes / (1024 * 1024)).toFixed(1) + " MB";
    }

    function setClearFileFlag(on) {
      if (clearFileField) clearFileField.value = on ? "1" : "0";
    }

    function showEmptyState() {
      if (!uploadZone) return;
      uploadZone.classList.remove("is-filled");
      if (zoneEmpty) zoneEmpty.hidden = false;
      if (zoneFilled) zoneFilled.hidden = true;
      if (fb) {
        fb.className = "alert-zone";
        fb.textContent = "";
      }
    }

    function showFilledState(name, meta, downloadUrl) {
      if (!uploadZone) return;
      uploadZone.classList.add("is-filled");
      if (zoneEmpty) zoneEmpty.hidden = true;
      if (zoneFilled) zoneFilled.hidden = false;
      if (fileNameEl) fileNameEl.textContent = name;
      if (fileMetaEl) fileMetaEl.textContent = meta || "";
      if (fileDownload) {
        if (downloadUrl) {
          fileDownload.href = downloadUrl;
          fileDownload.hidden = false;
        } else {
          fileDownload.hidden = true;
        }
      }
      if (fb) {
        fb.className = "alert-zone alert-ok";
        fb.textContent = "Puedes cambiar o eliminar el archivo antes de entregar.";
      }
    }

    function hasSelectedFile() {
      return uploadZone && uploadZone.classList.contains("is-filled");
    }

    function fileReady() {
      if (!requiresFile) {
        return hasSelectedFile() || (comment && comment.value.trim().length > 0);
      }
      return hasSelectedFile();
    }

    function validateSubmitReady() {
      if (!btnSubmit) return;
      var checksOk = Array.from(preChecks).every(function (c) {
        return c.checked;
      });
      btnSubmit.disabled = !(fileReady() && checksOk);
    }

    function applyFile(f) {
      if (!f) return;
      setClearFileFlag(false);
      hasServerFile = false;
      showFilledState(f.name, formatSize(f.size), null);
      validateSubmitReady();
    }

    function openPicker() {
      if (fileInput) fileInput.click();
    }

    function removeFile() {
      if (fileInput) fileInput.value = "";
      if (hasServerFile) setClearFileFlag(true);
      else setClearFileFlag(false);
      hasServerFile = false;
      showEmptyState();
      validateSubmitReady();
    }

    if (btnPick) btnPick.addEventListener("click", openPicker);
    if (btnChange) btnChange.addEventListener("click", openPicker);
    if (btnRemove) btnRemove.addEventListener("click", removeFile);

    if (uploadZone && fileInput) {
      if (zoneEmpty) {
        zoneEmpty.addEventListener("click", function (e) {
          if (e.target.closest("button, a")) return;
          openPicker();
        });
      }
      uploadZone.addEventListener("dragover", function (e) {
        e.preventDefault();
        uploadZone.classList.add("is-dragover");
      });
      uploadZone.addEventListener("dragleave", function () {
        uploadZone.classList.remove("is-dragover");
      });
      uploadZone.addEventListener("drop", function (e) {
        e.preventDefault();
        uploadZone.classList.remove("is-dragover");
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
          fileInput.files = e.dataTransfer.files;
          applyFile(e.dataTransfer.files[0]);
        }
      });
      fileInput.addEventListener("change", function () {
        if (!fileInput.files || !fileInput.files[0]) return;
        applyFile(fileInput.files[0]);
      });
    }

    if (hadServerFile) {
      var existing = form.getAttribute("data-existing-file");
      var dl = fileDownload ? fileDownload.getAttribute("href") : null;
      showFilledState(basename(existing), "Archivo guardado en el servidor", dl);
      setClearFileFlag(false);
    }

    if (comment) comment.addEventListener("input", validateSubmitReady);
    preChecks.forEach(function (c) {
      c.addEventListener("change", validateSubmitReady);
    });

    form.addEventListener("submit", function () {
      var hidden = document.getElementById("confirm-ready-field");
      var ok = document.getElementById("check-confirm-ready");
      if (hidden && ok) hidden.value = ok.checked ? "1" : "0";
    });

    validateSubmitReady();
  }

  function initInstitutionalCourseCatalog() {
    var instView = document.getElementById("inst-view-mode");
    var instRoot = document.getElementById("inst-course-root");
    var instTable = document.getElementById("inst-course-table");
    var instSort = document.getElementById("inst-sort-course");
    if (!instRoot) return;

    function applyInstCourseView() {
      if (!instView) return;
      var lista = instView.value === "lista";
      instRoot.className = "course-catalog-root course-catalog-root--" + (lista ? "lista" : "tarjeta");
      if (instTable) instTable.toggleAttribute("hidden", !lista);
    }

    function sortInstCards() {
      var grid = instRoot.querySelector(".course-catalog-grid");
      if (!grid || !instSort) return;
      var cards = Array.from(grid.querySelectorAll(".course-catalog-card"));
      var mode = instSort.value;
      cards.sort(function (a, b) {
        var an = a.getAttribute("data-sort-name") || "";
        var bn = b.getAttribute("data-sort-name") || "";
        var ac = a.getAttribute("data-sort-code") || "";
        var bc = b.getAttribute("data-sort-code") || "";
        if (mode.indexOf("code") === 0) {
          return mode.endsWith("desc") ? bc.localeCompare(ac) : ac.localeCompare(bc);
        }
        return mode.endsWith("desc") ? bn.localeCompare(an) : an.localeCompare(bn);
      });
      cards.forEach(function (c) {
        grid.appendChild(c);
      });
    }

    if (instView) {
      instView.addEventListener("change", applyInstCourseView);
      applyInstCourseView();
    }

    if (instSort) {
      instSort.addEventListener("change", sortInstCards);
      sortInstCards();
    }

    var instSearch = document.getElementById("inst-search-course");
    if (instSearch) {
      instSearch.addEventListener("input", function () {
        var needle = instSearch.value.trim().toLowerCase();
        instRoot.querySelectorAll("[data-catalog-scope]").forEach(function (el) {
          var t = (el.getAttribute("data-catalog-scope") || "") + " " + el.textContent;
          el.style.display = needle === "" || t.toLowerCase().indexOf(needle) !== -1 ? "" : "none";
        });
      });
    }
  }

  function initPortalHeaderChrome() {
    var filterForm = document.querySelector("[data-header-filter-form]");
    if (filterForm) {
      filterForm.addEventListener("submit", function (e) {
        e.preventDefault();
      });
    }

    var bellRoot = document.getElementById("header-bell");
    var bellTrigger = document.getElementById("header-bell-trigger");
    var bellMenu = document.getElementById("header-bell-menu");
    if (bellRoot && bellTrigger && bellMenu) {
      function setBellOpen(open) {
        bellRoot.classList.toggle("header-bell--open", open);
        bellTrigger.setAttribute("aria-expanded", open ? "true" : "false");
        bellMenu.hidden = !open;
      }
      bellTrigger.addEventListener("click", function (e) {
        e.stopPropagation();
        setBellOpen(!bellRoot.classList.contains("header-bell--open"));
      });
      document.addEventListener("click", function (e) {
        if (!bellRoot.contains(e.target)) setBellOpen(false);
      });
      bellMenu.querySelectorAll("[data-notification-id]").forEach(function (link) {
        link.addEventListener("click", function () {
          var id = link.getAttribute("data-notification-id");
          var fd = new FormData();
          fd.append("id", id);
          var csrf = document.querySelector("[name=csrfmiddlewaretoken]");
          if (csrf) fd.append("csrfmiddlewaretoken", csrf.value);
          fetch("/accounts/notifications/read/", {
            method: "POST",
            body: fd,
            headers: { "X-Requested-With": "XMLHttpRequest" },
            credentials: "same-origin",
          });
        });
      });
    }
  }

  function initPortalShellExtras() {
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

      profileMenu.querySelectorAll("a.header-profile__menu-link[href]").forEach(function (link) {
        link.addEventListener("click", function () {
          setProfileMenuOpen(false);
        });
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
  }

  function initPortalMobileNav() {
    var toggle = document.getElementById("portal-nav-toggle");
    var backdrop = document.getElementById("portal-nav-backdrop");
    var sidebar = document.getElementById("portal-sidebar") || document.querySelector(".sidebar");
    if (!toggle || !sidebar) return;

    function setOpen(open) {
      document.body.classList.toggle("is-portal-nav-open", open);
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      toggle.setAttribute("aria-label", open ? "Cerrar menú de navegación" : "Abrir menú de navegación");
      if (backdrop) backdrop.setAttribute("aria-hidden", open ? "false" : "true");
    }

    toggle.addEventListener("click", function () {
      setOpen(!document.body.classList.contains("is-portal-nav-open"));
    });

    if (backdrop) {
      backdrop.addEventListener("click", function () {
        setOpen(false);
      });
    }

    sidebar.querySelectorAll("a, button.sidebar__link").forEach(function (el) {
      el.addEventListener("click", function () {
        if (window.matchMedia("(max-width: 768px)").matches) setOpen(false);
      });
    });

    window.addEventListener("resize", function () {
      if (window.matchMedia("(min-width: 769px)").matches) setOpen(false);
    });
  }

  function initApp() {
    var isSearchPage = document.body.getAttribute("data-easylearn-page") === "search";
    var rolePage = document.body.getAttribute("data-easylearn-page");

    initPortalMobileNav();
    initPortalHeaderChrome();

    if (rolePage === "admin" || rolePage === "teacher") {
      initPortalShellExtras();

      if (rolePage === "teacher" && !document.getElementById("view-teacher-dashboard")) {
        return;
      }
      if (rolePage === "admin" && !document.getElementById("view-admin-dashboard")) {
        return;
      }

      function filterRoleDashboardRows(needleRaw) {
        var n = needleRaw === undefined || needleRaw === null ? "" : String(needleRaw).trim().toLowerCase();
        var root = document.querySelector(".canvas-body .view.is-visible") || document.querySelector(".canvas-body");
        if (!root) return;
        root.querySelectorAll("table tbody tr").forEach(function (tr) {
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
        root.querySelectorAll(".course-catalog-card").forEach(function (card) {
          var t = (card.getAttribute("data-catalog-scope") || "") + " " + card.textContent;
          card.style.display = n === "" || t.toLowerCase().indexOf(n) !== -1 ? "" : "none";
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
          if (!document.getElementById(targetId)) {
            window.location.assign(portalDashboardUrl() + "#" + canonical);
            return;
          }
          document.querySelectorAll(".canvas-body .view").forEach(function (v) {
            v.classList.toggle("is-visible", v.id === targetId);
          });
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
          if (qInputRole) filterRoleDashboardRows(qInputRole.value);
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
          btn.addEventListener("click", function (e) {
            var route = btn.getAttribute("data-route");
            var viewId = teacherRoutes[route];
            if (sidebarLinkUsesFullNavigation(btn, viewId)) return;
            e.preventDefault();
            goTeacher(route);
          });
        });

        window.addEventListener("hashchange", function () {
          if (document.body.getAttribute("data-easylearn-page") !== "teacher") return;
          var h = (location.hash || "").replace(/^#/, "");
          if (h === "rendimiento") h = "historial-calificaciones";
          if (teacherRoutes[h]) goTeacher(h);
        });

        function filterTeacherDeliveries() {
          var courseSel = document.getElementById("ent-filter-course");
          var statusSel = document.getElementById("ent-filter-status");
          if (!courseSel && !statusSel) return;
          function apply() {
            var course = courseSel ? courseSel.value : "";
            var status = statusSel ? statusSel.value : "";
            document
              .querySelectorAll(
                "#teacher-delivery-activity-table tbody tr[data-offering-id], #teacher-submissions-table tbody tr[data-offering-id]"
              )
              .forEach(function (tr) {
                var okCourse = !course || tr.getAttribute("data-offering-id") === course;
                var st = tr.getAttribute("data-status") || "";
                var okStatus = !status || st.indexOf(status) !== -1;
                tr.style.display = okCourse && okStatus ? "" : "none";
              });
          }
          if (courseSel) courseSel.addEventListener("change", apply);
          if (statusSel) statusSel.addEventListener("change", apply);
        }
        filterTeacherDeliveries();

        var hInit = (location.hash || "").replace(/^#/, "");
        if (hInit === "rendimiento") hInit = "historial-calificaciones";
        if (teacherRoutes[hInit]) goTeacher(hInit);
        else goTeacher("dashboard");
      }

      if (rolePage === "admin") {
        var adminRoutes = {
          dashboard: "view-admin-dashboard",
          usuarios: "view-admin-usuarios",
          carreras: "view-admin-carreras",
          ofertas: "view-admin-ofertas",
          matriculas: "view-admin-matriculas",
          periodos: "view-admin-periodos",
        };
        var adminTitles = {
          dashboard: "EasyLearn · Panel administrador",
          usuarios: "EasyLearn · Usuarios",
          carreras: "EasyLearn · Carreras",
          ofertas: "EasyLearn · Cursos ofertados",
          matriculas: "EasyLearn · Matrículas",
          periodos: "EasyLearn · Períodos",
        };
        var adminPendingFilter = null;

        function adminCrumbLabel(route) {
          if (route === "usuarios") return "Usuarios";
          if (route === "carreras") return "Carreras";
          if (route === "ofertas") return "Cursos ofertados";
          if (route === "matriculas") return "Matrículas";
          if (route === "periodos") return "Períodos";
          return route;
        }

        function renderAdminBreadcrumbs(route) {
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
            crumb(adminCrumbLabel(route), null);
        }

        function applyAdminTableFilters() {
          var roleSel = document.getElementById("admin-filter-user-role");
          var activeSel = document.getElementById("admin-filter-user-active");
          if (roleSel || activeSel) {
            var role = roleSel ? roleSel.value : "";
            var active = activeSel ? activeSel.value : "";
            document.querySelectorAll('tr[data-admin-row="usuarios"]').forEach(function (tr) {
              var okRole = !role || tr.getAttribute("data-role") === role;
              var okActive = active === "" || tr.getAttribute("data-active") === active;
              tr.style.display = okRole && okActive ? "" : "none";
            });
          }

          var offPeriod = document.getElementById("admin-filter-offering-period");
          var offProgram = document.getElementById("admin-filter-offering-program");
          var offTeacher = document.getElementById("admin-filter-offering-teacher");
          if (offPeriod || offProgram || offTeacher) {
            var pId = offPeriod ? offPeriod.value : "";
            var progId = offProgram ? offProgram.value : "";
            var teacherF = offTeacher ? offTeacher.value : "";
            document.querySelectorAll('tr[data-admin-row="ofertas"]').forEach(function (tr) {
              var okP = !pId || tr.getAttribute("data-period-id") === pId;
              var okProg = !progId || tr.getAttribute("data-program-id") === progId;
              var missing = tr.getAttribute("data-teacher-missing") === "1";
              var okT =
                !teacherF ||
                (teacherF === "missing" && missing) ||
                (teacherF === "assigned" && !missing);
              tr.style.display = okP && okProg && okT ? "" : "none";
            });
          }

          var enrPeriod = document.getElementById("admin-filter-enrollment-period");
          var enrProgram = document.getElementById("admin-filter-enrollment-program");
          var enrStatus = document.getElementById("admin-filter-enrollment-status");
          if (enrPeriod || enrProgram || enrStatus) {
            var ep = enrPeriod ? enrPeriod.value : "";
            var eprog = enrProgram ? enrProgram.value : "";
            var est = enrStatus ? enrStatus.value : "";
            document.querySelectorAll('tr[data-admin-row="matriculas"]').forEach(function (tr) {
              var okEp = !ep || tr.getAttribute("data-period-id") === ep;
              var okEprog = !eprog || tr.getAttribute("data-program-id") === eprog;
              var okEst = !est || tr.getAttribute("data-status") === est;
              tr.style.display = okEp && okEprog && okEst ? "" : "none";
            });
          }

          var perCurrent = document.getElementById("admin-filter-period-current");
          if (perCurrent) {
            var cur = perCurrent.value;
            document.querySelectorAll('tr[data-admin-row="periodos"]').forEach(function (tr) {
              var isCur = tr.getAttribute("data-is-current");
              var ok =
                cur === "" || (cur === "1" && isCur === "1") || (cur === "0" && isCur === "0");
              tr.style.display = ok ? "" : "none";
            });
          }
        }

        function applyAdminPendingFilter() {
          if (!adminPendingFilter) return;
          if (adminPendingFilter.program && document.getElementById("admin-filter-offering-program")) {
            document.getElementById("admin-filter-offering-program").value = adminPendingFilter.program;
          }
          if (adminPendingFilter.teacher && document.getElementById("admin-filter-offering-teacher")) {
            document.getElementById("admin-filter-offering-teacher").value = adminPendingFilter.teacher;
          }
          adminPendingFilter = null;
          applyAdminTableFilters();
        }

        function goAdmin(route) {
          if (!adminRoutes[route]) route = "dashboard";
          var targetId = adminRoutes[route];
          if (!document.getElementById(targetId)) {
            window.location.assign(portalDashboardUrl() + "#" + route);
            return;
          }
          document.querySelectorAll(".canvas-body .view").forEach(function (v) {
            v.classList.toggle("is-visible", v.id === targetId);
          });
          document.querySelectorAll(".sidebar__link[data-route]").forEach(function (link) {
            var r = link.getAttribute("data-route");
            var active = r === route;
            link.classList.toggle("is-active", active);
            if (active) link.setAttribute("aria-current", "page");
            else link.removeAttribute("aria-current");
          });
          renderAdminBreadcrumbs(route);
          document.title = adminTitles[route] || adminTitles.dashboard;
          try {
            history.replaceState(null, "", "#" + route);
          } catch (_) {}
          applyAdminPendingFilter();
          if (qInputRole) filterRoleDashboardRows(qInputRole.value);
        }

        var canvasAdmin = document.querySelector(".canvas-body");
        if (canvasAdmin) {
          canvasAdmin.addEventListener("click", function (e) {
            var tgt = e.target.closest("[data-goto]");
            if (!tgt) return;
            var r = tgt.getAttribute("data-goto");
            if (!adminRoutes[r]) return;
            e.preventDefault();
            var progFilter = tgt.getAttribute("data-admin-goto-filter-program");
            var teacherPreset = tgt.getAttribute("data-admin-preset-teacher");
            if (progFilter || teacherPreset) {
              adminPendingFilter = {
                program: progFilter || "",
                teacher: teacherPreset || "",
              };
            }
            goAdmin(r);
          });
        }

        document.querySelectorAll(".sidebar__link[data-route]").forEach(function (btn) {
          btn.addEventListener("click", function (e) {
            var route = btn.getAttribute("data-route");
            var viewId = adminRoutes[route];
            if (sidebarLinkUsesFullNavigation(btn, viewId)) return;
            e.preventDefault();
            goAdmin(route);
          });
        });

        window.addEventListener("hashchange", function () {
          if (document.body.getAttribute("data-easylearn-page") !== "admin") return;
          var h = (location.hash || "").replace(/^#/, "");
          if (adminRoutes[h]) goAdmin(h);
        });

        document
          .querySelectorAll("[data-admin-filter], #admin-filter-user-role, #admin-filter-user-active, #admin-filter-offering-period, #admin-filter-offering-program, #admin-filter-offering-teacher, #admin-filter-enrollment-period, #admin-filter-enrollment-program, #admin-filter-enrollment-status, #admin-filter-period-current")
          .forEach(function (sel) {
            sel.addEventListener("change", applyAdminTableFilters);
          });

        var hAdmin = (location.hash || "").replace(/^#/, "");
        if (adminRoutes[hAdmin]) goAdmin(hAdmin);
        else goAdmin("dashboard");
      }

      return;
    }

    if (isSearchPage) {
      initPortalShellExtras();
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
      return;
    }

    if (rolePage === "profile" || rolePage === "classroom" || !document.getElementById("view-dashboard")) {
      initPortalShellExtras();
      initInstitutionalCourseCatalog();
      initActivitySubmitPage();
      return;
    }

    renderDashboardMiniCal();
    initPortalMonthCalendar();

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
      btn.addEventListener("click", function (e) {
        var route = btn.getAttribute("data-route");
        var viewId = routes[route];
        if (sidebarLinkUsesFullNavigation(btn, viewId)) return;
        e.preventDefault();
        go(route);
      });
    });

    window.addEventListener("hashchange", function () {
      if (document.body.getAttribute("data-easylearn-page") === "search") return;
      var h = (location.hash || "").replace(/^#/, "");
      if (routes[h]) go(h);
    });

    initPortalShellExtras();

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

    initInstitutionalCourseCatalog();

    function setCalViewTab(tab) {
      document.querySelectorAll(".cal-view-tabs__btn").forEach(function (b) {
        var on = b.getAttribute("data-cal-tab") === tab;
        b.classList.toggle("is-on", on);
        b.setAttribute("aria-selected", on ? "true" : "false");
      });
      var ac = document.getElementById("cal-panel-academico");
      var rep = document.getElementById("cal-panel-repaso");
      if (ac) {
        ac.hidden = tab !== "academico";
        ac.classList.toggle("cal-panel--visible", tab === "academico");
      }
      if (rep) {
        rep.hidden = tab !== "repaso";
        rep.classList.toggle("cal-panel--visible", tab === "repaso");
      }
      if (tab === "academico") renderPortalMonthCal();
    }

    document.querySelectorAll(".cal-view-tabs__btn").forEach(function (btn) {
      btn.addEventListener("click", function () {
        setCalViewTab(btn.getAttribute("data-cal-tab"));
      });
    });

    var hash = (location.hash || "").replace(/^#/, "");
    if (hash === "mensajes") {
      try {
        history.replaceState(null, "", location.pathname + location.search);
      } catch (_) {}
      hash = "dashboard";
    }
    if (hash === "curso" || hash === "semana" || hash === "tareas" || hash === "cursos") {
      window.location.replace("/aula/");
      return;
    }
    go(routes[hash] ? hash : "dashboard");
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initApp);
  } else {
    initApp();
  }
})();
