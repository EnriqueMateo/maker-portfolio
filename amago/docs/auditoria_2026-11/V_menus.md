# AMAGO: auditoría visual de menús, pantallas sin HUD y arte de interfaz

Autor: dirección de arte (auditoría de solo lectura, no se ha tocado el repositorio).
Base: `amago/index.html` (CSS de menús en las líneas 474-1101, "menús (estilo Supercell): sistema de diseño"; plantillas `topbar()` 3335, `showHome()` 3355, `showHeroes()` 3409, `heroPage()` 3423, `showShop()` 3485, `showRoad()` 3540, `showPass()` 3575, `openBox/boxHTML` 3646/3716, `renderModal()` 3753, `arenaUp()` 4367) y las capturas de `scratchpad/qa/base_en/` (390×844 a dpr 2) y `scratchpad/qa/base/` (es, dpr 3).

## Diagnóstico general

El sistema de diseño (paneles `.pnl` con volumen, botones `.gbtn` con labio, contorno `.out`, cintas `.ribn`) va en buena dirección y ya se parece a Brawl Stars en los materiales. Lo que hoy separa a AMAGO de un juego de Supercell no es la calidad de cada pieza. Es la **falta de unidad**:

1. **Tres estilos de personaje a la vez.** En Inicio aparece el modelo 3D TRELLIS (plástico, otra cara). En las fichas aparece la ilustración de Gemini. En los textos aparecen emojis.
2. **Dos o tres versiones de cada componente.** Hay títulos de modal en píldora azul y en cinta. Las filas de Ajustes y de la selección de héroe usan un azul `#1E88E5` que no pertenece a la paleta. Las tarjetas de héroe tienen marcos de rareza que no se leen como rareza.
3. **Momentos de recompensa con poca escenificación.** Hay cofres que no se abren, una arena nueva que enseña la roca equivocada y una victoria de ronda que no llega a verse.
4. **Bloqueos que parecen pantallas muertas.** Siluetas negras sobre gris y pistas premium de color beige lavado.

Casi todo se arregla con CSS y con los recursos que ya existen en `sprites/`, `skins/`, `props/` y `ui/`.

---

## Hallazgos

### V1 · ALTO · Inicio: el héroe es el modelo 3D antiguo y no coincide con su ilustración
- **Pantallas:** `11_inicio.png`, `02_bienvenida_b.png`, `base/11_inicio.png`.
- **Qué falla:** `SHOW.set()` carga `models/<id>.glb` (`loadHero`), que según PROGRESO es el "3D antiguo (guardado, no se usa)". Flecha y Brasa salen con aspecto de plástico brillante, la cara deformada y los ojos planos. En Héroes, Tienda, Bienvenida y Selección se ven con la ilustración 2D de Gemini, que es más bonita. El jugador ve dos personajes distintos con el mismo nombre en la pantalla más importante del juego. Brawl Stars mantiene un único modelo del héroe en todos los menús.
- **Arreglo:** en `SHOW.set()`, usar siempre `skinHero(id,null)` (la figura 2D con `RIG2D`, `GFX.makeHero(id)`) en lugar de `loadHero(id)`, como ya se hace con los aspectos. Basta con cambiar la condición `(k&&GFX.SPRITES[k]?skinHero(id,k):loadHero(id))` por `(GFX.SPRITES[k||id]?skinHero(id,k):loadHero(id))`. Además, subir `HH` a 1,45 para que la figura 2D ocupe lo mismo y añadir una sombra de contacto (un disco con `MeshBasicMaterial` negro y opacidad 0,35 bajo los pies). Si se prefiere no tocar three.js, existe la alternativa sin `SHOW`: `.bigmodel` con `heroArt()`, que ya tiene `.godrays`, `.spot` y `.floorglow`.

### V2 · ALTO · Pantalla de arena nueva: Volcán enseña las rocas con musgo de Pradera
- **Pantalla:** `53_nueva_arena.png`.
- **Qué falla:** `ARENA_PROP={…volcan:"rocas",trono:"bandera_roja",olimpo:"bandera_azul"}` (línea 3135). El momento de progreso más importante del juego enseña piedras grises con musgo verde sobre un fondo rojo de lava. En Olimpo saldría la bandera azul del jugador.
- **Arreglo:** `ARENA_PROP={pradera:"arbol",bosque:"pino",volcan:"geiser_lava",trono:"estatua",olimpo:"columna_dorada"}`. Todos esos archivos existen en `props/`. Para que sea una escena y no un objeto suelto, `arenaUp()` debería componer tres props: el central a 170 px y dos laterales a 110 px (`roca_lava` y `arbol_quemado`, `antorcha` y `columna_rota`, `nube_dorada` y `veleta`) con `position:absolute`, sobre una isla dibujada con CSS (`border-radius:50%/40%` con un degradado del color de `ARENA_BG`). El mismo mapa alimenta `.arenab` en la barra de Inicio ("Hunter Forest" usa `pino`, que está bien).

