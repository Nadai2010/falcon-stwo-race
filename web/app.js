// Dashboard: renders the lanes from /api/config, streams /api/race, and draws what the server measures.
const $ = (sel, el = document) => el.querySelector(sel);
const GiB = 1024 ** 3;
const css = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();

const state = { lanes: [], view: {}, source: null, replayTimer: null, eyebrow: "" };

const fmt = {
  s: (v) => `${v.toFixed(v < 100 ? 2 : 1)} s`,
  gib: (b) => `${(b / GiB).toFixed(2)} GiB`,
  gas: (g) => g.toLocaleString("en-US"),
  x: (r) => `${r.toFixed(r < 10 ? 2 : 1)}×`,
};

async function init() {
  const cfg = await (await fetch("/api/config")).json();
  state.lanes = cfg.lanes;
  if (cfg.missing.length) showSetup(cfg.missing);
  const host = $("#lanes");
  const tpl = $("#lane-tpl");
  cfg.lanes.forEach((lane, i) => {
    const el = tpl.content.firstElementChild.cloneNode(true);
    el.style.setProperty("--i", i);
    el.dataset.lane = lane.id;
    $(".kicker", el).textContent = lane.kicker;
    $(".lane-title", el).textContent = lane.title;
    $(".lane-sub", el).textContent = lane.subtitle;
    const credit = lane.official.text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/@([\w-]+)/g, '<span class="who">@$1</span>');
    $(".official", el).innerHTML = `${credit} <a href="${lane.official.source}" target="_blank" rel="noopener">Source</a>, ${lane.official.date}.`;
    const ch = $(".challenge", el);
    ch.href = lane.challenge.url;
    $("span", ch).textContent = lane.challenge.text;
    for (const side of ["original", "record"]) {
      const s = $(`.side[data-side="${side}"]`, el);
      $(".side-label", s).textContent = lane[side].label;
      $(".chip", s).textContent = "ready";
    }
    if (lane.kind === "gas") {
      $(".plot", el).hidden = true;
      $(".gasbars", el).hidden = false;
    }
    host.append(el);
    state.view[lane.id] = { el, series: { original: [], record: [] }, done: {}, maxT: 10, maxM: GiB };
    drawPlot(lane.id);
  });
  loadPeople();
  clearMainnet();
  const rp = new URLSearchParams(location.search).get("replay");
  if (rp !== null) replay(rp === "sequential" ? "sample-run-sequential.json" : "sample-run.json");
  $("#go").addEventListener("click", toggle);

  state.eyebrow = $(".eyebrow").textContent;
  window.addEventListener("keydown", (e) => {
    if (e.target.closest("input, textarea") || e.ctrlKey || e.metaKey || e.altKey || e.repeat) return;
    if (e.key === "r" || e.key === "R") start();
    if (e.key === "Escape") stop();
  });
  window.addEventListener("resize", () => state.lanes.forEach((l) => drawPlot(l.id)));
  if ("ResizeObserver" in window) {
    const ro = new ResizeObserver(() => state.lanes.forEach((l) => drawPlot(l.id)));
    document.querySelectorAll(".viz").forEach((v) => ro.observe(v));
  }
}

// Replay of a recorded run (web/data/sample-run.json), clearly labelled: for screenshots and machines without builds.
async function replay(file) {
  const run = await (await fetch(`data/${file}`)).json();
  document.querySelector(`input[name="mode"][value="${run.mode}"]`).checked = true;
  $(".eyebrow").textContent = `Replay · a run recorded on ${run.recorded} · press Run to measure live`;
  const box = $("#setup");
  box.hidden = false;
  box.classList.add("replay");
  const how = run.mode === "parallel" ? "side by side" : "one after the other";
  box.textContent = `Replay of a run measured on ${run.recorded}, ${run.machine}, ${how}.`;
  for (const lane of state.lanes) reset(lane.id);
  let i = 0;
  const step = () => {
    for (let k = 0; k < 3 && i < run.events.length; k++) {
      const ev = run.events[i++];
      if (ev.type !== "end") handle(ev);
    }
    state.replayTimer = i < run.events.length ? setTimeout(step, 16) : null;
    if (!state.replayTimer) {
      mainnet({ lane: "falcon", state: "recorded" });
      setStatus("Replay finished. Press R to measure live.");
      document.querySelectorAll(".lane.active").forEach((l) => l.classList.remove("active"));
    }
  };
  step();
}

