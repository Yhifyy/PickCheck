"use strict";

const API_BASE = "/api";

const state = {
  user: null,
  checkerUsername: null,
  sscc: null,
  pallet: null,
  filter: "ALL",
  activeIndex: -1,
  verifyRow: false,      // true när användaren klickat rad för att verifiera fysiskt paket
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
  state.checkerUsername = user.username;
  localStorage.setItem("pickcheck_user", JSON.stringify(user));
  localStorage.setItem("pickcheck_last_username", user.username); // Spara användarnamn för nästa gång
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
  state.checkerUsername = null;
  localStorage.removeItem("pickcheck_user");
  document.getElementById("app-view").classList.add("hidden");
  document.getElementById("login-view").classList.remove("hidden");
  document.getElementById("login-pass").value = "";
  hideAuthError();
}

// Auto-login om användare finns i localStorage
(async function autoLogin() {
  const saved = localStorage.getItem("pickcheck_user");
  if (saved) {
    try {
      let user = JSON.parse(saved);
      if (user.username) {
        try {
          const res = await fetch(`${API_BASE}/auth/user/${encodeURIComponent(user.username)}`);
          if (res.ok) {
            const fresh = await res.json();
            user = { ...user, displayName: fresh.displayName, role: fresh.role };
          }
        } catch { /* använd sparad data */ }
      }
      completeLogin(user);
    } catch {
      // Gammalt format (bara sträng) – rensa
      localStorage.removeItem("pickcheck_user");
    }
  }
  
  // Fyll i senaste användarnamnet om det finns
  const lastUsername = localStorage.getItem("pickcheck_last_username");
  if (lastUsername) {
    document.getElementById("login-user").value = lastUsername;
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
    state.verifyRow = false;
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
  normalizePalletExtras(state.pallet);
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
  return line.checked && !line.notOnPallet && !line.wrongProduct && line.checkedQty !== line.pickedQty;
}
function isQtyMatch(line) {
  return line.checked && line.checkedQty === line.pickedQty && !line.wrongProduct && !isWrongPallet(line);
}
function getCheckedQtyClass(line) {
  if (!line.checked || line.checkedQty === null || line.checkedQty === "") return "";
  if (line.wrongProduct) return "qty-mismatch";
  if (line.checkedQty > line.pickedQty) return "qty-mismatch";
  if (line.checkedQty === line.pickedQty && !isWrongPallet(line)) return "qty-match";
  if (line.checkedQty < line.pickedQty) return "qty-mismatch";
  return "";
}
function lineHasError(line) {
  return line.notOnPallet || line.wrongProduct || isWrongPallet(line) || isWrongAmount(line);
}

function promoteLineToTop(index) {
  const lines = state.pallet.lines;
  const line = lines[index];
  if (!line || line.notOnPallet || index <= 0) return index;
  lines.splice(index, 1);
  lines.unshift(line);
  return 0;
}

function scrollToRow(index, block) {
  const tr = document.querySelector(`#lines-body tr[data-index="${index}"]`);
  if (tr) tr.scrollIntoView({ block: block || "start", behavior: "smooth" });
}

/* ---------- Produkt-skanning ---------- */

// Hämta amount från fältet (tillåter negativa tal för korrigering)
function getAmount() {
  const amountInput = document.getElementById("amount-input");
  const val = parseInt(amountInput.value, 10);
  return isNaN(val) ? 1 : val;
}

// Submit-knappen
document.getElementById("submit-scan-btn").addEventListener("click", () => {
  const scanInput = document.getElementById("scan-input");
  const amountInput = document.getElementById("amount-input");
  const code = scanInput.value.trim();
  if (!code) {
    scanInput.focus();
    return;
  }
  const amount = getAmount();
  const isCorrect = scanProduct(code, amount);
  
  // Återställ amount till 0 alltid
  amountInput.value = "";
  
  // Om rätt antal: töm produktkoden också
  if (isCorrect) {
    scanInput.value = "";
  }
  scanInput.focus();
});

// Enter i produktfältet → submit
document.getElementById("scan-input").addEventListener("focus", () => {
  clearRowSelection();
});
document.getElementById("scan-input").addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    e.preventDefault();
    document.getElementById("submit-scan-btn").click();
  }
});

// Enter i antal-fältet → submit
document.getElementById("amount-input").addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    e.preventDefault();
    document.getElementById("submit-scan-btn").click();
  }
});

