// Servidor online de AMAGO: sirve el juego y gestiona las salas con WebSocket.
// Modos: sala privada con código (amigos) y cola de emparejamiento por trofeos (online).
// El motor de reglas se lee del propio index.html (bloque ENGINE), así cliente y servidor juegan con las mismas reglas.
"use strict";
const http = require("http");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");
const { WebSocketServer } = require("ws");
const Store = require("./store");
const { makeApi, auth } = require("./api");
const { statsPage } = require("./stats");
let STORE = null;
let API = null;

const INDEX = path.join(__dirname, "..", "index.html");
const PORT = Number(process.env.PORT) || 8080;
const TICK_MS = 50;
const VIEW_EVERY = 2; // envía la vista cada 2 ticks (10 veces por segundo)
const COUNTDOWN_MS = 3300; // VS + 3, 2, 1
const BETWEEN_ROUNDS_MS = 4200;
const ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ";
// emparejamiento: rango de trofeos que se abre con la espera
const MM_BASE = 80; // ±trofeos al entrar en la cola
const MM_GROW = 40; // +trofeos por segundo de espera
const MM_EVERY_MS = 1000;
const BOT_AFTER_MS = 10000;
const GRACE_MS = 15000;
const PICK_MS = 20000; // quien no elige héroe en 20 s juega con uno al azar (nadie puede bloquear la partida) // si se corta la conexión (llamada, app en segundo plano), 15 s para volver a la partida // sin rival humano en este tiempo: rival bot de tu nivel
// límites contra abuso
const MAX_MSG_BYTES = 2048;
const MSG_PER_SEC = 30; // por conexión; muy por encima de lo que manda un jugador
const MAX_CONN_PER_IP = 8;
const MAX_CONN = 3000;
const MAX_ROOMS = 4000;
const MAX_BAD_JOINS = 8; // códigos erróneos por conexión antes de cortarla
const isHero = (id) => typeof id === "string" && Object.prototype.hasOwnProperty.call(E.HEROES, id);

function loadEngine() {
  const html = fs.readFileSync(INDEX, "utf8");
  const m = html.match(/\/\* ENGINE-START \*\/([\s\S]*?)\/\* ENGINE-END \*\//);
  if (!m) throw new Error("No encuentro el bloque ENGINE en index.html");
  return new Function(m[1] + "\nreturn AMAGO;")();
}
const E = loadEngine();

// archivos en memoria (y en gzip si es texto): el juego entero son unos MB
const cache = new Map();
function serve(req, res, file, type, maxAge) {
  let c = cache.get(file);
  if (!c) {
    if (!fs.existsSync(file)) {
      res.writeHead(404, { "content-type": "text/plain" });
      return res.end("No encontrado");
    }
    const body = fs.readFileSync(file);
    c = { body, gz: /text|javascript/.test(type) ? zlib.gzipSync(body) : null };
    if (process.env.NODE_ENV === "production" || process.env.RAILWAY_ENVIRONMENT) cache.set(file, c);
  }
  const gz = c.gz && /\bgzip\b/.test(req.headers["accept-encoding"] || "");
  const h = { "content-type": type, "cache-control": maxAge ? "public, max-age=" + maxAge : "no-cache" };
  if (gz) h["content-encoding"] = "gzip";
  res.writeHead(200, h);
  res.end(gz ? c.gz : c.body);
}

const clientIp = (req) => String(req.headers["x-forwarded-for"] || req.socket.remoteAddress || "").split(",")[0].trim();
const server = http.createServer((req, res) => {
  const url = req.url.split("?")[0];
  if (API && (url.startsWith("/api/") || url === "/stats")) {
    API(req, res, url, clientIp(req));
    return;
  }
  if (url === "/health") {
    res.writeHead(200, { "content-type": "text/plain" });
    res.end("ok " + wss.clients.size + " conectados, " + rooms.size + " salas, " + queue.length + " en cola");
    return;
  }
  const root = path.join(__dirname, "..");
  if (url === "/vendor/three.min.js") return serve(req, res, path.join(root, "vendor", "three.min.js"), "text/javascript; charset=utf-8", 86400);
  const asset = url.match(/^\/(models|portraits|arenas|sprites|props|ui|anim)\/([a-z0-9_-]+)\.(glb|webp)$/);
  if (asset) return serve(req, res, path.join(root, asset[1], asset[2] + "." + asset[3]), asset[3] === "glb" ? "model/gltf-binary" : "image/webp", 86400);
  const font = url.match(/^\/fonts\/([a-z0-9_-]+)\.woff2$/);
  if (font) return serve(req, res, path.join(root, "fonts", font[1] + ".woff2"), "font/woff2", 604800);
  if (url === "/privacidad" || url === "/privacy") return serve(req, res, path.join(root, "privacidad.html"), "text/html; charset=utf-8", 3600);
  if (url === "/" || url === "/index.html") return serve(req, res, INDEX, "text/html; charset=utf-8", 0);
  res.writeHead(404, { "content-type": "text/plain" });
  res.end("No encontrado");
});

const wss = new WebSocketServer({ server, maxPayload: MAX_MSG_BYTES });
const rooms = new Map();

const send = (ws, msg) => {
  if (ws && ws.readyState === 1) ws.send(JSON.stringify(msg));
};
const sideOf = (room, ws) => (room.players.p === ws ? "p" : room.players.b === ws ? "b" : null);
const other = (s) => (s === "p" ? "b" : "p");

function newCode() {
  for (let i = 0; i < 50; i++) {
    const c = Array.from({ length: 4 }, () => ALPHABET[Math.floor(Math.random() * ALPHABET.length)]).join("");
    if (!rooms.has(c)) return c;
  }
  return null;
}

// nombres: filtro de insultos (con acentos y "leet" normalizados); si no pasa, apodo automático
const BAD = ["puta", "puto", "mierda", "polla", "cono", "joder", "cabron", "maricon", "gilipollas", "zorra", "subnormal", "follar", "pene", "verga", "pendejo", "culero", "chinga", "nazi", "hitler", "fuck", "shit", "bitch", "nigg", "cunt", "dick", "pussy", "retard", "porn", "sexo", "sex", "kkk", "faggot", "whore", "slut", "rape", "viola"];
const norm = (t) =>
  t.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "")
    .replace(/0/g, "o").replace(/1/g, "i").replace(/3/g, "e").replace(/4/g, "a").replace(/5/g, "s").replace(/7/g, "t").replace(/@/g, "a").replace(/\$/g, "s")
    .replace(/[^a-z]/g, "");
