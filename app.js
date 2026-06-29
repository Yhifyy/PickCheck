"use strict";

const API_BASE = "/api";

const state = {
  user: null,
  sscc: null,
  pallet: null,
  filter: "ALL",
  activeIndex: -1,
  finished: {},          // sscc -> färdig pall (snapshot) som kan återöppnas
  lastFinishedSscc: null, // senast inskickade pall (för F6 / Ångra check)
  checkStartTime: null   // tidpunkt när pallen öppnades (för att mäta kontrolltid)
};

/* ---------- Ljud (genereras, inga filer behövs) ---------- */
let audioCtx = null;
function beep(type) {
  try {
    audioCtx = audioCtx || new (window.AudioContext || window.webkitAudioContext)();
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    if (type === "ok") {
      osc.frequency.value = 880;
      gain.gain.value = 0.05;
      osc.start();
      osc.stop(audioCtx.currentTime + 0.08);
    } else {
      osc.type = "square";
      osc.frequency.value = 220;
      gain.gain.value = 0.08;
      osc.start();
      osc.stop(audioCtx.currentTime + 0.25);
    }
  } catch (e) { /* ljud ej tillgängligt */ }
}

/* ---------- Banner ---------- */
let bannerTimer = null;
function banner(type, msg, sticky) {
  const el = document.getElementById("banner");
  el.className = type;
  el.textContent = msg;
  el.classList.remove("hidden");
  clearTimeout(bannerTimer);
  if (!sticky) bannerTimer = setTimeout(() => el.classList.add("hidden"), 2500);
}
function hideBanner() {
  document.getElementById("banner").classList.add("hidden");
}

/* ---------- Login / Registrering ---------- */

// Växla lösenordssynlighet
document.getElementById("pass-toggle").addEventListener("click", () => {
  const p = document.getElementById("login-pass");
  p.type = p.type === "password" ? "text" : "password";
});

// Växla mellan login och register flikar
document.querySelectorAll(".auth-tab").forEach(tab => {
  tab.addEventListener("click", () => {
    const target = tab.dataset.tab;
    document.querySelectorAll(".auth-tab").forEach(t => t.classList.remove("active"));
    tab.classList.add("active");
    document.getElementById("login-form").classList.toggle("hidden", target !== "login");
    document.getElementById("register-form").classList.toggle("hidden", target !== "register");
    hideAuthError();
  });
});

function showAuthError(msg) {
  const el = document.getElementById("login-error");
  el.textContent = msg;
  el.className = "auth-error";
}
function showAuthSuccess(msg) {
  const el = document.getElementById("login-error");
  el.textContent = msg;
  el.className = "auth-success";
}
function hideAuthError() {
  document.getElementById("login-error").classList.add("hidden");
}

function completeLogin(user) {
  state.user = user.displayName || user.username;
  localStorage.setItem("pickcheck_user", JSON.stringify(user));
  document.getElementById("login-view").classList.add("hidden");
  document.getElementById("app-view").classList.remove("hidden");
  document.getElementById("topbar-user").textContent = "\uD83D\uDC64 " + state.user + " \u25BE";
  focusSscc();
}

// Login-formulär
document.getElementById("login-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  hideAuthError();
  
  const username = document.getElementById("login-user").value.trim();
  const password = document.getElementById("login-pass").value;
  
  if (!username || !password) {
    showAuthError("Fyll i användarnamn och lösenord");
    return;
  }
  
  try {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });
    const data = await res.json();
    
    if (!res.ok) {
      showAuthError(data.error || "Inloggning misslyckades");
      return;
    }
    
    completeLogin(data.user);
  } catch (err) {
    showAuthError("Kunde inte ansluta till servern");
  }
});