function refocusScan() {
  const s = document.getElementById("scan-input");
  s.focus();
  s.select();
}

function lineMatchesCode(line, code) {
  const codeLower = code.toLowerCase();
  return line.productNumber.toLowerCase() === codeLower ||
         (line.gtin && line.gtin.toLowerCase() === codeLower) ||
         (line.gtinInner && line.gtinInner.toLowerCase() === codeLower);
}

function findLineIndexByCode(code) {
  return state.pallet.lines.findIndex((l) => lineMatchesCode(l, code));
}

function markLineWrongProduct(index, scannedCode, matchedIdx) {
  const line = state.pallet.lines[index];
  line.wrongProduct = true;
  line.checked = true;
  line.checkTime = new Date().toLocaleDateString("sv-SE");

  let scannedDesc = scannedCode;
  if (matchedIdx >= 0) {
    const matched = state.pallet.lines[matchedIdx];
    scannedDesc = `${matched.productNumber} (${matched.product})`;
  }

  const newIdx = promoteLineToTop(index);
  renderLines();
  updateStats();
  updateProgress();
  state.activeIndex = newIdx;
  state.verifyRow = false;
  highlightActive();
  banner("error", `FEL PRODUKT: Rad ska vara ${line.productNumber} – du skannade ${scannedDesc}`, true);
  beep("error");
  refocusScan();
  return false;
}

function applyScanToLine(idx, amount) {
  const line = state.pallet.lines[idx];

  if (state.filter !== "ALL" && line.pallet !== state.filter) {
    state.filter = "ALL";
    renderFilterBar();
  }

  // Rätt streckkod skannad → produkten stämmer, rensa ev. fel-produkt-markering
  line.wrongProduct = false;

  const newQty = (line.checkedQty || 0) + amount;
  line.checkedQty = Math.max(0, newQty);
  line.checked = line.checkedQty > 0;
  line.checkTime = line.checkedQty > 0 ? new Date().toLocaleDateString("sv-SE") : "";

  const newIdx = promoteLineToTop(idx);
  renderLines();
  updateStats();
  updateProgress();

  state.activeIndex = newIdx;
  state.verifyRow = false;
  highlightActive();

  const n = line.checkedQty, m = line.pickedQty;
  const isCorrect = (n === m) && !isWrongPallet(line);
  const loc = line.location || "okänd plats";
  const typ = line.packageType || "st";

  if (amount < 0) {
    banner("ok", `Korrigerat: ${line.product} – nu ${n}/${m}`, false);
    beep("ok");
  } else if (isWrongPallet(line)) {
    banner("error", `FEL PALL: ${line.product} ligger på ${line.pallet} men ska på ${line.correctPallet} (räknat ${n}) — Plats: ${loc}`, true);
    beep("error");
  } else if (n > m) {
    const extra = n - m;
    banner("error", `FÖR MYCKET: ${line.product} – ${extra} ${typ} för mycket. Lämna tillbaka ${extra} ${typ} till plats ${loc}`, true);
    beep("error");
  } else if (n === m) {
    banner("ok", `Klar: ${line.product} – ${n}/${m} ${typ}`, false);
    beep("ok");
  } else {
    banner("ok", `${line.product} – räknat ${n}/${m} ${typ}`, false);
    beep("ok");
  }

  if (isWrongAmount(line)) {
    focusQtyForCorrection(newIdx);
  } else {
    refocusScan();
  }
  return isCorrect;
}

function applyUnknownProductScan(code, amount) {
  if (state.filter !== "ALL") {
    state.filter = "ALL";
    renderFilterBar();
  }

  const lines = state.pallet.lines;
  let idx = lines.findIndex((l) => l.notOnPallet && lineMatchesCode(l, code));

  if (idx >= 0) {
    const line = lines[idx];
    line.checkedQty = Math.max(0, (line.checkedQty || 0) + amount);
    line.checked = line.checkedQty > 0;
    line.checkTime = line.checkedQty > 0 ? new Date().toLocaleDateString("sv-SE") : "";
    if (idx < lines.length - 1) {
      lines.splice(idx, 1);
      lines.push(line);
      idx = lines.length - 1;
    }
  } else {
    lines.push({
      productNumber: code,
      product: "Ska inte finnas med på pall",
      gtin: "",
      gtinInner: "",
      picker: "—",
      pickedQty: 0,
      pallet: "—",
      correctPallet: null,
      checkedQty: Math.max(0, amount),
      checked: amount > 0,
      wrongProduct: true,
      notOnPallet: true,
      checkTime: amount > 0 ? new Date().toLocaleDateString("sv-SE") : ""
    });
    idx = lines.length - 1;
  }

  renderLines();
  updateStats();
  updateProgress();

  state.activeIndex = idx;
  state.verifyRow = false;
  highlightActive();
  scrollToRow(idx, "end");

  const line = lines[idx];
  banner("error",
    `Ska inte finnas med på pall: ${code} (räknat ${line.checkedQty})`, true);
  beep("error");
  refocusScan();
  return false;
}

