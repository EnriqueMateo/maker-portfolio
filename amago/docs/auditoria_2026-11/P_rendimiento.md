# AMAGO: auditoría de rendimiento, memoria, carga y estabilidad

Área: rendimiento, memoria, carga y estabilidad en móviles reales (iPhone 11 a 16, Android de gama media).
Fecha: 6 nov 2026. Auditoría de solo lectura: no se ha cambiado ningún fichero del repositorio.

## Cómo se ha medido

- Código: `amago/index.html` (4769 líneas, 465 KB; 148 KB con gzip), `vendor/three.min.js` (r160, 712 KB; 184 KB con gzip), `server/server.js`, `app/scripts/build-www.js` y `app/ios/App/App/*.swift`.
- Recursos: `du`/`stat`, cabeceras de los WebP (dimensiones reales) y del JSON de los GLB (vértices, triángulos y tipos de atributo).
- Ejecución: Playwright y Chromium con SwiftShader contra `http://localhost:8098/`, con viewport de 390×844 y DPR 1 y 3. Se instrumentó WebGL (`texImage2D`/`texStorage2D`, `createBuffer`/`deleteBuffer`, `deleteTexture`, llamadas de dibujo y contextos creados), además de las peticiones de red, `performance.memory`, el número de nodos DOM y las tareas largas. Los scripts están en el scratchpad (`perf.js`, `perf2.js`, `perf3.js`, `perf4.js`, `bare.js` y `webpdim.py`).
- Aviso: SwiftShader renderiza por software. Los tiempos absolutos por fotograma no sirven para un teléfono. Sí valen las proporciones (por ejemplo, DPR 3 frente a DPR 1), los contadores (bytes, texturas, buffers y llamadas de dibujo) y las fugas.

### Números clave medidos

| Métrica | Valor |
|---|---|
| Peticiones hasta la pantalla de inicio (+4 s) | **105 peticiones, 15,5 MB** descomprimidos (arena GLB 5,3 MB, `models/flecha.glb` 2,3 MB, `anim/` 4,8 MB, sprites 0,84 MB, three 0,71 MB, props 0,52 MB, skins 0,36 MB, index 0,47 MB) |
| Tamaño del lienzo en partida con DPR 3 | **1170×2532** (3 MPx) con MSAA y sombras PCFSoft |
| Fotograma con SwiftShader, DPR 3 frente a DPR 1 | p50 2566 ms frente a 800-950 ms (unas 3 veces más: el coste depende de los píxeles) |
| Llamadas de dibujo por fotograma | inicio 33 · **partida 183-191** |
| Contextos WebGL creados | 3 (inicio, retratos y arena). **2 siguen vivos durante la partida** (3 `<canvas>` en el DOM) |
| Texturas en GPU tras 3 rondas | 107 subidas, **3 borradas**; unos 300 MB acumulados en la traza |
| Buffers GL tras 3 rondas y 3 reconstrucciones | **3344 creados, 237 borrados** (+460 por cada `B3.build`) |
| Por cada `B3.build` (cada ronda) | +3 texturas (+18 MB, entre ellas un mapa de sombras de 2048² nuevo), +460 buffers y 0 liberados |
| Memoria GPU de las tiras `anim/` por héroe (con mipmaps) | 100-129 MB (Ojo 129, Muro 124, Rayo 113…) |
| `loadArena` de trono/olimpo (con `bareMesh`) | soldadura de vértices: 194 ms en Node con CPU de escritorio (en teléfono, de 0,5 a 1 s bloqueando el hilo principal) |
| Heap JS | 20-36 MB, estable (el problema está en la GPU, no en el JS) |
| Nodos DOM | 88-152 (bien) |
| localStorage | `amago-v3` 1,3 KB y `amago-acc` 89 B (bien) |

---

## Hallazgos