// Registrerings-formulär
document.getElementById("register-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  hideAuthError();
  
  const username = document.getElementById("reg-user").value.trim();
  const displayName = document.getElementById("reg-display").value.trim();
  const password = document.getElementById("reg-pass").value;
  const password2 = document.getElementById("reg-pass2").value;
  
  if (!username || username.length < 2) {
    showAuthError("Användarnamn måste vara minst 2 tecken");
    return;
  }
  if (!password || password.length < 4) {
    showAuthError("Lösenord måste vara minst 4 tecken");
    return;
  }
  if (password !== password2) {
    showAuthError("Lösenorden matchar inte");
    return;
  }
  
  try {
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password, displayName })
    });
    const data = await res.json();
    
    if (!res.ok) {
      showAuthError(data.error || "Registrering misslyckades");
      return;
    }
    
    // Visa framgång och byt till login
    showAuthSuccess("Konto skapat! Du kan nu logga in.");
    document.getElementById("login-user").value = username;
    document.getElementById("login-pass").value = "";
    document.querySelectorAll(".auth-tab")[0].click();
  } catch (err) {
    showAuthError("Kunde inte ansluta till servern");
  }
});

// Logga ut
function doLogout() {
  state.user = null;
  localStorage.removeItem("pickcheck_user");
  document.getElementById("app-view").classList.add("hidden");
  document.getElementById("login-view").classList.remove("hidden");
  document.getElementById("login-pass").value = "";
  hideAuthError();
}

// Auto-login om användare finns i localStorage
(function autoLogin() {
  const saved = localStorage.getItem("pickcheck_user");
  if (saved) {
    try {
      const user = JSON.parse(saved);
      completeLogin(user);
    } catch {
      // Gammalt format (bara sträng) – rensa
      localStorage.removeItem("pickcheck_user");
    }
  }
})();

/* ---------- Fokus-hjälpare ---------- */
function focusSscc() {
  const el = document.getElementById("sscc-input");
  el.focus();
  el.select();
}

/* ---------- Sök pall ---------- */
document.getElementById("search-btn").addEventListener("click", doSearch);
document.getElementById("sscc-input").addEventListener("keydown", (e) => {
  if (e.key === "Enter") { e.preventDefault(); doSearch(); }
});

async function doSearch() {
  const sscc = document.getElementById("sscc-input").value.trim();
  if (!sscc) { focusSscc(); return; }

  // Om pallen redan är kontrollerad/inskickad → återöppna med sparad data
  if (state.finished[sscc]) {
    reopenPallet(sscc, "Pallen var redan kontrollerad – återöppnad för ändring");
    return;
  }

  // Hämta pall från API
  banner("ok", "Hämtar pall...", true);
  try {
    const res = await fetch(`${API_BASE}/pallet/${encodeURIComponent(sscc)}`);
    if (!res.ok) {
      banner("error", "Pall hittades inte: " + sscc);
      beep("error");
      focusSscc();
      return;
    }
    const src = await res.json();

    // Skapa en arbetskopia med kontrollfält per rad
    state.sscc = sscc;
    state.filter = "ALL";
    state.activeIndex = -1;
    state.checkStartTime = Date.now();
    state.pallet = {
      sscc: src.sscc,
      order: src.order,
      twoPallets: src.twoPallets,
      extras: [],
      lines: src.lines.map((l) => ({
        ...l,
        checkedQty: null,
        checked: false,
        wrongProduct: false,
        checkTime: ""
      }))
    };
    hideBanner();
    renderPallet();
    // Fokus på första radens antalsfält
    setTimeout(() => focusLine(firstVisibleIndex()), 0);
  } catch (err) {
    banner("error", "Kunde inte ansluta till servern");
    beep("error");
    console.error(err);
    focusSscc();
  }
}

function reopenPallet(sscc, message) {
  state.pallet = state.finished[sscc];      // ladda tillbaka sparad data
  delete state.finished[sscc];              // pallen är nu aktiv/öppen igen
  if (state.lastFinishedSscc === sscc) state.lastFinishedSscc = null;
  state.sscc = sscc;
  state.filter = "ALL";
  state.activeIndex = -1;
  state.checkStartTime = Date.now();        // återstarta tidmätning
  document.getElementById("sscc-input").value = sscc;
  updateUnfinishButton();
  renderPallet();
  banner("warn", message, true);
  beep("error");
  // Hoppa till första avvikelsen om någon finns, annars första raden
  const firstErr = state.pallet.lines.findIndex(lineHasError);
  setTimeout(() => focusLine(firstErr >= 0 ? firstErr : firstVisibleIndex()), 0);
}

