/* Static petition page. Reads a PUBLISHED CSV that contains ONLY
   name / english name / occupation. The spreadsheet holding email addresses
   is a different document and is never referenced here. See README.md */

var CSV_URL = "https://docs.google.com/spreadsheets/d/1NSkdyPTEOVKRDk4QLnpNHmEsEhqrH1O6dcG5orNLeYE/gviz/tq?tqx=out:csv";

/* ---------- language ---------- */

var LANGS = ["en", "zh", "ko"];

function setLang(lang) {
  var html = document.documentElement;
  html.setAttribute("data-lang", lang);
  html.setAttribute("lang", lang === "zh" ? "zh-Hant" : lang);
  var buttons = document.querySelectorAll("#lang button");
  for (var i = 0; i < buttons.length; i++) {
    buttons[i].setAttribute("aria-current", buttons[i].dataset.langSet === lang ? "true" : "false");
  }
  try { localStorage.setItem("lang", lang); } catch (e) {}
}

function initLang() {
  var saved = null;
  try { saved = localStorage.getItem("lang"); } catch (e) {}
  var nav = (navigator.language || "").toLowerCase();
  var guess = nav.indexOf("zh") === 0 ? "zh" : nav.indexOf("ko") === 0 ? "ko" : "en";
  setLang(LANGS.indexOf(saved) !== -1 ? saved : guess);

  document.getElementById("lang").addEventListener("click", function (e) {
    if (e.target.dataset.langSet) setLang(e.target.dataset.langSet);
  });
}

/* ---------- CSV ---------- */

function parseCsv(text) {
  var rows = [], row = [], field = "", quoted = false, i = 0;
  text = text.replace(/\r\n/g, "\n").replace(/\r/g, "\n");
  while (i < text.length) {
    var c = text[i];
    if (quoted) {
      if (c === '"') {
        if (text[i + 1] === '"') { field += '"'; i += 2; continue; }
        quoted = false; i++; continue;
      }
      field += c; i++; continue;
    }
    if (c === '"') { quoted = true; i++; continue; }
    if (c === ",") { row.push(field); field = ""; i++; continue; }
    if (c === "\n") { row.push(field); rows.push(row); row = []; field = ""; i++; continue; }
    field += c; i++;
  }
  row.push(field);
  if (row.length > 1 || row[0] !== "") rows.push(row);
  return rows;
}

function toSignatories(rows) {
  var out = [];
  for (var i = 0; i < rows.length; i++) {
    var name = (rows[i][0] || "").trim();
    var latin = (rows[i][1] || "").trim();
    var occupation = (rows[i][2] || "").trim();

    // Never render anything that looks like an address, whatever the sheet holds.
    if ((name + latin + occupation).indexOf("@") !== -1) continue;
    if (!name && !latin) continue;
    if (/^name\b/i.test(name)) continue;   // header row

    out.push({ name: name || latin, latin: name ? latin : "", occupation: occupation });
  }
  return out;
}

/* ---------- render ---------- */

function render(people) {
  var list = document.getElementById("list");
  list.textContent = "";

  people.forEach(function (p) {
    var li = document.createElement("li");
    var left = document.createElement("span");

    var n = document.createElement("span");
    n.className = "name";
    n.textContent = p.name;
    left.appendChild(n);

    if (p.latin) {
      var l = document.createElement("span");
      l.className = "latin";
      l.textContent = " " + p.latin;
      left.appendChild(l);
    }

    var occ = document.createElement("span");
    occ.className = "occupation";
    occ.textContent = p.occupation;

    li.appendChild(left);
    li.appendChild(occ);
    list.appendChild(li);
  });

  document.getElementById("count").textContent = " (" + people.length + ")";
}

function setStatus(en, zh, ko) {
  var s = document.getElementById("status");
  s.textContent = "";
  [["en", en], ["zh", zh], ["ko", ko]].forEach(function (pair) {
    var span = document.createElement("span");
    span.className = pair[0];
    span.textContent = pair[1];
    s.appendChild(span);
  });
}

function load() {
  if (CSV_URL.indexOf("http") !== 0) {
    setStatus("The list is not connected yet.", "名單尚未連結。", "명단이 아직 연결되지 않았습니다.");
    return;
  }
  setStatus("Loading…", "載入中…", "불러오는 중…");

  fetch(CSV_URL + (CSV_URL.indexOf("?") === -1 ? "?" : "&") + "cb=" + Date.now(),
        { cache: "no-store", referrerPolicy: "no-referrer" })
    .then(function (r) { if (!r.ok) throw new Error(r.status); return r.text(); })
    .then(function (text) {
      render(toSignatories(parseCsv(text)));
      document.getElementById("status").textContent = "";
    })
    .catch(function () {
      setStatus("Could not load the list. Please reload.",
                "無法載入名單，請重新整理。",
                "명단을 불러오지 못했습니다. 새로고침해 주세요.");
    });
}

/* ---------- init ---------- */

initLang();
if (document.getElementById("list")) load();
