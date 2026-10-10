// Almacenamiento de AMAGO: cuentas anónimas, guardado en la nube y eventos de analítica.
// Con DATABASE_URL (Postgres de Railway) usa la base de datos; si no, archivos en DATA_DIR (para probar en local).
"use strict";
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

const hash = (s) => crypto.createHash("sha256").update(String(s)).digest("hex");
const newId = () => crypto.randomBytes(9).toString("base64url"); // 12 caracteres
const newSecret = () => crypto.randomBytes(24).toString("base64url");

function fileStore(dir) {
  fs.mkdirSync(dir, { recursive: true });
  const uf = path.join(dir, "users.json");
  const ef = path.join(dir, "events.ndjson");
  let users = {};
  try {
    users = JSON.parse(fs.readFileSync(uf, "utf8"));
  } catch (e) {}
  let dirty = false;
  setInterval(() => {
    if (!dirty) return;
    dirty = false;
    fs.writeFile(uf + ".tmp", JSON.stringify(users), (err) => !err && fs.rename(uf + ".tmp", uf, () => {}));
  }, 2000).unref();
  return {
    kind: "archivos",
    async get(id) {
      return users[id] || null;
    },
    async put(u) {
      users[u.id] = u;
      dirty = true;
    },
    async del(id) {
      delete users[id];
      dirty = true;
    },
    async purge(cutoff) {
      for (const [id, u] of Object.entries(users)) if ((u.last || 0) < cutoff) delete users[id];
      dirty = true;
      try {
        const keep = fs.readFileSync(ef, "utf8").split("\n").filter((l) => l && JSON.parse(l).t >= cutoff);
        fs.writeFileSync(ef, keep.join("\n") + (keep.length ? "\n" : ""));
      } catch (e) {}
    },
    async addEvents(rows) {
      fs.appendFile(ef, rows.map((r) => JSON.stringify(r)).join("\n") + "\n", () => {});
    },
    async allEvents(since) {
      try {
        return fs.readFileSync(ef, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l)).filter((e) => e.t >= since);
      } catch (e) {
        return [];
      }
    },
    async allUsers() {
      return Object.values(users);
    },
  };
}

async function pgStore(url) {
  const { Pool } = require("pg");
  const pool = new Pool({ connectionString: url, ssl: /localhost|127\.0\.0\.1/.test(url) ? false : { rejectUnauthorized: false }, max: 5 });
  await pool.query(`create table if not exists users (id text primary key, data jsonb not null, updated timestamptz default now());
    create table if not exists events (id bigserial primary key, uid text, k text, t bigint, d jsonb);
    create index if not exists events_t on events (t);`);
  return {
    kind: "postgres",
    async get(id) {
      const r = await pool.query("select data from users where id=$1", [id]);
      return r.rows[0] ? r.rows[0].data : null;
    },
    async put(u) {
      await pool.query("insert into users (id,data,updated) values ($1,$2,now()) on conflict (id) do update set data=$2, updated=now()", [u.id, u]);
    },
    async del(id) {
      await pool.query("delete from users where id=$1", [id]);
      await pool.query("delete from events where uid=$1", [id]);
    },
    async purge(cutoff) {
      await pool.query("delete from users where coalesce((data->>'last')::bigint,0) < $1", [cutoff]);
      await pool.query("delete from events where t < $1", [cutoff]);
    },
    async addEvents(rows) {
      if (!rows.length) return;
      const vals = [];
      const ph = rows.map((r, i) => {
        vals.push(r.uid, r.k, r.t, r.d || null);
        return `($${i * 4 + 1},$${i * 4 + 2},$${i * 4 + 3},$${i * 4 + 4})`;
      });
      await pool.query("insert into events (uid,k,t,d) values " + ph.join(","), vals);
    },
    async allEvents(since) {
      const r = await pool.query("select uid,k,t,d from events where t>=$1", [since]);
      return r.rows.map((x) => ({ uid: x.uid, k: x.k, t: Number(x.t), d: x.d }));
    },
    async allUsers() {
      const r = await pool.query("select data from users");
      return r.rows.map((x) => x.data);
    },
  };
}

async function open() {
  if (process.env.DATABASE_URL) {
    try {
      const s = await pgStore(process.env.DATABASE_URL);
      console.log("Almacenamiento: Postgres");
      return s;
    } catch (e) {
      console.error("No se pudo abrir Postgres, uso archivos:", e.message);
    }
  }
  const dir = process.env.DATA_DIR || path.join(__dirname, "..", ".data");
  console.log("Almacenamiento: archivos en " + dir + (process.env.RAILWAY_ENVIRONMENT ? " (¡se pierden al redesplegar! añade Postgres en Railway)" : ""));
  return fileStore(dir);
}

module.exports = { open, hash, newId, newSecret };
