// Versión web del juego para portales gratuitos (itch.io, CrazyGames…), lista para subir como .zip.
// Uso: AMAGO_SERVER=https://… node scripts/build-portal.js [itch|crazygames]
// En CrazyGames no se permiten enlaces a otras tiendas: allí el botón «Móvil» va apagado.
"use strict";
const fs = require("fs"), path = require("path"), { execSync } = require("child_process");
const SRC = path.join(__dirname, "..", ".."), P = (process.argv[2] || "itch").toLowerCase();
const OUT = path.join(__dirname, "..", "portal", P), ZIP = path.join(__dirname, "..", "portal", `amago-web-${P}.zip`);
const SERVER = (process.env.AMAGO_SERVER || "").replace(/\/+$/, "");
const DIRS = ["vendor", "fonts", "models", "portraits", "arenas", "sprites", "skins", "props", "ui", "anim", "kk", "h3d"];
if (!/^https:\/\//.test(SERVER)) { console.error("Falta AMAGO_SERVER (https://…)."); process.exit(1); }
fs.rmSync(OUT, { recursive: true, force: true }); fs.mkdirSync(OUT, { recursive: true });
for (const d of DIRS) { const f = path.join(SRC, d); if (fs.existsSync(f)) fs.cpSync(f, path.join(OUT, d), { recursive: true }); }
const links = P !== "crazygames";
const boot = `<script>window.AMAGO_SERVER=${JSON.stringify(SERVER)};window.AMAGO_PORTAL=${JSON.stringify(P)};window.AMAGO_PORTAL_LINKS=${links}</script>`;
fs.writeFileSync(path.join(OUT, "index.html"), fs.readFileSync(path.join(SRC, "index.html"), "utf8").replace(/<head>/i, (m) => m + boot));
fs.rmSync(ZIP, { force: true });
execSync(`cd "${OUT}" && zip -qr -9 "${ZIP}" . -x "*.DS_Store"`);
console.log(`listo: ${ZIP} (${(fs.statSync(ZIP).size / 1e6).toFixed(1)} MB) · portal ${P} · enlaces a la App Store: ${links ? "sí" : "no"}`);