// Skanna produkt med angivet antal
// amount = antal att lägga till (default 1)
// Returnerar true om checkedQty === pickedQty (korrekt), annars false
function scanProduct(raw, amount = 1) {
  const code = (raw || "").trim();
  if (!code || !state.pallet) return false;

  const idx = findLineIndexByCode(code);
  const activeIdx = state.activeIndex;

  // Aktiv rad vald för verifiering → jämför skanning mot den raden (auto fel produkt)
  if (state.verifyRow && activeIdx >= 0 && activeIdx < state.pallet.lines.length) {
    const activeLine = state.pallet.lines[activeIdx];
    if (!lineMatchesCode(activeLine, code)) {
      return markLineWrongProduct(activeIdx, code, idx);
    }
    return applyScanToLine(activeIdx, amount);
  }

  if (idx === -1) {
    return applyUnknownProductScan(code, amount);
  }

  return applyScanToLine(idx, amount);
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
  
  // Hämta alla unika pallar från produktraderna (A, B, C, D, E...)
  const uniquePallets = [...new Set(state.pallet.lines.map(l => l.pallet))].sort();
  
  // Om bara en pall finns, visa ändå filtret men utan "Visa alla"
  const filters = uniquePallets.length > 1 
    ? [{ key: "ALL", label: "Visa alla" }, ...uniquePallets.map(p => ({ key: p, label: `${p}-pall` }))]
    : uniquePallets.map(p => ({ key: p, label: `${p}-pall` }));
  
  bar.innerHTML = "";
  filters.forEach((f) => {
    const b = document.createElement("button");
    b.className = "filter-btn" + (state.filter === f.key ? " active" : "");
    b.textContent = f.label;
    b.addEventListener("click", () => { state.filter = f.key; renderLines(); updateProgress(); });
    bar.appendChild(b);
  });
  
  // Om bara en pall, sätt filtret till den pallen
  if (uniquePallets.length === 1 && state.filter === "ALL") {
    state.filter = uniquePallets[0];
  }
}

function visibleLines() {
  const palletLines = state.pallet.lines
    .map((l, i) => ({ line: l, index: i }))
    .filter((x) => !x.line.notOnPallet)
    .filter((x) => state.filter === "ALL" || x.line.pallet === state.filter);
  const unknownLines = state.pallet.lines
    .map((l, i) => ({ line: l, index: i }))
    .filter((x) => x.line.notOnPallet);
  return [...palletLines, ...unknownLines];
}

function firstVisibleIndex() {
  const v = visibleLines();
  return v.length ? v[0].index : -1;
}