### V3 · ALTO · Apertura de cofre: el cofre no se abre y la composición deja medio pantallazo vacío
- **Pantallas:** `50_cofre.png`, `51_cofre_premio.png`, `52_cofre_final.png`.
- **Qué falla:**
  - En la fase *ready*, el cofre queda pegado abajo (y ≈ 900-1380 de 1688). El 50 % superior es azul vacío y el título "Big Chest" es una cinta pequeña de 20 px.
  - En la fase *items*, la tarjeta del premio queda arriba y el cofre abajo, con un hueco de unos 600 px entre los dos.
  - El cofre "abierto" es la misma imagen cerrada con `.lidglow` (no hay tapa abierta).
  - Clash Royale centra el cofre, lo hace saltar y cada objeto sale del cofre y vuela hacia el centro.
- **Arreglo:**
  - En `.boxov`, `justify-content:center`. En `.boxov .stage`, `margin-top:auto;margin-bottom:auto`. Cofre a `width:min(70vw,300px)`.
  - El título como `.ribn.gold` con `font-size:28px`, y `.godrays` centrados en el cofre (`top:55%`).
  - En la fase *items*, apilar la tarjeta (`.rwd`) **justo encima** del cofre (`.stage{height:200px;margin-top:-40px}`) y añadir en `.rwd.fly` una animación de salida desde el cofre: `@keyframes outOfChest{0%{transform:translateY(160px) scale(.2);opacity:0}60%{transform:translateY(-10px) scale(1.08)}100%{transform:none}}`, de 0,45 s con `var(--e-pop)`.
  - Para simular la tapa abierta sin arte nuevo, partir el cofre en dos con `clip-path`: un `<img class="lid">` con `clip-path:inset(0 0 58% 0)` y `transform:translateY(-38px) rotate(-14deg)`, y otra copia `.body` con `clip-path:inset(42% 0 0 0)`, más un haz vertical `linear-gradient(transparent,var(--g))` entre las dos.

### V4 · ALTO · Emojis como iconos de interfaz en Ajustes, Modo, Cómo jugar, Selección y avisos
- **Pantallas:** `31_ajustes.png` (👤✏️🔊📳📊❓🧾☁️🌐🔒♻️), `32_modo.png` (🙂😎😈), `38_como_jugar.png` (🙈 como imagen principal), `60_elegir.png` y `72_ronda_ganada.png` (⚡❤️👟💥🔔💧), `11_inicio.png` (⚠️ en la barra de invitado), `10_inicio_modal.png` (💎 dentro del botón CREAR CUENTA aunque existe `ui/gem.webp`), racha 🔥 en Inicio y en el resumen final, candado 🔒 en `.sbtn.lk .sq::after` (línea 1081).
- **Qué falla:** el código tiene unos 300 emojis en plantillas (💧 ×41, 🛡 ×17, 👀 ×17, 🎭 ×14, 👣 ×13, 🔒 ×11…). Se ven con el estilo de Apple, distinto en cada sistema, y rompen la línea de iconos 3D renderizados. En una captura de la App Store delatan "prototipo". Supercell no usa nunca emojis del sistema.
- **Arreglo:**
  1. Sustituir de inmediato los que ya tienen un equivalente en `ui/`: 💎→`ico("gem","s")`, 🔒→`<img src=UIA+"lock.webp">` (también en `.sbtn.lk .sq::after`, con `content:url(ui/lock.webp)` o un `<img class="lockc">`), ❤️→`heart.webp`, 💧→`drop.webp`, ⚡→`power.webp`, 🏆→`trophy.webp`, ⭐→`star.webp`, ⚔/💥→`swords.webp`, ⚙→`gear.webp`, 🎁→`chest1.webp`, 📅→`mission.webp`.
  2. Dificultades en `DIFFS` (líneas 3957-3959): en lugar de 🙂😎😈, el retrato del bot de ese nivel (`portraits/ojo.webp`, `portraits/truco.webp`, `portraits/sombra.webp`) con 1, 2 o 3 `star.webp` debajo.
  3. Cómo jugar (línea 1454, `i:"🙈"`): usar `sprites/ojo.webp` (el entrenador) en cada paso o una mini-isla 5×5 en CSS.
  4. Ajustes: quitar el icono de la fila o usar `gear.webp`, `heart.webp`, etc. Una fila sin icono siempre se ve mejor que una con emoji.