/* ---------- Avvikelse-hjälpare ---------- */
function isWrongPallet(line) {
  return line.correctPallet && line.correctPallet !== line.pallet;
}
function isWrongAmount(line) {
  return line.checked && !line.wrongProduct && line.checkedQty !== line.pickedQty;
}
function lineHasError(line) {
  return line.wrongProduct || isWrongPallet(line) || isWrongAmount(line);
}

/* ---------- Produkt-skanning ---------- */
document.getElementById("scan-input").addEventListener("keydown", (e) => {
  if (e.key === "Enter") { e.preventDefault(); scanProduct(e.target.value); e.target.value = ""; }
});

function refocusScan() {
  const s = document.getElementById("scan-input");
  s.focus();
  s.select();
}

function scrollToRow(index) {
  const tr = document.querySelector(`#lines-body tr[data-index="${index}"]`);
  if (tr) tr.scrollIntoView({ block: "center", behavior: "smooth" });
}

// Varje skanning räknar upp antalet med 1 (ett skannat paket = +1).
// Skannar du fler än plockat antal => extra registreras automatiskt.
function scanProduct(raw) {
  const code = (raw || "").trim();
  if (!code || !state.pallet) return;
  const idx = state.pallet.lines.findIndex(
    (l) => l.productNumber.toLowerCase() === code.toLowerCase());

  if (idx === -1) {
    // Varan finns inte på pallen alls → extra/okänd produkt
    state.pallet.extras.push(code); // varje skanning loggas (även dubbletter = fler extra)
    banner("error", "EXTRA PRODUKT – finns ej på denna pall: " + code, true);
    beep("error");
    updateStats();
    refocusScan();
    return;
  }

  const line = state.pallet.lines[idx];

  // Om raden är dold av filter → visa alla först
  if (state.filter !== "ALL" && line.pallet !== state.filter) {
    state.filter = "ALL";
    renderFilterBar();
  }

  // Räkna upp antalet
  line.checkedQty = (line.checkedQty || 0) + 1;
  line.checked = true;
  line.checkTime = new Date().toLocaleDateString("sv-SE");

  renderLines();
  updateStats();
  updateProgress();

  // Markera + scrolla raden, men behåll fokus i skannfältet
  state.activeIndex = idx;
  highlightActive();
  scrollToRow(idx);

  const n = line.checkedQty, m = line.pickedQty;
  if (isWrongPallet(line)) {
    banner("error", `FEL PALL: ${line.product} ligger på ${line.pallet} men ska på ${line.correctPallet} (räknat ${n})`, true);
    beep("error");
  } else if (n > m) {
    banner("error", `EXTRA: ${line.product} – räknat ${n} / plockat ${m} (+${n - m} för mycket)`, true);
    beep("error");
  } else if (n === m) {
    banner("ok", `Klar: ${line.product} – ${n}/${m}`, false);
    beep("ok");
  } else {
    banner("ok", `${line.product} – räknat ${n}/${m}`, false);
    beep("ok");
  }

  refocusScan();
}

/* ---------- Rendering ---------- */
function renderPallet() {
  document.getElementById("pallet-area").classList.remove("hidden");
  document.getElementById("pallet-number").textContent = state.pallet.sscc;
  document.getElementById("pallet-order").textContent = state.pallet.order ? "Order " + state.pallet.order : "";
  renderFilterBar();
  renderLines();
  updateStats();
  updateProgress();
}

function renderFilterBar() {
  const bar = document.getElementById("filter-bar");
  if (!state.pallet.twoPallets) { bar.innerHTML = ""; return; }
  const filters = [
    { key: "ALL", label: "Visa alla" },
    { key: "A", label: "A-pall" },
    { key: "B", label: "B-pall" }
  ];
  bar.innerHTML = "";
  filters.forEach((f) => {
    const b = document.createElement("button");
    b.className = "filter-btn" + (state.filter === f.key ? " active" : "");
    b.textContent = f.label;
    b.addEventListener("click", () => { state.filter = f.key; renderLines(); updateProgress(); });
    bar.appendChild(b);
  });
}

