(function () {
  'use strict';

  var DRAFT_KEY = 'ltc-draft';
  var GH_KEY = 'ltc-github';
  var main = document.getElementById('main');
  var POST_KEY = 'ltc-post-';   // + slug: unpublished Markdown body
  var DIRTY_KEY = 'ltc-posts-dirty';
  var D = null;          // site data being edited
  var tab = 'works';
  var sel = 0;           // selected work index
  var psel = 0;          // selected post index

  // ---------- storage ----------
  function save() {
    try { localStorage.setItem(DRAFT_KEY, JSON.stringify(D)); } catch (e) {}
    document.getElementById('saved').textContent = '草稿已存 ' + new Date().toLocaleTimeString();
  }
  function gh() {
    var def = { owner: 'aprilcoffee', repo: 'aprilcoffee.github.io', branch: 'main', dir: 'liutingchun', token: '' };
    try { return Object.assign(def, JSON.parse(localStorage.getItem(GH_KEY)) || {}); } catch (e) { return def; }
  }
  function setGh(c) { try { localStorage.setItem(GH_KEY, JSON.stringify(c)); } catch (e) {} }

  // Post bodies live in posts/<slug>.md; edits are kept locally until published.
  function dirtyPosts() {
    try { return JSON.parse(localStorage.getItem(DIRTY_KEY)) || []; } catch (e) { return []; }
  }
  function setPostBody(slug, text) {
    try {
      localStorage.setItem(POST_KEY + slug, text);
      var d = dirtyPosts();
      if (d.indexOf(slug) < 0) { d.push(slug); localStorage.setItem(DIRTY_KEY, JSON.stringify(d)); }
    } catch (e) {}
    document.getElementById('saved').textContent = '草稿已存 ' + new Date().toLocaleTimeString();
  }
  function getPostBody(slug) {
    var local = null;
    try { local = localStorage.getItem(POST_KEY + slug); } catch (e) {}
    if (local != null) return Promise.resolve(local);
    return fetch('../posts/' + encodeURIComponent(slug) + '.md', { cache: 'no-cache' })
      .then(function (r) { return r.ok ? r.text() : ''; });
  }
  function clearPostDrafts() {
    try {
      dirtyPosts().forEach(function (s) { localStorage.removeItem(POST_KEY + s); });
      localStorage.removeItem(DIRTY_KEY);
    } catch (e) {}
  }

  // ---------- tiny DOM helpers ----------
  function h(tag, attrs, kids) {
    var el = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) {
      if (k === 'on') Object.keys(attrs.on).forEach(function (ev) { el.addEventListener(ev, attrs.on[ev]); });
      else if (k === 'text') el.textContent = attrs[k];
      else if (k in el && k !== 'list') el[k] = attrs[k];
      else el.setAttribute(k, attrs[k]);
    });
    [].concat(kids || []).forEach(function (c) {
      if (c != null) el.appendChild(typeof c === 'string' ? document.createTextNode(c) : c);
    });
    return el;
  }
  function btn(text, fn, cls) { return h('button', { className: 'btn ' + (cls || ''), text: text, type: 'button', on: { click: fn } }); }

  // text input bound to obj[key]
  function field(label, obj, key, opts) {
    opts = opts || {};
    var input = opts.area
      ? h('textarea', { className: opts.cls || '', value: obj[key] || '' })
      : h('input', { type: 'text', value: obj[key] || '', placeholder: opts.ph || '' });
    input.addEventListener('input', function () { obj[key] = input.value; save(); if (opts.after) opts.after(); });
    return h('label', {}, [label, input]);
  }

  // list of objects edited as "a | b | c" lines
  function lines(label, owner, key, cols, hint, cls) {
    function ser(arr) {
      return (arr || []).map(function (o) {
        return cols.map(function (c) { return o[c] || ''; }).join(' | ').replace(/( \| )+$/, '');
      }).join('\n');
    }
    function parse(txt) {
      return txt.split('\n').map(function (l) { return l.trim(); }).filter(Boolean).map(function (l) {
        var parts = l.split(' | '), o = {};
        cols.forEach(function (c, i) {
          // the last column takes whatever remains
          o[c] = (i === cols.length - 1 ? parts.slice(i).join(' | ') : parts[i] || '').trim();
        });
        return o;
      });
    }
    var ta = h('textarea', { className: 'lines ' + (cls || ''), value: ser(owner[key]) });
    ta.addEventListener('input', function () { owner[key] = parse(ta.value); save(); });
    return h('div', { className: 'stack', style: 'gap:4px' }, [
      h('label', {}, [label, ta]),
      hint ? h('p', { className: 'hint', style: 'margin:0', text: hint }) : null
    ]);
  }

  function bar(title, right) {
    return h('div', { className: 'bar' }, [h('h2', { text: title })].concat(right || []));
  }

  function resolve(url) {
    if (!url) return '';
    return /^(https?:)?\/\//.test(url) ? url : '../' + url.replace(/^\//, '');
  }

  // ---------- tabs ----------
  var tabs = {};

  tabs.works = function () {
    var works = D.works;
    if (sel >= works.length) sel = works.length - 1;

    var list = h('div', { className: 'items' }, works.map(function (w, i) {
      return h('div', {
        className: 'item' + (i === sel ? ' on' : '') + (w.hidden ? ' off' : ''),
        on: { click: function () { sel = i; render(); } }
      }, [h('span', { text: w.title || '(untitled)' }), h('span', { className: 'y', text: w.year || '' })]);
    }));

    var w = works[sel];
    var editor = w ? workForm(w) : h('p', { text: '還沒有作品。' });

    main.append(
      bar('作品 Works', [
        btn('+ 新增作品', function () {
          works.unshift({ slug: 'new-work-' + Date.now().toString(36), title: 'New work', title_zh: '', year: String(new Date().getFullYear()),
            type: '', materials: '', collaborators: '', cover: '', images: [], video: '', links: [], credits: '', text: '', hidden: true });
          sel = 0; save(); render();
        }, 'primary')
      ]),
      h('div', { className: 'split' }, [list, editor])
    );
  };

  function workForm(w) {
    var thumbs = h('div', { className: 'thumbs' });
    function drawThumbs() {
      thumbs.innerHTML = '';
      [w.cover].concat(w.images || []).filter(Boolean).forEach(function (u) {
        thumbs.appendChild(h('img', { src: resolve(u), loading: 'lazy' }));
      });
    }
    drawThumbs();

    var imagesTa = h('textarea', { className: 'lines', value: (w.images || []).join('\n') });
    imagesTa.addEventListener('input', function () {
      w.images = imagesTa.value.split('\n').map(function (s) { return s.trim(); }).filter(Boolean);
      save(); drawThumbs();
    });

    var upload = h('input', { type: 'file', accept: 'image/*', multiple: true, style: 'display:none' });
    var upStatus = h('span', { className: 'status' });
    upload.addEventListener('change', function () {
      var files = Array.prototype.slice.call(upload.files);
      if (!files.length) return;
      var c = gh();
      if (!c.token) { alert('請先到「發佈」頁填入 GitHub token。'); return; }
      var done = 0;
      upStatus.textContent = '上傳中…';
      files.reduce(function (p, f) {
        return p.then(function () {
          var name = f.name.toLowerCase().replace(/[^a-z0-9._-]+/g, '-');
          var rel = 'images/' + (w.slug || 'misc') + '/' + name;
          return readB64(f).then(function (b64) {
            return putFile(c, c.dir + '/' + rel, b64, 'Upload image ' + rel);
          }).then(function () {
            w.images = (w.images || []).concat(rel);
            imagesTa.value = w.images.join('\n');
            done++; upStatus.textContent = '已上傳 ' + done + '/' + files.length;
            save(); drawThumbs();
          });
        });
      }, Promise.resolve()).catch(function (e) { upStatus.textContent = '上傳失敗：' + e.message; });
      upload.value = '';
    });

    var i = D.works.indexOf(w);
    function move(d) {
      var j = i + d;
      if (j < 0 || j >= D.works.length) return;
      D.works.splice(j, 0, D.works.splice(i, 1)[0]);
      sel = j; save(); render();
    }

    var hidden = h('input', { type: 'checkbox', checked: !!w.hidden });
    hidden.addEventListener('change', function () { w.hidden = hidden.checked; save(); render(); });

    return h('div', { className: 'form' }, [
      h('div', { className: 'actions' }, [
        btn('↑ 上移', function () { move(-1); }, 'sm'),
        btn('↓ 下移', function () { move(1); }, 'sm'),
        h('a', { className: 'btn sm', href: '../preview.html?preview#/works/' + encodeURIComponent(w.slug), target: 'ltc-preview', text: '預覽 ↗', style: 'text-decoration:none' }),
        btn('刪除', function () {
          if (confirm('刪除「' + w.title + '」？')) { D.works.splice(i, 1); save(); render(); }
        }, 'sm danger'),
        h('label', { className: 'check', style: 'margin-left:auto' }, [hidden, '隱藏（不顯示在網站）'])
      ]),
      h('div', { className: 'row' }, [
        field('標題 Title', w, 'title', { after: function () { document.querySelector('.item.on span').textContent = w.title; } }),
        field('中文標題', w, 'title_zh')
      ]),
      h('div', { className: 'row' }, [
        field('網址代稱 slug（只用英文小寫與 -）', w, 'slug'),
        field('年份 Year', w, 'year')
      ]),
      h('div', { className: 'row' }, [field('形式 Type', w, 'type'), field('媒材 Materials', w, 'materials')]),
      h('div', { className: 'row' }, [field('形式（德文 DE）', w, 'type_de'), field('媒材（德文 DE）', w, 'materials_de')]),
      h('div', { className: 'row' }, [field('形式（中文）', w, 'type_zh'), field('媒材（中文）', w, 'materials_zh')]),
      h('div', { className: 'row' }, [field('合作 With', w, 'collaborators'), field('影片 Vimeo / YouTube 網址', w, 'video')]),
      field('說明文字 English（空一行＝分段；以「# 」開頭＝小標題）', w, 'text', { area: true, cls: 'tall' }),
      field('說明文字 Deutsch（留空＝德文頁顯示英文）', w, 'text_de', { area: true, cls: 'tall' }),
      field('說明文字 中文（留空＝中文頁顯示英文）', w, 'text_zh', { area: true, cls: 'tall' }),
      field('Credits（每行一條）', w, 'credits', { area: true }),
      lines('連結（每行：名稱 | 網址）', w, 'links', ['label', 'url']),
      field('封面圖（留空＝用第一張圖）', w, 'cover', { after: drawThumbs }),
      h('label', {}, ['圖片（每行一個網址或 images/… 路徑）', imagesTa]),
      h('div', { className: 'actions' }, [btn('上傳圖片到 GitHub…', function () { upload.click(); }, 'sm'), upStatus, upload]),
      thumbs
    ]);
  }

  tabs.performances = function () {
    main.append(
      bar('表演影片 Performance'),
      h('div', { className: 'form' }, [
        lines('每行一支：標題 | 說明 | Vimeo/YouTube 網址 | 縮圖（選填）| 說明 DE | 說明 中文', D, 'performances', ['title', 'note', 'video', 'thumb', 'note_de', 'note_zh'], '順序即網站上的順序。點擊會在新分頁開啟 Vimeo / YouTube。沒有縮圖時自動用 Vimeo / YouTube 的縮圖。', 'tall')
      ])
    );
  };

  tabs.about = function () {
    var a = D.about;
    var box = h('div', { className: 'form' }, [field('簡介 Bio (English)', a, 'bio', { area: true }),
      field('簡介 Bio (Deutsch)', a, 'bio_de', { area: true }), field('簡介 Bio（中文）', a, 'bio_zh', { area: true })]);
    a.sections.forEach(function (sec, i) {
      box.appendChild(h('div', { className: 'card stack', style: 'gap:12px' }, [
        h('div', { className: 'actions' }, [
          h('div', { style: 'flex:1' }, [field('段落標題', sec, 'title')]),
          h('div', { style: 'flex:1' }, [field('DE', sec, 'title_de')]),
          h('div', { style: 'flex:1' }, [field('中文', sec, 'title_zh')]),
          btn('↑', function () { if (i) { a.sections.splice(i - 1, 0, a.sections.splice(i, 1)[0]); save(); render(); } }, 'sm'),
          btn('刪除', function () { if (confirm('刪除段落「' + sec.title + '」？')) { a.sections.splice(i, 1); save(); render(); } }, 'sm danger')
        ]),
        lines('每行：年份 | 內容 | 連結（選填）', sec, 'items', ['year', 'text', 'url'], null, sec.items.length > 8 ? 'tall' : '')
      ]));
    });
    box.appendChild(h('div', {}, [btn('+ 新增段落', function () { a.sections.push({ title: 'New section', items: [] }); save(); render(); })]));
    main.append(bar('關於 / CV'), box);
  };

  tabs.writing = function () {
    var posts = D.writing = D.writing || [];
    if (psel >= posts.length) psel = posts.length - 1;
    var list = h('div', { className: 'items' }, posts.map(function (p, i) {
      return h('div', {
        className: 'item' + (i === psel ? ' on' : '') + (p.hidden ? ' off' : ''),
        on: { click: function () { psel = i; render(); } }
      }, [h('span', { text: p.title || '(untitled)' }), h('span', { className: 'y', text: (p.date || '').slice(0, 4) })]);
    }));
    var p = posts[psel];
    main.append(
      bar('文章 Blog', [
        btn('+ 新增文章', function () {
          var slug = 'post-' + Date.now().toString(36);
          posts.unshift({ slug: slug, date: new Date().toISOString().slice(0, 10), title: 'New post', category: 'works',
            cover: '', excerpt: '', lang: 'zh-Hant', hidden: true });
          setPostBody(slug, '');
          psel = 0; save(); render();
        }, 'primary')
      ]),
      h('div', { className: 'split' }, [list, p ? postForm(p) : h('p', { text: '還沒有文章。' })])
    );
  };

  function postForm(p) {
    var i = D.writing.indexOf(p);
    var body = h('textarea', { className: 'tall', style: 'min-height:520px;font-family:ui-monospace,Menlo,monospace;font-size:13px', value: '載入中…', disabled: true });
    getPostBody(p.slug).then(function (t) { body.value = t; body.disabled = false; });
    body.addEventListener('input', function () { setPostBody(p.slug, body.value); });

    var hidden = h('input', { type: 'checkbox', checked: !!p.hidden });
    hidden.addEventListener('change', function () { p.hidden = hidden.checked; save(); render(); });

    var slugField = field('網址代稱 slug（改了會變成新網址）', p, 'slug');
    slugField.querySelector('input').addEventListener('change', function () {
      // keep the body attached to the new slug
      if (!body.disabled) setPostBody(p.slug, body.value);
    });

    return h('div', { className: 'form' }, [
      h('div', { className: 'actions' }, [
        btn('↑ 上移', function () { if (i > 0) { D.writing.splice(i - 1, 0, D.writing.splice(i, 1)[0]); psel = i - 1; save(); render(); } }, 'sm'),
        btn('↓ 下移', function () { if (i < D.writing.length - 1) { D.writing.splice(i + 1, 0, D.writing.splice(i, 1)[0]); psel = i + 1; save(); render(); } }, 'sm'),
        h('a', { className: 'btn sm', href: '../preview.html?preview#/writing/' + encodeURIComponent(p.slug), target: 'ltc-preview', text: '預覽 ↗', style: 'text-decoration:none' }),
        btn('刪除', function () {
          if (confirm('從列表刪除「' + p.title + '」？（GitHub 上的 .md 檔會保留）')) { D.writing.splice(i, 1); save(); render(); }
        }, 'sm danger'),
        h('label', { className: 'check', style: 'margin-left:auto' }, [hidden, '隱藏'])
      ]),
      field('標題', p, 'title', { after: function () { document.querySelector('.item.on span').textContent = p.title; } }),
      h('div', { className: 'row' }, [slugField, field('日期 YYYY-MM-DD', p, 'date')]),
      h('div', { className: 'row' }, [field('分類（works / technique）', p, 'category'), field('語言（zh-Hant / en）', p, 'lang')]),
      field('摘要（列表與搜尋引擎用，一兩句）', p, 'excerpt', { area: true }),
      field('封面圖（分享縮圖）', p, 'cover'),
      h('label', {}, ['內文（Markdown：空一行分段、### 小標、![說明](圖片網址)、```程式碼```；單獨一行的影片網址會變成播放器）', body])
    ]);
  }

  tabs.friends = function () {
    main.append(bar('朋友 Friends'), h('div', { className: 'form' }, [
      lines('每行一位：名字 | 網址 | 圖片', D, 'friends', ['name', 'url', 'image'], null, 'tall')
    ]));
  };

  tabs.site = function () {
    var s = D.site;
    main.append(bar('網站設定'), h('div', { className: 'form' }, [
      h('div', { className: 'row' }, [field('名字', s, 'name'), field('中文名字', s, 'name_zh')]),
      field('網站描述（搜尋引擎用）', s, 'description', { area: true }),
      h('div', { className: 'row' }, [field('網站描述 DE', s, 'description_de', { area: true }), field('網站描述 中文', s, 'description_zh', { area: true })]),
      field('Email', s, 'email'),
      field('首頁圖片', s, 'home_image'),
      field('首頁大字介紹 Statement', s, 'statement', { area: true }),
      h('div', { className: 'row' }, [field('Statement DE', s, 'statement_de', { area: true }), field('Statement 中文', s, 'statement_zh', { area: true })]),
      (function () {
        var ta = h('textarea', { value: (s.address || []).join('\n'), placeholder: 'Musterstraße 1\n12345 Berlin\nDeutschland' });
        ta.addEventListener('input', function () {
          s.address = ta.value.split('\n').map(function (x) { return x.trim(); }).filter(Boolean); save();
        });
        return h('label', {}, ['Impressum 地址（德國法規要求，每行一段）', ta]);
      })(),
      field('Google Analytics ID（G-…）', s, 'ga_id'),
      field('網站網址（搜尋引擎、分享連結用；換網域時改這裡）', s, 'base_url'),
      field('預設分享縮圖', s, 'og_image'),
      lines('側欄連結（每行：名稱 | 網址）', s, 'links', ['label', 'url'])
    ]));
  };

  tabs.publish = function () {
    var c = gh();
    var log = h('div', { className: 'log' });
    function say(t) { log.textContent = t; }

    main.append(bar('發佈 Publish'), h('div', { className: 'stack' }, [
      h('div', { className: 'card' }, [
        h('h3', { text: '方法 A：直接存到 GitHub（推薦）' }),
        h('p', { text: '需要一個只開放這個 repo「Contents: Read and write」權限的 fine-grained token（GitHub → Settings → Developer settings → Fine-grained tokens）。Token 只存在這台電腦的瀏覽器。' }),
        h('div', { className: 'form' }, [
          h('div', { className: 'row' }, [field('Owner', c, 'owner', { after: function () { setGh(c); } }), field('Repo', c, 'repo', { after: function () { setGh(c); } })]),
          h('div', { className: 'row' }, [field('Branch', c, 'branch', { after: function () { setGh(c); } }), field('網站資料夾', c, 'dir', { after: function () { setGh(c); } })]),
          (function () {
            var t = h('input', { type: 'password', value: c.token, placeholder: 'github_pat_…' });
            t.addEventListener('input', function () { c.token = t.value.trim(); setGh(c); });
            return h('label', {}, ['Token', t]);
          })(),
          h('div', { className: 'actions' }, [
            btn('發佈到 GitHub', function () {
              if (!c.token) return say('請先填 token。');
              say('發佈中…');
              var dirty = dirtyPosts();
              var steps = dirty.reduce(function (pr, slug) {
                return pr.then(function () {
                  return getPostBody(slug).then(function (t) {
                    say('發佈文章 ' + slug + '…');
                    return putFile(c, c.dir + '/posts/' + slug + '.md', b64utf8(t), 'Update post ' + slug);
                  });
                });
              }, Promise.resolve());
              steps.then(function () {
                return putFile(c, c.dir + '/data/site.json', b64utf8(JSON.stringify(D, null, 2) + '\n'), 'Update site content');
              }).then(function () {
                clearPostDrafts();
                say('✓ 已發佈' + (dirty.length ? '（含 ' + dirty.length + ' 篇文章）' : '') + '。GitHub 會自動重建頁面，約 1–2 分鐘後上線。');
              }).catch(function (e) { say('✗ 失敗：' + e.message); });
            }, 'primary'),
            btn('從 GitHub 重新載入', function () {
              if (!confirm('用 GitHub 上的版本覆蓋目前草稿？')) return;
              say('載入中…');
              api(c, 'GET', c.dir + '/data/site.json', null, true)
                .then(function (txt) { D = JSON.parse(txt); save(); say('✓ 已載入。'); })
                .catch(function (e) { say('✗ 失敗：' + e.message); });
            })
          ])
        ])
      ]),
      h('div', { className: 'card' }, [
        h('h3', { text: '方法 B：下載檔案手動上傳' }),
        h('p', { text: '下載 site.json，放到 repo 的 ' + c.dir + '/data/site.json 並 commit。文章內文不包含在內，請用方法 A 或直接改 posts/ 裡的 .md 檔。' }),
        h('div', { className: 'actions' }, [
          btn('下載 site.json', function () {
            var a = h('a', { href: URL.createObjectURL(new Blob([JSON.stringify(D, null, 2) + '\n'], { type: 'application/json' })), download: 'site.json' });
            document.body.appendChild(a); a.click(); a.remove();
          }),
          btn('捨棄草稿（重新讀取網站上的版本）', function () {
            if (!confirm('捨棄所有未發佈的修改？')) return;
            try { localStorage.removeItem(DRAFT_KEY); } catch (e) {}
            clearPostDrafts();
            location.reload();
          }, 'danger')
        ])
      ]),
      log
    ]));
  };

  // ---------- GitHub API ----------
  function api(c, method, path, body, raw) {
    var url = 'https://api.github.com/repos/' + c.owner + '/' + c.repo + '/contents/' +
      path.split('/').map(encodeURIComponent).join('/') + (method === 'GET' ? '?ref=' + encodeURIComponent(c.branch) : '');
    return fetch(url, {
      method: method,
      headers: {
        Authorization: 'Bearer ' + c.token,
        Accept: raw ? 'application/vnd.github.raw' : 'application/vnd.github+json'
      },
      body: body ? JSON.stringify(body) : undefined
    }).then(function (r) {
      if (r.status === 404 && method === 'GET' && !raw) return null;
      if (!r.ok) return r.text().then(function (t) { throw new Error(r.status + ' ' + t.slice(0, 200)); });
      return raw ? r.text() : r.json();
    });
  }

  function putFile(c, path, b64, message) {
    return api(c, 'GET', path).then(function (cur) {
      var body = { message: message, content: b64, branch: c.branch };
      if (cur && cur.sha) body.sha = cur.sha;
      return api(c, 'PUT', path, body);
    });
  }

  function b64utf8(s) {
    var bytes = new TextEncoder().encode(s), bin = '';
    for (var i = 0; i < bytes.length; i += 0x8000) bin += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000));
    return btoa(bin);
  }

  function readB64(file) {
    return new Promise(function (res, rej) {
      var r = new FileReader();
      r.onload = function () { res(String(r.result).split(',')[1]); };
      r.onerror = rej;
      r.readAsDataURL(file);
    });
  }

  // ---------- shell ----------
  function render() {
    main.innerHTML = '';
    Array.prototype.forEach.call(document.querySelectorAll('.side [data-tab]'), function (b) {
      b.classList.toggle('on', b.getAttribute('data-tab') === tab);
    });
    tabs[tab]();
  }

  Array.prototype.forEach.call(document.querySelectorAll('.side [data-tab]'), function (b) {
    b.addEventListener('click', function () { tab = b.getAttribute('data-tab'); render(); window.scrollTo(0, 0); });
  });

  var draft = null;
  try { draft = JSON.parse(localStorage.getItem(DRAFT_KEY)); } catch (e) {}
  if (draft) {
    D = draft;
    document.getElementById('saved').textContent = '載入本機草稿';
    render();
  } else {
    fetch('../data/site.json', { cache: 'no-cache' })
      .then(function (r) { return r.json(); })
      .then(function (d) { D = d; render(); })
      .catch(function () { main.textContent = '無法讀取 ../data/site.json'; });
  }
})();