### V5 · ALTO · Dos (o tres) estilos de título de modal
- **Pantallas:** píldora azul con forma de botón en `31_ajustes`, `32_modo`, `35_nube`, `36_amigos`, `37_cola`, `39_nombre`, `40_sin_gemas`, `41_info`, `43_compras`, `44_edad`, `10_inicio_modal`. Cinta `.ribn` en `33_misiones`, `34_calendario` (dorada), `42_vuelta`, `47_novedad`.
- **Qué falla:** el título en píldora azul con labio inferior (`.sheet>h2`) **parece un botón pulsable**: el usuario toca "Settings" o "Don't lose your progress!". Además, cada modal decide su estilo por su cuenta.
- **Arreglo:** una sola regla. `.sheet>h2` pasa a ser la cinta: aplicar los estilos de `.ribn` (y `.ribn.gold` para recompensas o novedades) a todos los `h2` de `.sheet`, o sustituir en `renderModal` cada `<h2 class="out">` por `<span class="ribn">`. Si se quiere mantener una cabecera tipo panel, que sea plana y sin labio: `background:none;box-shadow:none;border:0;font-size:30px`, como el texto de título de Brawl Stars.

### V6 · ALTO · Paleta rota: azul "Material" `#1E88E5` en Ajustes, Modo y Selección de héroe
- **Pantallas:** `31_ajustes.png` (filas `.toggle`), `32_modo.png` (tarjetas Online y Con amigos), `60_elegir.png` (tabla de estadísticas).
- **Qué falla:** esas superficies usan un azul cian saturado plano (`background:var(--bg)` de la capa antigua, línea 226) sin degradado ni brillo. Chocan con el índigo `--pnl-*` del panel que las contiene. Es la diferencia de material más visible del juego.
- **Arreglo:** en `.toggle`, `.modecard` y la tabla de estadísticas de la selección, aplicar el material `.pnl` (o `.well` para tablas: `background:var(--well)` con `inset 0 3px 0 rgba(0,0,0,.45)`). Los conmutadores (`.toggle i`) deben ser interruptores dibujados: una píldora de 52×28 con un pomo blanco, verde `var(--g-2)` si está activo y `var(--d-2)` si no, en lugar del texto "Yes/No".

### V7 · ALTO · Tarjetas de héroe: todas en verde "UPGRADE" y la rareza no se lee
- **Pantallas:** `2_heroes.png`.
- **Qué falla:**
  - Los 6 héroes desbloqueados muestran la misma placa verde `MEJORAR`. Con todo en verde no hay jerarquía.
  - La rareza (borde) se pierde: Flecha, Brasa y Sombra son azul grisáceo; Ojo y Truco, verde; nada destaca.
  - No hay barra de Poder (en Brawl Stars es la información principal de la tarjeta).
  - Los nombres a 16 px compiten con el texto MEJORAR.
- **Arreglo:**
  - En `showHeroes()`, mostrar siempre `bar.pow` con `S.pp/c.pp` y un botón verde pequeño `↑` (`.upt` como insignia flotante en `top:-8px;right:-8px`) solo cuando `up` sea verdadero, y no toda la placa verde.
  - En el CSS, un marco de rareza con brillo: `.card.r2{box-shadow:…,0 0 14px rgba(181,102,255,.6)}` y `.card.r3{…,0 0 18px rgba(255,194,26,.7)}`, una etiqueta de rareza (COMÚN/RARO/ÉPICO/LEGENDARIO) en la parte superior de `.art` y el fondo de `.art` con el color de rareza más saturado.
  - Ordenar por rareza y no por "puede mejorar", como Brawl Stars.

### V8 · ALTO · Estados bloqueados que parecen muertos
- **Pantallas:** `2_heroes.png` (Rayo, Mira y Bum en negro sobre gris), `2_pass.png` y `2_pass_abajo.png` (toda la pista Premium beige y desaturada), `02_bienvenida_b.png` (Misiones y Pase en gris).
- **Qué falla:** `.card.lock .art img{filter:brightness(0) opacity(.55)}` deja una mancha sobre un fondo `#7C849E`. `.ptile.p:has(.lockc){filter:saturate(.55) brightness(.82)}` convierte lo que se quiere vender (Premium) en lo menos atractivo de la pantalla. Brawl Stars y Clash Royale enseñan lo bloqueado **a todo color** con un candado: el deseo vende.
- **Arreglo:**
  - Héroes bloqueados: `filter:brightness(.0) drop-shadow(0 0 0 #000)` sustituido por `filter:saturate(.25) brightness(.55)` (se reconoce al personaje) y el marco de su rareza en lugar del gris. El texto del requisito sobre una cinta dorada "🏆220" con `trophy.webp`.
  - Pase Premium bloqueado: eliminar ese `filter` y dejar el oro intacto con el candado `ui/lock.webp` a 28 px y una veladura `::after{background:rgba(20,10,40,.25)}` como mucho.
  - Botones laterales bloqueados: `grayscale(.4)` en lugar de `.8`, con candado `lock.webp` y una etiqueta tipo "3 partidas".

