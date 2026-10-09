// Servidor online de AMAGO: sirve el juego y gestiona las salas con WebSocket.
// El motor de reglas se lee del propio index.html (bloque ENGINE), así cliente y servidor juegan con las mismas reglas.
"use strict";
const http = require("http");
const fs = require("fs");
const path = require("path");
const { WebSocketServer } = require("ws");

const INDEX = path.join(__dirname, "..", "index.html");
const PORT = Number(process.env.PORT) || 8080;
const TICK_MS = 50;
const VIEW_EVERY = 2; // envía la vista cada 2 ticks (10 veces por segundo)
const COUNTDOWN_MS = 3300; // VS + 3, 2, 1
const BETWEEN_ROUNDS_MS = 4200;
const ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ";

function loadEngine() {
  const html = fs.readFileSync(INDEX, "utf8");
  const m = html.match(/\/\* ENGINE-START \*\/([\s\S]*?)\/\* ENGINE-END \*\//);
  if (!m) throw new Error("No encuentro el bloque ENGINE en index.html");
  return new Function(m[1] + "\nreturn AMAGO;")();
}
const E = loadEngine();

const server = http.createServer((req, res) => {
  const url = req.url.split("?")[0];
  if (url === "/health") {
    res.writeHead(200, { "content-type": "text/plain" });
    res.end("ok");
    return;
  }
  if (url === "/vendor/three.min.js") {
    res.writeHead(200, { "content-type": "text/javascript; charset=utf-8", "cache-control": "public, max-age=86400" });
    res.end(fs.readFileSync(path.join(__dirname, "..", "vendor", "three.min.js")));
    return;
  }
  const asset = url.match(/^\/(models|portraits)\/([a-z0-9_-]+)\.(glb|webp)$/);
  if (asset) {
    const file = path.join(__dirname, "..", asset[1], asset[2] + "." + asset[3]);
    if (!fs.existsSync(file)) {
      res.writeHead(404, { "content-type": "text/plain" });
      res.end("No encontrado");
      return;
    }
    const type = asset[3] === "glb" ? "model/gltf-binary" : "image/webp";
    res.writeHead(200, { "content-type": type, "cache-control": "public, max-age=86400" });
    res.end(fs.readFileSync(file));
    return;
  }
  if (url === "/" || url === "/index.html") {
    res.writeHead(200, { "content-type": "text/html; charset=utf-8", "cache-control": "no-cache" });
    res.end(fs.readFileSync(INDEX));
    return;
  }
  res.writeHead(404, { "content-type": "text/plain" });
  res.end("No encontrado");
});

const wss = new WebSocketServer({ server });
const rooms = new Map();

const send = (ws, msg) => {
  if (ws && ws.readyState === 1) ws.send(JSON.stringify(msg));
};
const sideOf = (room, ws) => (room.players.p === ws ? "p" : room.players.b === ws ? "b" : null);
const other = (s) => (s === "p" ? "b" : "p");

function newCode() {
  let c;
  do c = Array.from({ length: 4 }, () => ALPHABET[Math.floor(Math.random() * ALPHABET.length)]).join("");
  while (rooms.has(c));
  return c;
}

function cleanPlayer(m) {
  const name = String(m.name || "Jugador").replace(/[<>&"]/g, "").trim().slice(0, 14) || "Jugador";
  const tro = Math.max(0, Math.min(99999, Number(m.tro) || 0));
  let unl = Array.isArray(m.unl) ? m.unl.filter((id) => E.HEROES[id]) : [];
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
      if (p.warn || p.hx != null) ev(p.d, { e: "fired", p: E.persp(p, p.d) });
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
  const R = E.newRound(room.picks.p, room.picks.b);
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
    R.paused = false;
    room.state = "play";
    broadcast(room, () => ({ t: "go" }));
    let last = Date.now();
    let n = 0;
    room.loop = setInterval(() => {
      const now = Date.now();
      E.tick(R, Math.min(0.1, (now - last) / 1000), room.hooks);
      last = now;
      if (room.R === R && !R.over && ++n % VIEW_EVERY === 0) {
        broadcast(room, (s) => ({ t: "view", v: E.viewFor(R, s) }));
      }
    }, TICK_MS);
  }, COUNTDOWN_MS);
}

function stopRound(room) {
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
        return { t: "matchEnd", result: a > b ? "win" : a < b ? "lose" : "draw", score: { you: a, opp: b } };
      });
    } else {
      room.round++;
      startPick(room);
    }
  }, BETWEEN_ROUNDS_MS);
}

