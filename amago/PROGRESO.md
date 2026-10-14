# AMAGO: estado del proyecto y siguientes pasos

Rama: `claude/eager-gates-4i58a1`. Juego jugable publicado (privado) en https://claude.ai/artifact/MS8opPSQAqRnR4aCtnmPHk

## Estado a 14 de octubre de 2026 (leer primero)

**Dónde está todo**
- Repo local: `~/Developer/AMAGO` (NO usar `~/Desktop/AMAGO`: es una copia vieja en iCloud que bloquea git/Xcode). Rama `claude/eager-gates-4i58a1`.
- Servidor: Railway, proyecto `stunning-balance`, servicio `maker-portfolio`, https://maker-portfolio-production-7712.up.railway.app (Postgres + `STATS_KEY`; métricas en `/stats?k=…`). Cada push a la rama despliega.
- App Store Connect: app 6821653359, bundle `com.enriquemateo.amago`, team 47TF333JU2. Versión 1.0 con **build 8** (si aún no, asignarlo). TestFlight: grupo interno «Equipo».
- Builds desde terminal: `cd amago/app && AMAGO_SERVER=https://maker-portfolio-production-7712.up.railway.app npm run sync`, luego `xcodebuild archive` + `-exportArchive` con `destination=upload` (subida automática, número de build automático).
- Vídeos y capturas: `~/Developer/amago-shorts` (Remotion + grabador del juego real con reloj virtual). `node scripts/store_shots.mjs` rehace las capturas de la App Store; `node scripts/scenes.mjs donde cerca` graba jugadas.

**Hecho del 11 al 14 de octubre**
- Cuentas: invitado automático + correo/contraseña + **Iniciar sesión con Apple** (plugin propio `AppleAuthPlugin.swift`, registrado en `MainViewController`, que crea `SceneDelegate`). Avisos al invitado. Borrar cuenta espera al servidor y revoca Apple (si están `APPLE_TEAM_ID/APPLE_KEY_ID/APPLE_PRIVATE_KEY`).
- Entrenamiento guiado (`TUT`) contra el Entrenador Ojo, nombre, primer cofre y mano en JUGAR.
- Auditoría (agentes) y arreglos: IP real para límites, `hello` único, trofeos y héroes desde la cuenta (el guardado no puede subir más de 20/partida), versión de guardado del servidor, día del servidor que no retrocede, ids opacos online, **el amago es indistinguible** (daño, huella, blur, impacto) y no sirve para espiar, salas privadas que caducan, presupuesto de desconexión, bot online indistinguible (tiempos, trofeos, sin cola en `/health`).
- Motor: pasos al ritmo exacto, impactos antes de moverse, escudo no se gasta con invulnerabilidad, descripciones fieles.
- Bot más humano (percepción con retraso, esquiva real, sospecha del amago, amaga antes, dispara a ciegas) y curva más suave.
- Equilibrio: Rayo 8, Bum 6, Brasa 5, Truco 3 (huella en cualquier casilla salvo la suya).
- **5 héroes nuevos ocultos** (`live:false`; probar con `window.AMAGO_DEV_HEROES`): Mina (topo, mina oculta), Salto (rana, salta sin pasos), Savia (hada, se cura tras 14 s), Mira (lince, 2 sin aviso, huella 4 s), Eco (murciélago, dos huellas). Ajustados por simulación al 43-56 %.
- **Reglas de arena** (solo contra el bot): Volcán (lava que delata cada 15 s), Trono (estatua que para un golpe), Olimpo (viento que desplaza disparos).
- Efectos: brillo aditivo, estelas, destello y quemadura en la casilla, temblor en «¡CERCA!», cámara lenta en el K.O., color y viñeta.
- Privacidad/legal: política con Apple, base legal RGPD y proveedores; `PrivacyInfo.xcprivacy`; responsable Enrique Mateo Cobo; descripción de la tienda corregida; capturas rehechas con los costes nuevos (es/en).

**Arte recibido el 14 oct (Gemini), aún sin meter en el juego**
- `art/concepts/`: `flecha` (sustituye al render de Blender), `mina`, `salto`, `savia`, `eco`, y aspectos `brasa_glacial`, `muro_magma`, `sombra_carmesi`, `truco_artico`, `ojo_nevado`.
- `art/props_src/`: Volcán (`roca_lava`, `geiser_lava`, `arbol_quemado`), Trono (`estatua`, `columna_rota`, `antorcha`), Olimpo (`nube_dorada`, `columna_dorada`, `veleta`) y cofres (`cofre_madera`, `cofre_oro_esmeraldas`, `cofre_epico`). Originales con varios objetos en `art/props_src/originales/`.
- Cobertura de arte: antes 7 de 38 piezas necesarias (18 %); ahora 29 de 38 (76 %). Faltan: **Mira (lince)** y los iconos llave, gema, moneda, frasco de Poder, trofeo y corona (+ revisar el resto de `ui/`).