### V9 · ALTO · Selección de héroe y "pantalla VS": composición plana, mitad inferior vacía y botón rosa
- **Pantallas:** `60_elegir.png`, `61_vs.png` (no hay VS: se pasa directamente a la arena), `72_ronda_ganada.png`, `73_tras_ronda.png`.
- **Qué falla:**
  - Entre y = 1340 y 1688 no hay nada (20 % de la pantalla).
  - El héroe elegido mide unos 160 px dentro de una caja azul claro.
  - El botón FIGHT es rosa `gbtn.red`, mientras que la acción principal del juego es amarilla (JUGAR) según la regla de color del propio sistema.
  - No hay transición VS con los dos jugadores frente a frente, que es el momento de tensión de Brawl Stars.
  - La captura de "ronda ganada" muestra ya la siguiente selección: la celebración no se llega a ver o dura muy poco.
- **Arreglo:**
  - En la selección, quitar `.ice`/azul claro y poner el héroe a 260 px de alto sobre `.godrays` y `.floorglow`, con el nombre debajo a 40 px. La tabla, en `.well`. FIGHT en amarillo `gbtn xl shine` anclado abajo (`position:sticky;bottom:16px`).
  - Pantalla VS nueva (unos 1,4 s): dos mitades en diagonal (`clip-path:polygon(0 0,100% 0,100% 45%,0 55%)`) en azul `--sky-2` y rojo `--r-2`, cada una con `sprites/<id>.webp` a 300 px entrando desde los lados (`translateX(±120%)→0`, `var(--e-pop)`), nombres y trofeos, y un "VS" de 90 px con `.out` y `scale 3→1`.
  - Mantener el cartel de ronda ganada al menos 1,6 s.

### V10 · MEDIO · Inicio: demasiadas capas en la columna central; la barra de invitado tapa el escenario
- **Pantalla:** `11_inicio.png`.
- **Qué falla:** entre el héroe y JUGAR se apilan tres barras de ancho completo (primera victoria, placa del héroe y aviso de invitado amarillo pálido). La crema `#FFF8D6` del aviso es el único panel claro de toda la pantalla y atrae más la vista que JUGAR. El texto "First win of the day" desborda por la derecha (el panel acaba en x ≈ 780).
- **Arreglo:**
  - Mover el aviso de invitado a una insignia roja "!" sobre el avatar (`.mprof`) y a un modal ocasional, como ya hace `guestnag`.
  - Convertir `firstwin` en una etiqueta pequeña encima de JUGAR (`position:absolute;top:-18px;right:10px`) con `key.webp` ×2, "+30" y "+20" (unos 140 px de ancho).
  - `.hplate` a `max-width:62%`. Así el héroe y el botón JUGAR quedan como en Brawl Stars: personaje grande en el centro y solo el botón de jugar debajo.

### V11 · MEDIO · Inicio: el fondo 3D es un cielo y un mar planos con árboles cortados
- **Pantallas:** `11_inicio.png`, `base/11_inicio.png`.
- **Qué falla:** el escenario es un cielo azul liso, un mar cian y dos árboles enormes cortados por los lados (el izquierdo tapa a medias los botones laterales). No hay profundidad, luz cálida ni ambiente. En la parte superior, la barra de recursos flota sobre un azul que la desdibuja.
- **Arreglo:**
  - Encima del canvas, un degradado de viñeta `radial-gradient(120% 80% at 50% 45%,transparent 50%,rgba(6,10,46,.55))` y otro superior `linear-gradient(#0E1F72cc,transparent 22%)` para asentar la barra.
  - Bajar la escala de los árboles de `SHOW` un 25 % y alejarlos 0,6 unidades en x.
  - Añadir los props de la arena actual (por ejemplo `props/bandera_azul.webp` y `rocas.webp`) como cartones al fondo, igual que en la arena. El fondo cambia con la arena (Volcán rojo, Trono morado) gracias a `ARENA_BG`.

### V12 · MEDIO · Barra de pestañas: iconos sin tamaño común y pestaña activa poco marcada
- **Pantallas:** todas (`2_shop.png`, `2_heroes.png`…).
- **Qué falla:** la gema de Tienda está más grande y saturada que las espadas de Héroes, que son finas, grises y casi invisibles sobre el índigo. La pestaña activa es un rectángulo azul claro con las esquinas de arriba redondeadas y no comparte material con el resto. Las insignias (! ↑ 13) se superponen con los iconos.
- **Arreglo:**
  - Normalizar los iconos a una caja de 46×46 (`.tabs img{width:46px;height:46px;object-fit:contain}`).
  - Pestaña activa: elevada (`transform:translateY(-10px) scale(1.12)`), fondo `linear-gradient(var(--b-1),var(--b-2))` con labio `inset 0 -5px 0 var(--b-lip)` y etiqueta en `.out` amarilla `--tx-hl`.
  - Las inactivas, a `opacity:.85` y etiqueta `--tx-3`.
  - Para Héroes, un icono con más masa: el retrato del héroe favorito (`portraits/<fav>.webp`) en lugar de `swords.webp`, como hace Brawl Stars con su icono de Brawlers.

