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
  for (const [e, f] of failed) if (f.until < now - 15 * 60000) failed.delete(e);
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

/* comprueba id + secreto; devuelve el usuario o null.
   Cada móvil tiene su propio secreto: sh (el que creó la cuenta) y shs (sesiones abiertas con correo y contraseña). */
async function auth(store, id, secret) {
  if (typeof id !== "string" || typeof secret !== "string" || id.length > 40 || secret.length > 80) return null;
  const u = await store.get(id);
  if (!u) return null;
  const b = Buffer.from(hash(secret), "hex");
  const same = (h) => {
    const a = Buffer.from(h || "", "hex");
    return a.length === b.length && crypto.timingSafeEqual(a, b);
  };
  return same(u.sh) || (u.shs || []).some(same) ? u : null;
}

/* cuentas con correo y contraseña (scrypt con sal) */
const MAX_SESSIONS = 6;
const normEmail = (e) => String(e || "").trim().toLowerCase();
const okEmail = (e) => e.length <= 120 && /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(e);
const okPass = (p) => typeof p === "string" && p.length >= 6 && p.length <= 128;
const scrypt = (pass, salt) => new Promise((res, rej) => crypto.scrypt(pass, salt, 32, { N: 16384, r: 8, p: 1 }, (e, k) => (e ? rej(e) : res(k))));
async function passHash(pass) {
  const salt = crypto.randomBytes(16);
  return salt.toString("hex") + ":" + (await scrypt(pass, salt)).toString("hex");
}
async function passCheck(pass, stored) {
  const [salt, h] = String(stored || "").split(":");
  if (!salt || !h) return false;
  const a = Buffer.from(h, "hex");
  const b = await scrypt(pass, Buffer.from(salt, "hex"));
  return a.length === b.length && crypto.timingSafeEqual(a, b);
}
const failed = new Map(); // correo → { n, until }: bloqueo tras muchos intentos fallidos

/* ---- Iniciar sesión con Apple ----
   Se comprueba la firma del identityToken con las claves públicas de Apple, el emisor, la audiencia (bundle id),
   la caducidad y el nonce. Con APPLE_TEAM_ID, APPLE_KEY_ID y APPLE_PRIVATE_KEY (clave .p8 de "Sign in with Apple")
   se guarda además el refresh token para revocarlo al borrar la cuenta, como pide Apple. */