function resetMatch(room) {
  room.score = { p: 0, b: 0 };
  room.round = 1;
  room.used = { p: [], b: [] };
  room.R = null;
}

function leave(ws, notify = true) {
  const code = ws.room;
  if (!code) return;
  const room = rooms.get(code);
  ws.room = null;
  if (!room) return;
  stopRound(room);
  const s = sideOf(room, ws);
  const o = s && room.players[other(s)];
  if (notify && o) {
    send(o, { t: "oppLeft" });
    o.room = null;
  }
  rooms.delete(code);
}

function handle(ws, m) {
  const room = ws.room ? rooms.get(ws.room) : null;
  switch (m.t) {
    case "hello":
      ws.player = cleanPlayer(m);
      break;
    case "create": {
      leave(ws);
      const code = newCode();
      const r = { code, players: { p: ws, b: null }, state: "lobby", rematch: {} };
      resetMatch(r);
      rooms.set(code, r);
      ws.room = code;
      send(ws, { t: "room", code });
      break;
    }
    case "join": {
      const code = String(m.code || "").toUpperCase().trim();
      const r = rooms.get(code);
      if (!r) return send(ws, { t: "error", msg: "No existe ninguna sala con el código " + code + "." });
      if (r.players.b || r.players.p === ws) return send(ws, { t: "error", msg: "Esa sala ya está llena." });
      leave(ws);
      r.players.b = ws;
      ws.room = code;
      broadcast(r, (s) => ({ t: "matched", code, opp: { name: r.players[other(s)].player.name, tro: r.players[other(s)].player.tro } }));
      setTimeout(() => rooms.get(code) === r && startPick(r), 1500);
      break;
    }
    case "pick": {
      if (!room || room.state !== "pick") return;
      const s = sideOf(room, ws);
      if (!available(room, s).includes(m.hero) || room.picks[s]) return;
      room.picks[s] = m.hero;
      send(room.players[other(s)], { t: "oppPicked" });
      if (room.picks.p && room.picks.b) startRound(room);
      break;
    }
    case "move":
    case "fire": {
      if (!room || room.state !== "play" || !room.R) return;
      const s = sideOf(room, ws);
      const x = Number(m.x);
      const y = Number(m.y);
      if (!Number.isInteger(x) || !Number.isInteger(y)) return;
      if (m.t === "move") E.moveTo(room.R, s, x, y);
      else E.fire(room.R, s, x, y, room.hooks);
      break;
    }
    case "rematch": {
      if (!room || room.state !== "end") return;
      const s = sideOf(room, ws);
      room.rematch[s] = true;
      if (room.rematch.p && room.rematch.b) {
        resetMatch(room);
        room.rematch = {};
        startPick(room);
      } else send(room.players[other(s)], { t: "rematchAsk" });
      break;
    }
    case "leave":
      leave(ws);
      break;
  }
}

wss.on("connection", (ws) => {
  ws.player = cleanPlayer({});
  ws.room = null;
  ws.alive = true;
  ws.on("pong", () => (ws.alive = true));
  ws.on("message", (data) => {
    let m;
    try {
      m = JSON.parse(data);
    } catch (e) {
      return;
    }
    if (m && typeof m.t === "string") handle(ws, m);
  });
  ws.on("close", () => leave(ws));
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

server.listen(PORT, () => console.log("AMAGO online en http://localhost:" + PORT));