### V13 · MEDIO · Pase: filas gigantes, sin raíl de progreso ni marca de "estás aquí"
- **Pantallas:** `2_pass.png`, `2_pass_abajo.png`.
- **Qué falla:** cada escalón mide unos 230 px, así que los 40 escalones suman unos 9.000 px de scroll. El número del escalón es un círculo oscuro sin raíl que lo una. No hay una barra que crezca ni un marcador del escalón actual. La cabecera "tier 0/40" con una barra vacía no motiva. La Bóveda es un panel vacío sin icono.
- **Arreglo:**
  - `.ptile{min-height:118px}` con el icono a 64 px.
  - Raíl vertical central como en el camino de trofeos (`.rail` y `.fill` reutilizados de `showRoad`) que se llena hasta el escalón actual. El nodo del escalón actual en oro y con pulso (`@keyframes pulse{50%{box-shadow:0 0 0 8px rgba(255,210,74,.35)}}`).
  - Al abrir, desplazar automáticamente al escalón actual (`scrollIntoView({block:"center"})`).
  - Bóveda: `ui/chest3.webp` a 96 px con `.godrays` dentro y una barra de 0/10.
  - Escalones conseguidos: tachados con un ✓ de `.got` en verde, no un emoji.

### V14 · MEDIO · Camino de trofeos: los 13 premios pendientes son bloques amarillos idénticos y no hay contexto de arena
- **Pantallas:** `2_road.png` y `2_road_abajo.png` (idénticas: el scroll no cambia o la lista es demasiado corta para verlo).
- **Qué falla:** con 13 premios por reclamar, toda la pantalla es una pared de `.rtile.claim` amarillos de 104 px con un icono pequeño (58 px). El mismo amarillo sirve para "listo para reclamar" y para el fondo de todo, sin jerarquía. Las etiquetas de trofeos (55, 40…) son píldoras azules iguales que los botones. No se ve la arena a la que pertenece cada tramo.
- **Arreglo:**
  - `.rtile.claim` en material `.pnl` con un **borde** dorado brillante (`border-color:var(--gold-2);box-shadow:0 0 0 3px var(--ink),0 0 16px rgba(255,200,60,.7)`), el icono a 80 px y una pequeña cinta "¡RECLAMAR!" encima. Solo el siguiente premio pendiente con `animation:bob`.
  - Separadores de arena (`.rnode.arena-n`) como tarjeta ancha con el prop de la arena (ver V2) y el fondo `ARENA_BG`.
  - Etiquetas de trofeos con el icono `trophy.webp` a 18 px y fondo `--well`, para que no parezcan botones.

### V15 · MEDIO · Tienda: precios en gris que parecen desactivados e inconsistencia gema cian/gris
- **Pantallas:** `2_shop.png` (Power Barrel, 176), `2_shop_abajo.png` (aspectos 150).
- **Qué falla:** los botones de precio en gemas de los aspectos y de la oferta del día usan el gris `--d-*` (el material de `:disabled`), mientras que los de los héroes usan un cian vivo. Visualmente dicen "no puedes comprar". Además, los precios en monedas son amarillos, el mismo color de JUGAR.
- **Arreglo:**
  - Precio en gemas siempre `gbtn green` (gema = verde, `--gem:#2EE87A`).
  - Precio en monedas en `gbtn` amarillo.
  - Gris solo cuando no alcanza, y en ese caso el número en rojo `--tx-dn` (ya existe `.short`).
  - Revisar en `showShop()` la clase con que se pintan `skin` y `deal`.

### V16 · MEDIO · Tienda: cintas de descuento cortadas e ilegibles
- **Pantalla:** `2_shop.png` (Rayo "-30 % TODA…", Power Barrel "20 %" cortado).
- **Qué falla:** la cinta diagonal se recorta con `overflow:hidden` y el texto ("−30 % HOY") no cabe, así que se lee "30 % TODA".
- **Arreglo:** texto corto ("−30 %"), `font:14px var(--f-game)`, cinta con `width:140px;right:-38px;top:16px;transform:rotate(40deg)` y `text-align:center`. Alternativa al estilo de Brawl Stars: una placa roja inclinada en la esquina (`transform:rotate(-8deg)`) sin recorte.

### V17 · MEDIO · Tienda, sección de recursos: tarjetas cortadas por la barra de pestañas y sin padding inferior
- **Pantallas:** `2_shop.png` (tarjetas de "Resources" asomando bajo las pestañas).
- **Qué falla:** el contenido termina detrás de `.tabs` y no hay espacio de seguridad, por lo que la última fila de cualquier pantalla queda medio oculta.
- **Arreglo:** en `.home` (contenedor de los menús), `padding-bottom:calc(110px + env(safe-area-inset-bottom))`. Lo mismo en Héroes, Pase y Camino.

