# AMAGO · Momentos de recompensa: diagnóstico y especificación de "juice"

Revisión de `amago/index.html` (sfx/tone/noise ~l.1028–1072, partículas ~l.1075–1100, `giveReward`/`rollChest` ~l.2187, `upgrade` l.2292, tienda/camino/pase/misiones l.2296–2388, cofres `openBox`/`boxTap`/`boxHTML` l.2390–2421, `renderModal` l.2424, `endMatch`/`endScreen` l.2581–2612, CSS de cofre l.671–697 y `.lvup` l.701–707) y de las capturas `i_box*`, `d_lvup`, `end_win` y `a_home`.

## 0. Diagnóstico rápido (qué falla hoy)

| Momento | Hoy | Problema de sensación |
|---|---|---|
| Abrir cofre | Cae (`drop` 550 ms), cada toque hace `shk` y el mismo `sfx("chest")`. Al último toque: flash blanco, 80 partículas, `sfx("open")` | Todos los toques suenan y se ven igual, sin escalada. No hay pausa antes de abrir. `rollChest` se hace **después** del último toque, así que no se puede anunciar nada antes |
| Revelar objeto | `itemin` 500 ms y número final estático (`+56`). Monedas y PP suenan con `sfx("coin")` (dos pitidos de 50 ms) | El número no cuenta, no hay partículas propias y el héroe raro solo cambia el color de los rayos y lanza `confetti()`. Un héroe legendario se siente casi igual que 20 monedas |
| Resumen y continuar | `boxsum` estático y luego se cierra | Los recursos **no viajan** a la barra superior. `.rpill.bump` está en el CSS (l.487) pero no se usa nunca |
| Subir nivel | `sfx("win")` + `confetti()` y la pantalla `.lvup` aparece de golpe | No se ve el coste que se paga ni el número que sube (2→3). Usa el mismo sonido que ganar una partida |
| Trofeos tras partida | Cuenta 20 pasos con `sfx("coin")` en los impares | Mismo tono en cada paso (sin subida de tono). Todo el resultado (fichas, XP, llaves, cofre, avisos) sale a la vez, sin orden |
| Arena nueva / nivel de cuenta | Solo un texto `¡Nivel N!` en la fila de XP. **El cambio de arena no tiene ningún momento** | Es el hito más importante de la progresión y no se celebra |
| Llave | `.keyrow img.new` hace `pop` 500 ms | No suena, no viaja y no se ve que la llave "entra" en el hueco |
| Misión cobrada | `sfx("coin")` + `floatText` en el centro de la pantalla | Las fichas no van a ningún sitio y la fila no cambia |
| Escalón del pase | No hay momento: solo cambia el número al abrir el pase | Se pierde un pico de recompensa gratis |
| Regalo diario / compra | `giveReward` abre el cofre a pantalla completa. Las monedas gastadas desaparecen sin animación | Gastar no se nota y no se ve de dónde sale el cofre |
| Audio | Cada `tone` va directo a `destination` sin bus maestro | Si suenan arpegio + ticks + confeti a la vez, satura y clipea |

Hay tres causas de fondo. **(a)** No hay coreografía: casi todo pasa en el mismo fotograma. **(b)** Faltan tres herramientas: contador animado, recursos que vuelan y destello o anillo de pantalla. **(c)** El sonido no escala: el tono no sube con la intensidad ni con la rareza.

---

## 1. Herramientas base (hay que crearlas antes que los momentos)

Todos los tiempos de abajo se apoyan en estas utilidades. Nombres propuestos:

```js
/* bus de audio: compresor + volumen maestro (evita clipping) */
function actx(){ ... if(!AU.ctx){AU.ctx=new AudioContext();
  const comp=AU.ctx.createDynamicsCompressor();comp.threshold.value=-14;comp.ratio.value=6;comp.attack.value=.003;comp.release.value=.15;
  AU.bus=AU.ctx.createGain();AU.bus.gain.value=.9;AU.bus.connect(comp).connect(AU.ctx.destination);} ... }
// en tone() y noise(): .connect(AU.bus) en vez de c.destination
// noise(): añadir 5º parámetro type="lowpass" para poder hacer "shimmer" con "highpass"
const NOTE=n=>440*Math.pow(2,(n-69)/12);              // midi→Hz
function arp(notes,step,type="triangle",vol=.08,d=.16,delay=0){notes.forEach((f,i)=>tone(f,d,type,vol,null,delay+i*step));}

/* háptica con patrón y presupuesto (máx. 1 cada 60 ms) */
let lastBuzz=0;const hap=p=>{const t=performance.now();if(t-lastBuzz<60||!S.vib)return;lastBuzz=t;try{navigator.vibrate&&navigator.vibrate(p);}catch(e){}};

/* esperas que se pueden "saltar" con un toque (fast-forward) */
const wait=ms=>UI.fast?Promise.resolve():sleep(ms);

/* destello de pantalla y anillo expansivo (DOM, baratos) */
function screenFlash(color="#fff",ms=380,op=.9){if(REDUCED)op*=.35;const e=document.createElement("div");e.className="sflash";e.style.cssText=`background:${color};--op:${op};animation-duration:${ms}ms`;document.body.appendChild(e);setTimeout(()=>e.remove(),ms);}
function ring(x,y,color="#ffe066",size=260,ms=520){if(REDUCED)return;const e=document.createElement("div");e.className="ring";e.style.cssText=`left:${x}px;top:${y}px;--c:${color};--s:${size}px;animation-duration:${ms}ms`;document.body.appendChild(e);setTimeout(()=>e.remove(),ms);}
function shakeScreen(px=6,ms=260){shake(document.body.lastElementChild,px>7);} // o reutilizar shake(el) sobre .boxov/.lvup

/* contador que sube con tic de tono ascendente */
function countUp(el,from,to,ms=600,{tick=true,base=1100,fmtf=fmt}={}){
  if(!el)return Promise.resolve();const steps=Math.min(24,Math.abs(to-from))||1,dt=ms/steps;
  return new Promise(res=>{let i=0;const iv=setInterval(()=>{i++;const v=Math.round(from+(to-from)*easeOut(i/steps));el.textContent=fmtf(v);
    if(tick&&i%2===0)tone(base*Math.pow(2,(i/steps)*.6),.035,"square",.03); // sube ~7 semitonos durante la cuenta
    if(i>=steps){clearInterval(iv);el.classList.remove("cpop");void el.offsetWidth;el.classList.add("cpop");res();}},UI.fast?0:dt);});
}
const easeOut=t=>1-Math.pow(1-t,3);
```

CSS común nuevo:

```css
.sflash{position:fixed;inset:0;z-index:90;pointer-events:none;opacity:0;animation:sflash ease-out both}
@keyframes sflash{0%{opacity:var(--op)}100%{opacity:0}}
.ring{position:fixed;z-index:89;width:var(--s);height:var(--s);margin:calc(var(--s)/-2) 0 0 calc(var(--s)/-2);border-radius:50%;border:6px solid var(--c);box-shadow:0 0 24px var(--c),inset 0 0 24px var(--c);pointer-events:none;animation:ringx ease-out both}
@keyframes ringx{0%{transform:scale(.15);opacity:1}100%{transform:scale(1.6);opacity:0;border-width:1px}}
.cpop{animation:cpop .35s cubic-bezier(.3,1.8,.5,1)}
@keyframes cpop{0%{transform:scale(1.45)}100%{transform:scale(1)}}
@keyframes squash{0%{transform:scale(1)}30%{transform:scale(1.14,.86)}60%{transform:scale(.94,1.08)}100%{transform:scale(1)}}
@keyframes slam{0%{transform:scale(2.4);opacity:0}55%{transform:scale(.92);opacity:1}75%{transform:scale(1.05)}100%{transform:scale(1)}}
@keyframes glowpulse{50%{filter:drop-shadow(0 0 22px var(--g)) brightness(1.25)}}
@keyframes numroll{0%{transform:translateY(0)}100%{transform:translateY(-100%)}}
```

Ampliar el sistema de partículas (`burst` de l.1077):
- `p.shape`: `"rect" | "dot" | "star" | "spark"`. Spark es una línea que se estira con la velocidad, para chispas al abrir.
- `p.glow`: dibujar con `globalCompositeOperation="lighter"` en los destellos.
- `p.drag` (0,94 en chispas y 0,98 en confeti) y `p.grow` para el polvo.
- Límite global: `if(FX.ps.length>450)` no emitir más. Con `REDUCED`, solo un `ring` atenuado y sin partículas, como ahora.
- Emisores nuevos: `sparkle(x,y,color,n=14)` (estrellas pequeñas, poca velocidad, gravedad −0,02, flotan) y `dust(x,y)` (12 puntos marrón y blanco, sp 3, grav 0,04, `grow` 1,02). Además, `fountain(x,y,colors,n,ms)` emite durante `ms` en vez de todo de golpe; sirve para la lluvia de monedas.

**Reglas de sonido.** Volumen máximo de una capa: 0,12 (0,3 solo en golpes graves de menos de 120 Hz, que se oyen menos). Cada momento tiene **una nota raíz** y la recompensa sube por escala mayor: Do5 523, Mi5 659, Sol5 784, Do6 1046, Mi6 1318, Sol6 1568, Do7 2093. Cuanto mejor la recompensa, más arriba termina el arpegio.

**Haptics.** `navigator.vibrate` solo funciona en Android/Chrome; en iOS Safari es un no-op, así que nunca puede ser la única señal. Añadir el ajuste `S.vib` (por defecto `true`) junto a `S.snd`.

---

## 2. Línea de tiempo por momento

Notación: `t=ms` desde el inicio del momento; **[A]** animación DOM/CSS, **[P]** partículas, **[S]** sonido, **[H]** háptica, **[F]** destello o temblor.

### 2.1 Apertura de cofre (`openBox` → `boxTap` → `boxHTML`)

**Cambio estructural clave:** llamar a `rollChest(tier)` dentro de `openBox()`, guardarlo en `M.items` (sin `applyItems` todavía) y calcular `M.best`: 0 = solo recursos; 1–4 = rareza+1 del héroe. Así la anticipación puede reflejar el resultado real (§3). `applyItems` se aplica al abrir, igual que ahora, para no perder nada si se cierra la app.

**Fase A: entrada (0–700 ms)**
- t=0 [A] `.boxov` hace fade-in del fondo (opacity 0→1, 150 ms). `.bt` (nombre del cofre) entra con `slam` 400 ms con 100 ms de retraso.
- t=0 [S] silbido de caída: `noise(.35,.10,2200)` + `tone(900,.4,"sine",.04,300)`.
- t=0–420 [A] el cofre cae (`drop` actual, pero 420 ms y `cubic-bezier(.5,0,.9,.6)` para que acelere al caer). Al tocar suelo, `squash` 260 ms.
- t=420 [S] golpe seco: `tone(95,.28,"sine",.3,45)` + `noise(.18,.32,260)`.
- t=420 [P] `dust(cx, chestBottom)`: 14 partículas a izquierda y derecha (ángulos de 180°±30° y 0°±30°).
- t=420 [F] `shake(.boxov)` suave (5 px, 260 ms). [H] `hap(25)`.
- t=700 [A] `.hint` aparece con fade y luego hace `pulse`. Los toques están bloqueados hasta t=500 (`M.ready`), para que el toque que abrió el cofre no se cuente como golpe.

**Fase B: cada toque k = 1…N−1 (si `CHESTS[tier].taps` > 1)**
- t=0 [A] el cofre hace `shk` con amplitud creciente. Con la variable CSS `--k`: `rotate(calc(-4deg - 3deg*var(--k)))`, escala 1,06+0,04·k, 300 ms.
- t=0 [A] una luz sale por la ranura de la tapa: un `::after` radial detrás del cofre con `opacity:.25*k` y color `--g` (ver §3.1). `filter:brightness(1+.12k)`.
- t=0 [P] `burst` de chispas desde la ranura (y ≈ 42 % de la altura del cofre): `n=8+8k`, `sp=4+k`, color `--g` y blanco, forma `spark`.
- t=0 [S] golpe que sube un tono por toque: `noise(.1,.22+.05k,320+180k)` + `tone([196,247,294][k-1],.14,"square",.07)` + `tone([392,494,587][k-1],.10,"triangle",.05,null,.03)`.
- t=0 [H] `hap(20+15k)`.
- [A] el contador de `.hint` ("Toca para abrir · 2") hace `cpop`.

**Fase C: último toque (pausa + apertura)**
- t=0 [A] el cofre se hincha: escala 1→1,18 y `brightness` 1→1,8, 380 ms ease-in, con micro-temblor de 2 px (keyframe `charge` con translate ±2 px cada 40 ms).
- t=0 [S] carga: `tone(180,.38,"sawtooth",.045,720)` + `tone(360,.38,"triangle",.04,1440)` + `noise(.38,.12,600)`.
- t=0 [H] `hap(15)`; t=200 `hap(15)`.
- t=380 **APERTURA.** [F] `screenFlash("#fff",420,.95)` y `shake(.boxov,true)` (9 px, 380 ms). Con `M.best ≥ 3`, el destello va en el color de rareza (`screenFlash(RAR.c,500,.8)`) seguido del blanco.
- t=380 [A] el cofre cambia a `chest{t}_open.webp` con `pop` 400 ms. Los rayos (`.rays`) pasan a `scale(.6)→scale(1.15)` en 500 ms y giran rápido durante 1 s (`animation-duration` de 26 s a 4 s, luego vuelve).
- t=380 [P] `ring(cx,cy,"#ffe066",320)`. `burst` de 70 chispas doradas y blancas (`spark`, sp 13, drag 0,94) y `fountain` hacia arriba de 30 monedas (`dot` doradas) durante 400 ms.
- t=380 [S] boom + brillo + arpegio: `tone(110,.45,"sine",.3,50)` + `noise(.5,.28,1400)` + `noise(.6,.06,6000,.05,"highpass")` (shimmer) + `arp([1046,1318,1568,2093],.06,"sine",.07,.2,.12)`.
- t=380 [H] `hap([40,30,60])`.
- t=900 empieza el primer objeto (2.2).

