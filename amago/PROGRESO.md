# AMAGO: estado del proyecto y siguientes pasos

Rama: `claude/eager-gates-4i58a1`. Juego jugable publicado (privado) en https://claude.ai/artifact/MS8opPSQAqRnR4aCtnmPHk

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

## Pendiente después

- Pulir: KO más claro, resumen de ronda, ronda de práctica guiada, pedir nombre tras la primera partida.
- Gastar monedas en más cosas (skins).
- Empaquetado App Store (Capacitor) y escritorio (Electron) con `window.AMAGO_SERVER`; desplegar el servidor (Render).
