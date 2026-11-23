// Economía en el servidor: lo que cuesta dinero real lo decide el servidor, no el móvil.
// - Gemas de pago (u.eco.gp): solo suben con una compra verificada; el guardado del móvil solo puede gastarlas.
// - Compras: la transacción firmada de Apple (StoreKit 2, JWS) se comprueba con la cadena de certificados hasta
//   la raíz de Apple (Apple Root CA - G3, guardada en apple-root-g3.pem) y cada transacción se entrega una sola vez.
// - Reembolsos: las notificaciones de App Store Server (V2) quitan lo entregado.
// - Recursos gratis (monedas, gemas gratis, Poder): tope diario generoso, para que editar el guardado no sirva.
"use strict";
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const BUNDLE = (process.env.APPLE_BUNDLE_ID || "com.enriquemateo.amago").split(",")[0];
// en pruebas se puede cambiar la raíz por una propia (APPLE_ROOT_PEM); en producción siempre la de Apple
const ROOT_PEM = process.env.APPLE_ROOT_PEM_TEST && !process.env.RAILWAY_ENVIRONMENT ? process.env.APPLE_ROOT_PEM_TEST : fs.readFileSync(path.join(__dirname, "apple-root-g3.pem"), "utf8");
const ROOT = new crypto.X509Certificate(ROOT_PEM);
const ROOT_FP = "63:34:3A:BF:B8:9A:6A:03:EB:B5:7E:9B:3F:5F:A7:BE:7C:4F:5C:75:6F:30:17:B3:A8:C4:88:C3:65:3E:91:79";
if (!process.env.APPLE_ROOT_PEM_TEST && ROOT.fingerprint256 !== ROOT_FP) throw new Error("apple-root-g3.pem no es la raíz de Apple");

/* qué entrega cada producto (el móvil tiene la misma tabla en SKUS; aquí manda la del servidor) */
const SKUS = {
  "amago.gems_80": { gems: 80 },
  "amago.gems_450": { gems: 450 },
  "amago.gems_1000": { gems: 1000 },
  "amago.gems_2200": { gems: 2200 },
  "amago.gems_6000": { gems: 6000 },
  "amago.pass_premium": { pass: "prem" },
  "amago.pass_plus": { pass: "plus" },
  "amago.pass_plus_upgrade": { pass: "plus", needs: "prem" },
  "amago.starter": { gems: 200, once: "starter" },
  "amago.bundle_power": { gems: 100, weekly: "bundle_power" },
};

/* topes diarios de lo que se gana gratis (muy por encima de lo que da jugar mucho: solo frenan ediciones a mano) */
const FREE_CAP = { coins: 25000, gemsFree: 600, pp: 25000 };

const b64u = (s) => Buffer.from(s, "base64url");
const day = (t) => Math.floor(t / 864e5);
const week = (t) => Math.floor((day(t) + 3) / 7);

function eco(u) {
  if (!u.eco || typeof u.eco !== "object") u.eco = { gp: 0, tx: {}, ent: {}, free: null };
  u.eco.tx = u.eco.tx || {};
  u.eco.ent = u.eco.ent || {};
  return u.eco;
}

/* comprueba un JWS de Apple (x5c: hoja, intermedio, raíz) y devuelve su contenido o null */
function verifyAppleJws(jws) {
  const [h64, p64, s64] = String(jws || "").split(".");
  if (!h64 || !p64 || !s64) return null;
  let head, pay;
  try {
    head = JSON.parse(b64u(h64).toString("utf8"));
    pay = JSON.parse(b64u(p64).toString("utf8"));
  } catch (e) {
    return null;
  }
  if (head.alg !== "ES256" || !Array.isArray(head.x5c) || head.x5c.length < 2) return null;
  try {
    const certs = head.x5c.map((c) => new crypto.X509Certificate(Buffer.from(c, "base64")));
    const now = Date.now();
    for (const c of certs) if (!(Date.parse(c.validFrom) <= now && now <= Date.parse(c.validTo))) return null;
    // cada certificado firmado por el siguiente y el último por la raíz de Apple
    for (let i = 0; i < certs.length - 1; i++) if (!certs[i].checkIssued(certs[i + 1]) || !certs[i].verify(certs[i + 1].publicKey)) return null;
    const top = certs[certs.length - 1];
    const anchored = top.fingerprint256 === ROOT.fingerprint256 || (top.checkIssued(ROOT) && top.verify(ROOT.publicKey));
    if (!anchored) return null;
    const ok = crypto.verify("sha256", Buffer.from(h64 + "." + p64), { key: certs[0].publicKey, dsaEncoding: "ieee-p1363" }, b64u(s64));
    return ok ? pay : null;
  } catch (e) {
    return null;
  }
}