**Prompts de Gemini que faltan por hacer (dárselos al usuario al retomar)** — base de estilo en `docs/arte_nuevos_heroes.md`:
- Héroe: `[BASE] Lince francotirador serio y elegante: orejas con pinceles, capa corta gris, ballesta larga con mira telescópica dorada, un ojo entrecerrado apuntando. Colores amarillo dorado y gris.` → `art/concepts/mira.jpg`
- Iconos (`[BASE OBJETO] Icono de videojuego: …, estilo Clash Royale.`): llave dorada, gema verde tallada, moneda dorada con estrella, frasco de Poder morado, trofeo dorado, corona dorada → `art/props_src/<nombre>.png`
- Opcional: rehacer la rana (Salto) con la cinta de otro color (la roja recuerda a las Tortugas Ninja) y murciélago/gólem a más resolución.

**Arte metido en el juego (14 oct, noche)** — build 10
- Aspectos con ilustración propia (`skins/<id>.webp`, `img:1` en `SKINS`): en menús, tienda, inicio (`SHOW.skinHero`) y en partida (figura 2D con esqueleto `RIG2D[<aspecto>]`).
- Héroes nuevos con figura 2D (`sprites/mina|salto|savia|eco.webp` + `RIG2D`); siguen ocultos (`live:false`). Retrato de Flecha de Gemini.
- Cofres nuevos en `ui/chest1-3.webp` (madera, morado, oro con esmeraldas); el abierto es el mismo con luz (`.lidglow`), ya no hay `_open`.
- Props de Volcán/Trono/Olimpo en `PSET` (tipos nuevos `k` fuego y `b` flota). Trono y Olimpo: `bareMesh` quita al cargar los objetos 3D viejos del GLB (todo lo que sobresale del suelo, salvo tableros) y deja islas + ilustraciones; Volcán solo cambia el puente roto por el dibujado. Blender ya no está instalado: si se reinstala, mejor rehornear con `AMAGO_BARE=1`.
- Recorte: entorno `~/Developer/AMAGO/.venv-art` (rembg). `AMAGO_CUT_MODEL=u2net` para imágenes con zonas claras (zorro ártico).

**Mira lanzada (15 oct 2026)** — build 13: `live:true`, camino de trofeos a 320, pack fijo en la tienda (`NEWHERO`: Mira + 200 de Poder por 800 monedas u 80 gemas, banner `ft==="new"`), aviso único de novedad (modal `news`, `S.news`). Para el siguiente héroe: cambiar `NEWHERO.id` y `road`, quitar su `live:false` y añadirlo a `ROAD`. Orden: Salto → Mina → Savia → Eco, uno cada 2-3 semanas.

**Siguiente**
1. Arte que queda por meter: recorte (`art/blender/cutout_ai.py`), contorno (`outline.py`), retratos y tiras de animación (`anim/<id>_f|b_<anim>.webp` + `ANIM3D`); aspectos como ilustración propia en vez del filtro `f` de `SKINS`; props en `PSET` para volcán/trono/olimpo; cofres en `ui/chest1-3.webp`.
2. Cuando estén Mira y las animaciones: activar los héroes de uno en uno (`live:true`), con pack fijo (sin azar) y desbloqueo jugando.
3. Reglas de arena online (los dos jugadores en la misma arena).
4. Tras la aprobación de Apple: StoreKit con validación de recibos en el servidor (`/api/iap`), gemas de pago y pase en el servidor, aspectos de pago.
5. Pendiente del usuario: correo de soporte (`[CORREO DE CONTACTO]` en privacidad/soporte), App Privacy «vinculado» y condición de comerciante (DSA) en App Store Connect, clave `.p8` de Sign in with Apple.
6. Revisiones que los agentes no terminaron: economía a 90 días, tutorial, emparejamiento, rendimiento, traducciones, accesibilidad.

## Estado actual