### 2.2 Revelado de cada objeto (`M.step`)

**Monedas / PP (normal)**
- t=0 [A] el icono sale **desde la boca del cofre abierto** (coordenadas de `.chopen`) en arco hacia el centro: WAAPI de 450 ms con keyframes `translate(0,180px) scale(.2)` → `translate(0,-30px) scale(1.15)` (60 %) → `translate(0,0) scale(1)`, `easing:cubic-bezier(.2,.9,.3,1.2)`. Rotación ligera de −15° a 0°.
- t=0 [S] fuera del cofre: `tone(520,.12,"triangle",.06,1040)`.
- t=250 [A] `.amt` cuenta de 0 a n con `countUp(el,0,n,650)`. Ticks cuadrados de 1100 Hz que suben unos 7 semitonos. [P] `sparkle` en el icono cada 160 ms durante la cuenta (6 por tanda).
- t=900 [A] `.amt` hace `cpop`. Debajo, la etiqueta `.lab` (fade-in, 200 ms).
- t=900 [S] ding final: monedas `tone(1568,.14,"triangle",.09)` + `tone(2093,.22,"sine",.07,null,.05)`. PP con timbre más "mágico": `tone(1318,.2,"sine",.08)` + `tone(1976,.3,"sine",.06,null,.06)` + `noise(.3,.04,7000,.05,"highpass")`.
- t=900 [H] `hap(12)`.
- **Gran botín:** si la tirada cae en el 20 % superior del rango (`n ≥ a+.8(b−a)` en `CHESTS[t].coins/pp`), aparece la etiqueta "¡GRAN BOTÍN!" con `slam`, 12 estrellas `sparkle` y un `arp([1568,2093],.05)` extra. Es azar real que se muestra, no un truco (ver §3).
- Icono en reposo después: `glowpulse` 1,6 s infinito con `--g` dorado o morado.
- Para saltarse la animación: un toque antes de t=900 activa `UI.fast` y termina la cuenta al instante; el siguiente toque pasa de objeto. Así nadie pierde la recompensa y quien tiene prisa tampoco se aburre.

**Héroe (raro): el momento estrella. Duración según rareza: Común 1,4 s, Raro 1,8 s, Épico 2,3 s, Legendario 2,8 s**
- t=0 [A] fondo: los rayos se tiñen del color de rareza (ya se hace) y se atenúan a 0,4. Sube un haz vertical desde el cofre: `div.beam`, `linear-gradient(transparent, var(--g))`, `scaleY` de 0 a 1 en 400 ms.
- t=0 [S] latido grave: `tone(70,.16,"sine",.32)` en t=0 y `tone(70,.16,"sine",.26,null,.22)`. Para Épico o Legendario, repetir en t=600 y t=820.
- t=150 [A] la **silueta** del héroe (`heroSVG` con `filter:brightness(0) drop-shadow(0 0 18px var(--g))`) sube desde el cofre (`itemin`), flotando con `bob`.
- t=150–(T−500) [P] `fountain` de chispas del color de rareza desde el cofre, 6 por cada 100 ms.
- t=150 [S] subida: `tone(220,T/1000-.5,"sawtooth",.035,880)` + `noise(T/1000-.5,.08,900)`. [H] `hap(10)` cada 300 ms (máx. 4).
- **t=T−500: revelado.** [F] `screenFlash(RAR.c,450,.85)` y temblor fuerte. [A] la silueta pasa a color (`filter` hasta `none` en 250 ms) con `squash`. `ring` del color de rareza (tamaño 380). El rótulo `.rar` ("ÉPICO · ¡NUEVO HÉROE!") entra con `slam`, y el nombre `.amt` 120 ms después.
- t=T−500 [P] `confetti()` con la paleta de la rareza: común azul y blanco; raro verde, blanco y amarillo; épico morado, rosa y blanco; legendario dorado, blanco y naranja + `sparkle` lenta durante 2 s.
- t=T−500 [S] fanfarria por rareza:
  - Común: `arp([523,659,784,1046],.07,"triangle",.09,.2)`
  - Raro: lo anterior + `tone(1318,.35,"sine",.07,null,.3)`
  - Épico: `arp([392,523,659,784,1046,1318],.065,"square",.05,.18)` + acorde final `[1046,1318,1568].forEach(f=>tone(f,.6,"triangle",.06,null,.42))`
  - Legendario: el épico + `noise(.9,.05,8000,.4,"highpass")` (brillo) + `tone(2093,.8,"sine",.06,null,.5)` + golpe `tone(80,.5,"sine",.3,40)` en el revelado
- t=T−500 [H] `hap([60,40,120])`; en Legendario, `hap([80,50,80,50,200])`.
- t=T [A] el héroe hace una animación de victoria si el canvas `SHOW` está disponible; si no, `bob`. Botón o pista "Toca para seguir" con 500 ms de retraso. Los toques se bloquean 700 ms tras el revelado.

### 2.3 Resumen del cofre y salida
- t=0 [A] las tarjetas de `.boxsum` entran en cascada (`itemin`, 90 ms entre cada una). [S] por tarjeta, `tone(784+i*131,.06,"triangle",.05)`.
- t=0+90i: la tarjeta del héroe lleva un brillo `shine` y un borde del color de rareza.
- Al pulsar **CONTINUAR**: guardar el `getBoundingClientRect()` de cada tarjeta, cerrar la capa y llamar a `flyRes("coins",n,rect)` y `flyRes("pp",n,rect)` (§4). La pantalla de debajo ya se ha redibujado con los contadores **en el valor anterior** gracias a `PEND`.

