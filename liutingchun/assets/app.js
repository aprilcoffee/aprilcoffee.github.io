(function () {
  'use strict';

  var DRAFT_KEY = 'ltc-draft';
  var main = document.getElementById('main');
  var side = document.getElementById('side');
  var DATA = null;

  // ---------- helpers ----------
  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function linkify(s) {
    return esc(s).replace(/https?:\/\/[^\s<]+/g, function (u) {
      return '<a href="' + u + '" target="_blank" rel="noopener">' + u + '</a>';
    });
  }

  // Blank-line separated paragraphs; a paragraph starting with "# " is a heading.
  function prose(text) {
    if (!text) return '';
    return text.split(/\n\s*\n/).map(function (p) {
      p = p.trim();
      if (!p) return '';
      if (p.indexOf('# ') === 0) return '<h3>' + esc(p.slice(2)) + '</h3>';
      return '<p>' + linkify(p).replace(/\n/g, '<br>') + '</p>';
    }).join('');
  }

  // Wix images are served resized; everything else as-is.
  function src(url, w) {
    if (!url) return '';
    if (!/^(https?:)?\/\//.test(url)) return url.replace(/^\//, '');
    var m = url.match(/^https:\/\/static\.wixstatic\.com\/media\/([^/?#]+)$/);
    if (!m || /\.gif$/i.test(m[1])) return url;
    return url + '/v1/fit/w_' + w + ',h_' + w + ',q_85,enc_auto/' + m[1];
  }

  function img(url, w, alt) {
    return '<img src="' + esc(src(url, w)) + '" data-orig="' + esc(url) +
      '" alt="' + esc(alt || '') + '" loading="lazy" onerror="if(this.dataset.orig&&this.src!==this.dataset.orig)this.src=this.dataset.orig">';
  }

  function videoId(url) {
    var m;
    if (!url) return null;
    if ((m = url.match(/vimeo\.com\/(?:video\/)?(\d+)/))) return { kind: 'vimeo', id: m[1] };
    if ((m = url.match(/(?:youtu\.be\/|v=|embed\/)([\w-]{11})/))) return { kind: 'youtube', id: m[1] };
    if (/\.(mp4|mov|webm)(\?|$)/.test(url)) return { kind: 'file', id: url };
    return null;
  }

  function embed(url) {
    var v = videoId(url);
    if (!v) return '';
    if (v.kind === 'file') return '<div class="embed"><video controls preload="none" playsinline src="' + esc(v.id) + '"></video></div>';
    var s = v.kind === 'vimeo'
      ? 'https://player.vimeo.com/video/' + v.id + '?dnt=1'
      : 'https://www.youtube-nocookie.com/embed/' + v.id;
    return '<div class="embed"><iframe src="' + s + '" loading="lazy" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen></iframe></div>';
  }

  function coverOf(w) {
    if (w.cover) return w.cover;
    if (w.images && w.images.length) return w.images[0];
    var v = videoId(w.video);
    if (v && v.kind === 'vimeo') return 'https://vumbnail.com/' + v.id + '.jpg';
    if (v && v.kind === 'youtube') return 'https://i.ytimg.com/vi/' + v.id + '/hqdefault.jpg';
    return '';
  }

  function visibleWorks() {
    return DATA.works.filter(function (w) { return !w.hidden; });
  }

  function setMeta(title, desc) {
    var s = DATA.site;
    document.title = title ? title + ' — ' + s.name : s.name + ' ' + (s.name_zh || '');
    var d = document.querySelector('meta[name="description"]');
    if (d) d.setAttribute('content', desc || s.description || '');
  }

  // ---------- views ----------
  var views = {
    home: function () {
      var s = DATA.site;
      setMeta('', s.description);
      main.classList.add('full');
      return '<section class="home">' +
        (s.home_image ? img(s.home_image, 2400, s.name) : '') +
        '</section>';
    },

    works: function () {
      setMeta('Works');
      return '<h1 class="page-title">Works</h1><div class="grid">' +
        visibleWorks().map(function (w) {
          var c = coverOf(w);
          return '<a class="card" href="#/works/' + esc(w.slug) + '">' +
            '<div class="thumb">' + (c ? img(c, 900, w.title) : '<span class="ph">' + esc(w.title) + '</span>') + '</div>' +
            '<div class="cap"><span>' + esc(w.title) +
            (w.title_zh ? ' <span class="zh">' + esc(w.title_zh) + '</span>' : '') +
            '</span><span class="mono">' + esc(w.year) + '</span></div></a>';
        }).join('') + '</div>';
    },

    work: function (slug) {
      var list = visibleWorks();
      var w = DATA.works.filter(function (x) { return x.slug === slug; })[0];
      if (!w) return views.notfound();
      setMeta(w.title, (w.text || '').split('\n')[0].slice(0, 200));

      var rows = [
        ['Year', esc(w.year)],
        ['Type', esc(w.type)],
        ['Materials', esc(w.materials)],
        ['With', esc(w.collaborators)]
      ];
      (w.links || []).forEach(function (l) {
        if (l.url) rows.push(['Link', '<a href="' + esc(l.url) + '" target="_blank" rel="noopener">' + esc(l.label || l.url) + '</a>']);
      });

      var i = list.indexOf(w);
      var prev = i > 0 ? list[i - 1] : null;
      var next = i >= 0 && i < list.length - 1 ? list[i + 1] : null;

      return '<article class="work"><aside class="work-info"><span class="idx">(' + (i + 1) + ')</span>' +
        '<h1>' + esc(w.title) + '</h1>' +
        (w.title_zh ? '<p class="zh">' + esc(w.title_zh) + '</p>' : '') +
        '<dl class="meta">' + rows.filter(function (r) { return r[1]; }).map(function (r) {
          return '<dt>' + r[0] + '</dt><dd>' + r[1] + '</dd>';
        }).join('') + '</dl>' +
        '<div class="prose">' + prose(w.text) + '</div>' +
        (w.credits ? '<p class="credits">' + esc(w.credits) + '</p>' : '') + '</aside>' +
        '<div class="plates">' + embed(w.video) +
        (w.images || []).map(function (u, k) {
          return '<figure' + (k === 0 && !w.video ? ' class="hero"' : '') + '>' + img(u, 2000, w.title) + '</figure>';
        }).join('') + '</div>' +
        '<nav class="pager">' +
        (prev ? '<a href="#/works/' + esc(prev.slug) + '"><span class="mono">←</span><span class="t">' + esc(prev.title) + '</span></a>' : '<span></span>') +
        (next ? '<a href="#/works/' + esc(next.slug) + '"><span class="mono">→</span><span class="t">' + esc(next.title) + '</span></a>' : '<span></span>') +
        '</nav></article>';
    },

    performance: function () {
      setMeta('Performance', 'Audio-visual performance records of Ting-Chun Liu.');
      return '<h1 class="page-title">Audio-Visual Performance</h1><div class="perf">' +
        DATA.performances.map(function (p) {
          return '<div>' + embed(p.video) + '<h3>' + esc(p.title) + '</h3><p>' + esc(p.note) + '</p></div>';
        }).join('') + '</div>';
    },

    about: function () {
      var a = DATA.about, s = DATA.site;
      setMeta('About', a.bio);
      return '<h1 class="page-title">About</h1><p class="bio">' + esc(a.bio) + '</p>' +
        a.sections.map(function (sec) {
          return '<section class="cv-sec"><h2>' + esc(sec.title) + '</h2><div>' +
            sec.items.map(function (it) {
              var t = it.url
                ? '<a href="' + esc(it.url) + '" target="_blank" rel="noopener">' + esc(it.text) + '</a>'
                : esc(it.text);
              return '<div class="cv-row"><span class="mono">' + esc(it.year) + '</span><span>' + t + '</span></div>';
            }).join('') + '</div></section>';
        }).join('') +
        '<p class="contact">Contact: <a href="mailto:' + esc(s.email) + '">' + esc(s.email) + '</a></p>';
    },

    writing: function () {
      setMeta('Blog Archive');
      return '<h1 class="page-title">Blog Archive</h1><ul class="list writing">' +
        (DATA.writing || []).filter(function (p) { return !p.hidden; }).map(function (p) {
          return '<li><a href="#/writing/' + esc(p.slug) + '">' +
            '<span class="mono">' + esc(p.date) + '</span><span class="wt">' + esc(p.title) + '<small>' + esc(p.excerpt) + '</small></span>' +
            '<span class="mono">' + esc(p.category) + '</span></a></li>';
        }).join('') + '</ul>';
    },

    post: function (slug) {
      var p = (DATA.writing || []).filter(function (x) { return x.slug === slug; })[0];
      if (!p) return views.notfound();
      setMeta(p.title, p.excerpt);
      var box = '<article class="post"><aside class="post-info"><h1>' + esc(p.title) + '</h1><dl class="meta"><dt>Date</dt><dd>' +
        esc(p.date) + '</dd><dt>Category</dt><dd>' + esc(p.category) + '</dd></dl></aside>' +
        '<div class="prose post-body" id="postBody">Loading…</div></article>';
      var local = null;
      try { local = localStorage.getItem('ltc-post-' + slug); } catch (e) {}
      (local != null ? Promise.resolve(local) : fetch('posts/' + encodeURIComponent(slug) + '.md', { cache: 'no-cache' }).then(function (r) { return r.text(); }))
        .then(function (md) {
          // a video URL alone on a line becomes a player, as on the real site
          md = md.replace(/^(https?:\/\/\S+|\S+\.(?:mp4|mov|webm))$/gm, function (u) { return embed(u) ? '\n' + embed(u) + '\n' : '<' + u + '>'; });
          var el = document.getElementById('postBody');
          if (el) el.innerHTML = window.marked ? marked.parse(md, { breaks: true }) : '<pre>' + esc(md) + '</pre>';
        });
      return box;
    },

    friends: function () {
      setMeta('Friends');
      return '<h1 class="page-title">Friends</h1><div class="grid friends">' +
        DATA.friends.map(function (f) {
          return '<a class="card" href="' + esc(f.url) + '" target="_blank" rel="noopener"><div class="thumb">' +
            (f.image ? img(f.image, 600, f.name) : '<span class="ph">' + esc(f.name) + '</span>') +
            '</div><div class="cap"><span>' + esc(f.name) + '</span><span class="mono">↗</span></div></a>';
        }).join('') + '</div>';
    },

    notfound: function () {
      setMeta('Not found');
      return '<h1 class="page-title">Not found</h1><p><a href="#/works">← Works</a></p>';
    }
  };

  // ---------- router ----------
  function route() {
    var parts = (location.hash.replace(/^#\/?/, '') || '').split('/').filter(Boolean);
    var html;
    main.classList.remove('full');
    if (!parts.length) html = views.home();
    else if (parts[0] === 'works' && parts[1]) html = views.work(decodeURIComponent(parts[1]));
    else if (parts[0] === 'writing' && parts[1]) html = views.post(decodeURIComponent(parts[1]));
    else if (views[parts[0]] && ['work', 'post', 'home'].indexOf(parts[0]) < 0) html = views[parts[0]]();
    else html = views.notfound();
    main.innerHTML = html;

    var key = parts[0] || '';
    Array.prototype.forEach.call(document.querySelectorAll('.nav a'), function (a) {
      a.classList.toggle('on', a.getAttribute('href') === '#/' + key);
    });
    side.classList.remove('open');
    document.getElementById('menuBtn').setAttribute('aria-expanded', 'false');
    window.scrollTo(0, 0);
  }

  function renderShell() {
    var s = DATA.site;
    Array.prototype.forEach.call(document.querySelectorAll('[data-bind]'), function (el) {
      el.textContent = s[el.getAttribute('data-bind')] || '';
    });
    document.getElementById('sideFoot').innerHTML =
      '<div><a href="mailto:' + esc(s.email) + '">' + esc(s.email) + '</a></div>' +
      '<div class="links">' + (s.links || []).map(function (l) {
        return '<a href="' + esc(l.url) + '" target="_blank" rel="noopener">' + esc(l.label) + '</a>';
      }).join('') + '</div>' +
      '<div>© ' + new Date().getFullYear() + ' ' + esc(s.name) + '</div>';
  }

  document.getElementById('menuBtn').addEventListener('click', function () {
    var open = side.classList.toggle('open');
    this.setAttribute('aria-expanded', open ? 'true' : 'false');
  });

  // ---------- boot ----------
  function start(data) {
    DATA = data;
    renderShell();
    route();
    window.addEventListener('hashchange', route);
  }

  var draft = null;
  if (/[?&]preview\b/.test(location.search)) {
    try { draft = JSON.parse(localStorage.getItem(DRAFT_KEY)); } catch (e) { draft = null; }
  }
  if (draft) {
    var flag = document.createElement('div');
    flag.className = 'preview-flag';
    flag.textContent = 'Preview (unpublished draft)';
    document.body.appendChild(flag);
    start(draft);
  } else {
    fetch('data/site.json', { cache: 'no-cache' })
      .then(function (r) { return r.json(); })
      .then(start)
      .catch(function () { main.innerHTML = '<p class="loading">Could not load data/site.json</p>'; });
  }
})();