### V18 · MEDIO · Barra superior: el bloque de perfil ocupa un tercio y los recursos quedan apretados
- **Pantallas:** todas las de menú; `02_bienvenida_b.png` (con "Jugador7307" el perfil llega a x = 350 de 780).
- **Qué falla:** con un nombre largo, `.mprof` empuja a las tres píldoras, que quedan pegadas (gemas en x 615-760) con el "+" casi en el borde. La píldora de gemas se superpone con su botón "+". El nivel del jugador es un número en una caja azul sin barra visible.
- **Arreglo:** `.mprof{max-width:44%}` con `b{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}`. Píldoras a `min-width:84px` y `gap:6px`. El "+" dentro de la píldora (`right:4px`) sin sobresalir. La barra de experiencia del avatar (`.mlv .bar`) a 6 px de alto y visible.

### V19 · MEDIO · Ficha de héroe: tarjetas de estadísticas blancas que rompen el material
- **Pantalla:** `30_heroe.png`.
- **Qué falla:**
  - Las cuatro estadísticas son `.ice` blanco azulado (`#EAF2FF`) con texto oscuro sobre fondo índigo. Contraste duro, y son las únicas superficies blancas del juego.
  - El ataque "Fireball" usa un patrón de cuadrícula y no ilustra el ataque.
  - El héroe flota sin suelo ni pedestal.
  - La barra de nivel son nueve cajitas sueltas.
  - No se ve el botón MEJORAR sin desplazar.
- **Arreglo:**
  - Estadísticas en `.pnl` oscuro con número en `--f-game` blanco de 28 px y etiqueta `--tx-3`; icono a 44 px.
  - Héroe sobre `.floorglow` y una isla de césped en CSS (`ellipse` verde `#5FD35A` con borde `--ink`).
  - El botón MEJORAR (o la barra de Poder y su coste) fijo abajo (`position:sticky;bottom:12px`), en verde con brillo `shine`.
  - Barra de nivel continua `bar.pow` con muescas (`background:repeating-linear-gradient(90deg,transparent 0 calc(11.1% - 2px),var(--ink) 0 11.1%)`).

### V20 · MEDIO · Momento de "volver" y de "héroe nuevo": recompensa diminuta
- **Pantallas:** `42_vuelta.png` (cofre de unos 110 px en un modal), `47_novedad.png`.
- **Qué falla:** un regalo de regreso enseña el cofre a 110 px sin rayos ni brillo, dentro de un modal estándar. El anuncio del héroe nuevo (Mira) es un modal con la ilustración sobre un índigo plano y el nombre en píldora-botón. Brawl Stars hace estos momentos a pantalla completa.
- **Arreglo:** usar el mismo contenedor `.lvup` de `arenaUp()` (pantalla completa, `.godrays`, `confetti()`, `screenFlash`) con el cofre a 240 px y `@keyframes hop`. En la novedad, un fondo `radial-gradient` con el color de su rareza, Mira a 360 px con entrada `scale(.3)→1` y `var(--e-pop)`, el nombre a 44 px `.out` y la cinta dorada "¡NUEVO HÉROE!".

### V21 · MEDIO · Opacidad del velo de los modales y fondo sin desenfoque
- **Pantallas:** `10_inicio_modal`, `32_modo`, `35_nube`, `36_amigos`, `37_cola`, `40_sin_gemas`, `41_info`.
- **Qué falla:** el velo (`rgba(6,8,30,.82)` en la regla, pero en las capturas el fondo se ve bastante claro) deja leer a la perfección la barra superior, los botones laterales y JUGAR. Compiten con el modal y parece que se pueden tocar.
- **Arreglo:** `.modal{background:rgba(4,6,28,.78);backdrop-filter:blur(6px) saturate(.8);-webkit-backdrop-filter:blur(6px) saturate(.8)}` y una entrada del `.sheet` con `scale(.85)→1` y `var(--e-pop)` en 0,22 s (sustituir la animación `coach`).

### V22 · MEDIO · Modal de Misiones: icono genérico y sin estado completado
- **Pantalla:** `33_misiones.png`.
- **Qué falla:** "Gana 2 rondas con Ojo" lleva el icono de una corona, no el de Ojo. Las misiones semanales repiten iconos (estrella, espadas). La recompensa (estrella amarilla) es igual al icono de la izquierda en la misión de rondas. El modal se sale por abajo, sin margen. El botón de cambiar (↻) es un cuadrado sin significado.
- **Arreglo:** si la misión menciona un héroe, usar `portraits/<id>.webp` en un marco redondo. Recompensa en fichas con un icono propio (por ejemplo `star.webp` sobre un disco cian `--token`). Misión completada: fondo verde `--g-2`, ✓ dibujado y botón RECLAMAR. Altura máxima del sheet `max-height:calc(100% - 32px)` con scroll interno (`overflow:auto`).

