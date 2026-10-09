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

## Siguiente paso (en curso)

**Arena con arte pintado del mismo estilo que los personajes.** El usuario va a generar con Gemini (texto común de "Stylized 3D game asset render, Supercell / Brawl Stars / Clash Royale art style … plain pure white background") estas imágenes: `arbol`, `pino`, `arbusto`, `rocas`, `flores`, `bandera_azul`, `bandera_roja`, `puente` y dos texturas cuadradas sin costuras `hierba`, `agua`. Plan: recortarlas con `cutout_ai.py`, colocar props como tarjetas/billboards alrededor de los tableros, usar las texturas para suelo y agua (en lugar del diorama de arcilla), mantener las casillas encima. Luego repetir para bosque/volcán/trono/olimpo.

## Pendiente después

- Pulir: KO más claro, resumen de ronda, ronda de práctica guiada, pedir nombre tras la primera partida.
- Gastar monedas en más cosas (skins).
- Empaquetado App Store (Capacitor) y escritorio (Electron) con `window.AMAGO_SERVER`; desplegar el servidor (Render).