const APPLE_AUD = (process.env.APPLE_BUNDLE_ID || "com.enriquemateo.amago").split(",");
const b64u = (s) => Buffer.from(s, "base64url");
let appleKeys = { at: 0, keys: [] };
async function appleJwks(force) {
  if (!force && Date.now() - appleKeys.at < 3600e3 && appleKeys.keys.length) return appleKeys.keys;
  const r = await fetch("https://appleid.apple.com/auth/keys");
  if (!r.ok) throw new Error("jwks");
  appleKeys = { at: Date.now(), keys: (await r.json()).keys || [] };
  return appleKeys.keys;
}
async function appleVerify(token, rawNonce) {
  const [h64, p64, s64] = String(token || "").split(".");
  if (!h64 || !p64 || !s64) return null;
  const head = JSON.parse(b64u(h64).toString("utf8"));
  const pay = JSON.parse(b64u(p64).toString("utf8"));
  if (head.alg !== "RS256") return null;
  let jwk = (await appleJwks()).find((k) => k.kid === head.kid);
  if (!jwk) jwk = (await appleJwks(true)).find((k) => k.kid === head.kid);
  if (!jwk) return null;
  const ok = crypto.verify("RSA-SHA256", Buffer.from(h64 + "." + p64), crypto.createPublicKey({ key: jwk, format: "jwk" }), b64u(s64));
  if (!ok || pay.iss !== "https://appleid.apple.com" || !APPLE_AUD.includes(pay.aud) || !(pay.exp * 1000 > Date.now()) || !pay.sub) return null;
  if (pay.nonce && crypto.createHash("sha256").update(String(rawNonce || "")).digest("hex") !== pay.nonce) return null;
  return pay;
}
const appleCfg = () => process.env.APPLE_TEAM_ID && process.env.APPLE_KEY_ID && process.env.APPLE_PRIVATE_KEY;
function appleClientSecret() {
  const now = Math.floor(Date.now() / 1000);
  const enc = (o) => Buffer.from(JSON.stringify(o)).toString("base64url");
  const data = enc({ alg: "ES256", kid: process.env.APPLE_KEY_ID }) + "." + enc({ iss: process.env.APPLE_TEAM_ID, iat: now, exp: now + 300, aud: "https://appleid.apple.com", sub: APPLE_AUD[0] });
  const key = crypto.createPrivateKey(process.env.APPLE_PRIVATE_KEY.replace(/\\n/g, "\n"));
  return data + "." + crypto.sign("sha256", Buffer.from(data), { key, dsaEncoding: "ieee-p1363" }).toString("base64url");
}
async function appleForm(path, fields) {
  return fetch("https://appleid.apple.com/auth/" + path, { method: "POST", headers: { "content-type": "application/x-www-form-urlencoded" }, body: new URLSearchParams({ client_id: APPLE_AUD[0], client_secret: appleClientSecret(), ...fields }) });
}
async function appleRefreshToken(code) {
  if (!appleCfg() || !code) return null;
  try {
    const r = await appleForm("token", { code, grant_type: "authorization_code" });
    const j = await r.json();
    return j.refresh_token || null;
  } catch (e) {
    return null;
  }
}
async function appleRevoke(rt) {
  if (!appleCfg() || !rt) return;
  try {
    await appleForm("revoke", { token: rt, token_type_hint: "refresh_token" });
  } catch (e) {}
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
          return json(res, 200, { save: u.save, saveAt: u.saveAt, tro: u.tro, email: u.email || null }), true;
        }
        case "/api/register": {
          // el invitado se da de alta: su cuenta (y su progreso) pasa a tener correo y contraseña
          if (limited(ip, "reg", 6)) return json(res, 429, { error: "Demasiados intentos. Espera un minuto." }), true;
          const u = await auth(store, b.id, b.secret);
          if (!u) return json(res, 401, { error: "cuenta" }), true;
          if (u.email) return json(res, 409, { error: "Esta partida ya tiene cuenta." }), true;
          const email = normEmail(b.email);
          if (!okEmail(email)) return json(res, 400, { error: "Ese correo no parece válido." }), true;
          if (!okPass(b.pass)) return json(res, 400, { error: "La contraseña necesita al menos 6 caracteres." }), true;
          if (!(await store.loginAdd(email, u.id))) return json(res, 409, { error: "Ya hay una cuenta con ese correo. Inicia sesión." }), true;
          u.email = email;
          u.ph = await passHash(b.pass);
          u.regAt = Date.now();
          await store.put(u);
          return json(res, 200, { ok: true, email }), true;
        }
        case "/api/login": {
          if (limited(ip, "login", 10)) return json(res, 429, { error: "Demasiados intentos. Espera un minuto." }), true;
          const email = normEmail(b.email);
          const f = failed.get(email);
          if (f && f.until > Date.now()) return json(res, 429, { error: "Demasiados intentos con ese correo. Espera 15 minutos." }), true;
          const uid = okEmail(email) && typeof b.pass === "string" ? await store.loginGet(email) : null;
          const u = uid ? await store.get(uid) : null;
          if (!u || !(await passCheck(b.pass, u.ph))) {
            const n = (f && f.until > Date.now() - 15 * 60000 ? f.n : 0) + 1;
            failed.set(email, { n, until: n >= 8 ? Date.now() + 15 * 60000 : 0 });
            return json(res, 401, { error: "Correo o contraseña incorrectos." }), true;
          }
          failed.delete(email);
          // nueva sesión para este móvil (las más antiguas caducan)
          const secret = newSecret();
          u.shs = [...(u.shs || []), hash(secret)].slice(-MAX_SESSIONS);
          u.last = Date.now();
          await store.put(u);
          return json(res, 200, { id: u.id, secret, email: u.email, save: u.save, saveAt: u.saveAt }), true;
        }
        case "/api/apple": {
          if (limited(ip, "apple", 10)) return json(res, 429, { error: "Demasiados intentos. Espera un minuto." }), true;
          let pay = null;
          try {
            pay = await appleVerify(b.token, b.nonce);
          } catch (e) {
            return json(res, 503, { error: "No se pudo comprobar con Apple. Prueba en un rato." }), true;
          }
          if (!pay) return json(res, 401, { error: "Apple no ha confirmado tu identidad." }), true;
          const key = "apple:" + pay.sub;
          const shown = (pay.email && !pay.is_private_email ? pay.email : "") || "Apple ID";
          const uid = await store.loginGet(key);
          if (uid) {
            // ya tiene cuenta: nueva sesión en este móvil
            const u = await store.get(uid);
            if (!u) return json(res, 404, { error: "Cuenta no encontrada." }), true;
            const secret = newSecret();
            u.shs = [...(u.shs || []), hash(secret)].slice(-MAX_SESSIONS);
            u.last = Date.now();
            if (!u.appleRt) u.appleRt = await appleRefreshToken(b.code);
            await store.put(u);
            return json(res, 200, { id: u.id, secret, email: u.email, save: u.save, saveAt: u.saveAt }), true;
          }
          // primera vez con Apple: la partida de invitado de este móvil pasa a esta cuenta
          let u = await auth(store, b.id, b.secret);
          let secret = b.secret;
          if (!u || u.email) {
            const now = Date.now();
            secret = newSecret();
            u = { id: newId(), sh: hash(secret), created: now, last: now, name: "", tro: 0, save: null, saveAt: 0, ranked: { w: 0, l: 0 } };
          }
          if (!(await store.loginAdd(key, u.id))) return json(res, 409, { error: "Prueba otra vez." }), true;
          u.apple = pay.sub;
          u.email = shown;
          u.regAt = Date.now();
          u.appleRt = await appleRefreshToken(b.code);
          await store.put(u);
          return json(res, 200, { id: u.id, secret, email: u.email, linked: true, save: u.save, saveAt: u.saveAt }), true;
        }
        case "/api/logout": {
          if (limited(ip, "logout", 10)) return json(res, 429, { error: "espera" }), true;
          const u = await auth(store, b.id, b.secret);
          if (!u) return json(res, 200, { ok: true }), true;
          const h = hash(b.secret);
          u.shs = (u.shs || []).filter((x) => x !== h);
          if (u.sh === h && u.email) u.sh = "";
          await store.put(u);
          return json(res, 200, { ok: true }), true;
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
          if (u.appleRt) await appleRevoke(u.appleRt);
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