### V23 · MEDIO · Calendario: el día 7 promete "héroe raro" con una corona y los días cobrados se ven feos
- **Pantalla:** `34_calendario.png`.
- **Qué falla:** el gran premio (día 7) usa `crown.webp`, que en el resto del juego significa "pase" o "favorito". Los días 1-2 cobrados se lavan a un gris-rosa sucio con un ✓ minúsculo en un color turquesa que no existe en la paleta. Hay textos solapados ("Day 1✓").
- **Arreglo:** día 7 con la silueta de un héroe raro (verde, `r1`) usando `heroArt()` con la clase `sil` y "?" encima, más `.godrays` dentro de la tarjeta. Cobrados: `opacity:.55` sin desaturar y un sello grande ✓ verde (círculo de 34 px con `--g-2` y borde `--ink`) centrado sobre el icono. Día actual con brillo pulsante.

### V24 · MEDIO · Pase Premium: rayos recortados con bordes rectos y panel sin margen lateral
- **Pantalla:** `45_premium.png`.
- **Qué falla:**
  - Los rayos del fondo terminan en un rectángulo duro (bordes visibles en x ≈ 30, x ≈ 750 e y ≈ 500): la máscara no difumina.
  - El panel de ventajas va de borde a borde (x 5-775), sin el margen de 16 px.
  - Solo se enseña uno de los tres aspectos.
  - El 25 % inferior está vacío.
  - Hay texto sin traducir ("quedan 20 días", "DESBLOQUEAR CON 450 GEMAS").
- **Arreglo:**
  - En el contenedor de rayos, `-webkit-mask:radial-gradient(closest-side,#000 30%,transparent 100%)` (como `.godrays`), o reutilizar directamente `<span class="godrays">`.
  - Panel con `margin:0 16px`.
  - Los tres aspectos en abanico (`skins/brasa_glacial.webp` en el centro a 300 px, `sombra_carmesi` y `muro_magma` a los lados a 200 px, girados ±8° y con `z-index` menor).
  - Botón de compra fijo abajo.
  - Pasar las cadenas por `TT()`.

### V25 · MEDIO · Bienvenida: logotipo y mascota bien, pero los enlaces secundarios son texto web subrayado
- **Pantalla:** `01_bienvenida.png`.
- **Qué falla:** "I already know how to play" e "I have an account: sign in" son enlaces HTML subrayados que parecen de una web. Debajo hay un 20 % vacío. La mascota no tiene suelo y el texto "I'm Ojo, your coach…" es pequeño (unos 13 px).
- **Arreglo:** convertirlos en `.pillbtn` (o `gbtn blue sm`) apilados, sin subrayado. Ojo a 300 px sobre `.floorglow` con `bob`. El subtítulo a 16 px. Repartir el espacio con `justify-content:space-evenly`.

### V26 · BAJO · Textos sin traducir dentro de la interfaz en inglés
- **Pantallas:** `31_ajustes` ("Invitado"), `35_nube` ("sin conexión ahora mismo"), `36_amigos` ("CÓDIGO" como placeholder), `40_sin_gemas` ("Necesitas 200 … y tienes 120."), `42_vuelta` ("Te hemos guardado un regalo por volver."), `43_compras` (un párrafo entero en español), `45_premium` ("quedan 20 días", "DESBLOQUEAR CON 450 GEMAS").
- **Qué falla:** el mezclado de idiomas es lo primero que nota un revisor o jugador anglófono y abarata la percepción de calidad.
- **Arreglo:** pasar esas plantillas por `TT()` e incluir las claves en `I18N_EN` (línea 1521). El placeholder del código, con `placeholder="${TT("CÓDIGO")}"`.

### V27 · BAJO · Modal "Your progress / account": la captura 46 sale vacía
- **Pantalla:** `46_cuenta.png` (solo el velo oscuro, sin modal).
- **Qué falla:** el modal de cuenta no llega a pintarse (o tarda), y el usuario ve la pantalla oscurecida y nada más. Puede ser un fallo de la captura, pero conviene comprobarlo.
- **Arreglo:** revisar en `renderModal()` la rama `acc` (posible `await` de red antes de `put()`). Pintar primero el sheet con un *spinner* (`ui/gear.webp` con `animation:spin 1s linear infinite`) y rellenarlo después.

### V28 · BAJO · Cola de búsqueda: anillo discontinuo de "cargando web"
- **Pantalla:** `37_cola.png`.
- **Qué falla:** el héroe dentro de un círculo de trazo discontinuo gris parece un spinner de formulario. El contador "171 s .." es texto suelto.
- **Arreglo:** sustituir el anillo por `.godrays` girando lentamente detrás del héroe y una lupa o radar: un `conic-gradient(from 0deg,rgba(62,230,255,.5),transparent 30%)` circular de 180 px con `animation:spin 1.6s linear infinite`. Tiempo en `--f-game` a 22 px y "Buscando rival…" con puntos animados.