### P1 · crítico · Las tiras de animación pre-renderizadas ocupan unos 100-130 MB de GPU por héroe y nunca se liberan
- **Evidencia:** `index.html:2404-2422` (`ANIM3D`, `loadAnim3d`). Cada héroe tiene 12 tiras WebP de hasta **4750×470** (muro) o **4580×509** (ojo). Con RGBA8 y mipmaps (three r160 y WebGL2 generan mipmaps también en NPOT; la traza muestra `2888x497 L12` y `3610x497 L12`), cada héroe ocupa **100-129 MB**. `anim3dHero` (`:2428`) clona las texturas en cada ronda y nada las libera (`dispose` no aparece en esa ruta). En una partida al mejor de 3 pueden salir hasta 6 héroes distintos (3 tuyos y 3 del bot), es decir, **unos 600-750 MB de VRAM** que nunca se liberan. Además, nada más arrancar se piden las tiras del favorito y de todos los desbloqueados (`:4762`, `loadAnim3d(S.unl)`; los 4 de inicio suman 4,8 MB de red y unos 430 MB de GPU en cuanto se muestren).
- **Impacto:** en iOS, WebGL va en el proceso WebContent del WKWebView y jetsam lo mata hacia 1,2-1,5 GB en equipos de 4 GB (iPhone 11, 12, 13 y SE 3). El síntoma es la pantalla en blanco o negro, o que la app «se reinicia» a mitad de partida. En Android de 4 GB pasa lo mismo, o el contexto WebGL se pierde.
- **Arreglo:**
  1. Reescalar los fotogramas a **≤256 px de alto** (el héroe ocupa unos 150 pt en pantalla) y empaquetarlos en **atlas de 2048×2048 como máximo**, uno por héroe y vista.
  2. Usar **KTX2 (Basis ETC1S/UASTC)** con `KTX2Loader`: ASTC/ETC2 se queda en 1 byte/px o menos, frente a 4.
  3. `t.generateMipmaps=false; t.minFilter=T.LinearFilter; t.anisotropy=1` (son tarjetas de cara a la cámara).
  4. Al terminar la partida, `tex.dispose()` de las tiras de los héroes del rival que no sean tuyos y de los clones.
  5. Objetivo: **≤12 MB de GPU por héroe y ≤40 MB en total para las animaciones de una partida.**

### P2 · crítico · `B3.dispose()` no libera nada de GPU y cada ronda deja 460 buffers, 50 o más materiales y un mapa de sombras de 2048²
- **Evidencia:** `index.html:2797-2802`. `dispose()` solo quita los listeners y llama a `rnd3.renderLists.dispose()`. `build()` (`:2711-2770`) crea en cada ronda una escena nueva con: luces nuevas (`GFX.lights(scene,true,rnd3)`, `:2535-2545`, con un `DirectionalLight` con `castShadow` y `mapSize 2048²`), 50 `MeshLambertMaterial`, 50 planos `dec` con su `PlaneGeometry` y su material, 50 `SpriteMaterial`, 50 materiales de anillo, la textura de espuma de 512² (`CanvasTexture` nueva), el cielo, 26 cajas de agua, 9 esferas de niebla, anillos y círculos. Lo medido (`perf3.js`): **cada reconstrucción suma 3 texturas (unos 18 MB) y 460 buffers GL; en 3 rondas, 3344 buffers creados frente a 237 borrados y 107 texturas frente a 3 borradas.** En r160, `WebGLBindingStates` guarda los VAO por `geometry.id` hasta que se llama a `geometry.dispose()`, así que el GC no basta.
- **Impacto:** la memoria de GPU crece de forma lineal con las rondas y las partidas (unos 20 MB por ronda, solo con el mapa de sombras y la espuma). Tras 10-15 partidas en una sesión se suma a P1 y aparecen tirones de GC del navegador y cierres.
- **Arreglo:** en `dispose()`, recorrer la escena y liberar:
  ```js
  scene.traverse(o=>{if(o.geometry&&o.geometry!==TILE_GEO&&!ringGeo.includes(o.geometry))o.geometry.dispose();
    const ms=Array.isArray(o.material)?o.material:[o.material];for(const m of ms){if(!m)continue;if(m.map&&!texCache_has(m.map)&&!isShared(m.map))m.map.dispose();m.dispose();}
    if(o.isLight&&o.shadow&&o.shadow.map){o.shadow.map.dispose();o.shadow.map=null;}});
  scene.background&&scene.background.dispose();
  ```
  Mejor todavía: **construir la escena estática una vez por arena** y en cada ronda solo reposicionar o reiniciar los héroes y los efectos. Que los 50 materiales de casilla compartan uno por color/semilla.
  Objetivo: de una ronda a otra, `renderer.info.memory.textures/geometries` constante (±2).