function renderLines() {
  const body = document.getElementById("lines-body");
  body.innerHTML = "";
  const showPallet = true; // Visa alltid pall-bokstaven (A, B, C, D...)

  visibleLines().forEach(({ line, index }) => {
    const tr = document.createElement("tr");
    tr.dataset.index = index;
    const wrongPallet = isWrongPallet(line);
    const hasError = lineHasError(line);
    const isUnknown = line.notOnPallet;

    if (isUnknown) tr.classList.add("unknown-product-row");
    if (line.checked && !hasError) tr.classList.add("ok-row");
    if (hasError) tr.classList.add("error-row");

    // Status-ikon
    let statusIcon = "";
    if (isUnknown) statusIcon = '<span class="status-error" title="Finns ej på pallen">\u2716</span>';
    else if (line.wrongProduct) statusIcon = '<span class="status-error" title="Fel produkt">\u2716</span>';
    else if (wrongPallet) statusIcon = '<span class="status-error" title="Fel pall">\u21C4</span>';
    else if (line.checked) {
      if (!hasError) statusIcon = '<span class="status-ok">\u2714</span>';
      else statusIcon = '<span class="status-error">\u26A0</span>';
    }

    // Pall-cell: vid fel pall visas "plockad → ska", annars bara pallen
    let palletPill = "";
    if (showPallet) {
      if (isUnknown) {
        palletPill = '<span class="unknown-pallet-badge">EJ PÅ PALLEN</span>';
      } else if (wrongPallet) {
        palletPill = `<span class="pill pill-${line.pallet}">${line.pallet}</span>` +
          ` <span class="pallet-arrow">\u2192</span> ` +
          `<span class="pill pill-${line.correctPallet}">${line.correctPallet}</span>`;
      } else {
        palletPill = `<span class="pill pill-${line.pallet}">${line.pallet}</span>`;
      }
    }

    const qtyClass = getCheckedQtyClass(line);
    const checkedVal = line.checkedQty === null || line.checkedQty === "" ? "" : line.checkedQty;
    const hasChecked = checkedVal !== "";
    const isExtra = !isUnknown && hasChecked && line.checkedQty > line.pickedQty;
    const extraBadge = isExtra
      ? `<span class="qty-extra">+${line.checkedQty - line.pickedQty} extra</span>`
      : (isUnknown && hasChecked ? '<span class="qty-extra">fel produkt</span>' : "");

    const productCell = isUnknown
      ? `<span class="unknown-product-label">${line.product}</span>`
      : line.product;
    const pickedCell = isUnknown ? "—" : line.pickedQty;

    const locationCell = isUnknown ? "—" : (line.location || "—");
    const typeCell = isUnknown ? "—" : (line.packageType || "—");

    tr.innerHTML = `
      <td class="status-cell">${statusIcon}</td>
      <td>${palletPill}</td>
      <td class="location-cell">${locationCell}</td>
      <td>${line.productNumber}</td>
      <td>${productCell}</td>
      <td class="type-cell">${typeCell}</td>
      <td>${line.picker}</td>
      <td class="picked-qty">${pickedCell}</td>
      <td class="checked-qty-cell">
        <div class="qty-ratio-wrap ${qtyClass}">
          <input type="number" class="qty-input ${qtyClass}" data-index="${index}" value="${checkedVal}" placeholder="${hasChecked ? "" : "0"}" />
          ${extraBadge}
        </div>
      </td>
      <td>${line.checkTime || ""}</td>
    `;
    body.appendChild(tr);

    tr.addEventListener("click", () => {
      if (state.activeIndex === index && state.verifyRow) {
        clearRowSelection();
      } else {
        setActiveRow(index, true, true);
      }
    });
  });

  // Koppla händelser på antalsfälten
  body.querySelectorAll(".qty-input").forEach((inp) => {
    inp.addEventListener("focus", () => {
      state.activeIndex = parseInt(inp.dataset.index, 10);
      highlightActive();
    });
    inp.addEventListener("input", () => { inp.dataset.dirty = "1"; });
    inp.addEventListener("keydown", onQtyKeydown);
  });

  if (state.activeIndex >= 0) highlightActive();
}

function clearRowSelection() {
  state.activeIndex = -1;
  state.verifyRow = false;
  highlightActive();
}

function setActiveRow(index, skipFocus, verify) {
  state.activeIndex = index;
  if (verify !== undefined) state.verifyRow = verify;
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
    inp.closest("tr").scrollIntoView({ block: "start", behavior: "smooth" });
  }
}

function focusQtyForCorrection(index) {
  state.activeIndex = index;
  state.verifyRow = false;
  highlightActive();
  setTimeout(() => focusLine(index), 0);
}

