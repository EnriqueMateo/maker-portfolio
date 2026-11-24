// Capturas de la App Store v2 (1290×2796): juego real con modelos 3D, título grande y un héroe ilustrado que sale del móvil.
import fs from "fs"; import path from "path"; import os from "os"; import { execFileSync } from "child_process";
import { openGame } from "./rec.mjs";
const OUT = path.join(os.homedir(), "Developer/AMAGO/amago/app/store/capturas");
const SPR = path.join(os.homedir(), "Developer/AMAGO/amago/sprites");
const TMP = "recordings/tmp/store"; fs.mkdirSync(TMP, { recursive: true });
const CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const SAVE = { tutDone: 1, games: 41, wins: 27, name: "Hoshi", tro: 230, troMax: 230, welcome: 1, seen: 99999, coins: 1520, pp: 860, gemsFree: 120,
  unl: ["flecha", "brasa", "sombra", "muro", "ojo", "truco", "rayo", "mira"], isle: { t: "noche", f: "oro" }, camp: { "0.0": 3, "0.1": 3, "0.2": 3, "0.3": 3, "0.4": 3, "1.0": 3, "1.1": 3, "1.2": 2, "1.3": 3, "1.4": 3, "2.0": 2, "2.1": 3, "2.2": 3, "2.3": 2 }, fav: "brasa", lv: { brasa: 4, flecha: 3, muro: 2 }, keys: 2, box: [2],
  gemOnce: { acc: 1, firstwin: 1, name: 1 }, mode: "bot", diff: "normal", hw: { brasa: 12, flecha: 9 } };