### P3 · alto · Dibujado a DPR 3 con MSAA y sombras suaves: demasiados píxeles para un móvil
- **Evidencia:** `index.html:2787` `prNow=Math.min(3,devicePixelRatio)`, `:2716` `new WebGLRenderer({antialias:true})` y `shadowMap.type=PCFSoftShadowMap`. Lienzo medido: **1170×2532 = 2,96 MPx** con MSAA 4×. La calidad adaptativa (`prWatch`, `:2789-2795`) solo baja si la media es >26 ms (<38 fps), nunca baja de **1,5**, nunca vuelve a subir y no tiene en cuenta el calor. En SwiftShader, DPR 3 cuesta unas 3 veces más por fotograma que DPR 1.
- **Impacto:** en iPhone 11 (A13, 828×1792 a 2×) y en Android de gama media, mucho fill-rate gastado: el móvil se calienta y baja de frecuencia a los 5-10 min y la batería cae rápido. En iPhone Pro (3×) se renderizan 9 veces más píxeles que a 1×, para una mejora visual mínima en sprites ilustrados.
- **Arreglo:** `prNow=Math.min(2,devicePixelRatio)`, y empezar en 1,5 si `navigator.hardwareConcurrency<=4` o si la GPU es antigua. `antialias:false` cuando `pr>=2` (a 2× apenas se notan los dientes de sierra; si hace falta, FXAA barato). Que la adaptativa también baje a 1,25 y vuelva a subir con histéresis. Objetivo: **≤1,6 MPx por fotograma** (por ejemplo, 2× en 390×844 = 1,3 MPx) y 60 fps estables en iPhone 11.

### P4 · alto · Pase de sombras de 2048² con PCFSoft en cada fotograma para casi ningún objeto
- **Evidencia:** `index.html:2540` (`d.shadow.mapSize.set(2048,2048)`, `radius:4`) con `keepR.shadowMap.enabled=true`. En la arena con GLB horneado no proyecta sombra casi nada: los héroes son tarjetas `MeshBasicMaterial` sin `castShadow` y los únicos que la proyectan son los proyectiles `part()` (rock y bomb). Aun así, las 50 casillas `MeshLambertMaterial` con `receiveShadow=true` muestrean el PCF suave en cada fragmento, y el mapa se actualiza en cada fotograma (`autoUpdate`). Ya hay sombras de mancha (`blob()` y `sh`).
- **Impacto:** un pase de profundidad extra, 16-20 MB de VRAM (que además se pierden por P2) y el coste de PCF en los fragmentos de 2 tableros, todo para una sombra que casi no se ve.
- **Arreglo:** en la arena, `shadowMap.enabled=false` y `castShadow=false` en la luz principal, con sombras de mancha para los proyectiles. Si se quiere conservar, `mapSize 512`, `PCFShadowMap` y `shadowMap.autoUpdate=false` con `needsUpdate=true` solo cuando haya proyectiles.

### P5 · alto · El inicio 3D (`SHOW`) mantiene un segundo contexto WebGL a DPR 3 con sombras, a 60 fps, y nunca lo libera
- **Evidencia:** `index.html:3057-3111`. `r=new WebGLRenderer({antialias:true})` con `PCFSoftShadowMap`, sombra de 1024², ACES y `pr=Math.min(3,dpr)` sin adaptativa; `loop()` dibuja sin parar mientras estás en el inicio, aunque el héroe esté quieto y aunque haya un modal a pantalla completa (misiones, ajustes o cofres). `unmount()` solo para el rAF: el `<canvas id="home3d">`, su contexto, el GLB del héroe (texturas JPEG de 768×1024, 6 subidas medidas), el PMREM y el mapa de sombras **siguen vivos durante la partida** (medido: 3 canvas en el DOM durante la partida). Además, `frame()` llama a `stage.getBoundingClientRect()` en cada fotograma.
- **Impacto:** el inicio es donde más tiempo pasa el jugador (tienda, pase, cofres): ahí gasta batería y calienta el móvil. Dos contextos vivos duplican la memoria de GPU base y aumentan la probabilidad de perder el contexto en iOS.
- **Arreglo:** limitar el inicio a **30 fps** (saltar un rAF de cada dos) y a **0 fps** con un modal abierto o cuando el héroe esté quieto más de 3 s. Usar DPR ≤2, sin sombra (basta la mancha `blob` que ya existe) y `antialias:false` a 2×. Mejor aún: **un solo renderer compartido** entre el inicio y la arena (`keepR`) que mueva su canvas, como ya se hace entre rondas. Si no, en `leaveHome` hacer `r.dispose(); r.forceContextLoss(); cv.remove(); r=null` y reconstruir al volver.

### P6 · alto · No se gestiona la pérdida del contexto WebGL
- **Evidencia:** `grep webglcontextlost|contextrestored` no da ningún resultado. Hay 2 o 3 contextos (inicio, arena y retratos). `envFor` guarda en caché `renderer.__env` (`:2525`), que tras una restauración apunta a un render target que ya no sirve. `B3.update` sigue llamando a `render` y la UI no se entera.
- **Impacto:** en iOS, al volver de segundo plano con presión de memoria (habitual tras P1 y P2), o en Android al cambiar de app, el lienzo queda **negro o congelado** y no se recupera: la partida se pierde.
- **Arreglo:**
  ```js
  canvas.addEventListener("webglcontextlost",e=>{e.preventDefault();stopLoop();showOverlay("Recuperando gráficos…");},false);
  canvas.addEventListener("webglcontextrestored",()=>{delete keepR.__env;texCache_clear();B3.build($("#gl"),R,arena);startLoop();hideOverlay();},false);
  ```
  Si a los 3 s no se ha restaurado, recrear el renderer. En una partida contra el bot, pausar (ver P15).