### 2.4 Subida de nivel (`upgrade` + modal `lvup`)
- t=0 [A] el botón MEJORAR hace `squash`. [S] `tone(660,.06,"square",.05)`.
- t=0 [A] **gasto visible**: `flyRes("pp",-c.pp,…)` y `flyRes("coins",-c.c,…)` en sentido inverso, de los pills al retrato del héroe de la ficha. 6 iconos cada uno, 380 ms, y los pills bajan con `countUp` (sin tic, con un `tone(400,.04,"triangle",.03)` sordo).
- t=420 [A] el retrato de la ficha se ilumina (`brightness` 1→2, 200 ms). [S] carga `tone(300,.3,"sawtooth",.04,1200)`.
- t=600 [A] se monta `.lvup`. El héroe entra como silueta blanca (`brightness(3)`) y pasa a color en 300 ms. Los rayos aceleran como en el cofre.
- t=600 [F] `screenFlash("#c07bff",400,.7)`. [P] `ring(cx,heroY,"#c58bff",340)` y `burst` de 50 `spark` morados y blancos.
- t=600 [S] golpe `tone(110,.35,"sine",.25,55)` + `noise(.3,.2,1000)`.
- t=900 [A] **hexágono de nivel con rodillo**: `.pwr` muestra el nivel viejo; el número sale hacia arriba y entra el nuevo desde abajo (`numroll` 280 ms, `overflow:hidden` en un `span` de dos líneas). Después `cpop` + `glowpulse` morado. [S] `tone(784,.1,"square",.06)` → `tone(1046,.25,"triangle",.08,null,.1)`. [H] `hap(30)`.
- t=1150 [A] el título `h2` entra con `slam`. [S] `arp([523,659,784,1046,1318],.06,"triangle",.07,.18)`.
- t=1450 y siguientes [A] **cada mejora en su línea** (hoy van todas juntas en un `<p>`): "Recarga de elixir +9 % → +12 %". El número cuenta con `countUp` 400 ms y la línea entra deslizando desde la izquierda, con 250 ms entre líneas. La línea "+1 vida" lleva un corazón con `slam` y `sparkle` roja. [S] por línea, `tone(1046+i*262,.12,"triangle",.06)`.
- t=1450 [P] `confetti()` (hoy se lanza en t=0 sobre la ficha y queda tapado).
- Si llega a `LV_MAX`: hexágono dorado (`.pwr.max`) con ráfaga dorada, fanfarria de legendario y `hap([60,40,120])`.
- Toques bloqueados hasta t=1200; después, "Toca para seguir".

### 2.5 Trofeos tras la partida (`endMatch`): **mostrarlo como secuencia, no todo junto**

La pantalla de fin debe montarse con las filas `.endrow` ocultas (`opacity:0`) y una función `async revealEnd()` que las enseñe una a una. Un toque en cualquier parte activa `UI.fast`.

- t=0 [A] "¡VICTORIA!" entra con `slam` y los héroes con `itemin` en cascada (120 ms). [S] `sfx("win")` actual. [P] `confetti()`.
- t=700 [A] fila de trofeos (`itemin`). En t=850, la etiqueta "+9" entra con `slam` junto al número.
- t=1000 [A] **la etiqueta "+9" se parte en 9 trofeos** (1 icono por trofeo, máx. 12) que vuelan al número `#tro` (120 ms entre cada uno, 420 ms de vuelo en arco). Cada llegada suma 1, `cpop` del número y tic con tono ascendente: `tone(NOTE(72+i),.06,"square",.045)` + `tone(NOTE(84+i),.05,"sine",.03)`. Escala cromática de Do5 hacia arriba, así que 9 trofeos acaban en La5. [H] `hap(8)` cada llegada.
- Al acabar: `sparkle` dorada en el número y la barra de `roadBar` (si se muestra) se llena con transición de 500 ms.
- **Derrota:** el "−3" se cuenta despacio hacia abajo (60 ms por paso) con `tone(330-i*15,.07,"sine",.04)`, sin temblor, sin rojo intenso y sin vibración. No se castiga dos veces. Con el escudo de novato, el número no se mueve y un 🛡️ hace `slam` con `tone(880,.2,"triangle",.06)`.
- t≈2100 fichas del pase (+25): `countUp` de 400 ms y 5 estrellitas vuelan hacia… nada. Esta pantalla no tiene barra superior, así que basta con `cpop` + `sparkle` azul. [S] `tone(1318,.1,"sine",.06)`.
- t≈2500 XP (+40): igual. Si sube el **nivel de cuenta**, la fila se agranda (`squash`), aparece una insignia "¡NIVEL 4!" con `slam` y suena `arp([784,1046,1318],.07)`. Ver 2.6 para la versión completa.
- t≈2900 llaves (2.7).
- t≈3400 cofre ganado, misión lista y premios del camino: cada aviso entra con `itemin` y 200 ms de separación. El botón "JUGAR OTRA" aparece el último con `slam` y su `shine`.

Duración total con victoria y llave: unos 3,5 s; con toque, menos de 0,5 s. Hoy dura 0,9 s, pero todo llega a la vez y no hay momento que recordar.

### 2.6 Nueva arena / nivel de cuenta (rango): momento nuevo
Se detecta en `endMatch`: `arenaOf(before).a.k !== arenaOf(S.tro).a.k` (subida, no bajada). Si ocurre, al terminar 2.5 sale una capa a pantalla completa `.arenaup` (z-index 62, mismo patrón que `.lvup`).

- t=0 [A] el fondo se funde del `bg` de la arena vieja al de la nueva (dos capas con crossfade de 600 ms). [S] ráfaga `noise(.6,.12,2500)`.
- t=200 [A] tarjeta de la arena vieja en el centro; se agrieta (clip-path en dos mitades) y sale despedida a los lados (400 ms). [S] `noise(.25,.3,1800)` + `tone(140,.3,"sine",.2,60)`. [H] `hap(40)`.
- t=600 [A] la tarjeta de la arena nueva baja desde arriba como el cofre (`drop` + `squash`). [F] temblor fuerte y `screenFlash(arena.bg,400,.6)`. [P] `ring` + `confetti()` en los colores de la arena.
- t=600 [S] fanfarria larga de dos compases: `arp([392,523,659,784],.09,"square",.05,.2)` + en t+0,45 `arp([659,784,1046,1318],.09,"square",.05,.2)` + acorde `[523,659,784,1046].forEach(f=>tone(f,.9,"triangle",.05,null,.9))`.
- t=1000 [A] el nombre "BOSQUE CAZADOR" entra con `slam`. Debajo, "Nuevos premios en el camino" y los iconos de los 2 premios siguientes en cascada.
- t=1600 "Toca para seguir". El primer `setBg()` del inicio ya usa la arena nueva.
- **Nivel de cuenta** (`level()` sube): versión corta dentro de la fila de XP del 2.5. Si se quiere, una capa como `lvup` pero azul con "¡NIVEL 5!" y sin recompensa: 1,2 s.

