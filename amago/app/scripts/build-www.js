// Copia el juego (index.html y recursos) a www/ para meterlo dentro de la app.
// AMAGO_SERVER: dirección del servidor online (Railway). La app la necesita porque no la sirve el servidor.
"use strict";
const fs = require("fs");
const path = require("path");

const SRC = path.join(__dirname, "..", "..");
const OUT = path.join(__dirname, "..", "www");
const SERVER = (process.env.AMAGO_SERVER || "").replace(/\/+$/, "");
const DIRS = ["vendor", "fonts", "models", "portraits", "arenas", "sprites", "props", "ui", "anim"];

if (!/^https:\/\//.test(SERVER) && !/^http:\/\/localhost(:\d+)?$/.test(SERVER)) {
  console.error("Falta AMAGO_SERVER (https://…), la dirección del servidor en Railway.");
  process.exit(1);
}
fs.rmSync(OUT, { recursive: true, force: true });
fs.mkdirSync(OUT, { recursive: true });
for (const d of DIRS) {
  const from = path.join(SRC, d);
  if (fs.existsSync(from)) fs.cpSync(from, path.join(OUT, d), { recursive: true });
}
const html = fs.readFileSync(path.join(SRC, "index.html"), "utf8");
const boot = `<script>window.AMAGO_SERVER=${JSON.stringify(SERVER)};window.AMAGO_APP=true</script>`;
fs.writeFileSync(path.join(OUT, "index.html"), html.replace(/<head>/i, (m) => m + boot));
console.log("www listo · servidor " + SERVER);
