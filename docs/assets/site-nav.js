/* One nav for every page on chrisgraham.com.
   Desktop: minimal links, upper right, same font and colour as the site.
   Mobile: a hamburger in the upper LEFT (Chris's call) opening a full screen menu.
   Injected rather than pasted into each page because index.html is a funnel
   export that should not be hand-edited more than it has to be. */
(function () {
  var LINKS = [
    { label: 'Home', href: '/' },
    { label: 'Podcasting', href: 'https://thechampeons.com/' },
    { label: 'AI Coaching', href: '/coaching' },
    { label: 'Employee Ownership', href: '/pete#employee-ownership' },
    { label: 'Pete the Pigeon', href: '/pete' }
  ];

  var CSS = [
    '#cg-nav{position:fixed;top:0;left:0;right:0;z-index:9000;pointer-events:none;',
    '  font-family:"Open Sans",Helvetica,Arial,sans-serif;}',
    '#cg-nav .cg-nav-in{display:flex;align-items:center;justify-content:flex-end;gap:26px;',
    '  max-width:1200px;margin:0 auto;padding:18px 24px;}',
    '#cg-nav a{pointer-events:auto;font-size:12px;letter-spacing:.18em;text-transform:uppercase;',
    '  color:rgba(255,255,255,.62);text-decoration:none;white-space:nowrap;}',
    '#cg-nav a:hover{color:rgb(193,151,238);}',
    '#cg-burger{display:none;pointer-events:auto;position:fixed;top:14px;left:14px;z-index:9100;',
    '  width:42px;height:42px;padding:10px;border:0;background:rgba(0,0,0,.55);border-radius:4px;cursor:pointer;}',
    '#cg-burger span{display:block;height:2px;margin:4px 0;background:#fff;border-radius:2px;',
    '  transition:transform .2s,opacity .2s;}',
    '#cg-burger[aria-expanded="true"] span:nth-child(1){transform:translateY(6px) rotate(45deg);}',
    '#cg-burger[aria-expanded="true"] span:nth-child(2){opacity:0;}',
    '#cg-burger[aria-expanded="true"] span:nth-child(3){transform:translateY(-6px) rotate(-45deg);}',
    '#cg-nav a[aria-current="page"],#cg-sheet a[aria-current="page"]{color:rgb(193,151,238);}',
    '#cg-nav a:focus-visible,#cg-sheet a:focus-visible,#cg-burger:focus-visible{outline:2px solid rgb(193,151,238);outline-offset:3px;}',
    '#cg-sheet{position:fixed;inset:0;z-index:9050;background:#000;display:none;',
    '  flex-direction:column;align-items:flex-start;justify-content:center;gap:26px;padding:0 34px;}',
    '#cg-sheet.open{display:flex;}',
    '#cg-sheet a{pointer-events:auto;font-family:"EB Garamond",Georgia,serif;font-size:30px;',
    '  letter-spacing:0;text-transform:none;color:#fff;text-decoration:none;}',
    '#cg-sheet a:hover{color:rgb(193,151,238);}',
    '@media (max-width:759px){#cg-nav .cg-nav-in{display:none;}#cg-burger{display:block;}}'
  ].join('\n');

  function markCurrent(a, l) {
    var path = location.pathname.replace(/\/index\.html$/, '/').replace(/\.html$/, '');
    if (path.length > 1) path = path.replace(/\/$/, '');
    if (l.href === path) a.setAttribute('aria-current', 'page');
  }

  function build() {
    if (document.getElementById('cg-nav')) return;

    var style = document.createElement('style');
    style.id = 'cg-nav-style';
    style.textContent = CSS;
    document.head.appendChild(style);

    var bar = document.createElement('div');
    bar.id = 'cg-nav';
    var inner = document.createElement('div');
    inner.className = 'cg-nav-in';
    LINKS.forEach(function (l) {
      var a = document.createElement('a');
      a.href = l.href;
      a.textContent = l.label;
      markCurrent(a, l);
      inner.appendChild(a);
    });
    bar.appendChild(inner);

    var sheet = document.createElement('div');
    sheet.id = 'cg-sheet';
    LINKS.forEach(function (l) {
      var a = document.createElement('a');
      a.href = l.href;
      a.textContent = l.label;
      markCurrent(a, l);
      sheet.appendChild(a);
    });

    var burger = document.createElement('button');
    burger.id = 'cg-burger';
    burger.type = 'button';
    burger.setAttribute('aria-label', 'Menu');
    burger.setAttribute('aria-expanded', 'false');
    burger.innerHTML = '<span></span><span></span><span></span>';

    function setOpen(open) {
      sheet.classList.toggle('open', open);
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
      burger.setAttribute('aria-label', open ? 'Close menu' : 'Menu');
      document.documentElement.style.overflow = open ? 'hidden' : '';
      if (open) {
        var first = sheet.querySelector('a');
        if (first) first.focus();
      }
    }
    burger.addEventListener('click', function () {
      setOpen(!sheet.classList.contains('open'));
    });
    sheet.addEventListener('click', function (e) {
      if (e.target === sheet || e.target.tagName === 'A') setOpen(false);
    });
    document.addEventListener('keydown', function (e) {
      if (!sheet.classList.contains('open')) return;
      if (e.key === 'Escape') {
        setOpen(false);
        burger.focus();
      } else if (e.key === 'Tab') {
        // Trap focus: sheet links plus the burger (which closes the sheet).
        var items = Array.prototype.slice.call(sheet.querySelectorAll('a'));
        items.push(burger);
        var i = items.indexOf(document.activeElement);
        var next = e.shiftKey ? (i <= 0 ? items.length - 1 : i - 1)
                              : (i < 0 || i === items.length - 1 ? 0 : i + 1);
        e.preventDefault();
        items[next].focus();
      }
    }, true);

    document.body.appendChild(bar);
    document.body.appendChild(sheet);
    document.body.appendChild(burger);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', build);
  } else {
    build();
  }
})();