### 2.7 Llave ganada
- t=0 [A] una llave grande (56 px) aparece sobre "¡VICTORIA!" con `slam`, gira 360° y vuela en arco (500 ms) hasta su hueco `img.new` de `.keyrow`.
- t=500 [A] el hueco pasa de gris a color con `cpop` y `glowpulse` dorado ×2. [P] `sparkle` dorada (10).
- t=500 [S] tintineo metálico: `tone(2637,.07,"triangle",.07)` + `tone(3520,.12,"sine",.05,null,.04)` + `noise(.05,.08,9000,0,"highpass")`. [H] `hap(15)`.
- **Tercera llave:** tras su llegada (t=700), las 3 llaves se juntan en el centro de la fila (300 ms) y se funden en un destello (`ring` dorado). Del destello sale el botón `.endchest` con `drop` + `squash`, y se oye `sfx("chest")` + `arp([784,1046,1318,1568],.05)`. [H] `hap([30,30,60])`. El cofre de `.endchest` hace luego el `hop` del inicio.
- Si los cofres están al máximo (`BOX_MAX`), la llave sale gris y "rebota" contra el hueco con `shk` y un `tone(300,.1,"triangle",.04)` suave. Se ve claro por qué no cuenta, sin sonido de error.

### 2.8 Misión completada (`misClaim`)
- **Al completarla** (en `misTrack`, cuando `m.v` llega a `m.n` durante la partida): no interrumpir. En el fin de partida, aviso con `itemin` y ✅ que hace `slam` + `tone(1046,.08,"triangle",.06)` + `tone(1568,.14,"triangle",.06,null,.07)`.
- **Al cobrar:** t=0 el botón COBRAR hace `squash`. [S] `tone(660,.05,"square",.05)`.
- t=80 [A] la barra `.ppbar` destella en blanco (100 ms). Un sello "✓" grande hace `slam` con rotación de −12°, de 2,4× a 1×, 350 ms. [S] sello: `noise(.08,.3,500)` + `tone(180,.1,"square",.08)`. [H] `hap(25)`.
- t=300 [A] `flyRes("tk",m.tk,btnRect)`: 6–8 estrellas vuelan al botón "Pase" del inicio si se ve; si no, a la cabecera del modal. Cuando no hay destino, se acumulan en el título del modal ("Misiones diarias") con `cpop`.
- t=300–800 [S] tics de llegada de estrellas: `tone(1318*2**(i/12),.04,"sine",.05)`.
- t=800 [A] la fila pasa a `.done` con transición de opacidad (300 ms) y se desliza 4 px. Si se completa un escalón del pase con esas fichas, encadena 2.9.
- Se elimina el `floatText` del centro (queda redundante con el vuelo).

### 2.9 Escalón del pase alcanzado
Pasa al sumar fichas (fin de partida o misión) cuando `floor(tk/100)` sube.
- t=0 [A] en la cabecera del pase (o en una minibarra temporal tipo toast arriba, si no se está en el pase), la barra se llena hasta 100 % (400 ms, `ease-out`).
- t=400 [F] la barra destella en blanco. [P] `sparkle` azul y blanca en la barra (16). [S] `arp([784,1046,1318],.06,"triangle",.07)` + `noise(.2,.05,8000,0,"highpass")`.
- t=500 [A] el número del escalón "4/30" pasa a "5/30" con rodillo (`numroll`) y `cpop`. [H] `hap(30)`.
- t=650 [A] la barra vuelve a 0 y se rellena con lo que sobra (300 ms).
- t=700 [A] el nodo nuevo del pase (`.pnode`) pasa a `.reach`, su botón RECLAMAR entra con `slam` y su `shine`, y el badge del botón "Pase" del inicio hace `badge` ×3.
- **Al reclamar** (`passClaim`): el nodo hace `squash` y su icono vuela al centro (FLIP: posición de `.ri` → centro, 400 ms) antes de abrir `openItems` / `openBox`. Así el premio *sale del camino* y no aparece de la nada. Mismo patrón para `claim(t)` en el camino de trofeos.

### 2.10 Regalo diario (`claimGift`)
- En el inicio y la tienda, el cofre del regalo hace el `hop` del inicio con un brillo `shine` (ya existe en el botón).
- Al tocar GRATIS: t=0 el botón hace `squash` y `tone(660,.05,"square",.05)`.
- t=0 [A] FLIP: la imagen `chest1.webp` de `.gift` crece y viaja al centro (450 ms, `cubic-bezier(.3,1.4,.5,1)`) mientras el fondo `.boxov` hace fade-in. [S] `tone(400,.4,"triangle",.06,1200)`.
- t=450 sigue la fase A de 2.1 **sin la caída** (ya llegó volando): solo `squash`, golpe, polvo y `hap(25)`.
- Al terminar, el botón muestra "✓" con `slam` y el texto "Nuevo regalo en 7 h 12 min".

### 2.11 Compra (`buy` / `buyOffer` / `buyBox`)
- t=0 [A] el botón de precio hace `squash`. [S] "caja registradora": `tone(1568,.05,"square",.05)` + `tone(1046,.08,"square",.05,null,.05)` + `noise(.06,.1,4000,.03)`.
- t=0 [A] `flyRes("coins",-price,…)`: 6 monedas salen del pill `#coinsn` hacia la tarjeta comprada (350 ms). El pill baja con `countUp` 350 ms y tic sordo.
- t=380 [A] la tarjeta hace `squash` y luego una etiqueta "COMPRADO" con `slam`. [H] `hap(20)`.
- t=450 empieza la recompensa: FLIP desde la tarjeta al centro, como en 2.10, y luego 2.1 o 2.2.
- **Sin monedas suficientes** (hoy solo hay un `toast`): el pill `#coinsn` hace un `shake` horizontal de 5 px en 260 ms y se pone rojo 400 ms. [S] `tone(220,.12,"square",.05,165)`. [H] `hap(40)`. El mensaje solo sale la primera vez (el `toast` ya funciona así con `S.tips`).

---

## 3. Recompensa variable y anticipación (ética)

**Principio:** la anticipación **dramatiza un resultado ya decidido y verdadero**. Nunca enseña algo mejor de lo que sale (sin "casi"), nunca castiga y nunca presiona con tiempo o dinero.

### 3.1 Color de rareza antes del objeto ("tell" de luz)
- Al llamar a `openBox`, tirar `rollChest` y calcular `M.best`: 0 solo recursos, 1 común, 2 raro, 3 épico, 4 legendario.
- Color de la luz que sale por la ranura (`--g`): sin héroe, dorado `#ffcc1f` atenuado al 60 %; común `#8fb4e0`, raro `#41e08a`, épico `#c07bff`, legendario `#ffcc1f` brillante + `#fff`. Es decir, `RAR[...].c`, con una diferencia de **intensidad** entre "dorado de monedas" y "dorado legendario": el legendario añade `sparkle` blanca y halo de 40 px.
- **Escalada por toques sin near-miss:** con N toques, la luz del toque k es `min(best, k)` en orden de rareza (azul → verde → morado → dorado) y **nunca supera `best`**. Si `best` es 0, la luz es dorada y estable en todos los toques, con brillo creciente (`opacity .25k`) pero sin cambiar de color. Así el jugador aprende que "verde = al menos raro", lo que es una promesa honesta.
- Cofre de 1 toque: el color de `best` aparece solo durante la pausa de 380 ms (fase C).
- En el revelado de cada objeto, la tarjeta "Quedan 3" (`.left`) puede llevar un punto de color si queda un héroe: "aún queda algo especial". Es verdad y crea anticipación sin mentir.

