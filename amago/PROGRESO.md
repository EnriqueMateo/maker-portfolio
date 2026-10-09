# AMAGO: estado del proyecto y siguientes pasos

Notas de trabajo para retomar el proyecto. Rama: `claude/eager-gates-4i58a1`.

## Lo que está hecho y funciona

- **Juego** (`index.html`): duelo 1 contra 1 en tiempo real con elixir, 3 rondas con un héroe distinto cada una, objetos cebo en la misma casilla de las dos islas, huellas al disparar, ¡CERCA!, muerte súbita. Bot con mapa de probabilidad.
- **Menús estilo brawler:** inicio con héroe de portada en 3D, perfil y nivel, trofeos y arenas, colección de héroes por rareza, camino de trofeos con premios, cofres.
- **Arena 3D** con Three.js (`vendor/three.min.js`): dos islas, río, árboles, proyectiles 3D, partículas y temblor de cámara.
- **Héroes 3D procedurales** (módulo `GFX` en `index.html`): cuerpo de gominola con materiales con barniz, sin tone mapping para colores vivos. Es una solución provisional: el usuario la considera insuficiente.
- **Online** (`server/`): servidor Node + `ws` autoritativo, salas por código de 4 letras, revancha y aviso de abandono. El motor de reglas se lee de `index.html` (bloque `ENGINE-START`/`ENGINE-END`). Probado entre dos navegadores con la versión 3D.

## En curso: personajes de calidad profesional con Blender (gratis)

El usuario quiere personajes al nivel de Brawl Stars, Clash, Fall Guys y Mario: esculpidos, expresivos y con materiales buenos. Solución gratuita encontrada: **Blender 4.2 como módulo de Python (`bpy`) instalado desde PyPI**, modelando y renderizando por código.

- Instalación: `python3.11 -m venv /tmp/blendenv && /tmp/blendenv/bin/pip install bpy==4.2.0` (unos 500 MB).
- `art/blender/lib.py`: utilidades. `Blob` une volúmenes (esferas, elipsoides, cápsulas, positivos y negativos) con remallado en vóxeles, booleanos y suavizado laplaciano, lo que da una superficie continua tipo escultura. Además: materiales Principled (piel con subsurface, tela con sheen, cuero, metal, ojos con coat), `rbox`, `torus`, `tube`, `shell_cut` (párpados) y estudio de render.
- `art/blender/flecha.py`: Flecha completa con jerarquía de rig (`root/body/head/armL/armR/legL/legR`). Uso: `python flecha.py -- hero --norender` genera `flecha.blend`.
- `art/blender/shoot.py`: render de estudio de un `.blend`. Uso: `python shoot.py -- flecha.blend salida.png agx 900` (variantes `agx`, `std` y sufijo `t` para fondo transparente). **AgX Punchy es el look elegido.**
- Render actual: `art/renders/flecha_v2.png`.

### Pendiente con Flecha (crítica de dirección de arte)

1. La boca sigue leyéndose como un grito oscuro: mostrar la fila de dientes delante, hueco menos alto y sonrisa con las comisuras subidas.
2. La capucha parece un casco redondo: ajustarla, con caída sobre los hombros y que se vea más pelo.
3. Pose más dinámica para la foto promocional (como las referencias): mano en la cadera o pulgar arriba, peso en una pierna.
4. Opcional: dedos más definidos y nudillos.

### Siguientes pasos

1. Cerrar a Flecha y modelar los otros 7 héroes con la misma técnica: Brasa (dragón), Sombra (ninja), Muro (gólem), Ojo (búho), Truco (zorro), Rayo (mago) y Bum (bomba).
2. Renders Cycles con fondo transparente como retratos de los menús, sustituyendo a `GFX.PORTRAIT`.
3. Exportar cada héroe a GLB (diezmado a unas 15-30 mil caras, nodos con los nombres del rig) para el juego. Hace falta GLTFLoader: empaquetar Three.js y GLTFLoader en un IIFE con esbuild (npm funciona), sustituyendo a `vendor/three.min.js`. Cargar los GLB y mapear los nodos del rig para reutilizar `GFX.animate`.
4. Después: arenas distintas según los trofeos, ajustes de jugabilidad, y empaquetado para App Store (Capacitor) y escritorio (Electron), con `window.AMAGO_SERVER` para el online.

## Nuevo flujo de personajes (sustituye al modelado a mano)

1. Imagen de concepto con Gemini (prompts en la conversación; estilo común + descripción del héroe) → `art/concepts/<id>.jpg`.
2. Imagen → modelo 3D con TRELLIS (licencia MIT): web de Hugging Face (1-2 al día) o en lote con el cuaderno de Kaggle `art/kaggle/amago_trellis.ipynb` (GPU T4 gratis; se lanza con `!wget ... && %run`). El cuaderno usa el PyTorch de Kaggle, sustitutos propios de xformers y kaolin (`art/kaggle/shim`), nvdiffrast 0.4 y `CUMM_DISABLE_JIT=1`.
3. En Blender: `glb_view.py` (normaliza y revisa vistas), `glb_hero.py` (render promocional; con `t` fondo transparente), `portrait_crop.py` (retrato cuadrado webp) y `glb_game.py` (versión ligera de unas 30 mil caras y texturas de 1024).
4. Juego: copiar a `models/<id>.glb` y `portraits/<id>.webp` y añadir el id a `MODEL_LIST` en `GFX`. Si un héroe no tiene modelo se usa el procedural.

Hecho: Flecha integrado (inicio, selección, arena y retratos). Pendientes de modelo: Brasa, Sombra, Ojo, Truco, Muro, Rayo y Bum (imágenes ya en `art/concepts`).

## Notas del entorno

- Las CDN (cdnjs, jsdelivr) y blender.org están bloqueadas desde el contenedor; PyPI y npm funcionan.
- Las pruebas de navegador usan Playwright con `--use-gl=swiftshader`.