function visibleLines() {
  return state.pallet.lines
    .map((l, i) => ({ line: l, index: i }))
    .filter((x) => state.filter === "ALL" || x.line.pallet === state.filter);
}

function firstVisibleIndex() {
  const v = visibleLines();
  return v.length ? v[0].index : -1;
}

function renderLines() {
  const body = document.getElementById("lines-body");
  body.innerHTML = "";
  const showPallet = state.pallet.twoPallets;

  visibleLines().forEach(({ line, index }) => {
    const tr = document.createElement("tr");
    tr.dataset.index = index;
    const wrongPallet = isWrongPallet(line);
    const hasError = lineHasError(line);

    if (line.checked && !hasError) tr.classList.add("ok-row");
    if (hasError) tr.classList.add("error-row");      // fel pall lyser rött direkt, även före kontroll

    // Status-ikon
    let statusIcon = "";
    if (wrongPallet) statusIcon = '<span class="status-error" title="Fel pall">\u21C4</span>';
    else if (line.checked) {
      if (!hasError) statusIcon = '<span class="status-ok">\u2714</span>';
      else statusIcon = '<span class="status-error">\u26A0</span>';
    }

    // Pall-cell: vid fel pall visas "plockad → ska", annars bara pallen
    let palletPill = "";
    if (showPallet) {
      if (wrongPallet) {
        palletPill = `<span class="pill pill-${line.pallet}">${line.pallet}</span>` +
          ` <span class="pallet-arrow">\u2192</span> ` +
          `<span class="pill pill-${line.correctPallet}">${line.correctPallet}</span>`;
      } else {
        palletPill = `<span class="pill pill-${line.pallet}">${line.pallet}</span>`;
      }
    }

    tr.innerHTML = `
      <td class="status-cell">${statusIcon}</td>
      <td>${palletPill}</td>
      <td>${line.productNumber}</td>
      <td>${line.product}</td>
      <td>${line.picker}</td>
      <td>${line.pickedQty}</td>
      <td><input type="number" class="qty-input" data-index="${index}"
           value="${line.checkedQty === null ? "" : line.checkedQty}" /></td>
      <td>${line.checkTime}</td>
    `;
    body.appendChild(tr);

    tr.addEventListener("click", () => setActiveRow(index));
  });

  // Koppla händelser på antalsfälten
  body.querySelectorAll(".qty-input").forEach((inp) => {
    inp.addEventListener("focus", () => setActiveRow(parseInt(inp.dataset.index, 10), true));
    inp.addEventListener("keydown", onQtyKeydown);
  });

  if (state.activeIndex >= 0) highlightActive();
}

function setActiveRow(index, skipFocus) {
  state.activeIndex = index;
  highlightActive();
  if (!skipFocus) focusLine(index);
}

function highlightActive() {
  document.querySelectorAll("#lines-body tr").forEach((tr) => {
    tr.classList.toggle("active-row", parseInt(tr.dataset.index, 10) === state.activeIndex);
  });
}

function focusLine(index) {
  if (index < 0) return;
  const inp = document.querySelector(`.qty-input[data-index="${index}"]`);
  if (inp) {
    inp.focus();
    inp.select();
    inp.closest("tr").scrollIntoView({ block: "center", behavior: "smooth" });
  }
}

/* ---------- Antalsfält: tangentbord ---------- */
function onQtyKeydown(e) {
  const index = parseInt(e.target.dataset.index, 10);

  if (e.key === "Enter") {
    e.preventDefault();
    if (e.shiftKey) { toggleWrongProduct(index); return; }
    confirmLine(index, e.target.value);
  } else if (e.key === "ArrowDown") {
    e.preventDefault();
    moveRelative(index, 1);
  } else if (e.key === "ArrowUp") {
    e.preventDefault();
    moveRelative(index, -1);
  }
}

function moveRelative(fromIndex, dir) {
  const v = visibleLines().map((x) => x.index);
  const pos = v.indexOf(fromIndex);
  const next = v[pos + dir];
  if (next !== undefined) focusLine(next);
}