### 3.2 Cofre que "sube de categoría" mientras se toca
Solo si **la mejora viene decidida desde la tirada** y la probabilidad se publica:
- `CHESTS[t].upChance`: Cofre→Cofre grande 10 %, Cofre grande→Megacofre 5 %, tirado en `openBox` y guardado como `M.upTo`.
- En el toque k = 1 (antes de las chispas normales): el cofre tiembla más (`shk` ×1,5), destello blanco de 200 ms, el sprite cambia a `chest{t+1}.webp` con `squash` y el título `.bt` pasa a "¡COFRE GRANDE!" con `slam`. [S] `arp([523,784,1046,1568],.05,"square",.06)` + golpe `tone(120,.3,"sine",.25,60)`. [H] `hap([30,30,60])`.
- Como mucho **una** mejora por cofre. **Nunca** se enseña una mejora que luego "falla". En la ficha del cofre (tienda, `keysInfo`) se muestra: "10 % de que mejore al abrirlo".

### 3.3 Evitar near-miss y transparencia
- **Prohibido:** girar una ruleta que pasa por el legendario y se para en común, mostrar el legendario "casi" o escribir "¡Por poco!".
- **Probabilidades visibles:** en la tienda, con el icono ⓘ de cada cofre: "Héroe: 8 % / 20 % / 50 %" (`CHESTS[t].hero`) y los rangos de monedas y PP (ya se muestran PP).
- **Contador de garantía (pity)** visible y real: `S.pity` +1 por cofre sin héroe. Con `pity ≥ 8` (Cofre=1, Grande=2, Mega=4 puntos), el siguiente cofre con héroes bloqueados da un héroe seguro. En el inicio, debajo de las llaves: "Héroe garantizado en ≤ 3 cofres" (barra pequeña). Cuando salta la garantía, la luz del 3.1 es la normal de la rareza; no se presenta como un milagro.
- No hay duplicados de héroe (ya solo salen bloqueados) y los rangos de monedas son estrechos (15–30), así que no hay "premios de humo".

### 3.4 Rachas
- `S.streak` (victorias seguidas) y `S.dayStreak` (días seguidos jugando o cobrando el regalo).
- **Racha de victorias:** en el fin de partida, si `streak ≥ 2`, una insignia 🔥×N junto a "¡VICTORIA!" con `slam` y tono `NOTE(72+min(streak,12))`. Con 3, 5 y 10, una llamita extra de `sparkle` naranja. **No da premios extra** (evita jugar compulsivamente) y al romperse no hay mensaje ni animación negativa: simplemente no aparece.
- **Racha de días:** en el regalo diario, una fila de 7 puntos (los días hechos, llenos) con `cpop` en el de hoy. El día 7 cambia el regalo a `chest2` (anunciado de antemano en la fila). Si se pierde un día, la racha **no vuelve a 0**: baja un punto, lo que evita la ansiedad de "perderlo todo".
- **Racha de trofeos en el camino:** al ganar, la barra de `roadBar` del inicio hace un `shine` una sola vez.

### 3.5 Parámetros de ritmo (resumen)
| Parámetro | Valor |
|---|---|
| Bloqueo anti-toque tras cada revelado | 500 ms (objetos), 700 ms (héroe), 1200 ms (subida de nivel) |
| Pausa antes de abrir el cofre | 380 ms |
| Duración del revelado de héroe | 1400 / 1800 / 2300 / 2800 ms por rareza |
| Separación entre recursos que vuelan | 35–45 ms; vuelo de 550–750 ms |
| Máximo de partículas | 450 |
| Volumen máximo por capa | 0,12 (graves de menos de 120 Hz: 0,3) |
| Vibración máxima por momento | 250 ms en total |

---

## 4. Recursos que vuelan a la barra superior

### 4.1 Comportamiento
1. **Origen:** el rect del icono de la recompensa (tarjeta del resumen, botón COBRAR, nodo del camino). **Destino:** el icono `.ico` dentro del `.rpill` correspondiente (`#coinsn` monedas, `#ppn` PP). Fichas ⭐: el botón `[data-t=pass]` de la barra de pestañas o el de la columna izquierda del inicio. Trofeos: `.mroad .num`.
2. **Valor mostrado retrasado:** antes de volar, el pill debe mostrar el valor **anterior**. Como `topbar()` se redibuja con `innerHTML`, se añade un objeto `PEND={coins:0,pp:0,tk:0}` y `topbar()` usa `fmt(S.coins-PEND.coins)`. `applyItems`/`giveReward` siguen cambiando `S` al momento (el guardado es seguro) y el vuelo va restando lo pendiente según llegan las piezas.
3. **Número de piezas:** `k=clamp(round(3*log2(1+|n|/5)),4,14)`. Por ejemplo, 20 monedas → 7, 56 PP → 11, 250 → 14.
4. **Trayectoria:** al salir, explotan hacia fuera en abanico (60–90 px en 180 ms con `ease-out`). Luego viajan en curva de Bézier cuadrática hacia el destino (450–650 ms, `cubic-bezier(.55,0,.85,.35)`, es decir, aceleran al final). Escala 1→0,55 y giro aleatorio ±180°.
5. **Llegada de cada pieza:** el valor mostrado sube `n/k` (la última ajusta el resto) y el pill hace `bump` (reiniciado para que se encadene). Tic con tono ascendente: monedas `tone(1400*2**(i/k*.5),.04,"square",.035)`; PP `tone(1100*2**(i/k*.5),.05,"sine",.05)`. `hap(6)` solo en la primera y la última pieza.
6. **Al acabar:** `cpop` en el número, `sparkle` en el icono del pill (8, dorado o morado) y ding: `tone(2093,.16,"sine",.06)`.
7. **Gasto** (n<0): el mismo sistema al revés (del pill al destino), 6 piezas, sin abanico, 350 ms, tic sordo `tone(500,.04,"triangle",.03)`. El pill baja al salir la primera pieza, no al llegar, porque el dinero ya se ha ido.
8. **Capa:** las piezas van en un contenedor `#fly` con `position:fixed;z-index:95;pointer-events:none`, por encima de `.boxov` (60) y `.lvup` (61). Si el pill está tapado por una capa a pantalla completa, primero se cierra la capa y luego se vuela (ver 2.3). Con `REDUCED`: sin vuelo; el contador sube en 300 ms y `bump`.

### 4.2 Esbozo de código