/* ---------- Antalsfält: tangentbord ---------- */
function onQtyKeydown(e) {
  const index = parseInt(e.target.dataset.index, 10);

  if (e.key === "Enter") {
    e.preventDefault();
    if (e.shiftKey) { toggleWrongProduct(index); return; }
    confirmAllQtyInputs(index);
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

function shouldProcessQtyInput(inp, triggerIndex) {
  const raw = inp.value.trim();
  if (raw === "") return false;
  const index = parseInt(inp.dataset.index, 10);
  const line = state.pallet.lines[index];
  if (!line || line.notOnPallet) return false;
  if (isNaN(parseInt(raw, 10))) return false;
  if (inp.dataset.dirty === "1") return true;
  if (index !== triggerIndex) return false;
  const val = parseInt(raw, 10);
  if (line.checked && val === line.checkedQty && val === line.pickedQty && !lineHasError(line)) {
    return false;
  }
  return true;
}

function applyQtyDeltaToLine(index, delta) {
  const line = state.pallet.lines[index];
  const newQty = Math.max(0, (line.checkedQty || 0) + delta);
  line.checkedQty = newQty;
  line.checked = newQty > 0;
  line.checkTime = newQty > 0 ? new Date().toLocaleDateString("sv-SE") : "";

  if (newQty === line.pickedQty && !isWrongPallet(line)) {
    line.wrongProduct = false;
  }
  promoteLineToTop(index);
  return { line, newQty, delta };
}

function confirmAllQtyInputs(triggerIndex) {
  const inputs = [...document.querySelectorAll("#lines-body .qty-input")];
  const toProcess = inputs.filter((inp) => shouldProcessQtyInput(inp, triggerIndex));

  if (!toProcess.length) {
    banner("warn", "Ange ett antal");
    beep("error");
    return;
  }

  const results = [];
  toProcess.forEach((inp) => {
    const index = parseInt(inp.dataset.index, 10);
    const delta = parseInt(inp.value.trim(), 10);
    delete inp.dataset.dirty;
    const r = applyQtyDeltaToLine(index, delta);
    if (r) results.push(r);
  });

  renderLines();
  updateStats();
  updateProgress();

  let errorCount = 0;
  results.forEach(({ line, newQty }) => {
    if (lineHasError(line)) errorCount++;
    else if (newQty === line.pickedQty && !isWrongPallet(line)) line.wrongProduct = false;
  });

  if (results.length === 1) {
    const { line, newQty, delta } = results[0];
    if (delta < 0) {
      banner("ok", `Korrigerat: ${line.product} – nu ${newQty}/${line.pickedQty}`, false);
      beep("ok");
    } else if (!lineHasError(line)) {
      banner("ok", `Klar: ${line.product} – ${newQty}/${line.pickedQty}`, false);
      beep("ok");
    } else {
      beep("error");
      const loc = line.location || "okänd plats";
      const typ = line.packageType || "st";
      let diff;
      if (isWrongPallet(line)) diff = `FEL PALL: ligger på ${line.pallet} men ska på ${line.correctPallet} — Plats: ${loc}`;
      else if (line.wrongProduct) diff = "fel produkt";
      else if (newQty > line.pickedQty) diff = `${newQty - line.pickedQty} ${typ} för mycket — Lämna tillbaka till plats ${loc}`;
      else diff = `${line.pickedQty - newQty} ${typ} saknas — Hämta från plats ${loc}`;
      banner("error", `Avvikelse: ${line.product} (${diff})`);
    }
  } else {
    const okCount = results.length - errorCount;
    if (errorCount === 0) {
      banner("ok", `Registrerade ${results.length} rader`, false);
      beep("ok");
    } else {
      banner("error", `Registrerade ${results.length} rader (${okCount} ok, ${errorCount} avvikelser)`, true);
      beep("error");
    }
  }

  const qtyErrorIdx = state.pallet.lines.findIndex((l) => isWrongAmount(l));

  if (qtyErrorIdx >= 0) {
    focusQtyForCorrection(qtyErrorIdx);
  } else {
    const next = nextUncheckedIndex(triggerIndex);
    if (next >= 0) {
      setActiveRow(next);
    } else {
      const allDone = state.pallet.lines
        .filter((l) => !l.notOnPallet)
        .every((l) => l.checked);
      if (allDone) {
        banner("ok", "Alla produkter kontrollerade \u2013 tryck F4 för Finish Check", true);
        document.getElementById("finish-btn").focus();
      }
    }
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
    if (!state.pallet.lines[idx].checked && !state.pallet.lines[idx].notOnPallet) return idx;
  }
  return -1;
}

/* ---------- Progress ---------- */
function updateProgress() {
  const palletLines = state.pallet.lines.filter((l) => !l.notOnPallet);
  const visible = palletLines.filter((l) => state.filter === "ALL" || l.pallet === state.filter);
  const done = visible.filter((l) => l.checked).length;
  document.getElementById("progress-text").textContent =
    `Kontrollerade ${done} av ${visible.length} produkter`;
}

/* ---------- Statistik ---------- */
function updateStats() {
  const lines = state.pallet.lines;
  const wrongAmount = lines.filter(isWrongAmount);
  const wrongProduct = lines.filter((l) => l.wrongProduct && !l.notOnPallet);
  const wrongPallet = lines.filter(isWrongPallet);
  const unknownLines = lines.filter((l) => l.notOnPallet);

  let html = "";
  html += statsGroup("Fel antal", wrongAmount.map((l) => {
    const loc = l.location || "okänd plats";
    const typ = l.packageType || "st";
    if (l.checkedQty > l.pickedQty) {
      const extra = l.checkedQty - l.pickedQty;
      return `${l.productNumber} ${l.product} — <strong>${extra} ${typ} för mycket → Lämna tillbaka till plats ${loc}</strong>`;
    } else {
      const missing = l.pickedQty - l.checkedQty;
      return `${l.productNumber} ${l.product} — <strong>${missing} ${typ} saknas → Hämta från plats ${loc}</strong>`;
    }
  }));
  html += statsGroup("Fel produkt", wrongProduct.map(
    (l) => `${l.productNumber} ${l.product}` + (state.pallet.twoPallets ? ` <span class="pill pill-${l.pallet}">${l.pallet}</span>` : "")));
  html += statsGroup("Fel pall", wrongPallet.map(
    (l) => `${l.productNumber} ${l.product} <strong>(ligger på <span class="pill pill-${l.pallet}">${l.pallet}</span> \u2192 ska på <span class="pill pill-${l.correctPallet}">${l.correctPallet}</span>) — Plats: ${l.location || "okänd"}</strong>`));
  html += statsGroup("Ska inte finnas med på pall", unknownLines.map(
    (l) => `${l.productNumber} <strong>Ska inte finnas med på pall</strong> (räknat ${l.checkedQty}) — Lämna tillbaka`));

  if (!wrongAmount.length && !wrongProduct.length && !wrongPallet.length && !unknownLines.length) {
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
  const unknownLines = state.pallet.lines.filter((l) => l.notOnPallet);
  const unchecked = state.pallet.lines.filter((l) => !l.notOnPallet && !l.checked).length;
  const totalErrors = errors.length;

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
    checkedByUsername: state.checkerUsername || getCheckerUsername(),
    finishedAt: finishedAt,
    durationSeconds: durationSeconds,
    lines: state.pallet.lines,
    extras: aggregateUnknownLines(unknownLines)
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

function normalizePalletExtras(pallet) {
  if (!pallet || !pallet.extras || !pallet.extras.length) return;
  aggregateExtras(pallet.extras).forEach(({ code, count }) => {
    if (!pallet.lines.some((l) => l.notOnPallet && l.productNumber === code)) {
      pallet.lines.push({
        productNumber: code,
        product: "Ska inte finnas med på pall",
        gtin: "", gtinInner: "",
        picker: "—", pickedQty: 0, pallet: "—", correctPallet: null,
        checkedQty: count, checked: true, wrongProduct: true, notOnPallet: true,
        checkTime: new Date().toLocaleDateString("sv-SE")
      });
    }
  });
  pallet.extras = [];
}

function aggregateUnknownLines(lines) {
  const counts = {};
  lines.forEach((l) => {
    const code = l.productNumber;
    counts[code] = (counts[code] || 0) + (l.checkedQty || 1);
  });
  return Object.keys(counts).map((code) => ({ code, count: counts[code] }));
}

function aggregateExtras(arr) {
  const counts = {};
  arr.forEach((c) => { counts[c] = (counts[c] || 0) + 1; });
  return Object.keys(counts).map((code) => ({ code, count: counts[code] }));
}

function getCheckerUsername() {
  try {
    const saved = localStorage.getItem("pickcheck_user");
    if (saved) {
      const user = JSON.parse(saved);
      return user.username || null;
    }
  } catch { /* ignore */ }
  return localStorage.getItem("pickcheck_last_username") || null;
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
  if (e.key === "Escape") { e.preventDefault(); clearRowSelection(); refocusScan(); return; }
  if (e.key === "F2") { e.preventDefault(); hideBanner(); focusSscc(); }
  if (e.key === "F4") { e.preventDefault(); finishCheck(); }
  if (e.key === "F6") { e.preventDefault(); unfinishCheck(); }
});