/* entrega una compra verificada; idempotente por transacción (también entre cuentas, con el índice global) */
async function grantPurchase(store, u, jws, season) {
  const t = verifyAppleJws(jws);
  if (!t) return { ok: false, error: "firma" };
  if (t.bundleId !== BUNDLE) return { ok: false, error: "app" };
  if (t.revocationDate) return { ok: false, error: "reembolsada" };
  const sku = String(t.productId || ""), P = SKUS[sku];
  if (!P) return { ok: false, error: "producto" };
  const tid = String(t.transactionId || "");
  if (!tid) return { ok: false, error: "transacción" };
  const e = eco(u);
  if (e.tx[tid]) return { ok: true, dup: true, sku, tx: tid, gp: e.gp, grant: e.tx[tid].grant };
  const owner = await store.loginGet("tx:" + tid);
  if (owner && owner !== u.id) return { ok: false, error: "otra cuenta" };
  const now = Date.now();
  const grant = {};
  if (P.once) { if (e.ent[P.once]) return { ok: false, error: "ya comprado" }; e.ent[P.once] = now; }
  if (P.weekly) { if (e.ent[P.weekly] === week(now)) return { ok: false, error: "esta semana ya" }; e.ent[P.weekly] = week(now); }
  if (P.pass) {
    const s = String(season == null ? "" : season).slice(0, 12);
    e.ent.pass = e.ent.pass || {};
    if (P.needs && e.ent.pass[s] !== P.needs) return { ok: false, error: "requiere premium" };
    e.ent.pass[s] = P.pass;
    grant.pass = P.pass;
    grant.season = s;
  }
  if (P.gems) { e.gp += P.gems; grant.gems = P.gems; }
  e.tx[tid] = { sku, at: now, env: t.environment || "", grant };
  e.paid = (e.paid || 0) + 1; // las cuentas que han pagado nunca se borran por inactividad
  if (!owner) await store.loginAdd("tx:" + tid, u.id);
  return { ok: true, sku, tx: tid, gp: e.gp, grant };
}

/* reembolso (App Store Server Notifications V2): quita las gemas que queden de esa compra */
async function refund(store, signedPayload) {
  const n = verifyAppleJws(signedPayload);
  if (!n || !n.data || n.data.bundleId !== BUNDLE) return { ok: false };
  if (!/^(REFUND|REVOKE)$/.test(n.notificationType || "")) return { ok: true, ignored: n.notificationType };
  const t = verifyAppleJws(n.data.signedTransactionInfo);
  if (!t) return { ok: false };
  const tid = String(t.transactionId || "");
  const uid = await store.loginGet("tx:" + tid);
  const u = uid && (await store.get(uid));
  if (!u) return { ok: true, unknown: tid };
  const e = eco(u), r = e.tx[tid];
  if (!r || r.refunded) return { ok: true };
  r.refunded = Date.now();
  if (r.grant && r.grant.gems) e.gp = Math.max(0, e.gp - r.grant.gems);
  if (r.grant && r.grant.pass && e.ent.pass) delete e.ent.pass[r.grant.season];
  if (u.save && typeof u.save === "object") u.save.gemsPaid = Math.min(Number(u.save.gemsPaid) || 0, e.gp);
  u.rev = (u.rev || 0) + 1;
  await store.put(u);
  return { ok: true, refunded: tid };
}

/* aplica las reglas al guardado que sube el móvil (muta save y u.eco) */
function checkSave(u, save, now, exempt) {
  const e = eco(u);
  const num = (v) => (Number.isFinite(Number(v)) ? Math.max(0, Math.floor(Number(v))) : 0);
  // gemas de pago: el móvil solo puede gastarlas
  const gp = Math.min(num(save.gemsPaid), e.gp);
  save.gemsPaid = gp;
  e.gp = gp;
  // compras: lo que diga el móvil no cuenta; el registro de compras es el del servidor
  if (save.purch && typeof save.purch === "object") {
    const tx = {};
    for (const [k, v] of Object.entries(e.tx)) if (!v.refunded) tx[k] = { sku: v.sku, t: v.at };
    save.purch.tx = tx;
    save.purch.starter = !!e.ent.starter;
  }
  if (exempt) { e.free = null; return; }
  // recursos gratis: tope por día de lo que pueden subir entre guardados
  const d = day(now);
  const prev = u.save && typeof u.save === "object" ? u.save : null;
  if (!e.free || e.free.d !== d) e.free = { d, coins: 0, gemsFree: 0, pp: 0 };
  for (const k of Object.keys(FREE_CAP)) {
    const before = prev ? num(prev[k]) : 0, after = num(save[k]);
    if (!prev) { save[k] = Math.min(after, FREE_CAP[k]); e.free[k] += save[k]; continue; }
    const up = Math.max(0, after - before), room = Math.max(0, FREE_CAP[k] - e.free[k]), ok = Math.min(up, room);
    save[k] = after > before ? before + ok : after;
    e.free[k] += ok;
  }
}

module.exports = { SKUS, FREE_CAP, eco, verifyAppleJws, grantPurchase, refund, checkSave };