function notice(text) {
  const box = $("#setup");
  box.hidden = false;
  box.classList.remove("replay");
  box.textContent = text;
}

function showSetup(missing) {
  const box = $("#setup");
  box.hidden = false;
  box.innerHTML = `Not built yet on this machine: <code>${missing.join("</code>, <code>")}</code>.<br>Run <code>make setup</code> (see docs/setup.md), or point <code>config.local.json</code> at existing builds.`;
}

function toggle() { state.source ? stop() : start(); }

function setStatus(text, live = false) {
  const el = $("#status");
  el.textContent = text;
  el.classList.toggle("live", live);
}

function stopReplay() {
  clearTimeout(state.replayTimer);
  state.replayTimer = null;
  $(".eyebrow").textContent = state.eyebrow;
  const box = $("#setup");
  if (box.classList.contains("replay")) { box.hidden = true; box.classList.remove("replay"); }
}

async function start() {
  if (state.source) return;
  stopReplay();
  try {
    const st = await (await fetch("/api/status")).json();
    if (st.busy) { notice("A race is still running or stopping. Try again in a few seconds."); return; }
  } catch { notice("The race server is not reachable. Start it with make run."); return; }
  for (const lane of state.lanes) reset(lane.id);
  const mode = document.querySelector('input[name="mode"]:checked').value;
  const src = new EventSource(`/api/race?mode=${mode}`);
  state.source = src;
  const go = $("#go");
  go.classList.add("running");
  $(".go-run", go).setAttribute("aria-hidden", "true");
  $(".go-stop", go).removeAttribute("aria-hidden");
  setStatus("Starting…", true);
  src.onmessage = (m) => handle(JSON.parse(m.data));
  src.onerror = () => stop();
}

function stop() {
  if (!state.source) return;
  state.source.close();
  state.source = null;
  const go = $("#go");
  go.classList.remove("running");
  $(".go-stop", go).setAttribute("aria-hidden", "true");
  $(".go-run", go).removeAttribute("aria-hidden");
  setStatus("Done. Press R to race again.");
  document.querySelectorAll(".chip.run").forEach((c) => { c.className = "chip"; c.textContent = "stopped"; });
  document.querySelectorAll(".lane.active").forEach((l) => l.classList.remove("active"));
}

function reset(id) {
  const v = state.view[id];
  v.series = { original: [], record: [] };
  v.done = {};
  v.maxT = 10;
  v.maxM = GiB;
  $(".verdict", v.el).hidden = true;
  for (const side of ["original", "record"]) {
    const s = sideEl(id, side);
    $(".r-main", s).textContent = "—";
    $(".r-sub", s).textContent = "";
    setChip(id, side, "", "waiting");
    $(`.gasbar[data-side="${side}"]`, v.el).classList.remove("scan");
    $(`.gasbar[data-side="${side}"] i`, v.el).style.width = "0";
    $(`.gasbar[data-side="${side}"] b`, v.el).textContent = "";
    if (id === "falcon") clearMainnet();

  }
  drawPlot(id);
}

const sideEl = (id, side) => $(`.side[data-side="${side}"]`, state.view[id].el);
function setChip(id, side, cls, text) {
  const c = $(".chip", sideEl(id, side));
  c.className = `chip ${cls}`.trim();
  c.textContent = text;
}

