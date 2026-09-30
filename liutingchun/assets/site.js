(function () {
  'use strict';

  var me = document.currentScript;

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
    f.title = el.getAttribute('aria-label') || 'Video';
    var wrap = document.createElement('div');
    wrap.className = 'embed';
    wrap.appendChild(f);
    el.replaceWith(wrap);
  });

  // p5.js effects: loaded only when a page has one, after everything else is done,
  // so they never compete with the content for bandwidth.
  if (!me || !document.querySelector('[data-effect]')) return;
  function load(src, cb) {
    var s = document.createElement('script');
    s.src = src;
    s.async = true;
    s.onload = cb;
    document.body.appendChild(s);
  }
  function start() {
    var idle = window.requestIdleCallback || function (f) { setTimeout(f, 200); };
    idle(function () {
      load(me.getAttribute('data-p5'), function () { load(me.getAttribute('data-effects')); });
    });
  }
  if (document.readyState === 'complete') start();
  else window.addEventListener('load', start);
})();
