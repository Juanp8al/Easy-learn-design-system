(function () {
  var list = document.getElementById("sitio-nav-list");
  var openBtn = document.getElementById("sitio-menu-btn");
  var closeBtn = document.getElementById("sitio-menu-close");
  if (!list || !openBtn) return;

  function setOpen(open) {
    list.classList.toggle("is-open", open);
    openBtn.setAttribute("aria-expanded", open ? "true" : "false");
    document.body.classList.toggle("sitio-nav-open", open);
  }

  openBtn.addEventListener("click", function () {
    setOpen(!list.classList.contains("is-open"));
  });

  window.addEventListener("resize", function () {
    if (window.matchMedia("(min-width: 790px)").matches) setOpen(false);
  });

  if (closeBtn) {
    closeBtn.addEventListener("click", function () {
      setOpen(false);
    });
  }

  list.querySelectorAll("a").forEach(function (link) {
    link.addEventListener("click", function () {
      setOpen(false);
    });
  });
})();