### P7 · alto · El arranque descarga 15,5 MB (105 peticiones) antes de mostrar el inicio, con un tope de 45 s
- **Evidencia:** `index.html:4759-4763`. `Promise.all([loadSprites(), loadAnim3d([S.fav]), SHOW.preload(S.fav), loadProps(), loadArena(...)])`, y nada más terminar `loadAnim3d(S.unl)`. Medido: **15,5 MB**: `arenas/pradera.glb` 5,3 MB (no hace falta en el inicio), `models/flecha.glb` 2,3 MB, `anim/` 4,8 MB, `sprites` 0,84 MB (incluye los 4 héroes ocultos `live:false`: mina, salto, savia y eco), `skins` 0,36 MB (los 5, aunque no los tengas), `props` 0,52 MB (los de las 5 arenas). El tope es `setTimeout(…,45000)` y la barra de carga es una animación CSS (`@keyframes lbar`), no el progreso real.
- **Impacto:** en la **versión web** con 4G normal (unos 5-10 Mbps reales) son 12-25 s hasta el inicio, y con 3G o 4G lento más de 45 s: la gente se va. En la app (ficheros locales) no hay red, pero sí hay que decodificar unos 15 MB al arrancar (tareas largas de 6 s y 7 s medidas en SwiftShader).
- **Arreglo:** ruta crítica = three + index + **el GLB del héroe del inicio + sus texturas** (o un sprite 2D del héroe como cartel provisional mientras carga). Pedir la arena y las tiras de los dos héroes en `showPick` o `startMatch` (ya existe `ensureAnim`). Sprites y skins solo de los héroes `live` y de los aspectos que tengas. Props solo de la arena actual (`PSET[k]`). Barra de progreso real. Objetivo: **≤2,5 MB y ≤25 peticiones hasta el inicio** en la web y **<2 s de arranque en frío** en un iPhone 11.

### P8 · alto · Arenas GLB de 5,3 MB sin comprimir: colores en float, UV que no se usan e índices de 32 bits
- **Evidencia:** `arenas/*.glb` = 5,25-5,36 MB cada una (26 MB en total en el paquete de la app). Pradera tiene 96 760 vértices y 183 352 triángulos: `POSITION` float (1,16 MB), **`TEXCOORD_0` float (0,77 MB), que no se usa** (`MeshBasicMaterial({vertexColors:true})`, `:2212`), **`COLOR_0` float VEC3 (1,16 MB)** e índices uint32 (2,2 MB). Además, el servidor **no aplica gzip a los GLB** (`server.js:61`, con la regex `/text|javascript/`; con gzip pasarían de 5,3 a 2,6 MB). En tiempo de ejecución se suma `computeVertexNormals` (`:2732`, +1,16 MB y CPU).
- **Impacto:** red (P7), tamaño de la app, unos 6 MB de RAM y VRAM por arena y tiempo de análisis.
- **Arreglo:** exportar sin UV y con normales horneadas (las usa `detailMat`), `gltfpack -cc -vc 8 -vpn` (meshopt con colores en unorm8 y posiciones cuantizadas) o Draco, y simplificar a unos 60k triángulos (son islas vistas desde lejos). Añadir `model/gltf-binary` al gzip del servidor. Objetivo: **≤0,8 MB por arena** (≤0,5 MB con gzip).

### P9 · medio · `bareMesh` reprocesa 99k vértices en el hilo principal en cada carga de Trono, Olimpo y Volcán
- **Evidencia:** `index.html:2189-2207`. Soldadura de vértices con claves `toFixed(3)` de cadena en un `Map` (99 012 cadenas) más union-find y filtrado de triángulos. Medido en Node, solo la soldadura: **194 ms en CPU de escritorio**, lo que en A13 o un Snapdragon 7xx son unos 0,5-1 s. Se ejecuta en `showPick` y al subir de arena (`:3352`, `:3975`), justo cuando el jugador toca la pantalla.
- **Impacto:** un congelón de medio segundo o más en la pantalla de elegir héroe, y basura de cadenas que provoca un GC.
- **Arreglo:** hornearlo una sola vez en el GLB (lo que dice el propio PROGRESO: «rehornear con `AMAGO_BARE=1`»). Mientras tanto, claves numéricas (`Math.round(x*1000)` combinadas en un entero) o hacerlo en un Worker.

