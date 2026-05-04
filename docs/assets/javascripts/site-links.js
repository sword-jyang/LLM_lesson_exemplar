(function () {
  var headerLogo = document.querySelector(".md-header .md-logo[data-md-component='logo']");
  var sidebarLogo = document.querySelector(".md-sidebar--primary .md-nav__button.md-logo[data-md-component='logo']");

  if (headerLogo) {
    headerLogo.href = "https://cu-esiil.github.io/home/";
    headerLogo.title = "ESIIL home";
    headerLogo.setAttribute("aria-label", "ESIIL home");
  }

  if (sidebarLogo) {
    sidebarLogo.href = "https://cu-esiil.github.io/LLM_lesson_exemplar/";
    sidebarLogo.title = "Geospatial Harmonization with LLMs home";
    sidebarLogo.setAttribute("aria-label", "Geospatial Harmonization with LLMs home");
  }

  document.querySelectorAll(".md-content__inner").forEach(function (content) {
    var title = content.querySelector(":scope > h1");
    var hero = content.querySelector(":scope > p > img.page-hero");

    if (title && hero) {
      content.insertBefore(hero.parentElement, title);
    }
  });
})();
