// API HTTP de AMAGO: cuentas anónimas, guardado en la nube, código de traspaso entre móviles,
// eventos de analítica y panel de métricas (/stats).
"use strict";
const crypto = require("crypto");
const { hash, newId, newSecret } = require("./store");

const MAX_BODY = 64 * 1024;
const MAX_SAVE = 48 * 1024;
const LINK_TTL = 15 * 60 * 1000;
const links = new Map(); // código → { id, until }
const LINK_ABC = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";

/* límite de peticiones por IP y por tipo (ventana de 1 minuto) */
const hits = new Map();
function limited(ip, kind, perMin) {
  const k = ip + "|" + kind;
  const now = Date.now();
  let h = hits.get(k);
  if (!h || now - h.t > 60000) h = { t: now, n: 0 };
  h.n++;
  hits.set(k, h);
  return h.n > perMin;
}
setInterval(() => {
  const now = Date.now();
  for (const [k, h] of hits) if (now - h.t > 60000) hits.delete(k);
  for (const [c, l] of links) if (l.until < now) links.delete(c);
}, 60000).unref();

function readBody(req) {
  return new Promise((res, rej) => {
    let n = 0;
    const parts = [];
    req.on("data", (c) => {
      n += c.length;
      if (n > MAX_BODY) {
        rej(new Error("demasiado grande"));
        req.destroy();
      } else parts.push(c);
    });
    req.on("end", () => {
      try {
        res(JSON.parse(Buffer.concat(parts).toString("utf8") || "{}"));
      } catch (e) {
        rej(e);
      }
    });
    req.on("error", rej);
  });
}
const json = (res, code, obj) => {
  res.writeHead(code, { "content-type": "application/json; charset=utf-8", "cache-control": "no-store", "access-control-allow-origin": "*", "access-control-allow-headers": "content-type" });
  res.end(JSON.stringify(obj));
};

/* comprueba id + secreto; devuelve el usuario o null */
async function auth(store, id, secret) {
  if (typeof id !== "string" || typeof secret !== "string" || id.length > 40 || secret.length > 80) return null;
  const u = await store.get(id);
  if (!u) return null;
  const a = Buffer.from(u.sh, "hex");
  const b = Buffer.from(hash(secret), "hex");
  return a.length === b.length && crypto.timingSafeEqual(a, b) ? u : null;
}