### P10 · alto · Una sola excepción en el bucle de partida congela el juego para siempre; no hay manejadores globales de errores
- **Evidencia:** `loop()` (`index.html:4236-4248`) solo vuelve a pedir el `requestAnimationFrame` al final, sin `try/catch`. Si `AMAGO.tick`, `B3.update` o `renderLive` lanzan (por ejemplo, `tiles[b][…]` undefined o un `R` cambiado durante `playReplay`, `:4216`), la partida se queda quieta. Pasa lo mismo con `fxLoop` (`:1800`), `SHOW.loop` y `playReplay.step`. No hay `window.onerror` ni `unhandledrejection`: hay 77 `async/await` y varias funciones `async` lanzadas sin `catch` (`startRound()` desde handlers, `accSubmit`…), y los errores no llegan a `EV` (telemetría).
- **Impacto:** cuelgues que no se ven ni se pueden reproducir, sin datos en `/stats`.
- **Arreglo:** pedir el rAF al principio y envolver el cuerpo en `try{…}catch(e){reportErr(e)}`. Añadir `addEventListener("error",…)` y `addEventListener("unhandledrejection",…)` que manden `EV.add("err",{m,stack:stack.slice(0,500)})` con límite (máximo 5 por sesión).

### P11 · medio · Las estelas de los proyectiles crean una geometría y un material nuevos en casi cada fotograma, y algunos materiales nunca se liberan
- **Evidencia:** `index.html:2954` `if(p.trail&&Math.random()<(p.dense?.7:.35))burst(pos,…,3,…)`. Cada `burst` (`:2850`) crea `BufferGeometry` (2 buffers GL), `PointsMaterial` y un `Vector3` por partícula. Al terminar (`:2960`) solo se libera la geometría: **`PointsMaterial` de `pts`, el material de `shock()` (anillo) y los de los proyectiles nunca se liberan**. Medido: hasta 0,85 buffers nuevos por fotograma de media en partida. Los impactos crean de 24 a 90 partículas por casilla.
- **Impacto:** asignaciones de GPU en el bucle caliente, que dan tirones de unos ms en el driver móvil, y fuga lenta de materiales.
- **Arreglo:** un **único `Points` con un pool fijo** (por ejemplo, 512 partículas en un `Float32Array` reutilizado, `setDrawRange` y un material compartido). `shock` y `glow` con materiales de un pool o reutilizados. Objetivo: **0 `createBuffer` por fotograma** en régimen estable.

### P12 · medio · 185 llamadas de dibujo por fotograma, la mitad de objetos que no se ven
- **Evidencia:** medido: 183-191 llamadas por fotograma en partida (frente a 33 en el inicio). En `build()` (`:2747-2756`) hay 50 casillas (una malla cada una), **50 planos `dec` que se dibujan aunque tengan `opacity=0`** (`visible` sigue a true), 50 iconos y 50 anillos (estos se ocultan bien), 26 cajas de espuma, 9 esferas de niebla, props y el pase de sombras (P4).
- **Impacto:** CPU del hilo principal (en WebGL cada llamada cuesta unos 20-50 µs en móvil) más los cambios de estado; con P3 y P4, menos margen para 60 fps.
- **Arreglo:** `tl.dec.visible=dop>0.01`. Casillas con **`InstancedMesh`** (2 llamadas) y color/textura por instancia (atlas de casillas). Las 26 franjas de agua y las 9 nubes, en una sola geometría unida o en `InstancedMesh`. Objetivo: **≤60 llamadas por fotograma**.

### P13 · medio · Texturas de casilla de 512² generadas con canvas: 18 por arena (unos 25 MB de GPU y 18 MB de canvas) y una caché que nunca se vacía
- **Evidencia:** `tileTex` (`index.html:2593-2612`): canvas de `N=512` (dibujado a 256 lógicos con `g.scale(2,2)`). Por arena hay 6 semillas × 2 colores tuyos más 6 × 2 rivales; la traza muestra **18 subidas de `512x512 L10`**. Cada una ocupa 1,4 MB de GPU y 1 MB de canvas retenido en `texCache`. `texCache` se suma por cada arena que se visita (claves `tile+hex`) y no se libera. En pantalla, una casilla mide unos 70 pt.
- **Impacto:** unos 45 MB de memoria por arena para un detalle que se ve a 70-140 px.
- **Arreglo:** `N=128` (con mipmaps, de sobra para 70 pt a 2×), o **un único atlas de 512² con las 24 variantes** (2 MB en total). Soltar el canvas tras subirla (`t.image=null` no vale con CanvasTexture: usar `ImageBitmap` y `close()`). Vaciar `texCache` de las claves de otras arenas al cambiar de arena.