const POP = ["brasa", "sombra", "ojo", "mira", "coloso", "flecha"];
const TEXT = {
  es: [["Duelos <em>a ciegas</em>", "1 contra 1 · ¿dónde se esconde tu rival?"], ["¡Pilla y <em>K.O.</em>!", "Partidas de 2 minutos en tiempo real"], ["<em>Héroes</em> únicos", "Cada uno con su vida, velocidad y ataque"],
       ["Tu isla, <em>tu estilo</em>", "Colores y marcos que ganas jugando"], ["Vence a los <em>jefes</em>", "Campaña con 5 mundos y 75 estrellas"], ["Sube de <em>arena</em>", "Trofeos, cofres y retos con amigos"]],
  en: [["<em>Blind</em> duels", "1v1 · where is your rival hiding?"], ["Spot them, <em>K.O.!</em>", "2-minute real-time matches"], ["<em>Unique</em> heroes", "Each with its own health, speed and attack"],
       ["Your island, <em>your style</em>", "Colors and frames you earn by playing"], ["Beat the <em>bosses</em>", "Campaign with 5 worlds and 75 stars"], ["Climb the <em>arenas</em>", "Trophies, chests and friend challenges"]],
};
const BG = [["#3a6cf0", "#1c2a7a"], ["#22a35a", "#0e4a35"], ["#8a3ad8", "#3a1470"], ["#f0782a", "#7a2a10"], ["#2a8cf0", "#122a70"], ["#e04a7a", "#6a1440"]];
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const quiet = (page) => page.evaluate(() => {
  localStorage.setItem("amago-acc", JSON.stringify({ id: "rec", secret: "rec", email: "rec@amago" }));
  ACC = { id: "rec", secret: "rec", email: "rec@amago" }; S.tips = new Proxy({}, { get: () => 1 });
  document.querySelectorAll(".toast,.tcoach,.tuthand").forEach((e) => e.remove());
});
async function shots(lang) {
  const g = await openGame({ lang, save: { ...SAVE, statsOk: 1, notif: 0, news: { mira: 1 }, fw: 99999 }, vw: 393, vh: 852 });
  const { page } = g; await quiet(page);
  const snap = async (i) => { await sleep(900); await page.evaluate(() => document.querySelectorAll(".toast").forEach((e) => e.remove())); await page.screenshot({ path: `${TMP}/${lang}_${i}.png` }); };
  // 2 partida: Brasa en la arena justo tras disparar
  await page.evaluate((opp) => { G = { online: false, score: { p: 0, b: 0 }, round: 1, used: { p: [], b: [] }, tutorial: false, opp: { name: opp, tro: 236 }, oppPool: ["flecha"] }; G.pickSel = "brasa"; startRound(); }, lang === "es" ? "NinjaMiau" : "Rayito_x");
  for (let i = 0; i < 60; i++) { if (await page.evaluate(() => R && !R.paused && UI.screen === "game")) break; await sleep(200); }
  await page.evaluate(() => { const p = R.heroes.p, b = R.heroes.b; p.x = 2; p.y = 3; b.x = 1; b.y = 1; R.bot.passiveUntil = 1e9; R.nextBoost = 1e9; R.now = 8; R.elx.p = 9; });
  await sleep(900);
  // 2b K.O.: el sello encima de la partida
  await page.evaluate(() => { try { koStamp(); } catch (e) {} });
  await sleep(330); await page.evaluate(() => document.querySelectorAll(".toast").forEach((e) => e.remove())); await page.screenshot({ path: `${TMP}/${lang}_2.png` });
  // 1b la primera captura es la partida sin sello (más clara): se rehace tras quitarlo
  await page.evaluate(() => document.querySelectorAll(".kostamp").forEach((e) => e.remove()));
  await page.evaluate(() => { const p = R.heroes.p, b = R.heroes.b; b.x = 3; b.y = 2; R.marks.b.push({ t: "huella", x: 3, y: 2, at: R.now, until: R.now + 3 }); });
  await sleep(400); await page.screenshot({ path: `${TMP}/${lang}_1.png` });
  // 6 victoria 2-0
  await page.evaluate((opp) => { stopLoop(); UI.modal = null; renderModal(); G = { online: false, score: { p: 2, b: 0 }, round: 2, used: { p: ["brasa", "flecha"], b: ["flecha", "muro"] }, opp: { name: opp, tro: 230 }, oppPool: ["flecha", "muro", "ojo"] }; R = null; S.keys = 2; endMatch(); }, lang === "es" ? "NinjaMiau" : "Rayito_x");
  await sleep(4500); await snap(6);
  // 3 héroes
  await page.evaluate(() => { stopLoop(); R = null; G = null; showHeroes(); }); await sleep(1500); await snap(3);
  // 4 Mi isla
  await page.evaluate(() => { showHome(); UI.modal = { k: "isle" }; renderModal(); }); await sleep(1500); await snap(4);
  // 5 campaña
  await page.evaluate(() => { UI.modal = null; renderModal(); showCamp(2); }); await sleep(1800); await snap(5);
  await g.close();
}
function compose(lang) {
  const css = fs.readFileSync("recordings/tmp/store/style.css", "utf8");
  for (let i = 1; i <= 6; i++) {
    const [t, sub] = TEXT[lang][i - 1], [c1, c2] = BG[i - 1];
    const html = `<!doctype html><html><head><meta charset="utf-8"><style>${css}
      body{background:radial-gradient(80% 55% at 50% 30%,${c1},${c2} 75%,#0a0d2a)}</style></head><body>
      <div class="rays"></div><div class="t">${t}</div><div class="s">${sub}</div>
      <div class="phone"><img src="file://${path.resolve(TMP, lang + "_" + i + ".png")}"></div><img class="pop ${i % 2 ? "l" : "r"}" src="file://${SPR}/${POP[i - 1]}.webp"></body></html>`;
    fs.writeFileSync(`${TMP}/c_${lang}_${i}.html`, html);
    const out = path.join(OUT, lang, String(i).padStart(2, "0") + ".png");
    execFileSync(CHROME, ["--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1", "--allow-file-access-from-files", "--window-size=1290,2796", "--screenshot=" + out, "file://" + path.resolve(TMP, `c_${lang}_${i}.html`)], { stdio: "ignore" });
    // sin canal alfa (lo pide Apple)
    execFileSync("python3", ["-c", `from PIL import Image;Image.open(${JSON.stringify(out)}).convert("RGB").save(${JSON.stringify(out)})`]);
  }
}
const fontDir = path.join(os.homedir(), "Developer/AMAGO/amago/fonts");
fs.writeFileSync(`${TMP}/style.css`, `@font-face{font-family:Lilita;src:url(file://${fontDir}/lilitaone.woff2)}@font-face{font-family:Nunito;src:url(file://${fontDir}/nunito.woff2);font-weight:200 1000}
*{margin:0;box-sizing:border-box}body{width:1290px;height:2796px;overflow:hidden;position:relative;text-align:center}
.rays{position:absolute;inset:-40%;background:repeating-conic-gradient(from 0deg at 50% 30%,rgba(255,255,255,.07) 0deg 6deg,transparent 6deg 15deg)}
.t{position:relative;margin-top:120px;font-family:Lilita;font-size:128px;color:#fff;-webkit-text-stroke:10px #13163a;paint-order:stroke fill;text-shadow:0 12px 0 #13163a;line-height:1}
.s{position:relative;margin-top:26px;font-family:Nunito;font-weight:900;font-size:58px;color:#e8eeff}
.phone{position:absolute;left:150px;top:470px;width:990px;height:2180px;border-radius:120px;background:#0d0f26;padding:26px;box-shadow:0 40px 90px rgba(0,0,0,.5),inset 0 0 0 6px #2a2f5a}
.phone img{width:100%;height:100%;object-fit:cover;object-position:top;border-radius:96px}
.t em{font-style:normal;color:#ffd23f}
.pop{position:absolute;bottom:-10px;width:470px;filter:drop-shadow(0 26px 30px rgba(0,0,0,.55))}.pop.l{left:-40px}.pop.r{right:-40px}`);
for (const lang of (process.argv[2] ? [process.argv[2]] : ["es", "en"])) { await shots(lang); compose(lang); console.log("capturas", lang, "listas"); }
