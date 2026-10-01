/* "Ask about the work": sends the conversation to the Cloudflare Worker (worker/) and
   shows the streamed answer. Only text is rendered; https links become links.
   The conversation lives in this page only and is gone on reload. */
(function () {
  'use strict';
  var box = document.getElementById('ask');
  if (!box || !window.fetch || !window.TextDecoder) return;
  var endpoint = box.getAttribute('data-endpoint');
  var msgs = JSON.parse(box.getAttribute('data-msgs') || '{}');
  var log = box.querySelector('.ask-log');
  var form = box.querySelector('.ask-form');
  var input = form.querySelector('input');
  var btn = form.querySelector('button');
  var history = [];
  var busy = false;

  // Plain text with clickable https URLs (trailing punctuation stays outside the link).
  function render(el, text) {
    el.textContent = '';
    var re = /https:\/\/[^\s<>()"'“”「」（）]+/g, last = 0, m;
    while ((m = re.exec(text))) {
      var href = m[0].replace(/[.,;:!?。，、；：！？]+$/, '');
      el.appendChild(document.createTextNode(text.slice(last, m.index)));
      var a = document.createElement('a');
      a.href = href;
      a.textContent = href.replace(/^https:\/\/(www\.)?/, '').replace(/\/$/, '');
      if (a.hostname !== location.hostname) { a.target = '_blank'; a.rel = 'noopener'; }
      el.appendChild(a);
      last = m.index + href.length;
    }
    el.appendChild(document.createTextNode(text.slice(last)));
  }

  function line(cls, text) {
    var p = document.createElement('p');
    p.className = cls;
    p.textContent = text || '';
    log.appendChild(p);
    return p;
  }

  function ask(q) {
    q = q.trim();
    if (!q || busy) return;
    busy = true;
    btn.disabled = true;
    box.classList.add('open');
    line('ask-q', q);
    var out = line('ask-a pending');
    history.push({ role: 'user', content: q });
    var text = '';

    function finish(problem) {
      out.classList.remove('pending');
      if (problem) {
        out.classList.add('err');
        if (problem === 'ask_refusal') text = '';  // never leave half of a declined answer
        render(out, (text ? text + '\n\n' : '') + (msgs[problem] || msgs.ask_err));
        history.pop();  // keep the conversation well-formed for the next question
      } else {
        history.push({ role: 'assistant', content: text });
      }
      busy = false;
      btn.disabled = false;
    }

    fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages: history.slice(-12) })
    }).then(function (res) {
      if (res.status === 429) return finish('ask_busy');
      if (!res.ok || !res.body) return finish('ask_err');
      var reader = res.body.getReader();
      var dec = new TextDecoder();
      function pump() {
        return reader.read().then(function (r) {
          if (r.done) {
            // The Worker ends the stream with \0refusal or \0error when something went wrong.
            var i = text.indexOf('\u0000');
            if (i >= 0) {
              var code = text.slice(i + 1);
              text = text.slice(0, i).trim();
              return finish(code === 'refusal' ? 'ask_refusal' : 'ask_err');
            }
            return text.trim() ? finish() : finish('ask_err');
          }
          text += dec.decode(r.value, { stream: true });
          var shown = text.split('\u0000')[0];
          if (shown) { out.classList.remove('pending'); render(out, shown); }
          return pump();
        });
      }
      return pump();
    }).catch(function () { finish('ask_err'); });
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var q = input.value;
    input.value = '';
    ask(q);
  });
  box.querySelector('.ask-chips').addEventListener('click', function (e) {
    var b = e.target.closest('button');
    if (b) ask(b.textContent);
  });
})();