### P14 · medio · `bakePortraits` crea un tercer contexto WebGL y un PMREM en cada arranque para no hornear nada
- **Evidencia:** `index.html:2548-2562` y `:4753`, `:4763`. Crea `new WebGLRenderer({antialias:true,preserveDrawingBuffer:true})` y `lights(sc,false,r)`, que llama a `envFor` (compila el shader del PMREM y renderiza una esfera de 32×16 más 4 planos). Luego, en el bucle, **todos los héroes salen por `ANIM3D` o `SPRITES`** y se hace `continue`: no se hornea ninguno. Medido: `ctx: 3` en la traza.
- **Impacto:** de 100 a 300 ms de arranque en un teléfono (crear el contexto y compilar shaders) y presión sobre el límite de contextos de iOS.
- **Arreglo:** calcular primero `PORTRAIT[id]` para los que tienen imagen y crear el renderer **solo si queda alguno por hornear** (hoy, ninguno).

### P15 · medio · Pasar a segundo plano a mitad de partida: sin pausa, el guardado en la nube puede perderse y el audio se reanuda fuera de un gesto
- **Evidencia:**
  - Contra el bot: `loop` deja de llamar a `tick` si `document.hidden` (`:4241`) y rAF se para, pero al volver la partida sigue al instante, sin pausa ni cuenta atrás (`:4749` solo reinicia `lastT`). No se escucha `pagehide` ni `freeze`, y `AppDelegate.swift` tiene `applicationWillResignActive` vacío.
  - Online: si pasas más de 25 s fuera, el servidor te da por perdido (`AWAY_BUDGET_MS`).
  - `visibilitychange → CLOUD.push(true)` (`:1712`) programa un `setTimeout(0)` y un `fetch` **sin `keepalive`** (`CLOUD.send`, `:1606`): iOS suspende el JS antes de que salga y **se pierde el guardado del último cambio**. Solo `EV.flush` usa `sendBeacon`.
  - Audio (`:1722`): `ctx.resume()` en `visibilitychange` está fuera de un gesto; tras una llamada (estado `interrupted`) iOS puede rechazarlo y no hay listener `statechange`, así que no hay sonido hasta el siguiente `sfx`, y a veces tampoco entonces.
- **Impacto:** golpes que recibes «sin estar» al volver, progreso que no se sube a la nube y partidas sin sonido tras una llamada.
- **Arreglo:** en `visibilitychange(hidden)` contra el bot, poner `R.paused=true` y al volver mostrar un modal «Pausa · Seguir» con una cuenta atrás de 3. El guardado al ocultarse, con `navigator.sendBeacon(APIU+"save",…)` o `fetch(…,{keepalive:true})`. Audio: `AU.ctx.onstatechange` y reanudar en el siguiente `pointerdown` global (`addEventListener("pointerdown",()=>AU.ctx&&AU.ctx.state!=="running"&&AU.ctx.resume(),{capture:true})`). Online: avisar al servidor con un mensaje `away` para que el rival vea «se ha ido» y no se pierdan los 25 s sin explicación.

### P16 · medio · Al arrancar se cargan recursos que el jugador no va a ver
- **Evidencia:** `SPRITE_LIST` (`:2227`) incluye mina, salto, savia y eco (`live:false`, ocultos). `SKIN_LIST` carga los 5 aspectos de pago. `PROP_LIST` (`:2235`) carga los props de Volcán, Trono y Olimpo con 50 trofeos (Pradera). `loadAnim3d(S.unl)` en segundo plano (`:4762`) baja las tiras de **todos** los héroes desbloqueados: 4,8 MB de red y, cuando se muestran, unos 430 MB de GPU (ver P1). Con 13 sprites, 5 skins y 17 props, las imágenes decodificadas ocupan unos 61 MB de GPU con mipmaps (`webpdim.py`).
- **Impacto:** red, RAM decodificada y tiempo de decodificación sin beneficio.
- **Arreglo:** filtrar por `HEROES[id].live!==false`, por los aspectos que tienes (`S.own.skin`) y por la arena actual (`PSET[arena]`). Tiras de animación solo de los dos héroes de la ronda (con `ensureAnim` en `startRound`, que ya existe) y del siguiente que sea probable.