- **Juego** (`index.html`): duelo 1v1 en tiempo real sobre islas 5×5 (tuya verde abajo, rival roja arriba), elixir, huellas, objetos cebo, 3 rondas con héroe distinto, al mejor de 2. Rondas de 75 s; muerte súbita a los 45 s (ataques sin aviso, pings cada 5 s).
- **Bot** con 3 dificultades (`DIFFS`: facil por defecto, normal, dificil). Simulado: un novato aleatorio gana ~78 % en Fácil.
- **Equilibrio** ajustado con ~80.000 rondas simuladas (todos los héroes 44–55 %).
- **Progresión**: ~9 trofeos por victoria; 3 victorias = 1 cofre (máx. 3 sin abrir); cofres dan monedas (10 % héroe); camino de trofeos (Ojo 40, Truco 110, Rayo 220, Bum 400); **tienda** (héroes 100/180/320/550 por rareza, oferta del día −30 %, cofre 60).
- **Personajes 2D**: ilustraciones de Gemini (`art/concepts/*.jpg`) recortadas con IA (`art/blender/cutout_ai.py`, rembg isnet; modelo en `~/.u2net`) → `art/sprites_raw/`, con contorno de pegatina (`art/blender/outline.py`) → `sprites/<id>.webp`. En la arena son tarjetas que miran a la cámara (`spriteHero`/`animateSprite` en `GFX`) con animación de muelle. Flecha usa un render de Blender del modelo 3D (no hay imagen de Gemini).
- **Arenas 3D** horneadas en Blender (`art/blender/arena.py <tema>` → `arenas/<tema>.glb`): pradera, bosque, volcan, trono, olimpo (por trofeos). Casillas con textura pintada; rival en rojo.
- **3D antiguo** (guardado, no se usa): modelos TRELLIS rigged en `models/*.glb` (`art/blender/rig.py`, configs `art/rig/*.json`), retratos `portraits/`. `MODEL_LIST=[]` en `GFX`.
- **Interfaz** brillante estilo Brawl; HUD grande; avisos arriba sin robar toques; transiciones cortas; un único renderer persistente para la arena.
- **Online** (`server/`): Node + ws, salas por código. Sirve `/models|portraits|arenas|sprites/…`.

## Publicar el artifact

El host solo sirve ciertos tipos: los GLB se suben como JSON `{"glb":"<base64>"}` y la página lleva `<script>window.AMAGO_EXT=".json"</script>` antes del contenido entre `<!--ARTIFACT-START-->` y `<!--ARTIFACT-END-->`. Sprites `.webp` tal cual. Ficheros de soporte: `vendor/three.min.js` (Three r160 + GLTFLoader + SkeletonUtils, esbuild), `sprites/*.webp`, `arenas/*.json`.

## Pruebas

Servidor local: `cd server && PORT=8091 node server.js`. Scripts Playwright en el scratchpad (`test13/testplay/testround/testend/testall.js`) con `--use-gl=swiftshader`. Simulación del bot: `simbot.js`.

## Arena ilustrada (hecha: Pradera)

Props de Gemini recortados con `cutout_ai.py` en `art/props_src` → `art/props_raw` → `props/*.webp` (bandera roja = azul con el tono cambiado; la azul sale de un fotograma del vídeo). `arena.py` con `AMAGO_BARE=1` genera solo islas, colinas y flores; el juego coloca los props como cartones de cara a la cámara (`PSET` y `addProps` en index.html: árboles que se mecen, banderas, rocas, puente tumbado), pinta hierba sobre lo verde del diorama (`detailMat(grass)`) y usa agua pintada que se mueve. `hierba.webp`/`agua.webp` son provisionales (`art/blender/paint_tex.py`); cambiar por las de Gemini si el usuario las sube como archivo. Al publicar, añadir `props/*.webp` a `files`.

Siguiente: arbusto y flores de Gemini para Pradera; luego bosque/volcán/trono/olimpo con sus props (`PSET[k]`).

## Animaciones 2D (esqueleto sobre la ilustración)

`RIG2D` en index.html marca articulaciones por héroe (coordenadas 0..1 de la imagen). `skin2D` crea huesos (raíz, columna, cabeza, brazos, piernas y extras como cola, bufanda, gorro o mecha) y pesa cada vértice de una malla 22×26 por distancia a los huesos; `applySkin` deforma la malla en CPU cada fotograma. `animateSprite` hace reposo (respira), andar (piernas por turnos, brazos, rebote), ataque según estilo (`shoot`/`throw`/`slam`/`breath`, carga corta porque el proyectil sale al instante), golpe (destello, retroceso, temblor), KO (cae girando sobre un pie) y victoria (saltos, vuelta). Regla: no girar brazos más de ~0,8 rad o la ilustración se deforma. Tamaño en arena `HSCALE=1.02`. Polvo al andar (`puff`). Banco de pruebas: `testanim3.js` / `testgif2.js` en el scratchpad.

## Progresión y menús (estilo Supercell)