```js
const PEND={coins:0,pp:0,tk:0};
const FLY_ICO={coins:"coin",pp:"power",tk:"star"};
const FLY_DST={coins:"#coinsn",pp:"#ppn",tk:'[data-t="pass"]'};
const FLY_TICK={coins:i=>tone(1400*2**i,.04,"square",.035),pp:i=>tone(1100*2**i,.05,"sine",.05),tk:i=>tone(1318*2**i,.045,"sine",.045)};

/* kind: coins|pp|tk; n: cantidad (+ gana, − gasta); from: Element|DOMRect|{x,y} */
function flyRes(kind,n,from){
  const dstEl=$(FLY_DST[kind]),pill=dstEl&&dstEl.closest(".rpill,button");
  if(n>0)PEND[kind]+=n;                                      // el contador aún enseña el valor viejo
  const shown=()=>(kind==="tk"?S.pass.tk:S[kind])-PEND[kind];
  const settle=()=>{if(dstEl&&dstEl.id)dstEl.textContent=fmt(shown());};
  if(!pill||REDUCED){PEND[kind]=0;settle();pill&&bumpEl(pill);return Promise.resolve();}
  const r0=from.getBoundingClientRect?from.getBoundingClientRect():from,
        x0=(r0.left!=null?r0.left+r0.width/2:r0.x),y0=(r0.top!=null?r0.top+r0.height/2:r0.y),
        rd=(pill.querySelector(".ico")||pill).getBoundingClientRect(),x1=rd.left+rd.width/2,y1=rd.top+rd.height/2;
  const gain=n>0,a=Math.abs(n),k=Math.max(4,Math.min(14,Math.round(3*Math.log2(1+a/5))));
  const [sx,sy,ex,ey]=gain?[x0,y0,x1,y1]:[x1,y1,x0,y0];
  const layer=$("#fly")||document.body.appendChild(Object.assign(document.createElement("div"),{id:"fly"}));
  let landed=0,given=0;
  if(!gain){PEND[kind]=0;settle();bumpEl(pill);}              // al gastar, baja ya
  return new Promise(done=>{
    for(let i=0;i<k;i++){
      const im=document.createElement("img");im.src=UIA+FLY_ICO[kind]+".webp";im.className="flyico";layer.appendChild(im);
      const ang=-Math.PI/2+(Math.random()-.5)*2.4,sp=gain?60+Math.random()*30:0,
            mx=sx+Math.cos(ang)*sp,my=sy+Math.sin(ang)*sp,           // abanico
            cx=(mx+ex)/2+(Math.random()-.5)*120,cy=Math.min(my,ey)-80-Math.random()*60; // punto de control
      const pts=[];for(let s=0;s<=10;s++){const t=s/10,u=1-t;pts.push({x:u*u*mx+2*u*t*cx+t*t*ex,y:u*u*my+2*u*t*cy+t*t*ey,t});}
      const kf=[{transform:`translate(${sx}px,${sy}px) scale(.4)`,opacity:0,offset:0},
                {transform:`translate(${mx}px,${my}px) scale(1.1)`,opacity:1,offset:gain?.25:0.05},
                ...pts.slice(1).map(p=>({transform:`translate(${p.x}px,${p.y}px) scale(${1.1-.55*p.t}) rotate(${p.t*(i%2?200:-200)}deg)`,
                     offset:(gain?.25:.05)+p.t*(gain?.75:.95)}))];
      const dur=gain?600+Math.random()*150:350;
      im.animate(kf,{duration:dur,delay:i*(gain?40:30),easing:"cubic-bezier(.55,0,.85,.35)",fill:"both"}).onfinish=()=>{
        im.remove();landed++;
        if(gain){const step=landed===k?PEND[kind]:Math.round(a/k);PEND[kind]-=step;given+=step;settle();bumpEl(pill);
          FLY_TICK[kind](landed/k*.5);if(landed===1||landed===k)hap(6);}
        else tone(500,.04,"triangle",.03);
        if(landed===k){if(gain){sparkleAt(x1,y1,kind);tone(2093,.16,"sine",.06);const num=$(FLY_DST[kind]);num&&num.classList.add("cpop");}done();}
      };
    }
  });
}
function bumpEl(el){el.classList.remove("bump");void el.offsetWidth;el.classList.add("bump");}
function sparkleAt(x,y,kind){burst(x,y,kind==="pp"?["#c07bff","#fff"]:kind==="tk"?["#5fd8ff","#fff"]:["#ffcc1f","#fff"],8,2.5,-.02);}
```
```css
#fly{position:fixed;inset:0;z-index:95;pointer-events:none}
.flyico{position:absolute;left:0;top:0;width:34px;height:34px;margin:-17px 0 0 -17px;will-change:transform;filter:drop-shadow(0 2px 0 rgba(0,0,0,.35))}
.rpill.bump{animation:bump .22s cubic-bezier(.3,1.8,.5,1)}   /* más corta que la actual (.5s) para poder encadenarla */
@keyframes bump{40%{transform:scale(1.22)}}
```
Detalles: `topbar()` debe usar `fmt(S.coins-PEND.coins)` y `fmt(S.pp-PEND.pp)`. Si se cambia de pantalla a mitad del vuelo, `settle()` vuelve a buscar el elemento por id. Al terminar, `PEND` queda en 0.

---

## 5. Inicio vivo (sin ruido)

Ya existen: rayos girando (26 s), cofre con `hop`, `shine` en JUGAR, héroe que respira y reacciona al toque alternando ataque y victoria (`SHOW`, l.2100).

### 5.1 Qué añadir
| Elemento | Comportamiento | Parámetros |
|---|---|---|
| Gestos del héroe en reposo | Si no hay toques, un gesto aleatorio (mirar a un lado, saludo, mini salto) | cada 9–15 s al azar; solo si la pestaña está visible y la pantalla es `home`; no en los primeros 4 s |
| Toque al héroe | Ya alterna ataque y victoria; añadir sonido propio y partículas | sonido por héroe: `tone(base,.08,"triangle",.06,base*1.5)` con `base` distinto por héroe (330–660 Hz); 5 `sparkle` en el punto tocado; `hap(8)`; enfriamiento de 500 ms |
| Racha de toques | 5 toques en menos de 2 s = giro de celebración + `confetti` pequeño (20) | máx. 1 vez por minuto (pequeño premio por curiosear) |
| Partículas de ambiente | 6–8 motas brillantes que suben despacio en los rayos | canvas `#fx` en modo continuo `ambient`: vy −0,15…−0,35, vida 6–9 s, alpha ≤ 0,35, tamaño 2–4 px; se para si la pestaña está oculta o con `REDUCED` |
| Brillo en botones de acción | `shine` solo en el CTA más importante | JUGAR siempre (subir el ciclo de 3,4 s a 5 s); los demás `shine` solo cuando hay algo listo |
| Badges | Al aparecer un badge nuevo: `slam` + 3 ciclos de `badge` y después quietos | no pulsar para siempre (hoy `@keyframes badge` existe para eso) |
| Llaves | Con 2/3 llaves, la tercera ranura brilla tenue (`glowpulse`, 2,4 s) | "una más y hay cofre" |
| Barra de trofeos | Si `claimable()>0`, el icono del siguiente premio `.nx` hace `hop` | igual que el cofre |
| Pill con mejora posible | Si `anyUp()`, la flecha ↑ del badge de Héroes sube y baja 3 px | 1,2 s |