const isClean = (name) => { const n = norm(name); return !BAD.some((w) => n.includes(w)); };
const ANIMALS = ["Lince", "Zorro", "Búho", "Halcón", "Tejón", "Lobo", "Nutria", "Puma", "Erizo", "Cuervo", "Gecko", "Panda", "Koala", "Tigre", "Delfín", "Cobra"];
const ADJ = ["Veloz", "Astuto", "Sigiloso", "Bravo", "Rojo", "Azul", "Dorado", "Feroz", "Listo", "Loco"];
const alias = () => `${ANIMALS[Math.floor(Math.random() * ANIMALS.length)]} ${ADJ[Math.floor(Math.random() * ADJ.length)]} ${10 + Math.floor(Math.random() * 90)}`;

function cleanPlayer(m) {
  let name = String(m.name || "Jugador").replace(/[<>&"]/g, "").replace(/\s+/g, " ").trim().slice(0, 14) || "Jugador";
  if (!isClean(name)) name = alias();
  const tro = Math.max(0, Math.min(99999, Number(m.tro) || 0));
  let unl = Array.isArray(m.unl) ? m.unl.slice(0, 32).filter(isHero) : [];
  unl = [...new Set(unl)];
  if (unl.length < 3) unl = E.STARTERS.slice();
  return { name, tro, unl };
}

function broadcast(room, fn) {
  for (const s of ["p", "b"]) if (room.players[s]) send(room.players[s], fn(s));
}

function startPick(room) {
  room.state = "pick";
  room.picks = {};
  broadcast(room, (s) => ({
    t: "pickPhase",
    round: room.round,
    score: { you: room.score[s], opp: room.score[other(s)] },
    used: room.used[s],
  }));
  clearTimeout(room.pickTimer);
  room.pickTimer = setTimeout(() => {
    if (rooms.get(room.code) !== room || room.state !== "pick") return;
    for (const s of ["p", "b"])
      if (!room.picks[s] && room.players[s]) {
        const av = available(room, s);
        room.picks[s] = av[Math.floor(Math.random() * av.length)];
      }
    if (room.picks.p && room.picks.b) startRound(room);
  }, PICK_MS);
  const bot = room.players.b;
  if (bot && bot.isBot) {
    const R0 = room.R;
    setTimeout(() => {
      if (rooms.get(room.code) !== room || room.state !== "pick" || room.picks.b) return;
      const av = available(room, "b");
      room.picks.b = av[Math.floor(Math.random() * av.length)];
      send(room.players.p, { t: "oppPicked" });
      if (room.picks.p && room.picks.b) startRound(room);
    }, 1500 + Math.random() * 2500);
  }
}

/* rival bot para el online: nombre, trofeos y héroes como los de un jugador de tu nivel */
function makeBot(forWs) {
  const tro = Math.max(0, (forWs.player.tro || 0) + Math.floor(Math.random() * 41) - 20);
  const maxR = Math.min(3, 1 + Math.floor(tro / 150));
  const pool = E.IDS.filter((id) => E.HEROES[id].rar <= maxR).sort(() => Math.random() - 0.5);
  const k = tro / 400; // 0 = flojo, 1+ = fuerte
  const lerp = (a, b) => a + (b - a) * Math.min(1, k) + (Math.random() - 0.5) * (b - a) * 0.2;
  const name = alias();
  return {
    isBot: true,
    readyState: 0, // send() lo ignora
    alias: name,
    player: { name, tro, unl: pool.slice(0, Math.max(3, pool.length)) },
    params: { think: lerp(0.8, 0.25), react: lerp(0.9, 0.5), dodge: lerp(0.45, 0.85), eps: lerp(0.35, 0.1), passive: lerp(4, 1.5), gap: lerp(3, 0.4), thr: lerp(1.3, 1), moveP: lerp(0.5, 0.95) },
  };
}

function available(room, s) {
  const p = room.players[s].player;
  const left = p.unl.filter((id) => !room.used[s].includes(id));
  return left.length ? left : p.unl;
}

function makeHooks(room) {
  const ev = (s, e) => send(room.players[s], Object.assign({ t: "ev" }, e));
  return {
    fired(p) {
      ev(p.o, { e: "fired", p: E.persp(p, p.o) });
      if (p.warn) ev(p.d, { e: "fired", p: E.persp(p, p.d) });
      else if (p.hx != null) {
        // sin aviso: el defensor solo ve desde dónde se disparó, nunca a qué casillas ni cuándo cae
        const q = E.persp(p, p.d);
        delete q.cells;
        delete q.hitAt;
        ev(p.d, { e: "fired", p: q });
      }
    },
    impact(p) {
      for (const s of ["p", "b"]) ev(s, { e: "impact", p: E.persp(p, s) });
    },
    pickup(s, b) {
      ev(s, { e: "pickup", s: "p", b });
      ev(other(s), { e: "pickup", s: "b", b });
    },
    boost() {
      for (const s of ["p", "b"]) ev(s, { e: "boost" });
    },
    noElx(s) {
      ev(s, { e: "noElx" });
    },
    sudden() {
      for (const s of ["p", "b"]) ev(s, { e: "sudden" });
    },
    ping() {
      for (const s of ["p", "b"]) ev(s, { e: "ping" });
    },
    roundOver(w) {
      endRound(room, w);
    },
  };
}

function startRound(room) {
  clearTimeout(room.pickTimer);
  room.track = { p: [], b: [] };
  const bot = room.players.b && room.players.b.isBot ? room.players.b : null;
  const R = E.newRound(room.picks.p, room.picks.b, bot ? { bot: bot.params } : undefined);
  room.R = R;
  room.state = "count";
  room.hooks = makeHooks(room);
  broadcast(room, (s) => ({
    t: "roundStart",
    round: room.round,
    you: room.picks[s],
    opp: room.picks[other(s)],
    view: E.viewFor(R, s),
  }));
  room.timer = setTimeout(() => {
    if (room.R !== R) return;
    R.paused = !!(room.away && Object.keys(room.away).length); // si alguien se ha desconectado, sigue en pausa
    room.state = "play";
    broadcast(room, () => ({ t: "go" }));
    let last = Date.now();
    let n = 0;
    room.loop = setInterval(() => {
      const now = Date.now();
      E.tick(R, Math.min(0.1, (now - last) / 1000), room.hooks);
      last = now;
      if (!R.paused) {
        const tr = (room.track = room.track || { p: [], b: [] });
        for (const s of ["p", "b"]) {
          const h = R.heroes[s];
          const a = tr[s];
          const lt = a[a.length - 1];
          if (!lt || lt[1] !== h.x || lt[2] !== h.y) a.push([Math.round(R.now * 100) / 100, h.x, h.y]);
          while (a.length > 1 && R.now - a[1][0] > 7) a.shift(); // siempre queda la última casilla conocida
        }
      }
      if (room.R === R && !R.over && ++n % VIEW_EVERY === 0) {
        broadcast(room, (s) => ({ t: "view", v: E.viewFor(R, s) }));
      }
    }, TICK_MS);
  }, COUNTDOWN_MS);
}

function stopRound(room) {
  clearTimeout(room.pickTimer);
  clearInterval(room.loop);
  clearTimeout(room.timer);
  room.loop = null;
  room.timer = null;
}

function endRound(room, w) {
  const R = room.R;
  stopRound(room);
  room.state = "roundEnd";
  if (w) room.score[w]++;
  room.used.p.push(R.heroes.p.type);
  room.used.b.push(R.heroes.b.type);
  broadcast(room, (s) => {
    const o = other(s);
    const h = R.heroes[o];
    return {
      t: "roundEnd",
      w: w === null ? null : w === s ? "you" : "opp",
      score: { you: room.score[s], opp: room.score[o] },
      reveal: { x: h.x, y: h.y, type: h.type },
      track: room.track ? room.track[o] : [], // por dónde se movió el rival en los últimos segundos (para la repetición)
      hp: { you: R.heroes[s].hp, opp: h.hp },
    };
  });
  room.timer = setTimeout(() => {
    if (room.score.p >= 2 || room.score.b >= 2 || room.round >= 5) {
      room.state = "end";
      room.rematch = {};
      broadcast(room, (s) => {
        const a = room.score[s];
        const b = room.score[other(s)];
        const result = a > b ? "win" : a < b ? "lose" : "draw";
        const msg = { t: "matchEnd", result, score: { you: a, opp: b } };
        if (room.ranked && room.players[s]) msg.tro = rankedResult(room.players[s], result);
        return msg;
      });
    } else {
      room.round++;
      startPick(room);
    }
  }, BETWEEN_ROUNDS_MS);
}

/* trofeos de las partidas online: los calcula y guarda el servidor */
const troLoss = (t) => (t < 30 ? 0 : t < 300 ? 2 : t < 600 ? 4 : 6);
function rankedResult(ws, res) {
  const before = ws.player.tro || 0;
  const d = res === "win" ? 8 + Math.floor(Math.random() * 3) : res === "lose" ? -Math.min(before, troLoss(before)) : 0;
  ws.player.tro = Math.max(0, before + d);
  if (STORE && ws.uid)
    STORE.get(ws.uid)
      .then((u) => {
        if (!u) return;
        u.tro = Math.max(0, (u.tro || 0) + d);
        u.ranked = u.ranked || { w: 0, l: 0 };
        if (res === "win") u.ranked.w++;
        if (res === "lose") u.ranked.l++;
        return STORE.put(u);
      })
      .catch(() => {});
  return { d, now: ws.player.tro };
}

function resetMatch(room) {
  room.score = { p: 0, b: 0 };
  room.round = 1;
  room.used = { p: [], b: [] };
  room.R = null;
}

function makeRoom(a, b, ranked) {
  const code = rooms.size < MAX_ROOMS ? newCode() : null;
  if (!code) return null;
  const r = { code, players: { p: a, b }, state: "lobby", rematch: {}, ranked };
  resetMatch(r);
  rooms.set(code, r);
  a.room = code;
  if (b) b.room = code;
  return r;
}

function matchRoom(r) {
  r.tokens = { p: require("crypto").randomBytes(12).toString("base64url"), b: require("crypto").randomBytes(12).toString("base64url") };
  // en el modo Online el rival ve un apodo automático (nada escrito por otros jugadores); con amigos, el nombre filtrado
  broadcast(r, (s) => {
    const o = r.players[other(s)];
    return { t: "matched", code: r.code, token: r.tokens[s], ranked: !!r.ranked, opp: { name: r.ranked ? o.alias : o.player.name, tro: o.player.tro } };
  });
  setTimeout(() => rooms.get(r.code) === r && startPick(r), 1500);
}

/* cola online: empareja por trofeos; el rango crece con la espera de los dos */
const queue = [];
const unqueue = (ws) => {
  const i = queue.indexOf(ws);
  if (i >= 0) queue.splice(i, 1);
};
const range = (ws, now) => MM_BASE + MM_GROW * ((now - ws.qAt) / 1000);
function matchmake() {
  const now = Date.now();
  for (let i = queue.length - 1; i >= 0; i--) if (queue[i].readyState !== 1) queue.splice(i, 1);
  queue.sort((x, y) => x.player.tro - y.player.tro);
  for (let i = 0; i < queue.length - 1; ) {
    const a = queue[i];
    const b = queue[i + 1];
    const gap = Math.abs(a.player.tro - b.player.tro);
    if (gap <= Math.min(range(a, now), range(b, now))) {
      queue.splice(i, 2);
      const r = makeRoom(a, b, true);
      if (r) matchRoom(r);
      else {
        queue.push(a, b); // sin salas libres: siguen en cola
        break;
      }
    } else i++;
  }
}
function botFill() {
  const now = Date.now();
  for (let i = queue.length - 1; i >= 0; i--) {
    const ws = queue[i];
    if (ws.readyState !== 1 || now - ws.qAt < BOT_AFTER_MS) continue;
    queue.splice(i, 1);
    const r = makeRoom(ws, makeBot(ws), true);
    if (r) matchRoom(r);
    else queue.push(ws);
  }
}
setInterval(() => {
  matchmake();
  botFill();
}, MM_EVERY_MS);

/* conexión cortada en mitad de una partida: se pausa y se espera GRACE_MS antes de darla por abandonada */
function onClose(ws) {
  unqueue(ws);
  const room = ws.room && rooms.get(ws.room);
  const s = room && sideOf(room, ws);
  if (room && s && ["pick", "count", "play", "roundEnd"].includes(room.state)) {
    room.away = room.away || {};
    if (room.R && !room.R.over) room.R.paused = true;
    send(room.players[other(s)], { t: "oppAway", sec: GRACE_MS / 1000 });
    room.away[s] = setTimeout(() => {
      if (room.players[s] !== ws) return; // ya volvió con otra conexión
      delete room.away[s];
      leave(ws);
    }, GRACE_MS);
    return;
  }
  leave(ws);
}

function leave(ws, notify = true) {
  unqueue(ws);
  const code = ws.room;
  if (!code) return;
  const room = rooms.get(code);
  ws.room = null;
  if (!room) return;
  stopRound(room);
  const s = sideOf(room, ws);
  let o = s && room.players[other(s)];
  if (o && o.isBot) o = null;
  const midMatch = room.ranked && room.state !== "end" && room.state !== "lobby";
  if (midMatch) rankedResult(ws, "lose");
  if (notify && o) {
    send(o, midMatch ? { t: "oppLeft", tro: rankedResult(o, "win") } : { t: "oppLeft" });
    o.room = null;
  }
  rooms.delete(code);
}

function handle(ws, m) {
  const room = ws.room ? rooms.get(ws.room) : null;
  switch (m.t) {
    case "hello":
      ws.player = cleanPlayer(m);
      if (STORE && m.id && m.secret)
        auth(STORE, m.id, m.secret)
          .then((u) => {
            if (!u) return;
            ws.uid = u.id;
            ws.player.tro = u.tro || 0; // para emparejar cuentan los trofeos guardados en el servidor
          })
          .catch(() => {});
      break;
    case "create": {
      leave(ws);
      const r = makeRoom(ws, null, false);
      if (!r) return send(ws, { t: "error", msg: "El servidor está lleno. Prueba en un rato." });
      send(ws, { t: "room", code: r.code });
      break;
    }
    case "queue": {
      leave(ws);
      ws.qAt = Date.now();
      queue.push(ws);
      send(ws, { t: "queued", n: queue.length });
      matchmake();
      break;
    }
    case "join": {
      const code = String(m.code || "").toUpperCase().trim();
      const r = rooms.get(code);
      if (!r) {
        if (++ws.badJoins > MAX_BAD_JOINS) return ws.terminate();
        return send(ws, { t: "error", msg: "No existe ninguna sala con el código " + code.replace(/[^A-Z]/g, "").slice(0, 4) + "." });
      }
      if (r.players.b || r.players.p === ws) return send(ws, { t: "error", msg: "Esa sala ya está llena." });
      leave(ws);
      r.players.b = ws;
      ws.room = code;
      matchRoom(r);
      break;
    }
    case "pick": {
      if (!room || room.state !== "pick") return;
      const s = sideOf(room, ws);
      if (!isHero(m.hero) || !available(room, s).includes(m.hero) || room.picks[s]) return;
      room.picks[s] = m.hero;
      send(room.players[other(s)], { t: "oppPicked" });
      if (room.picks.p && room.picks.b) startRound(room);
      break;
    }
    case "move":
    case "amago":
    case "fire": {
      if (!room || room.state !== "play" || !room.R) return;
      const s = sideOf(room, ws);
      const x = Number(m.x);
      const y = Number(m.y);
      if (!Number.isInteger(x) || !Number.isInteger(y)) return;
      if (m.t === "move") E.moveTo(room.R, s, x, y);
      else if (m.t === "amago") E.amago(room.R, s, x, y, room.hooks);
      else E.fire(room.R, s, x, y, room.hooks);
      break;
    }
    case "rematch": {
      if (!room || room.state !== "end" || room.ranked) return;
      const s = sideOf(room, ws);
      room.rematch[s] = true;
      if (room.rematch.p && room.rematch.b) {
        resetMatch(room);
        room.rematch = {};
        startPick(room);
      } else send(room.players[other(s)], { t: "rematchAsk" });
      break;
    }
    case "resume": {
      const r = rooms.get(String(m.code || ""));
      const s = r && r.tokens && ["p", "b"].find((k) => r.tokens[k] && r.tokens[k] === m.token);
      if (!r || !s || !r.away || !r.away[s]) return send(ws, { t: "resumeFail" });
      clearTimeout(r.away[s]);
      delete r.away[s];
      const old = r.players[s];
      ws.player = old.player;
      ws.uid = old.uid;
      ws.alias = old.alias;
      old.room = null;
      leave(ws, false); // por si estaba en otra cola o sala
      r.players[s] = ws;
      ws.room = r.code;
      if (r.R && !r.R.over && r.state === "play" && !Object.keys(r.away).length) r.R.paused = false;
      send(r.players[other(s)], { t: "oppBack" });
      send(ws, {
        t: "resumed",
        state: r.state,
        round: r.round,
        score: { you: r.score[s], opp: r.score[other(s)] },
        used: r.used[s],
        picked: !!(r.picks && r.picks[s]),
        you: r.picks && r.picks[s],
        opp: r.picks && r.picks[other(s)],
        view: r.R && !r.R.over ? E.viewFor(r.R, s) : null,
      });
      break;
    }
    case "leave":
      leave(ws);
      break;
  }
}

const perIp = new Map();
wss.on("connection", (ws, req) => {
  // un error en una conexión (mensaje gigante, cierre brusco) no puede tumbar el servidor
  ws.on("error", () => ws.terminate());
  // Railway pone la IP real en x-forwarded-for
  const ip = String(req.headers["x-forwarded-for"] || req.socket.remoteAddress || "").split(",")[0].trim();
  const n = (perIp.get(ip) || 0) + 1;
  if (n > MAX_CONN_PER_IP || wss.clients.size > MAX_CONN) return ws.close(1013, "demasiadas conexiones");
  perIp.set(ip, n);
  ws.on("close", () => {
    const k = (perIp.get(ip) || 1) - 1;
    if (k > 0) perIp.set(ip, k);
    else perIp.delete(ip);
  });
  ws.badJoins = 0;
  ws.rate = { t: Date.now(), n: 0 };
  ws.player = cleanPlayer({});
  ws.alias = alias();
  ws.room = null;
  ws.alive = true;
  ws.on("pong", () => (ws.alive = true));
  ws.on("message", (data) => {
    const now = Date.now();
    if (now - ws.rate.t >= 1000) ws.rate = { t: now, n: 0 };
    if (++ws.rate.n > MSG_PER_SEC) {
      if (ws.rate.n > MSG_PER_SEC * 3) ws.terminate();
      return;
    }
    let m;
    try {
      m = JSON.parse(data);
    } catch (e) {
      return;
    }
    if (!m || typeof m.t !== "string") return;
    try {
      handle(ws, m);
    } catch (e) {
      console.error("Mensaje que rompe el servidor:", m.t, e.message);
    }
  });
  ws.on("close", () => onClose(ws));
});

setInterval(() => {
  for (const ws of wss.clients) {
    if (!ws.alive) {
      ws.terminate();
      continue;
    }
    ws.alive = false;
    ws.ping();
  }
}, 20000);

Store.open()
  .then((st) => {
    STORE = st;
    API = makeApi(st, { statsPage });
    // la política de privacidad promete borrar lo que lleve 24 meses sin uso
    const purge = () => st.purge(Date.now() - 730 * 864e5).catch((e) => console.error("Limpieza:", e.message));
    purge();
    setInterval(purge, 864e5).unref();
  })
  .catch((e) => console.error("Sin almacenamiento:", e.message))
  .finally(() => server.listen(PORT, () => console.log("AMAGO online en http://localhost:" + PORT)));
