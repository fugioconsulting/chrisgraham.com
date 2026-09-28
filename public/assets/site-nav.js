/* One nav for every page on chrisgraham.com (2026-09 redesign).
   Injected so each page stays a plain HTML file. */
(function () {
  var LINKS = [
    { label: 'AI Coaching', href: '/coaching' },
    { label: 'Pete the Pigeon', href: '/pete' },
    { label: 'Employee Ownership', href: '/pete#employee-ownership' },
    { label: 'About', href: '/about' },
    { label: 'Podcast', href: 'https://champeonsofemployeeownership.com' }
  ];
  function build() {
    if (document.querySelector('.nav')) return;
    var here = location.pathname.replace(/\.html$/, '').replace(/\/$/, '') || '/';
    var nav = document.createElement('nav');
    nav.className = 'nav';
    var html = '<div class="nav-in"><a class="brand" href="/">Chris Graham</a>' +
      '<button class="burger" type="button" aria-label="Menu" aria-expanded="false"><span></span><span></span><span></span></button>' +
      '<div class="links">';
    LINKS.forEach(function (l) {
      var cur = l.href === here ? ' aria-current="page"' : '';
      html += '<a href="' + l.href + '"' + cur + '>' + l.label + '</a>';
    });
    html += '<a class="btn" href="/#book">Book a demo</a></div></div>';
    nav.innerHTML = html;
    document.body.insertBefore(nav, document.body.firstChild);
    var b = nav.querySelector('.burger');
    b.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      b.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    nav.querySelectorAll('.links a').forEach(function (a) {
      a.addEventListener('click', function () { nav.classList.remove('open'); });
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', build); else build();
})();