### P17 · medio · DOM del HUD: lectura de `innerHTML` y anchos que fuerzan el layout 12,5 veces por segundo; aviso de peligro con `box-shadow` animado a pantalla completa
- **Evidencia:** `renderLive` (`:4508-4521`) cada 80 ms: `$("#hp-p").innerHTML!==hp` (lee `innerHTML`, que **serializa el DOM**) y `document.querySelectorAll("#esegs i b").forEach(b=>b.style.width=…)`, que invalida el layout de 10 elementos. `renderStatus` compara `el.innerHTML`. `@keyframes dangerp{to{box-shadow:inset 0 0 90px 26px …}}` repinta toda la pantalla en cada fotograma encima del lienzo WebGL mientras dura el peligro. Hay 47 animaciones CSS infinitas y `.out` usa 8 `text-shadow`.
- **Impacto:** recalcular estilos y layout más repintar cada 80 ms, y una capa a pantalla completa repintada en el peor momento (cuando te van a dar), lo que provoca tirones justo en el momento crítico.
- **Arreglo:** guardar el último valor en JS (`if(last.hp!==hp){…}`) en lugar de leer `innerHTML`. Barra de elixir con `transform:scaleX()` y `transform-origin:left` (compuesta, sin layout). El aviso de peligro, como una capa estática con el degradado ya pintado y solo `opacity` animada. Pausar las animaciones infinitas de los menús con `body.game *{animation-play-state:paused}` cuando no se ven.

### P18 · bajo · Asignaciones por fotograma en el bucle de la arena
- **Evidencia:** `anim3dHero` `card.onBeforeRender` (`:2436`): `new T.Vector3()` ×2 por héroe y fotograma. `update()` (`:2878-2970`): `tileWorld()` crea un `Vector3` en cada llamada (varias por fotograma), `R.marks.b.filter(...)` **dentro del bucle de 50 casillas**, `R.projs.filter` ×2, `p.from.clone().lerp`, `pos.clone().sub(prev)` y `hero.position.clone()` en los efectos. En total, unas 200-300 asignaciones pequeñas por fotograma.
- **Impacto:** pausas menores de GC (unos ms cada pocos segundos) en Android de gama media.
- **Arreglo:** vectores temporales a nivel de módulo (`_v1`, `_v2`), `tileWorld(b,x,y,out)` con salida, y precalcular un índice `marksByTile` una vez por fotograma.

### P19 · bajo · El listener `pointerleave` se acumula en el canvas persistente
- **Evidencia:** `index.html:2764`, `canvas.addEventListener("pointerleave",()=>hover=null)` con una función anónima en cada `build`. `dispose()` no puede quitarla y el canvas es el mismo `keepR.domElement` toda la sesión.
- **Impacto:** un closure más por ronda, que retiene el ámbito de `build`. Es poco, pero crece sin límite.
- **Arreglo:** una función con nombre (`onLeave`) que se quite en `dispose`, o `{signal}` de un `AbortController` por build.

### P20 · medio · Caché web: `index.html` sin validadores, recursos sin huella de versión y sin service worker
- **Evidencia:** `server.js:52-69`. `/` sale con `cache-control: no-cache` **sin `ETag` ni `Last-Modified`**, así que se descargan los 148 KB con gzip en cada visita. Los recursos salen con `max-age=86400` sin hash en el nombre: tras un despliegue que cambie `ANIM3D` (tamaños de fotograma) y las tiras, un usuario puede tener el `index.html` nuevo con WebP viejos durante 24 h (animaciones descuadradas). Los GLB no van con gzip (P8). No hay service worker: sin red, la web no arranca.
- **Impacto:** en la web, descargas repetidas, mezcla de versiones y nada sin conexión. (La app nativa no se ve afectada porque lleva los ficheros dentro).
- **Arreglo:** `ETag` (hash del cuerpo) y respuesta 304. Nombres con huella o `?v=<build>` en `BASE`, con `Cache-Control: public, max-age=31536000, immutable`. gzip o brotli para GLB y JSON. Un service worker sencillo (precarga de index, three, fuentes y lo de la arena actual, con *stale-while-revalidate*).

### P21 · bajo · Tirón la primera vez que sale cada animación: las tiras de hasta 4750 px se suben a la GPU y generan mipmaps en mitad de la ronda
- **Evidencia:** las texturas se suben en el primer `render` en que se usan (cambiar `mat.map` a `tex.f.attack` en mitad de la ronda). La subida de una tira de 4750×470 más `generateMipmap` (12 niveles) cuesta varios ms en un móvil. `t.anisotropy=8` (`:2421`) y `4` en sprites y props no aportan nada en tarjetas de cara a la cámara y forman parte de la clave de caché.
- **Impacto:** un tirón la primera vez que tu héroe ataca, recibe un golpe o cae KO en cada partida.
- **Arreglo:** `renderer.initTexture(t)` de las 24 tiras de los dos héroes durante la cuenta atrás (`vsAndCountdown`). Sin mipmaps ni anisotropía (P1).

