(function () {
  'use strict';

  // Links from the first version of the site used #/works/slug style URLs.
  var m = location.hash.match(/^#\/(.*)$/);
  if (m) {
    var base = document.querySelector('.brand').getAttribute('href');
    location.replace(base + (m[1] ? m[1].replace(/\/?$/, '/') : ''));
    return;
  }

  var side = document.getElementById('side');
  var btn = document.getElementById('menuBtn');
  btn.addEventListener('click', function () {
    var open = side.classList.toggle('open');
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
  });

  // Video thumbnails turn into the player on click.
  document.addEventListener('click', function (e) {
    var el = e.target.closest && e.target.closest('.embed.lite');
    if (!el) return;
    var f = document.createElement('iframe');
    f.src = el.getAttribute('data-src');
    f.allow = 'autoplay; fullscreen; picture-in-picture';
    f.allowFullscreen = true;
    var wrap = document.createElement('div');
    wrap.className = 'embed';
    wrap.appendChild(f);
    el.replaceWith(wrap);
  });
})();
