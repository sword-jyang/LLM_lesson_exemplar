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
})();
