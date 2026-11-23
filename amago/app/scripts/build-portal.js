// Versión web del juego para portales gratuitos (itch.io, CrazyGames…), lista para subir como .zip.
// Uso: AMAGO_SERVER=https://… node scripts/build-portal.js [itch|crazygames] [--embed]
// --embed: un .zip diminuto que abre el juego del servidor dentro del portal. Se sube UNA vez y se actualiza solo con cada push
//          (inconveniente: en Safari el progreso del invitado puede no guardarse dentro del portal; con cuenta sí).
// En CrazyGames no se permiten enlaces a otras tiendas: allí el botón «Móvil» va apagado.
"use strict";
const fs = require("fs"), path = require("path"), { execSync } = require("child_process");
const SRC = path.join(__dirname, "..", ".."), P = (process.argv[2] || "itch").toLowerCase();
const OUT = path.join(__dirname, "..", "portal", P), ZIP = path.join(__dirname, "..", "portal", `amago-web-${P}.zip`);
const SERVER = (process.env.AMAGO_SERVER || "").replace(/\/+$/, "");
const EMBED = process.argv.includes("--embed");
const DIRS = ["vendor", "fonts", "models", "portraits", "arenas", "sprites", "skins", "props", "ui", "anim", "kk", "h3d"];
if (!/^https:\/\//.test(SERVER)) { console.error("Falta AMAGO_SERVER (https://…)."); process.exit(1); }
fs.rmSync(OUT, { recursive: true, force: true }); fs.mkdirSync(OUT, { recursive: true });
if (EMBED) {
  const links0 = P !== "crazygames";
  fs.rmSync(OUT, { recursive: true, force: true }); fs.mkdirSync(OUT, { recursive: true });
  fs.writeFileSync(path.join(OUT, "index.html"), `<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><title>AMAGO</title>
<style>html,body{margin:0;height:100%;background:#1b2a6b;overflow:hidden}iframe{border:0;width:100%;height:100%;display:block}</style></head>
<body><iframe src="${SERVER}/?portal=${P}" allow="fullscreen; autoplay; clipboard-write; web-share" allowfullscreen></iframe></body></html>`);
  const zip = ZIP.replace(/\.zip$/, "-embed.zip"); fs.rmSync(zip, { force: true });
  execSync(`cd "${OUT}" && zip -qr -9 "${zip}" .`);
  console.log(`listo: ${zip} · abre ${SERVER}/?portal=${P} · se actualiza solo · enlaces a la App Store: ${links0 ? "sí" : "no"}`);
  process.exit(0);
}
for (const d of DIRS) { const f = path.join(SRC, d); if (fs.existsSync(f)) fs.cpSync(f, path.join(OUT, d), { recursive: true }); }
const links = P !== "crazygames";
const boot = `<script>window.AMAGO_SERVER=${JSON.stringify(SERVER)};window.AMAGO_PORTAL=${JSON.stringify(P)};window.AMAGO_PORTAL_LINKS=${links}</script>`;
fs.writeFileSync(path.join(OUT, "index.html"), fs.readFileSync(path.join(SRC, "index.html"), "utf8").replace(/<head>/i, (m) => m + boot));
fs.rmSync(ZIP, { force: true });
execSync(`cd "${OUT}" && zip -qr -9 "${ZIP}" . -x "*.DS_Store"`);
console.log(`listo: ${ZIP} (${(fs.statSync(ZIP).size / 1e6).toFixed(1)} MB) · portal ${P} · enlaces a la App Store: ${links ? "sí" : "no"}`);