### 5.2 Presupuesto de atención (lo más importante)
- **Una sola** llamada de atención animada a la vez, además del héroe, los rayos y el `shine` de JUGAR. Prioridad: cofre para abrir > regalo gratis > misión para cobrar > pase para reclamar > premio del camino > mejora disponible. Solo el primero de la lista hace `hop` o `badge`; el resto muestra el badge **quieto**.
- Cada llamada animada **descansa**: 1 ciclo cada 4–6 s (`animation: hop 1.6s` con `animation-delay` y un keyframe que deje el 70 % del ciclo quieto), no un rebote continuo. El `hop` actual ya está quieto el 60 % del ciclo; dejarlo así y alargar la duración total a 4 s.
- Nada se anima mientras hay un modal abierto ni durante 1,5 s tras volver al inicio (deja leer la pantalla).
- `document.visibilitychange`: pausar `SHOW`, la capa ambiental y los `setInterval`.
- `prefers-reduced-motion`: quietos rayos, ambiente, gestos y `hop`; quedan los badges estáticos y el contador que sube sin vuelo.
- Sonido en el inicio: **ninguno ambiental**. Solo suena lo que el jugador toca.

---

## 6. Cambios de código por impacto

1. **`flyRes` + `PEND` + `bumpEl` + `countUp`** (§4, §1). Usarlo en: CONTINUAR de `boxHTML`, `misClaim`, `buy`/`buyOffer`/`buyBox` (gasto), `upgrade` (gasto). Hace que el `.rpill.bump` que ya existe, pero no se usa, empiece a funcionar. *Mayor impacto con menos riesgo.*
2. **Rehacer `boxTap`/`boxHTML`:** tirar `rollChest` en `openBox`; `M.best`/`--g`; fases A/B/C con `--k` creciente; pausa de 380 ms; objetos que salen de `.chopen`; `countUp` en `.amt`; revelado de héroe con silueta y fanfarria por rareza; `M.ready` y `UI.fast`. Nuevos keyframes: `squash`, `slam`, `charge`, `glowpulse`; nuevos sfx: `"drop"`, `"land"`, `"tap1".."tap3"`, `"charge"`, `"burst"`, `"ding"`, `"ppding"`, `"hero0".."hero3"`.
3. **Bus de audio** en `actx()` (compresor + ganancia) y `noise(...,type)`. Hoy, el `sfx("open")` + `confetti()` + ticks pueden saturar. Además, separar `sfx("levelup")` de `sfx("win")`.
4. **`endMatch` en secuencia:** `revealEnd()` async con `wait()`; trofeos que vuelan uno a uno con tono cromático (sustituye el bucle de 20 pasos de l.2604); llave que vuela (2.7) y fusión de 3 llaves en cofre; detectar arena nueva y nivel de cuenta.
5. **Momento de arena nueva** (`showArenaUp(oldK,newK)`, CSS `.arenaup`). Hoy no existe y es el hito principal.
6. **Rehacer `.lvup`:** gasto que vuela, hexágono con rodillo (`numroll`), líneas de mejora una a una con `countUp`, `confetti` en t=1450 y no en t=0.
7. **`burst` ampliado:** formas `star`/`spark`, `glow` con `lighter`, `drag`; emisores `sparkle`, `dust`, `fountain`; límite de 450.
8. **`screenFlash`, `ring`, `hap` con presupuesto** y ajuste `S.vib`.
9. **Pase y misiones:** sello ✓, estrellas que vuelan, barra que se llena y desborda (`passTierUp(prev,next)`), y FLIP del nodo al centro en `passClaim`/`claim`.
10. **Regalo diario y compra:** FLIP del cofre desde la tarjeta (`flipToCenter(el)` devuelve una promesa antes de `openBox`), y pill que tiembla en rojo si faltan monedas.
11. **Ética y anticipación:** `upChance` y `M.upTo`, `S.pity` con contador visible en el inicio, probabilidades en ⓘ, `S.streak`/`S.dayStreak`.
12. **Inicio vivo:** gestos en reposo en `SHOW` (temporizador de 9–15 s), sonido por héroe al tocar, motas de ambiente, presupuesto de atención (`attentionTarget()` elige un único elemento animado) y pausa con `visibilitychange`.

### Nuevos `case` de `sfx` (para pegar)
```js
case "drop":noise(.35,.10,2200);tone(900,.4,"sine",.04,300);break;
case "land":tone(95,.28,"sine",.3,45);noise(.18,.32,260);break;
case "tap1":noise(.1,.27,500);tone(196,.14,"square",.07);tone(392,.10,"triangle",.05,null,.03);break;
case "tap2":noise(.1,.32,680);tone(247,.14,"square",.07);tone(494,.10,"triangle",.05,null,.03);break;
case "tap3":noise(.1,.37,860);tone(294,.14,"square",.07);tone(587,.10,"triangle",.05,null,.03);break;
case "charge":tone(180,.38,"sawtooth",.045,720);tone(360,.38,"triangle",.04,1440);noise(.38,.12,600);break;
case "burst":tone(110,.45,"sine",.3,50);noise(.5,.28,1400);noise(.6,.06,6000,.05,"highpass");arp([1046,1318,1568,2093],.06,"sine",.07,.2,.12);break;
case "ding":tone(1568,.14,"triangle",.09);tone(2093,.22,"sine",.07,null,.05);break;
case "ppding":tone(1318,.2,"sine",.08);tone(1976,.3,"sine",.06,null,.06);noise(.3,.04,7000,.05,"highpass");break;
case "key":tone(2637,.07,"triangle",.07);tone(3520,.12,"sine",.05,null,.04);noise(.05,.08,9000,0,"highpass");break;
case "stamp":noise(.08,.3,500);tone(180,.1,"square",.08);break;
case "buy":tone(1568,.05,"square",.05);tone(1046,.08,"square",.05,null,.05);noise(.06,.1,4000,.03);break;
case "nope":tone(220,.12,"square",.05,165);break;
case "levelup":tone(110,.35,"sine",.25,55);noise(.3,.2,1000);arp([523,659,784,1046,1318],.06,"triangle",.07,.18,.3);break;
case "arena":arp([392,523,659,784],.09,"square",.05,.2);arp([659,784,1046,1318],.09,"square",.05,.2,.45);[523,659,784,1046].forEach(f=>tone(f,.9,"triangle",.05,null,.9));break;
```
(Requiere `arp` de §1 y el parámetro `type` en `noise`.)
