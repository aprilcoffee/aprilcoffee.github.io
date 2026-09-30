/* Small p5.js sketches used as quiet graphic elements.
   field  — home: a drifting field of characters. The characters are ordered by how much of
            their box they fill, measured with the Monte Carlo method from the 2019 post
            "Processing 蒙地卡羅演算法做文字動畫". The mouse raises the density locally,
            and uncovers keywords hidden in the field (site.hidden_words), in water blue.
   signal — sidebar: a thin noise line, like an oscilloscope left running. */
(function () {
  'use strict';
  if (!window.p5) return;

  var INK = [20, 20, 20];
  var RED = [228, 3, 46];
  var BLUE = [22, 170, 222];   // water blue, only for the hidden keywords
  var still = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // characters and their ink density (% of the glyph box), from the post
  var CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ~!@#$%^&*()-+ '.split('');
  var DENS = [4.595, 5.98, 3.475, 5.964, 4.46, 3.819, 6.538, 5.446, 2.25, 3.421, 5.131, 2.788, 7.01, 4.547, 4.703,
    5.808, 5.809, 2.502, 3.456, 3.181, 4.626, 3.487, 6.27, 3.945, 4.296, 4.2, 6.145, 7.078, 5.328, 7.283, 5.367,
    4.456, 6.068, 6.606, 2.782, 3.793, 5.865, 3.744, 9.116, 7.354, 7.154, 5.516, 8.077, 6.755, 4.99, 4.363, 5.898,
    4.961, 9.212, 5.624, 4.408, 5.674, 1.737, 2.119, 7.047, 5.383, 5.19, 6.321, 2.727, 7.452, 1.506, 2.689, 2.71,
    1.173, 2.911, 0.0];
  var RAMP = CHARS.map(function (c, i) { return [DENS[i], c]; })
    .sort(function (a, b) { return a[0] - b[0]; })
    .map(function (d) { return d[1]; });

  // pause sketches that are off screen
  function watch(el, p) {
    if (!('IntersectionObserver' in window) || still) return;
    new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) p.loop(); else p.noLoop(); });
    }).observe(el);
  }

  var sketches = {
    field: function (el) {
      return function (p) {
        var cell, cols, rows, t = 0, mx = -9999, my = -9999, font;
        var WORDS = [], placed = [], at = {};
        try { WORDS = JSON.parse(el.getAttribute('data-words') || '[]'); } catch (e) {}

        // scatter the keywords over the grid, a few cells apart, same layout on every visit
        function place() {
          placed = []; at = {};
          p.randomSeed(85227);
          var taken = {};
          WORDS.forEach(function (w) {
            var chars = Array.from(w), n = chars.length;
            if (n + 4 > cols) return;
            for (var tries = 0; tries < 60; tries++) {
              var j = 2 + Math.floor(p.random(Math.max(1, rows - 4)));
              var i = 2 + Math.floor(p.random(Math.max(1, cols - n - 4)));
              var free = true;
              for (var dj = -2; dj <= 2 && free; dj++)
                for (var di = -2; di < n + 2 && free; di++) if (taken[(j + dj) + ',' + (i + di)]) free = false;
              if (!free) continue;
              var word = { x: (i + (n - 1) / 2) * cell, y: j * cell * 1.25, a: 0 };
              chars.forEach(function (c, k) { taken[j + ',' + (i + k)] = 1; at[j + ',' + (i + k)] = [word, c]; });
              placed.push(word);
              return;
            }
          });
        }
        function size() {
          cell = el.clientWidth < 700 ? 13 : 16;
          p.resizeCanvas(el.clientWidth, el.clientHeight);
          cols = Math.ceil(p.width / cell) + 1;
          rows = Math.ceil(p.height / (cell * 1.25)) + 1;
          place();
        }
        p.setup = function () {
          var c = p.createCanvas(el.clientWidth, el.clientHeight);
          c.parent(el);
          font = (getComputedStyle(document.body).getPropertyValue('--mono') || 'monospace').trim();
          p.textFont(font);
          p.textAlign(p.CENTER, p.CENTER);
          p.frameRate(24);
          p.noiseDetail(3, 0.45);
          size();
          if (still) p.noLoop();
          watch(el, p);
        };
        p.windowResized = size;
        p.mouseMoved = function () { mx = p.mouseX; my = p.mouseY; };
        p.touchMoved = function () { mx = p.mouseX; my = p.mouseY; };
        p.draw = function () {
          p.clear();
          p.textSize(cell * 0.78);
          // a keyword fades in while the pointer is near it, and fades out again
          placed.forEach(function (w) {
            var d = Math.sqrt((w.x - mx) * (w.x - mx) + (w.y - my) * (w.y - my));
            var target = Math.max(0, Math.min(1, (190 - d) / 110));
            w.a += (target - w.a) * 0.18;
          });
          var rh = cell * 1.25, hot = null, best = 1e9;
          for (var j = 0; j < rows; j++) {
            for (var i = 0; i < cols; i++) {
              var x = i * cell, y = j * rh;
              var kw = at[j + ',' + i];
              if (kw && kw[0].a > 0.03) {
                p.fill(BLUE[0], BLUE[1], BLUE[2], 255 * kw[0].a);
                p.text(kw[1], x, y);
                continue;
              }
              var v = p.noise(i * 0.06, j * 0.075, t);
              var d2 = (x - mx) * (x - mx) + (y - my) * (y - my);
              v += 0.55 * Math.exp(-d2 / (2 * 130 * 130));
              v = Math.min(1, Math.max(0, (v - 0.32) * 1.7));
              if (v < 0.04) continue;
              var ch = RAMP[Math.min(RAMP.length - 1, Math.floor(v * v * RAMP.length))];
              p.fill(INK[0], INK[1], INK[2], 14 + v * 115);
              p.text(ch, x, y);
              if (d2 < best) { best = d2; hot = [x, y, ch]; }
            }
          }
          // the one red character sits under the pointer
          if (hot && best < cell * cell * 4) {
            p.fill(RED[0], RED[1], RED[2]);
            p.text(hot[2] === ' ' ? '#' : hot[2], hot[0], hot[1]);
          }
          t += 0.006;
        };
      };
    },

    signal: function (el) {
      return function (p) {
        var t = 0, energy = 0;
        p.setup = function () {
          var c = p.createCanvas(el.clientWidth, el.clientHeight);
          c.parent(el);
          p.frameRate(30);
          p.noFill();
          if (still) p.noLoop();
          window.addEventListener('mousemove', function () { energy = Math.min(1, energy + 0.02); }, { passive: true });
        };
        p.windowResized = function () { p.resizeCanvas(el.clientWidth, el.clientHeight); };
        p.draw = function () {
          p.clear();
          p.stroke(INK[0], INK[1], INK[2], 150);
          p.strokeWeight(1);
          var mid = p.height / 2, amp = p.height * (0.18 + 0.3 * energy);
          p.beginShape();
          for (var x = 0; x <= p.width; x += 2) {
            var n = p.noise(x * 0.018, t) - 0.5;
            var s = Math.sin(x * 0.09 + t * 14) * 0.18 * energy;
            p.vertex(x, mid + (n + s) * 2 * amp);
          }
          p.endShape();
          energy *= 0.97;
          t += 0.012;
        };
      };
    }
  };

  document.querySelectorAll('[data-effect]').forEach(function (el) {
    var make = sketches[el.getAttribute('data-effect')];
    if (make && el.offsetParent !== null) new window.p5(make(el));
  });
})();