function makeApi(store, opts) {
  const statsKey = process.env.STATS_KEY || (process.env.RAILWAY_ENVIRONMENT ? null : "local");
  return async function api(req, res, url, ip) {
    if (!url.startsWith("/api/") && url !== "/stats") return false;
    if (req.method === "OPTIONS") {
      json(res, 204, {});
      return true;
    }
    try {
      if (url === "/stats") {
        const k = new URL(req.url, "http://x").searchParams.get("k");
        if (!statsKey || k !== statsKey) {
          res.writeHead(404, { "content-type": "text/plain" });
          res.end("No encontrado");
          return true;
        }
        res.writeHead(200, { "content-type": "text/html; charset=utf-8", "cache-control": "no-store" });
        res.end(await opts.statsPage(store));
        return true;
      }
      if (req.method !== "POST") return json(res, 405, { error: "método" }), true;
      const b = await readBody(req);
      switch (url) {
        case "/api/acc": {
          // cuenta nueva y anónima: el móvil guarda id + secreto
          if (limited(ip, "acc", 10)) return json(res, 429, { error: "espera" }), true;
          const id = newId();
          const secret = newSecret();
          const now = Date.now();
          await store.put({ id, sh: hash(secret), created: now, last: now, name: "", tro: 0, save: null, saveAt: 0, ranked: { w: 0, l: 0 } });
          return json(res, 200, { id, secret }), true;
        }
        case "/api/load": {
          if (limited(ip, "load", 30)) return json(res, 429, { error: "espera" }), true;
          const u = await auth(store, b.id, b.secret);
          if (!u) return json(res, 401, { error: "cuenta" }), true;
          u.last = Date.now();
          await store.put(u);
          return json(res, 200, { save: u.save, saveAt: u.saveAt, tro: u.tro }), true;
        }
        case "/api/save": {
          if (limited(ip, "save", 30)) return json(res, 429, { error: "espera" }), true;
          const u = await auth(store, b.id, b.secret);
          if (!u) return json(res, 401, { error: "cuenta" }), true;
          const at = Number(b.at) || 0;
          if (!b.save || typeof b.save !== "object") return json(res, 400, { error: "datos" }), true;
          if (JSON.stringify(b.save).length > MAX_SAVE) return json(res, 413, { error: "grande" }), true;
          if (at <= (u.saveAt || 0)) return json(res, 200, { ok: false, newer: true, saveAt: u.saveAt }), true;
          u.save = b.save;
          u.saveAt = at;
          u.last = Date.now();
          // trofeos: el guardado trae los de las partidas contra el bot; los de las partidas online los suma el servidor
          if (typeof b.save.tro === "number") u.tro = Math.max(0, Math.min(99999, Math.round(b.save.tro)));
          await store.put(u);
          return json(res, 200, { ok: true }), true;
        }
        case "/api/link": {
          // código de 6 letras para pasar la cuenta a otro móvil (15 min)
          if (limited(ip, "link", 5)) return json(res, 429, { error: "espera" }), true;
          const u = await auth(store, b.id, b.secret);
          if (!u) return json(res, 401, { error: "cuenta" }), true;
          let code;
          do code = Array.from({ length: 6 }, () => LINK_ABC[crypto.randomInt(LINK_ABC.length)]).join("");
          while (links.has(code));
          links.set(code, { id: u.id, until: Date.now() + LINK_TTL });
          return json(res, 200, { code, minutes: 15 }), true;
        }
        case "/api/claim": {
          if (limited(ip, "claim", 6)) return json(res, 429, { error: "Demasiados intentos. Espera un minuto." }), true;
          const code = String(b.code || "").toUpperCase().replace(/[^A-Z0-9]/g, "");
          const l = links.get(code);
          if (!l || l.until < Date.now()) return json(res, 404, { error: "Ese código no existe o ha caducado." }), true;
          links.delete(code);
          const u = await store.get(l.id);
          if (!u) return json(res, 404, { error: "Cuenta no encontrada." }), true;
          // nuevo secreto: el móvil antiguo deja de poder guardar en esta cuenta
          const secret = newSecret();
          u.sh = hash(secret);
          await store.put(u);
          return json(res, 200, { id: u.id, secret, save: u.save, saveAt: u.saveAt }), true;
        }
        case "/api/del": {
          // borrar progreso: la cuenta y su guardado desaparecen del servidor
          if (limited(ip, "del", 5)) return json(res, 429, { error: "espera" }), true;
          const u = await auth(store, b.id, b.secret);
          if (!u) return json(res, 401, { error: "cuenta" }), true;
          await store.del(u.id);
          return json(res, 200, { ok: true }), true;
        }
        case "/api/ev": {
          if (limited(ip, "ev", 40)) return json(res, 429, { error: "espera" }), true;
          const uid = typeof b.id === "string" ? b.id.slice(0, 40) : "";
          const list = Array.isArray(b.ev) ? b.ev.slice(0, 60) : [];
          const now = Date.now();
          const rows = [];
          for (const e of list) {
            if (!e || typeof e.k !== "string" || !/^[a-z0-9_]{1,32}$/.test(e.k)) continue;
            const t = Number(e.t);
            const d = e.d && typeof e.d === "object" ? e.d : null;
            if (d && JSON.stringify(d).length > 400) continue;
            rows.push({ uid, k: e.k, t: Number.isFinite(t) && Math.abs(t - now) < 7 * 864e5 ? t : now, d });
          }
          await store.addEvents(rows);
          return json(res, 200, { ok: rows.length }), true;
        }
      }
      return json(res, 404, { error: "ruta" }), true;
    } catch (e) {
      return json(res, 400, { error: "petición" }), true;
    }
  };
}

module.exports = { makeApi, auth };
