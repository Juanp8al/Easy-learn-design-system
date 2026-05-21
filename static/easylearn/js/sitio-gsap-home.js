(function () {
  var home = document.querySelector(".el-home");
  if (!home) return;

  function showAll() {
    home.querySelectorAll(".el-gsap").forEach(function (el) {
      el.style.opacity = "1";
      el.style.transform = "none";
    });
    home.classList.add("is-gsap-ready");
  }

  if (typeof gsap === "undefined" || typeof ScrollTrigger === "undefined") {
    showAll();
    return;
  }

  gsap.registerPlugin(ScrollTrigger);
  if (typeof ScrollToPlugin !== "undefined") {
    gsap.registerPlugin(ScrollToPlugin);
  }

  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reduced) {
    showAll();
    return;
  }

  function fromVars(el) {
    var dir = el.getAttribute("data-gsap-from") || "up";
    var delay = parseFloat(el.getAttribute("data-gsap-delay") || "0") * 0.14;
    var vars = {
      opacity: 0,
      duration: 0.95,
      ease: "power4.out",
      delay: delay,
    };

    switch (dir) {
      case "down":
        vars.y = -72;
        break;
      case "left":
        vars.x = -90;
        vars.rotation = -4;
        break;
      case "right":
        vars.x = 90;
        vars.rotation = 4;
        break;
      case "center":
        vars.scale = 0.55;
        vars.y = 0;
        vars.ease = "back.out(1.6)";
        break;
      default:
        vars.y = 72;
    }
    return vars;
  }

  function scrollOffsetY() {
    var topbar = document.querySelector(".sitio-topbar");
    return topbar ? topbar.offsetHeight + 16 : 0;
  }

  /* —— Hero · timeline al cargar —— */
  var heroTl = gsap.timeline({
    defaults: { ease: "power4.out" },
    onComplete: function () {
      home.classList.add("is-gsap-ready");
    },
  });

  heroTl
    .from(".el-home-hero__orb", {
      scale: 0,
      opacity: 0,
      duration: 1.2,
      stagger: 0.12,
      ease: "power2.out",
    })
    .from(
      ".el-home-hero__logo",
      { scale: 0.4, opacity: 0, duration: 1.1, ease: "back.out(1.7)" },
      "-=0.6"
    )
    .from(".el-home-hero__tagline", { y: -64, opacity: 0, duration: 0.85 }, "-=0.55")
    .from(".el-home-hero__actions", { y: 56, opacity: 0, duration: 0.75 }, "-=0.45")
    .from(
      ".el-home-hero__actions .el-home-hero__btn",
      { y: 28, opacity: 0, stagger: 0.1, duration: 0.55, ease: "power3.out" },
      "-=0.4"
    );

  /* Orbes flotantes continuos */
  gsap.to(".el-home-hero__orb--1", {
    y: 28,
    x: 12,
    duration: 4.5,
    repeat: -1,
    yoyo: true,
    ease: "sine.inOut",
  });
  gsap.to(".el-home-hero__orb--2", {
    y: -22,
    x: -18,
    duration: 5.2,
    repeat: -1,
    yoyo: true,
    ease: "sine.inOut",
    delay: 0.4,
  });
  gsap.to(".el-home-hero__orb--3", {
    y: 18,
    duration: 3.8,
    repeat: -1,
    yoyo: true,
    ease: "sine.inOut",
    delay: 0.8,
  });

  /* Parallax suave del hero al scroll */
  gsap.to(".el-home-hero", {
    backgroundPosition: "50% 85%",
    ease: "none",
    scrollTrigger: {
      trigger: ".el-home-hero",
      start: "top top",
      end: "bottom top",
      scrub: 0.6,
    },
  });

  /* —— Secciones al entrar en pantalla —— */
  home.querySelectorAll("[data-gsap-section]").forEach(function (section) {
    var items = section.querySelectorAll(".el-gsap");
    items.forEach(function (el) {
      var vars = fromVars(el);
      vars.scrollTrigger = {
        trigger: el,
        start: "top 86%",
        toggleActions: "play none none none",
      };
      gsap.from(el, vars);
    });
  });

  /* Cajas del flujo · stagger coordinado */
  var feaBoxes = home.querySelectorAll("#flujo .el-home-fea-box");
  if (feaBoxes.length) {
    gsap.from(feaBoxes, {
      scrollTrigger: {
        trigger: "#flujo .el-home-fea-base",
        start: "top 80%",
        toggleActions: "play none none none",
      },
      y: 80,
      opacity: 0,
      duration: 0.85,
      stagger: 0.18,
      ease: "power3.out",
      x: function (i) {
        if (i === 0) return -70;
        if (i === 2) return 70;
        return 0;
      },
    });
  }

  /* —— «Ver cómo funciona» —— */
  function playFlujoSequence() {
    var flujo = document.getElementById("flujo");
    if (!flujo) return;

    var title = flujo.querySelector(".el-home-section-title");
    var lead = flujo.querySelector(".el-home-section-lead");
    var boxes = flujo.querySelectorAll(".el-home-fea-box");

    gsap.killTweensOf([title, lead].concat(Array.prototype.slice.call(boxes)));

    var tl = gsap.timeline({ defaults: { ease: "power4.out" } });
    gsap.set([title, lead, boxes], { clearProps: "transform,opacity" });

    tl.from(title, { y: -56, opacity: 0, duration: 0.65 })
      .from(lead, { y: -40, opacity: 0, duration: 0.55 }, "-=0.35")
      .from(
        boxes,
        {
          y: 70,
          opacity: 0,
          stagger: 0.14,
          duration: 0.75,
          x: function (i) {
            if (i === 0) return -60;
            if (i === 2) return 60;
            return 0;
          },
        },
        "-=0.25"
      );
  }

  home.querySelectorAll('a[href="#flujo"]').forEach(function (link) {
    link.addEventListener("click", function (e) {
      e.preventDefault();
      var flujo = document.getElementById("flujo");
      if (!flujo) return;

      var y = flujo.getBoundingClientRect().top + window.scrollY - scrollOffsetY();

      if (typeof ScrollToPlugin !== "undefined") {
        gsap.to(window, {
          duration: 1.15,
          scrollTo: { y: y, autoKill: true },
          ease: "power3.inOut",
          onComplete: playFlujoSequence,
        });
      } else {
        window.scrollTo({ top: y, behavior: "smooth" });
        window.setTimeout(playFlujoSequence, 650);
      }
    });
  });

  if (window.location.hash === "#flujo") {
    window.setTimeout(playFlujoSequence, 500);
  }

  window.addEventListener("load", function () {
    ScrollTrigger.refresh();
  });
})();