function handle(ev) {
  if (ev.type === "end") return stop();
  const v = state.view[ev.lane];
  if (!v) return;
  const lane = state.lanes.find((l) => l.id === ev.lane);
  if (ev.type === "lane") {
    v.el.classList.toggle("active", ev.state === "running");
    if (ev.state === "running") {
      if (state.source && window.innerWidth < 1100) v.el.scrollIntoView({ behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth", block: "center" });
      setStatus(`Racing: ${lane.title}`, true);
      for (const side of ["original", "record"]) {
        setChip(ev.lane, side, "run", lane.kind === "gas" ? "compiling" : "proving");
        if (lane.kind === "gas") $(`.gasbar[data-side="${side}"]`, v.el).classList.add("scan");
      }
      if (ev.mode === "sequential" && lane.kind !== "gas") setChip(ev.lane, "record", "", "next");
    }
    if (ev.state === "error") {
      for (const side of ["original", "record"]) setChip(ev.lane, side, "bad", "error");
      $(".r-sub", sideEl(ev.lane, "original")).textContent = ev.error;
    }
    return;
  }
  if (ev.type === "tick") {
    if (v.done[ev.side]) return;
    if (lane.kind !== "gas") setChip(ev.lane, ev.side, "run", "proving");
    v.series[ev.side].push([ev.t, ev.rss]);
    v.maxT = Math.max(v.maxT, ev.t * 1.08);
    v.maxM = Math.max(v.maxM, ev.peak * 1.12);
    const s = sideEl(ev.lane, ev.side);
    if (lane.kind === "gas") {
      $(".r-main", s).textContent = fmt.s(ev.t);
      $(".r-sub", s).textContent = "snforge running";
    } else {
      $(".r-main", s).textContent = lane.metric === "memory" ? fmt.gib(ev.peak) : fmt.s(ev.t);
      $(".r-sub", s).textContent = lane.metric === "memory" ? `peak · ${fmt.s(ev.t)}` : `${fmt.gib(ev.rss)} now`;
    }
    schedule(ev.lane);
    return;
  }
  if (ev.type === "done") {
    v.done[ev.side] = ev;
    const s = sideEl(ev.lane, ev.side);
    if (!ev.ok) { setChip(ev.lane, ev.side, "bad", "failed"); $(".r-sub", s).textContent = ev.tail.slice(-120); return; }
    if (lane.kind !== "gas") {
      $(".r-main", s).textContent = lane.metric === "memory" ? fmt.gib(ev.peak) : fmt.s(ev.t);
      $(".r-sub", s).textContent = lane.metric === "memory" ? `peak · ${fmt.s(ev.t)}` : `peak ${fmt.gib(ev.peak)}`;
      setChip(ev.lane, ev.side, "", "proof done");
    }
    schedule(ev.lane);
    return;
  }
  if (ev.type === "verified") {
    v.done[ev.side].verified = ev.ok;
    v.done[ev.side].bytes = ev.bytes;
    setChip(ev.lane, ev.side, ev.ok ? "ok" : "bad", ev.ok ? "verified" : "rejected");
    verdict(lane);
    return;
  }
  if (ev.type === "mainnet") {
    mainnet(ev);
    return;
  }
  if (ev.type === "gas") {
    v.done[ev.side] = { ...(v.done[ev.side] || {}), gas: ev.gas, ok: ev.ok };
    const s = sideEl(ev.lane, ev.side);
    $(`.gasbar[data-side="${ev.side}"]`, v.el).classList.remove("scan");
    if (!ev.ok || ev.gas == null) { setChip(ev.lane, ev.side, "bad", "failed"); return; }
    countUp($(".r-main", s), ev.gas);
    $(".r-sub", s).textContent = "Sierra gas";
    setChip(ev.lane, ev.side, "ok", "valid");
    const max = Math.max(...["original", "record"].map((k) => v.done[k]?.gas || 0));
    for (const k of ["original", "record"]) {
      const g = v.done[k]?.gas;
      if (!g) continue;
      $(`.gasbar[data-side="${k}"] i`, v.el).style.width = `${(100 * g) / max}%`;
      $(`.gasbar[data-side="${k}"] b`, v.el).textContent = `${(g / 1e6).toFixed(1)}M gas`;
    }
    verdict(lane);
  }
}

function verdict(lane) {
  const v = state.view[lane.id];
  const a = v.done.original, b = v.done.record;
  if (!a || !b) return;
  let ratio, text;
  if (lane.kind === "gas") {
    if (!a.ok || !b.ok || !a.gas || !b.gas) return;
    ratio = a.gas / b.gas; text = "cheaper to verify";
  } else {
    if (a.verified === undefined || b.verified === undefined || !a.verified || !b.verified) return;
    if (lane.metric === "memory") { ratio = a.peak / b.peak; text = "less memory, same proof"; }
    else { ratio = a.t / b.t; text = "faster, same verifier"; }
  }
  const box = $(".verdict", v.el);
  $(".verdict-num", box).textContent = fmt.x(ratio);
  $(".verdict-txt", box).textContent = text;
  box.hidden = false;
  box.classList.remove("pop"); void box.offsetWidth; box.classList.add("pop");
}

// Empty until the Falcon race has finished and signed: nothing is priced before that.
function clearMainnet() {
  const v = state.view.falcon;
  const box = v && $(".mainnet", v.el);
  if (!box) return;
  box.classList.remove("busy");
  for (const el of box.querySelectorAll(".mn-strk, .mn-usd")) el.textContent = "—";
  $(".mn-ratio", box).textContent = "";
  $(".mn-meta", box).textContent = "priced after the Falcon race";
  $(".mn-src", box).textContent = "";
}

// Mainnet price of one Falcon-signed transaction per account: live simulation, or the recorded one.
async function mainnet(ev) {
  const box = $(".mainnet", state.view[ev.lane].el);
  if (!box) return;
  if (ev.state === "running") {
    $(".mn-meta", box).textContent = "signing and simulating on mainnet…";
    box.classList.add("busy");
    return;
  }
  box.classList.remove("busy");
  let data = ev.data, live = ev.state === "done";
  if (!data) {
    try { data = await (await fetch("data/mainnet-sim.json")).json(); } catch { return; }
  }
  let price = null;
  try { price = await (await fetch("/api/price")).json(); } catch {}
  const usd = price && price.usd;
  for (const side of ["original", "record"]) {
    const row = $(`.mn-row[data-side="${side}"]`, box);
    const fee = data.sides[side].invoke.fee_strk;
    $(".mn-strk", row).textContent = `${fee.toFixed(3)} STRK`;
    $(".mn-usd", row).textContent = usd ? `$${(fee * usd).toFixed(3)}` : "";
  }
  const a = data.sides.original.invoke, b = data.sides.record.invoke;
  const when = new Date(data.timestamp * 1000).toISOString().slice(0, 10);
  $(".mn-meta", box).textContent = `${live ? "signed now" : "last simulation"} · block ${data.block.toLocaleString("en-US")}${live ? "" : ` · ${when}`}`;
  $(".mn-ratio", box).textContent = `${(a.fee_strk / b.fee_strk).toFixed(2)}× cheaper`;
  $(".mn-src", box).textContent = usd ? `USD via ${price.source}` : "USD unavailable";
}

function countUp(el, target) {
  const t0 = performance.now(), dur = 1200;
  const step = (now) => {
    const k = Math.max(0, Math.min(1, (now - t0) / dur));
    el.textContent = fmt.gas(Math.round(target * (1 - (1 - k) ** 3)));
    if (k < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}

const pending = new Set();
function schedule(id) {
  if (pending.has(id)) return;
  pending.add(id);
  requestAnimationFrame(() => { pending.delete(id); drawPlot(id); });
}

function drawPlot(id) {
  const v = state.view[id];
  const canvas = $(".plot", v.el);
  if (canvas.hidden) return;
  const dpr = window.devicePixelRatio || 1;
  const w = canvas.clientWidth, h = canvas.clientHeight;
  if (!w) return;
  canvas.width = w * dpr; canvas.height = h * dpr;
  const g = canvas.getContext("2d");
  g.scale(dpr, dpr);
  const pad = { l: 46, r: 12, t: 12, b: 24 };
  const pw = w - pad.l - pad.r, ph = h - pad.t - pad.b;
  const X = (t) => pad.l + (t / v.maxT) * pw;
  const Y = (m) => pad.t + ph - (m / v.maxM) * ph;
  g.font = `400 10px ${css("--mono")}`;
  g.fillStyle = css("--faint");
  g.strokeStyle = css("--line-soft");
  g.lineWidth = 1;
  const gStep = niceStep(v.maxM / GiB, 4);
  for (let m = 0; m <= v.maxM / GiB + 1e-9; m += gStep) {
    const y = Y(m * GiB);
    g.beginPath(); g.moveTo(pad.l, y); g.lineTo(w - pad.r, y); g.stroke();
    g.fillText(`${m.toFixed(gStep < 1 ? 1 : 0)} GiB`, 2, y + 3);
  }
  const tStep = niceStep(v.maxT, 6);
  for (let t = 0; t <= v.maxT; t += tStep) g.fillText(`${Math.round(t)}s`, X(t) - 6, h - 6);
  for (const side of ["original", "record"]) {
    const pts = v.series[side];
    if (pts.length < 2) continue;
    const color = side === "record" ? css("--rec") : css("--orig");
    g.beginPath();
    pts.forEach(([t, m], i) => (i ? g.lineTo(X(t), Y(m)) : g.moveTo(X(t), Y(m))));
    g.strokeStyle = color; g.lineWidth = side === "record" ? 2.2 : 1.6;
    g.shadowColor = side === "record" ? css("--rec-glow") : "transparent"; g.shadowBlur = side === "record" ? 12 : 0;
    g.stroke();
    g.shadowBlur = 0;
    g.lineTo(X(pts.at(-1)[0]), Y(0)); g.lineTo(X(pts[0][0]), Y(0)); g.closePath();
    g.fillStyle = side === "record" ? "rgba(255,106,43,0.08)" : "rgba(169,178,184,0.06)";
    g.fill();
    const fin = v.done[side];
    if (fin?.ok) {
      const x = X(fin.t);
      g.strokeStyle = color; g.setLineDash([3, 4]); g.lineWidth = 1;
      g.beginPath(); g.moveTo(x, pad.t); g.lineTo(x, pad.t + ph); g.stroke(); g.setLineDash([]);
      g.fillStyle = color; g.font = `600 11px ${css("--mono")}`;
      g.fillText(fmt.s(fin.t), Math.min(x + 6, w - 70), pad.t + 12 + (side === "record" ? 0 : 16));
      g.font = `400 10px ${css("--mono")}`;
    }
  }
}

function niceStep(range, target) {
  const raw = range / target;
  const p = 10 ** Math.floor(Math.log10(raw || 1));
  return [1, 2, 2.5, 5, 10].map((k) => k * p).find((s) => s >= raw) || p * 10;
}

async function loadPeople() {
  try {
    const data = await (await fetch("data/contributors.json")).json();
    const ul = $("#people");
    for (const p of data.people) {
      const li = document.createElement("li");
      const a = document.createElement("a");
      a.href = `https://github.com/${encodeURIComponent(p.login)}`;
      a.target = "_blank";
      a.rel = "noopener";
      const img = document.createElement("img");
      img.alt = "";
      img.loading = "lazy";
      img.src = `https://avatars.githubusercontent.com/u/${Number(p.user_id)}?s=128`;
      a.dataset.login = `@${p.login} · ${p.activity}`;
      a.setAttribute("aria-label", `@${p.login}, ${p.activity} contributions`);
      img.src = `https://avatars.githubusercontent.com/u/${Number(p.user_id)}?s=96`;
      a.append(img);
      li.append(a);
      ul.append(li);
    }
    $("#people-count").textContent = `${data.people.length} people, ${data.people.reduce((n, p) => n + p.activity, 0).toLocaleString("en-US")} contributions`;
    $("#people-date").textContent = `fetched ${data.fetched}`;
  } catch {
    $("#people-count").textContent = "run make contributors";
  }
}

init();
