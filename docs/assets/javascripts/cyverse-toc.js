(function () {
  var path = window.location.pathname.replace(/\/+$/, "");
  if (path.endsWith("/cyverse")) {
    document.body.classList.add("oasis-cyverse-page");
  }
})();