function confirmLine(index, rawValue) {
  const line = state.pallet.lines[index];
  const val = parseInt(rawValue, 10);
  if (isNaN(val)) { banner("warn", "Ange ett antal"); beep("error"); return; }

  line.checkedQty = val;
  line.checked = true;
  line.checkTime = new Date().toLocaleDateString("sv-SE");

  if (!lineHasError(line)) {
    beep("ok");
  } else {
    beep("error");
    let diff;
    if (isWrongPallet(line)) diff = `FEL PALL: ligger på ${line.pallet} men ska på ${line.correctPallet}`;
    else if (line.wrongProduct) diff = "fel produkt";
    else diff = `plockat ${line.pickedQty} / räknat ${val}`;
    banner("error", `Avvikelse: ${line.product} (${diff})`);
  }

  renderLines();
  updateStats();
  updateProgress();

  // Auto-hoppa till nästa okontrollerade rad
  const next = nextUncheckedIndex(index);
  if (next >= 0) {
    setActiveRow(next);
  } else {
    banner("ok", "Alla produkter kontrollerade \u2013 tryck F4 för Finish Check", true);
    document.getElementById("finish-btn").focus();
  }
}

function toggleWrongProduct(index) {
  const line = state.pallet.lines[index];
  line.wrongProduct = !line.wrongProduct;
  if (line.checked || line.wrongProduct) {
    line.checked = true;
    if (!line.checkTime) line.checkTime = new Date().toLocaleDateString("sv-SE");
  }
  banner(line.wrongProduct ? "warn" : "ok",
    line.wrongProduct ? "Markerad som FEL PRODUKT: " + line.product : "Fel produkt borttagen");
  beep(line.wrongProduct ? "error" : "ok");
  renderLines();
  updateStats();
  setActiveRow(index, true);
}

function nextUncheckedIndex(fromIndex) {
  const v = visibleLines().map((x) => x.index);
  const start = v.indexOf(fromIndex);
  for (let i = 1; i <= v.length; i++) {
    const idx = v[(start + i) % v.length];
    if (!state.pallet.lines[idx].checked) return idx;
  }
  return -1;
}

/* ---------- Progress ---------- */
function updateProgress() {
  const v = visibleLines();
  const done = v.filter((x) => x.line.checked).length;
  document.getElementById("progress-text").textContent =
    `Kontrollerade ${done} av ${v.length} produkter`;
}

/* ---------- Statistik ---------- */
function updateStats() {
  const lines = state.pallet.lines;
  const wrongAmount = lines.filter(isWrongAmount);
  const wrongProduct = lines.filter((l) => l.wrongProduct);
  const wrongPallet = lines.filter(isWrongPallet);

  const extras = state.pallet.extras || [];

  let html = "";
  html += statsGroup("Wrong amount", wrongAmount.map(
    (l) => `${l.productNumber} ${l.product} <strong>(${l.pickedQty}\u2192${l.checkedQty})</strong>`));
  html += statsGroup("Wrong product", wrongProduct.map(
    (l) => `${l.productNumber} ${l.product}` + (state.pallet.twoPallets ? ` <span class="pill pill-${l.pallet}">${l.pallet}</span>` : "")));
  html += statsGroup("Wrong pallet", wrongPallet.map(
    (l) => `${l.productNumber} ${l.product} <strong>(ligger på <span class="pill pill-${l.pallet}">${l.pallet}</span> \u2192 ska på <span class="pill pill-${l.correctPallet}">${l.correctPallet}</span>)</strong>`));
  const extraCounts = {};
  extras.forEach((c) => { extraCounts[c] = (extraCounts[c] || 0) + 1; });
  html += statsGroup("Extra product", Object.keys(extraCounts).map(
    (c) => `${c} (okänd på pallen)` + (extraCounts[c] > 1 ? ` <strong>\u00d7${extraCounts[c]}</strong>` : "")));

  if (!wrongAmount.length && !wrongProduct.length && !wrongPallet.length && !extras.length) {
    html = '<div class="stats-empty">\u2714 Inga avvikelser</div>' + html;
  }
  document.getElementById("stats-content").innerHTML = html;
}