- Monedas + Puntos de Poder (⚡) suben a los héroes del nivel 1 al 9 (`UPG`). Efecto en partida (motor, `lvBonus`): +3 % de recarga de elixir por nivel y +1 vida en los niveles 5 y 9. El bot juega a un nivel parecido, limitado por los trofeos (`startRound`). Online (amistoso) va a nivel 1.
- Cofres en 3 tipos (`CHESTS`): Cofre, Cofre grande y Megacofre; dan monedas, ⚡ y a veces un héroe. Se abren a pantalla completa (`boxHTML`/`boxTap`). 3 victorias = 3 llaves = cofre; máximo `BOX_MAX` sin abrir.
- Camino de trofeos (`ROAD`) con premios cada pocos trofeos y avisos de arena nueva. Pase de temporada (`PASS`, 30 escalones de 100 fichas, 14 días desde `SEASON0`). Misiones diarias (`MISSIONS`, 3 al día) dan fichas. Tienda: regalo diario gratis, 3 ofertas del día, cofres y héroes.
- Iconos y cofres renderizados en 3D: `art/blender/icons.py` (pieza por pieza) → `art/blender/ui_icons.py` (recorte + contorno) → `ui/*.webp`. Al publicar el artifact, añadir `ui/*.webp` a `files`.
- CSS de menús al final del `<style>` (bloque "menús (estilo Supercell)"); `.mbg` es el fondo a rayas, `.tabs` la barra de pestañas.

## Retención y monetización (análisis con 4 agentes: retención, monetización, dirección de arte, "juice")

Informes completos en `docs/` (retencion.md, monetizacion.md, direccion_arte_ui.md, recompensas_juice.md). Implementado:
- **Economía:** `UPG` nuevo (héroe 1→9: 6.000 monedas y 3.600 ⚡), `CHESTS` (solo se ganan jugando, con garantía `PITY_MAX`), monedas por victoria según dificultad (tope 100/día), primera victoria del día (llave doble +30 monedas +20 ⚡), trofeos según dificultad (Fácil deja de dar trofeos en 300), rachas, escudo tras 2 derrotas, bot según trofeos (máx. 1 nivel por encima) y **tope de nivel por arena** `LV_CAP` (pagar no compra victorias).
- **Retención:** calendario de 7 días sin castigo (`CAL1`/`CAL2`), misiones diarias (con 1 cambio gratis) y semanales, maestría por héroe (`MASTERY`, usa `S.hw`), premios de regreso (3/10/30 días), regalo de bienvenida, camino de trofeos infinito, amistosos que cuentan para misiones y pase.
- **Pase:** temporadas de 28 días, 40 escalones de 200 fichas, pista gratis `PASS_F` y Premium `PASS_P` (solo contenido fijo), bóveda tras el 40, recuperación ×2 si vas con retraso, cobro automático al cambiar de temporada (`seasonRollover`).
- **Monetización:** gemas (gratis y de pago separadas), Pase Premium 4,99 € o 450 gemas (retroactivo), Plus 9,99 €, saltos de escalón (solo Premium), pack de inicio 1,99 €, lote semanal, aceleradores con gemas con límite diario, cofres de la tienda "a la vista" (contenido fijo), aspectos (filtro de color, también en partida), pregunta de edad y tope de 30 €/mes para 13-17 (menores de 13 sin compras), máximo 1 oferta emergente al día y nunca tras perder, "Información de compras y probabilidades", "Restaurar compras".
- **Pagos:** adaptador `PAY` (`PAY_TEST` simula sin cobrar con `?paytest=1` o `window.AMAGO_PAY_TEST`; `PAY_NONE` oculta lo de pago; la app nativa debe poner `window.AMAGO_PAY` con RevenueCat o cordova-plugin-purchase). Entrega idempotente (`grantSku`). **Antes de cobrar de verdad: guardado en la nube y validación de recibos en el servidor.**
- **UI:** sistema de diseño nuevo (bloque CSS "menús (estilo Supercell): sistema de diseño"), ficha de héroe a pantalla completa, pase de dos pistas, tienda con destacado, camino con raíl, apertura de cofre con luz de rareza honesta, subida de nivel con comparación, resultados en secuencia, recursos que vuelan a la barra (`flyRes`), bus de audio con compresor y sonidos nuevos.
- Iconos 3D provisionales (Blender) en `ui/`: el usuario los sustituirá por arte de Gemini con los mismos nombres. Al publicar el artifact, poner `window.AMAGO_PAY_TEST=true` para probar compras sin cobro.

## Pendiente después

- Pulir: KO más claro, resumen de ronda, ronda de práctica guiada, pedir nombre tras la primera partida.
- Gastar monedas en más cosas (skins).
- Empaquetado App Store (Capacitor) y escritorio (Electron) con `window.AMAGO_SERVER`; desplegar el servidor (Render).
