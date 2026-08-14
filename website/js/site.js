(function () {
  var nav = document.querySelector(".nav");
  var btn = document.querySelector(".nav-toggle");
  if (!nav || !btn) return;
  btn.addEventListener("click", function () {
    var open = nav.classList.toggle("open");
    btn.setAttribute("aria-expanded", open ? "true" : "false");
  });
})();