### P22 · bajo · La repetición graba vídeo dibujando el lienzo completo en cada fotograma
- **Evidencia:** `playReplay` (`:4196-4223`): `MediaRecorder` a 30 fps y 2,5 Mbps, más un `drawImage` del canvas WebGL de 1170×2532 a un canvas 2D de 540×960 en cada rAF, con la cámara lenta y todos los efectos activos.
- **Impacto:** pico de CPU y GPU, y de calor, en los 8-9 s de repetición. En iPhone 11 puede bajar a unos 30 fps justo en la jugada final.
- **Arreglo:** grabar solo si el jugador va a compartir (o grabar a 24 fps), dibujar el clip cada 2 fotogramas y bajar el DPR de la arena a 1 durante la repetición.

---

## Lo que está bien (no tocar)

- Un único renderer para todas las rondas (`keepR`, sin recompilar shaders): la idea es buena, solo falta liberar los recursos (P2).
- Heap JS estable (20-36 MB), DOM pequeño (88-152 nodos) y localStorage mínimo (1,4 KB), con escrituras dentro de `try/catch`.
- `sendBeacon` para la telemetría al ocultarse. `prefers-reduced-motion` respetado en el CSS y en `burst`. `dt` limitado a 0,1 s al volver al primer plano.
- Fuentes locales en woff2 (50 KB) con `font-display:swap`. index y three con gzip desde el servidor.
- La piel 2D en CPU (`applySkin`) es barata: **0,05 ms por héroe y fotograma** medido (malla de 22×26 y unos 10 huesos). No es un cuello de botella.

---

## Los 5 recursos más pesados

| # | Recurso | Tamaño actual | Qué tiene | Objetivo y formato recomendado |
|---|---|---|---|---|
| 1 | `arenas/trono.glb` | 5,36 MB | 99k vértices y 182k triángulos, colores float, UV sin usar, índices u32. `bareMesh` en tiempo de ejecución | GLB con **meshopt (`gltfpack -cc`)**, color unorm8, sin UV, normales horneadas, *bare* ya horneado: **≤0,8 MB** (≤0,5 MB con gzip) |
| 2 | `arenas/olimpo.glb` | 5,33 MB | igual | igual: **≤0,8 MB** |
| 3 | `arenas/volcan.glb` | 5,33 MB | igual | igual: **≤0,8 MB** |
| 4 | `arenas/pradera.glb` | 5,30 MB | 96 760 vértices y 183 352 triángulos (se descarga al arrancar) | igual: **≤0,8 MB**, y cargarla al empezar la partida, no al arrancar |
| 5 | `arenas/bosque.glb` | 5,25 MB | igual | igual: **≤0,8 MB** |

Siguientes en tamaño y, sobre todo, **en memoria de GPU**:

| Recurso | Actual | Objetivo |
|---|---|---|
| `models/flecha.glb` (inicio 3D) | 2,30 MB (33 832 vértices y texturas JPEG de 227 + 111 KB) | meshopt y texturas KTX2 o WebP a 512²: **≤0,6 MB** |
| `models/*.glb` (otros 7) | 1,3-1,5 MB cada uno | **≤0,4 MB** cada uno |
| `anim/<héroe>_*.webp` (12 tiras por héroe) | 1,0-1,55 MB de disco por héroe, pero **100-129 MB de GPU** (tiras de hasta 4750×509 con mipmaps) | fotogramas de ≤256 px de alto en un atlas de ≤2048², **KTX2 ETC1S/UASTC**: **≤0,5 MB de disco y ≤12 MB de GPU por héroe** |
| `sprites/*.webp` y `skins/*.webp` | hasta 855×700 (3,2 MB de GPU cada uno) | ≤512 px de alto: 1,3 MB de GPU, y solo los que se usan |
| `vendor/three.min.js` | 712 KB (184 KB con gzip), con GLTFLoader y SkeletonUtils | construcción con tree-shaking (solo las clases usadas): unos 450 KB (unos 120 KB con gzip) |

## Prioridad recomendada

1. **P1 y P2** (memoria de GPU: los cierres en iPhone de 4 GB), **P6** (pérdida del contexto) y **P10** (congelones sin rastro). Son los que provocan cierres y partidas perdidas.
2. **P3, P4 y P5** (DPR, sombras y el inicio a 60 fps): calor y batería; el cambio de código es pequeño y el efecto se nota mucho.
3. **P7, P8, P16 y P20** (carga y tamaño): sobre todo para la web y el arranque en frío.
4. El resto, como pulido.