### V29 · BAJO · Botones laterales de Inicio: la etiqueta pisa el botón y la columna derecha no se alinea con la izquierda
- **Pantalla:** `11_inicio.png`.
- **Qué falla:** "Open it!" se superpone al cofre (el texto corta la parte baja del cofre morado). La columna derecha (cofre y llaves) no comparte la rejilla de la izquierda: los cuadrados de la izquierda miden 120 px y el módulo de llaves 150 px. Las llaves apagadas son casi invisibles.
- **Arreglo:** `.sbtn .lb{margin-top:-6px;position:relative;z-index:2}` con la imagen del cofre a `max-height:84%`. Mismo tamaño `.sq` (120×120) en ambas columnas y `top` común. Llaves apagadas: `img.off{filter:brightness(0) opacity(.35)}` dentro de un `.well` visible, para que se lean como huecos por llenar (Clash Royale enseña las ranuras vacías con claridad).

### V30 · BAJO · Tipografía: tres familias y pesos mezclados en un mismo bloque
- **Pantallas:** `47_novedad.png`, `33_misiones.png`, `2_pass.png`.
- **Qué falla:** se combinan `--f-game` (Lilita), la fuente de cuerpo en 900 y la fuente de cuerpo en 700 con tamaños muy cercanos (16-18 px), sin una escala clara. Los textos secundarios en `--tx-3` (`#93A2DE`) sobre `--pnl-2` quedan cerca del límite de contraste (unos 4,3:1).
- **Arreglo:** escala fija de 40, 28, 20, 16 y 13 px (`.t-h0`, `.t-h1`, `.t-h2`, `.t-body`, `.t-small`). Títulos y números siempre en `--f-game` con `.out`, y cuerpo en 800. `--tx-3` subido a `#A9B6EC` (mejor de 5:1).

### V31 · BAJO · Animaciones de entrada de pantalla y de pestaña
- **Pantallas:** todas las de menú (por el CSS).
- **Qué falla:** al cambiar de pestaña se sustituye el `innerHTML` de golpe. Solo existe `.stagger` en Héroes. En Supercell, las pestañas se deslizan lateralmente y las tarjetas aparecen escalonadas.
- **Arreglo:** en el cambio de pestaña, añadir `app.animate([{opacity:0,transform:"translateX(${dir*24}px)"},{opacity:1,transform:"none"}],{duration:180,easing:"cubic-bezier(.2,.8,.2,1)"})` (`dir` según el índice de la pestaña) y aplicar `.stagger` también a `.pgrid` de la tienda, a las filas del pase y a los nodos del camino.

### V32 · BAJO · Brillos y destellos: solo JUGAR tiene `shine`
- **Pantallas:** `11_inicio.png`, `2_shop.png`.
- **Qué falla:** el destello (`.shine::after`) solo está en JUGAR y en los botones premium. Los objetos de valor (gema, oferta destacada, cofre listo y Mira en la tienda) no brillan.
- **Arreglo:** `.shine` también en la tarjeta destacada de la tienda (`.feat`), en el botón "¡Ábrelo!" y en las ofertas con descuento. Pequeños destellos de estrella animados con `@keyframes twinkle{0%,100%{opacity:0;transform:scale(.4)}50%{opacity:1;transform:scale(1)}}` sobre las gemas de la barra superior (con un `::after` de un SVG de estrella de cuatro puntas).

---

## Top 10 de mayor impacto (más calidad percibida por esfuerzo)

1. **V1**: en Inicio, mostrar la ilustración 2D animada (`skinHero`) en lugar del modelo 3D antiguo. Es el cambio de una condición en `SHOW.set()` y unifica la cara del juego.
2. **V4**: eliminar los emojis usados como iconos y sustituirlos por `ui/*.webp`, retratos y sprites. Es lo que más "huele a prototipo" en las capturas de la tienda.
3. **V2**: corregir `ARENA_PROP` (geiser_lava, estatua, columna_dorada) y componer la pantalla de arena nueva con tres props.
4. **V3**: rehacer la apertura de cofre: centrarlo, sacar los objetos del cofre y simular la tapa con `clip-path`.
5. **V8**: estados bloqueados a color (Premium dorado intacto y héroes reconocibles con su rareza).
6. **V6 y V5**: un único material de panel (fuera el azul `#1E88E5`) y un único estilo de título de modal (cinta).
7. **V9**: selección de héroe con el héroe grande y FIGHT amarillo, más una pantalla VS de 1,4 s.
8. **V7**: tarjetas de héroe con barra de Poder, rareza legible y la mejora como insignia, no como placa verde.
9. **V10 y V11**: Inicio despejado (fuera la barra de invitado, primera victoria como etiqueta) y viñeta o degradados sobre el escenario 3D.
10. **V13 y V14**: pase y camino con raíl, "estás aquí", filas compactas y recompensas pendientes distinguidas por borde brillante y no por un bloque amarillo.