function statsGroup(title, items) {
  if (!items.length) return "";
  return `<div class="stats-group wrong"><h4>${title}</h4><ul>` +
    items.map((i) => `<li>${i}</li>`).join("") + `</ul></div>`;
}

/* ---------- Finish check ---------- */
document.getElementById("finish-btn").addEventListener("click", finishCheck);

async function finishCheck() {
  if (!state.pallet) return;

  // Finish Check går ALLTID igenom. Avvikelser (fel pall, fel antal, extra)
  // blockerar inte – de skickas vidare så ledarna ser dem i IMI.
  const errors = state.pallet.lines.filter(lineHasError);
  const extrasArr = state.pallet.extras || [];
  const unchecked = state.pallet.lines.filter((l) => !l.checked).length;
  const totalErrors = errors.length + extrasArr.length;

  if (totalErrors === 0 && unchecked === 0) {
    banner("ok", "\u2714 Pall OK \u2013 inga avvikelser", false);
    beep("ok");
  } else {
    let msg = `Pall klar med ${totalErrors} avvikelse(r)`;
    if (unchecked > 0) msg += ` \u00b7 ${unchecked} ej kontrollerade`;
    banner("error", msg, false);
    beep("error");
  }

  // Spara pallen så att den kan ångras/återöppnas (Unfinish)
  const sscc = state.pallet.sscc;
  const finishedAt = new Date().toISOString();
  state.pallet.finishedAt = finishedAt;
  state.finished[sscc] = state.pallet;
  state.lastFinishedSscc = sscc;
  updateUnfinishButton();

  // Beräkna kontrolltid
  const durationSeconds = state.checkStartTime
    ? Math.round((Date.now() - state.checkStartTime) / 1000)
    : 0;

  // Skicka resultatet till servern (i bakgrunden, blockerar ej)
  saveCheckToServer({
    sscc: sscc,
    checkedBy: state.user,
    finishedAt: finishedAt,
    durationSeconds: durationSeconds,
    lines: state.pallet.lines,
    extras: aggregateExtras(extrasArr)
  });

  // Återställ för nästa pall (snabbflöde)
  setTimeout(() => {
    document.getElementById("pallet-area").classList.add("hidden");
    state.pallet = null;
    state.sscc = null;
    state.checkStartTime = null;
    document.getElementById("sscc-input").value = "";
    focusSscc();
  }, 1200);
}

function aggregateExtras(arr) {
  const counts = {};
  arr.forEach((c) => { counts[c] = (counts[c] || 0) + 1; });
  return Object.keys(counts).map((code) => ({ code, count: counts[code] }));
}

async function saveCheckToServer(data) {
  try {
    await fetch(`${API_BASE}/check`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });
  } catch (err) {
    console.error("Kunde inte spara check till server:", err);
  }
}

/* ---------- Unfinish / Ångra check ---------- */
function updateUnfinishButton() {
  const btn = document.getElementById("unfinish-btn");
  if (state.lastFinishedSscc) {
    btn.classList.remove("hidden");
    btn.textContent = "\u21BA Ångra check (F6)";
    btn.title = "Återöppna senaste inskickade pall: " + state.lastFinishedSscc;
  } else {
    btn.classList.add("hidden");
  }
}

function unfinishCheck() {
  const sscc = state.lastFinishedSscc;
  if (!sscc || !state.finished[sscc]) {
    banner("warn", "Ingen check att ångra");
    return;
  }
  reopenPallet(sscc, "Check ångrad – pall återöppnad med dina inmatningar");
}

document.getElementById("unfinish-btn").addEventListener("click", unfinishCheck);

/* ---------- Globala snabbkommandon ---------- */
document.addEventListener("keydown", (e) => {
  if (document.getElementById("app-view").classList.contains("hidden")) return;
  if (e.key === "F2") { e.preventDefault(); hideBanner(); focusSscc(); }
  if (e.key === "F4") { e.preventDefault(); finishCheck(); }
  if (e.key === "F6") { e.preventDefault(); unfinishCheck(); }
});
