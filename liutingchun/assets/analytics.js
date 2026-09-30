/* Google Analytics 4, loaded only after consent (Consent Mode "basic").
   Before a visitor clicks OK nothing is sent to Google. The choice is stored per browser
   and shared by every page on aprilcoffee.github.io (liutingchun/, sun/, heat_as_image/).

   <script async src="/liutingchun/assets/analytics.js" data-ga="G-XXXX" data-banner></script>
   data-banner: show the consent notice on this page (only the main site does).
   Any element with [data-consent-reset] clears the choice (used on the privacy page). */
(function () {
  'use strict';
  var me = document.currentScript;
  var id = me && me.getAttribute('data-ga');
  if (!id || /[?&]preview\b/.test(location.search)) return;

  var KEY = 'ga-consent';
  var choice = null;
  try { choice = localStorage.getItem(KEY); } catch (e) {}

  function start() {
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag('consent', 'default', {
      analytics_storage: 'granted', ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied'
    });
    window.gtag('js', new Date());
    window.gtag('config', id);
    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(id);
    document.head.appendChild(s);
  }

  function ready(fn) {
    if (document.body) fn(); else document.addEventListener('DOMContentLoaded', fn);
  }

  ready(function () {
    document.querySelectorAll('[data-consent-reset]').forEach(function (b) {
      b.addEventListener('click', function () {
        try { localStorage.removeItem(KEY); } catch (e) {}
        location.reload();
      });
    });
  });

  if (choice === 'granted') { start(); return; }
  if (choice || !me.hasAttribute('data-banner')) return;

  ready(function () {
    var base = me.getAttribute('src').replace(/assets\/analytics\.js.*$/, '');
    var box = document.createElement('div');
    box.className = 'consent';
    box.setAttribute('role', 'dialog');
    box.setAttribute('aria-label', 'Analytics');
    // in the language of the page (other project pages without a matching lang get all three)
    var T = {
      en: ['May this site use Google Analytics (with cookies) to count visits?', 'Privacy', 'No'],
      de: ['Darf diese Website Google Analytics (mit Cookies) verwenden, um Besuche zu zählen?', 'Datenschutz', 'Nein'],
      zh: ['本網站可以使用 Google Analytics（含 cookie）統計瀏覽嗎？', '隱私權', '不要']
    };
    var t = T[(document.documentElement.lang || '').slice(0, 2)] ||
      [T.en[0] + '<br>' + T.zh[0] + '<br>' + T.de[0], 'Datenschutz / Privacy', 'No'];
    box.innerHTML = '<p>' + t[0] + '</p>' +
      '<a class="note" href="' + base + 'datenschutz/">' + t[1] + '</a>' +
      '<button type="button" class="no">' + t[2] + '</button><button type="button" class="ok">OK</button>';
    function decide(v) {
      try { localStorage.setItem(KEY, v); } catch (e) {}
      if (v === 'granted') start();
      box.remove();
    }
    box.querySelector('.ok').onclick = function () { decide('granted'); };
    box.querySelector('.no').onclick = function () { decide('denied'); };
    document.body.appendChild(box);
  });
})();
