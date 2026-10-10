// Panel de métricas de AMAGO (/stats?k=CLAVE): retención, embudo de la primera sesión, partidas y héroes.
"use strict";
const DAY = 864e5;
const day = (t) => Math.floor(t / DAY);
const pct = (a, b) => (b ? Math.round((a / b) * 1000) / 10 + " %" : "–");
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);

async function statsPage(store) {
  const now = Date.now();
  const ev = await store.allEvents(now - 60 * DAY);
  const users = await store.allUsers();
  const by = {};
  for (const e of ev) (by[e.uid] = by[e.uid] || []).push(e);
  const uids = Object.keys(by).filter(Boolean);

  // retención por cohorte (día del primer evento)
  const first = {};
  const days = {};
  for (const u of uids) {
    const ts = by[u].map((e) => e.t);
    first[u] = day(Math.min(...ts));
    days[u] = new Set(ts.map(day));
  }
  const today = day(now);
  const ret = (n) => {
    const elig = uids.filter((u) => first[u] + n <= today);
    return [elig.filter((u) => days[u].has(first[u] + n)).length, elig.length];
  };
  const [d1, d1n] = ret(1), [d7, d7n] = ret(7), [d30, d30n] = ret(30);

  // embudo de la primera sesión
  const has = (u, k, f) => by[u].some((e) => e.k === k && (!f || f(e)));
  const fn = [
    ["Abre el juego", (u) => has(u, "app_open")],
    ["Toca JUGAR", (u) => has(u, "play_tap")],
    ["Empieza la ronda 1", (u) => has(u, "round_start")],
    ["Primer disparo", (u) => has(u, "first_shot")],
    ["Termina la 1.ª partida", (u) => has(u, "match_end")],
    ["Juega una 2.ª partida", (u) => by[u].filter((e) => e.k === "match_end").length >= 2],
    ["Juega 5 partidas", (u) => by[u].filter((e) => e.k === "match_end").length >= 5],
    ["Vuelve otro día", (u) => days[u].size >= 2],
  ];
  const fnRows = fn.map(([n, f]) => [n, uids.filter(f).length]);

  // partidas y rondas
  const rounds = ev.filter((e) => e.k === "round_end" && e.d);
  const durs = rounds.map((e) => e.d.dur).filter((x) => typeof x === "number").sort((a, b) => a - b);
  const med = durs.length ? durs[durs.length >> 1].toFixed(1) + " s" : "–";
  const matches = ev.filter((e) => e.k === "match_end" && e.d);
  const quits = ev.filter((e) => e.k === "quit_mid").length;
  const firstWin = uids.map((u) => by[u].find((e) => e.k === "match_end")).filter(Boolean);
  const fw = firstWin.filter((e) => e.d && e.d.win).length;
  const modes = {};
  for (const m of matches) modes[m.d.mode || "bot"] = (modes[m.d.mode || "bot"] || 0) + 1;

  // héroes: veces elegido y rondas ganadas
  const H = {};
  for (const r of rounds) {
    const h = r.d.hero;
    if (!h) continue;
    H[h] = H[h] || { n: 0, w: 0 };
    H[h].n++;
    if (r.d.win) H[h].w++;
  }
  const decoys = ev.filter((e) => e.k === "amago").length;

  // usuarios activos por día (14 días)
  const dau = [];
  for (let i = 13; i >= 0; i--) {
    const d = today - i;
    dau.push([new Date(d * DAY).toISOString().slice(5, 10), uids.filter((u) => days[u].has(d)).length, uids.filter((u) => first[u] === d).length]);
  }

  const row = (c) => "<tr>" + c.map((x) => `<td>${esc(x)}</td>`).join("") + "</tr>";
  return `<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>AMAGO · métricas</title>
<style>body{margin:0;background:#0e1440;color:#eef2ff;font:15px/1.5 system-ui,sans-serif}main{max-width:820px;margin:auto;padding:20px 16px}
h1{margin:0 0 4px}h2{margin:26px 0 8px;color:#ffd23a;font-size:18px}.k{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px}
.c{background:#18205a;border-radius:12px;padding:12px}.c b{display:block;font-size:26px}.c small{color:#b9c3f2}table{width:100%;border-collapse:collapse}td{padding:6px 8px;border-bottom:1px solid #2a3480}
td:not(:first-child){text-align:right}.n{color:#b9c3f2;font-size:13px}</style></head><body><main>
<h1>AMAGO · métricas</h1><p class="n">Últimos 60 días · ${uids.length} jugadores con eventos · ${users.length} cuentas · almacenamiento: ${esc(store.kind)}</p>
<div class="k"><div class="c"><small>Vuelven al día siguiente (D1)</small><b>${pct(d1, d1n)}</b><small>${d1}/${d1n} · objetivo ≥35 %</small></div>
<div class="c"><small>Vuelven a la semana (D7)</small><b>${pct(d7, d7n)}</b><small>${d7}/${d7n} · objetivo ≥12 %</small></div>
<div class="c"><small>Vuelven al mes (D30)</small><b>${pct(d30, d30n)}</b><small>${d30}/${d30n} · objetivo ≥4 %</small></div>
<div class="c"><small>Duración mediana de ronda</small><b>${med}</b><small>${durs.length} rondas · objetivo 35-45 s</small></div></div>
<h2>Embudo de la primera sesión</h2><table>${fnRows.map(([n, v]) => row([n, v, pct(v, fnRows[0][1])])).join("")}</table>
<h2>Partidas</h2><table>${row(["Partidas terminadas", matches.length])}${row(["Ganan su primera partida", pct(fw, firstWin.length)])}${row(["Abandonos a mitad", quits])}${row(["Amagos usados", decoys])}${Object.entries(modes).map(([k, v]) => row(["Modo " + k, v])).join("")}</table>
<h2>Héroes (rondas)</h2><table>${row(["Héroe", "Rondas", "Ganadas"])}${Object.entries(H).sort((a, b) => b[1].n - a[1].n).map(([h, v]) => row([h, v.n, pct(v.w, v.n)])).join("")}</table>
<h2>Jugadores por día</h2><table>${row(["Día", "Activos", "Nuevos"])}${dau.map(row).join("")}</table>
</main></body></html>`;
}

module.exports = { statsPage };
