# Auditoría A: visuales de arena y partida (AMAGO)

Alcance: lo que se ve dentro de la partida. Es una auditoría de solo lectura: no se ha tocado el repositorio.
Fuentes: `amago/index.html` (GFX ~1898-2563, B3 2567-3036, HUD 4494-4545, CSS 150-730), capturas `qa/base_en/60-75`, `qa/base/` y capturas propias en `audit/vis_game/` (`pra_board`, `pra_hero_close`, `pra_warn`, `pra_hit`, `pra_myshot`, `pra_myimpact`, `pra_sudden`, `pra_ko`, `pra_ko2`, `pra_vs`). Todas a 390×844 y DPR 2-3, con swiftshader.

## Diagnóstico general

La base es sólida. La arena horneada se ve limpia, los héroes tienen animaciones prerenderizadas (`anim3dHero`), el HUD sigue el estilo de los menús y los avisos de peligro son muy legibles. La sensación de «barato» frente a Brawl Stars o Clash Royale viene sobre todo de seis cosas:

1. **Iluminación plana.** El renderer de la arena va sin tone mapping (`setupRenderer(keepR)` → `NoToneMapping`). Las casillas son casi emisivas (`emissiveIntensity:.45` con `emissiveMap` = la propia textura). El terreno es `MeshBasicMaterial` con color por vértice. Todo queda al mismo brillo y no se distingue lo importante.
2. **La cámara desperdicia la pantalla.** Mi isla verde, que casi siempre está vacía, ocupa ~40 % del alto. La isla rival, que es donde se juega, ocupa ~25 %.
3. **Héroes que se ven como pegatinas.** No tienen sombra de contacto real: solo un blob al 28 %. Se dibujan con `depthTest:false`, así que tapan todo. Si te apuntan, quedan al 50 % de opacidad y parecen fantasmas. Son demasiado grandes para su casilla.
4. **VFX pobres.** Los proyectiles son esferas sin forma, las partículas son `Points` cuadrados y los impactos son anillos planos y pequeños. El K.O. no tiene un momento propio.
5. **Superposiciones a pantalla completa demasiado fuertes.** En muerte súbita y en peligro, todo el canvas se tiñe de rojo y la escena pierde lectura.
6. **Entorno vacío y repetitivo.** Agua plana, espuma estática, cielo de dos colores sin horizonte, «niebla» invisible y una arena (bosque) sin props.

---

## Hallazgos

### A1 · ALTO · Sin tone mapping ni gradación de color en la arena
- **Captura:** `63_partida.png`, `pra_board.png`
- **Problema:** `build()` (l. 2716) llama a `GFX.setupRenderer(keepR)` sin `tm`, así que la arena se renderiza con `NoToneMapping`. El escaparate del inicio (l. 3094) usa ACES con exposición 1.05, y por eso menú y partida no casan. Los blancos se queman: el halo de los proyectiles y el destello `setRGB(3,3,3)` se ven planos. Los verdes salen saturados sin control. El parche actual es `filter:saturate(1.1) contrast(1.04)` en `#gl` (l. 411), que además es caro en iOS porque obliga a componer el canvas.
- **Arreglo:** usar `GFX.setupRenderer(keepR,'aces')` con `toneMappingExposure≈1.1`. Quitar el `filter` de `#gl` y pasar la gradación al shader. En los materiales que deban saltarse el tone mapping (héroes, iconos y HUD 3D) mantener `toneMapped:false`. Después, reequilibrar la luz (A2), porque ACES oscurece los medios tonos.

### A2 · ALTO · La luz no separa el tablero del entorno
- **Captura:** `63_partida.png`
- **Problema:** `lights()` (l. 2535) suma `HemisphereLight` 1.15, fill 0.9, key 2.1 y un rim de 2.2 que viene de detrás. Pero el terreno es `MeshBasicMaterial` (`detailMat`, l. 2628) y no recibe ninguna de esas luces, y las casillas son casi autoiluminadas. Resultado: el tablero, el fondo y los árboles tienen la misma luminancia y nada lleva la mirada a la zona de juego.
- **Arreglo:** hacer una «luz de escenario». Multiplicar el color de `detailMat` por una viñeta en espacio mundo: `diffuseColor.rgb *= mix(.72,1.,smoothstep(9.,4.,length(vWp.xz*vec2(1.,.6))))`. Así el entorno lejano baja ~25 % de brillo y los tableros quedan como un foco. Subir el key a 2.6 con un tono cálido `0xfff1d6` y bajar el hemisferio a 0.8 con suelo `0x5a7a9a`, más frío, para tener contraste cálido/frío como Supercell.

### A3 · ALTO · Casillas casi emisivas: sin volumen ni bisel real
- **Captura:** `pra_board.png`, `63_partida.png`
- **Problema:** l. 2748: `MeshLambertMaterial({map:tx,emissive:0xffffff,emissiveMap:tx,emissiveIntensity:.45})`. Casi la mitad del color es emisivo, así que el bisel de `TILE_GEO` (`rbox(.96,.3,.96,.07,5)`) apenas se nota. El «bisel» pintado en `tileTex` (líneas a 12 px) no casa con el bisel geométrico. Las casillas se ven como pegatinas lisas.
- **Arreglo:** bajar `emissiveIntensity` a .15 y pasar a `MeshStandardMaterial({roughness:.75,metalness:0,envMapIntensity:.6})`, porque ya existe `sc.environment` (`envFor`). Activar `castShadow` en las casillas solo con `shadowMap.autoUpdate=false` y una actualización por ronda, porque las casillas no se mueven salvo el bump. Quitar las dos líneas de bisel pintadas en `tileTex` (las de `g.lineWidth=12` y `10`) y dejar que la geometría haga el trabajo. Añadir un AO de contacto entre casillas: una franja oscura en el `bed` (l. 2742) con un `MeshBasicMaterial` `0x0e2a0a`, que ya existe, pero bajando las casillas 1 cm.

### A4 · ALTO · La cámara reparte mal la pantalla: mi isla vacía ocupa el 40 %
- **Captura:** `63_partida.png`, `62_escondete.png`
- **Problema:** `fitCamera()` (l. 2767) encaja los dos tableros enteros con `dir=V(0,1,.82)` y `tgt=V(0,0,-.15)`. En perspectiva, mi tablero, que está más cerca, sale casi el doble de grande que el rival. Pero el jugador apunta a la isla roja, donde las casillas miden ~100 px frente a ~125 px de las verdes. Brawl Stars y Clash Royale inclinan más la cámara y la centran en la zona de interacción.
- **Arreglo:** usar una cámara más cenital y con tele: `fov 30` en vez de 40, `dir=V(0,1,.55)` y `tgt=V(0,0,-.6)`. Con eso las dos islas quedan casi iguales. Probar también a recortar las esquinas de `corners` con `z=+5.2` en mi lado: la última fila verde puede tocar la barra de elixir. La meta es que las casillas rivales midan ≥115 px de ancho en 390 px.

### A5 · ALTO · Héroe sin anclaje: sombra débil y `depthTest:false`
- **Captura:** `pra_hero_close.png`, `63_partida.png`
- **Problema:** l. 2440: `mat.depthTest=false` con `renderOrder=6`. El héroe se dibuja encima de todo, incluido el puente y la cuerda (en `pra_hero_close` la cuerda del puente queda detrás de la cabeza pero «delante» del cuerpo). La única sombra es un `CircleGeometry(.36)` al 28 % (`blob`, l. 2764), que el anillo azul tapa. Parece flotar sobre la casilla.
- **Arreglo:** sustituir el blob por una sombra con textura radial (reutilizar `glowTex()` con color `0x000000`, mezcla normal, opacidad .55 y escala `(.9,.5)`) colocada debajo del anillo. Hacer que la sombra se estire en los saltos: escala `1-R.y*2` en `animateSprite` y `animate3d`. Volver a activar `depthTest:true` con un desplazamiento: `polygonOffset` o mover la carta `+0.15` hacia la cámara en `onBeforeRender`. Así los pies no se cortan y los props sí ocultan al héroe.

### A6 · ALTO · El héroe es demasiado grande y se sale de su casilla
- **Captura:** `63_partida.png` (Brasa en (0,0) invade la isla rival y el borde de la isla), `pra_ko.png`
- **Problema:** `HERO_K=1.18` × `HSCALE=1.02` × `1.12`: Brasa mide ~1,4 casillas de ancho y tapa 2-3 casillas vecinas, justo las que el jugador tiene que tocar para huir. En la fila delantera tapa también la fila trasera del rival.
- **Arreglo:** bajar `HERO_K` a ~1.0. Para compensar la legibilidad, añadir un contorno de equipo: un segundo mesh detrás de la carta con la misma textura, `color` azul o rojo, escala 1.06 y `alphaTest` (contorno por silueta). Clash Royale distingue los equipos por color, no por tamaño.

### A7 · ALTO · Mi héroe se vuelve fantasma al 50 % cuando me apuntan
- **Captura:** `pra_warn.png`
- **Problema:** l. 2900: `hero.userData.mat.opacity=inc.some(...)?.5:1`. Justo en el momento de más tensión, mi personaje se ve lavado y sin peso. Además ya hay otras tres señales a la vez: casillas rojas, `dangerv` y texto.
- **Arreglo:** mantener la opacidad a 1. Para que se vea el aviso de debajo, dibujar el anillo y la `⚠️` de esa casilla con `renderOrder 7` por encima del héroe y a un tamaño menor. Otra opción es hacer temblar al héroe (`R.x=sin(t*40)*.01`) con un tinte rojo pulsante (`u.mat.color.setRGB(1,.6+.4*sin(t*16),.6)`), que comunica «estás en peligro» sin quitarle cuerpo.

### A8 · ALTO · Muerte súbita y peligro tiñen de rojo toda la escena
- **Captura:** `pra_sudden.png`, `pra_ko.png`, `70_muerte_subita.png`
- **Problema:** `body.sudden .g3::after` (l. 722), con `inset 0 0 70px 10px rgba(255,60,30,.45)`, más `.dangerv` (l. 719), con `36px 6px .7`. En 390 px de ancho, el resplandor rojo cubre ~25 % de cada lado y todo el campo queda en un tono rosa sucio: casillas verdes apagadas y botones morados. El jugador pierde lectura justo cuando más la necesita.
- **Arreglo:** muerte súbita: dejar el borde en `inset 0 0 28px 4px rgba(255,50,30,.35)` y pasar el resto del ambiente al 3D. Teñir el cielo con `scene.background=skyTex(["#5a1030","#ff7a4a"])`, poner `HemisphereLight.color` en `0xffc0a0` y hacer chispas o ascuas cayendo (ver A20). Peligro: un borde solo arriba y abajo de 8 px, sin cubrir las casillas.

### A9 · ALTO · Proyectiles sin forma ni personalidad
- **Captura:** `pra_myshot.png`, `64_mi_disparo.png`
- **Problema:** `PROJ_MAKERS` (l. 2817): la bola de fuego son dos esferas (`0xffd27a` y `0xff6b3d` al 55 %) y el ojo es una esfera amarilla. La flecha mide 0,6 de largo, con un astil de 0,025 que a esta distancia ocupa 1-2 px. La estela es `burst()` de 3 `Points` cuadrados. A la distancia de la cámara apenas se ve un punto con halo.
- **Arreglo:** construir cada proyectil con 3 capas de sprites aditivos: núcleo blanco, halo del color del héroe y estela. La estela puede ser una tira (`TubeGeometry` de 12 segmentos, o un `Mesh` de cinta reconstruido con las últimas 10 posiciones) con degradado de alfa y `AdditiveBlending`. Subir la escala de los proyectiles ×1.6. La flecha necesita una estela de cinta blanca muy visible y un `glowSprite` del doble de tamaño. Rotar la bola de fuego y añadir 2-3 «lenguas» (sprites alargados orientados según la velocidad).

### A10 · ALTO · Impacto pequeño y plano: no hay *game feel*
- **Captura:** `65_impacto.png`, `pra_myimpact.png`
- **Problema:** `impactFx()` (l. 2867): 24 `Points` de tamaño .14 (cuadrados, porque `PointsMaterial` no lleva `map`), un anillo `RingGeometry(.2,.32)` que crece ×5 en .5 s, un halo de .6 y una quemadura al 32 %. En la captura, 1,2 s después ya no queda nada más que manchas grises. No hay *hitstop*, destello de pantalla, *debris* ni números grandes con rebote.
- **Arreglo:**
  - Darle a `PointsMaterial` un `map` redondo (`dustTex`) con `AdditiveBlending` y `sizeAttenuation`, y tamaños de .25 a .35.
  - Añadir un destello: un plano aditivo del área de impacto en blanco, opacidad 1→0 en 120 ms.
  - Añadir una onda de choque doble: anillo grueso rápido más anillo fino lento, con textura degradada y no con `RingGeometry` plana.
  - Hacer saltar las casillas (`bump`) con caída escalonada a las vecinas.
  - Con TOCADO, congelar 70 ms (`SLOW.until` con `dt*=0`) y luego aplicar `shake`.
  - Quemadura con textura de grieta o salpicadura en vez de un círculo liso.

### A11 · ALTO · El K.O. no tiene un momento propio
- **Captura:** `71_ko.png` / `72_ronda_ganada.png` (al capturar ya está en la elección de la ronda 2), `pra_ko2.png`
- **Problema:** con K.O. solo hay cámara lenta de 650 ms (`SLOW`, l. 4244), un `floatText` «¡K.O.!» y `finalReveal`. No hay zoom, ni pantalla congelada, ni oscurecimiento del fondo, ni explosión de estrellas. `revealFoe` espera 2 s con la cámara fija y luego `roundBanner` es texto HTML sobre la escena.
- **Arreglo:** hacer una secuencia de K.O. en B3:
  1. *Hitstop* de 120 ms con destello blanco a pantalla completa (div al 60 % durante 80 ms).
  2. Interpolar la cámara hacia el perdedor durante 0,6 s: `cam.position.lerp(foePos+dir*6,…)` y `fov 40→28`.
  3. Atenuar el resto de la escena (plano negro al 40 % entre la cámara y el tablero, con el héroe en `renderOrder` superior).
  4. Lanzar 60-90 estrellas o monedas con `burst` texturizado, más el anillo dorado.
  5. Volver a la cámara base antes del banner.

  Todo en `finalReveal()`/`update()` con un estado `koCam`.

### A12 · MEDIO · Agua plana y sin profundidad
- **Captura:** `63_partida.png` (franjas turquesa entre islas y laterales)
- **Problema:** l. 2723: el agua es un `PlaneGeometry(80,80)` `MeshBasicMaterial` con `agua.webp` repetida 16× y desplazada en x a .012/s. No tiene variación de profundidad ni brillos ni reflejo de las islas, y la orilla es un corte duro donde el agua toca la base del GLB.
- **Arreglo:** un `ShaderMaterial` barato con dos muestreos de `agua.webp` a escalas y direcciones distintas (`uv*1.0+t*.01`, `uv*1.7-t*.013`) mezclados, más un degradado de profundidad: más claro cerca de las islas, a partir de la distancia a los dos rectángulos (SDF de cajas redondeadas en el fragment shader) y más oscuro lejos. Añadir brillos con `pow(noise,8)` aditivos. Coste: un solo pase y sin texturas nuevas.

### A13 · MEDIO · Espuma estática y difuminada
- **Captura:** `63_partida.png`
- **Problema:** l. 2726-2733: espuma de canvas con `blur(6px)`, un solo trazo y una pulsación global de opacidad (`.6+sin*.2`). Se ve como un halo borroso y no como espuma de dibujo animado (en Brawl o Clash Royale son bandas blancas nítidas que avanzan y retroceden).
- **Arreglo:** dibujar 2-3 contornos concéntricos nítidos (sin `blur`, `lineWidth` 5/3/2) y animarlos en el shader con un desplazamiento hacia fuera: `alpha*=step(.5,fract(dist*3.-t*.4))`. También vale una textura de bandas con `offset` animado en dirección normal a la costa. Mantenerla en un plano.

### A14 · MEDIO · Cielo y horizonte vacíos
- **Captura:** `63_partida.png` (franja superior detrás del HUD)
- **Problema:** `skyTex` es un degradado de 2 colores. Como la cámara está muy inclinada, casi no se ve. Lo que sí se ve, detrás del HUD, es una colina verde con árboles sin capas de profundidad. No hay perspectiva atmosférica: `scene.fog` no existe en la arena (`fitCamera` lo ajusta solo «si existe», l. 2780, pero en `build()` nunca se crea).
- **Arreglo:** crear `scene.fog=new T.Fog(theme.sky[1], d+8, d+26)` para que los props lejanos (z<-7) se aclaren hacia el color del cielo. Activar `fog:true` en los `MeshBasicMaterial` de los props, que lo admiten. Así se gana profundidad de forma inmediata.

### A15 · MEDIO · La «niebla» del tablero rival no se ve
- **Captura:** `63_partida.png` (no se aprecia)
- **Problema:** l. 2761: 9 esferas blancas al 6 % de opacidad. Son invisibles en un móvil, aunque deberían ser la metáfora visual central del juego (el rival está escondido).
- **Arreglo:** sustituirlas por 6-8 sprites con `puffTex()`, que ya existe en l. 3038, al 25-35 %, a la deriva lenta sobre la isla roja y a la altura de las rodillas del héroe (y≈.3). Cuando haya visión (`me.visionUntil`) o un K.O., alejarlas o apagarlas. Así el «oculto o revelado» se lee al instante.

### A16 · MEDIO · Isla rival con textura de piedra salmón: rompe el tema y baja la legibilidad
- **Captura:** `63_partida.png`, `pra_board.png`
- **Problema:** l. 2747: el rival siempre usa `[0xf08a6a,0xe07458]` con `stone=true`. En Pradera, una isla de baldosas salmón junto a otra de césped parece de otro juego. El tablero de ajedrez es casi invisible en las dos islas: la diferencia de luminancia entre odd y even es ~4 %.
- **Arreglo:** usar el mismo material del tema en las dos islas y marcar el bando con un tinte rojizo (mezcla de `theme.tile` con `0xff6a5a` al 25 %) más el marco rojo, que ya existe. Subir el contraste del tablero de ajedrez a ~10-12 % de luminancia (por ejemplo `0x8ade52`/`0x6cc23e`). Clash Royale y Brawl usan un tablero suave pero perceptible.

### A17 · MEDIO · Las casillas rivales se oscurecen en cuanto no puedes disparar
- **Captura:** `62_escondete.png`, `64_mi_disparo.png` frente a `63_partida.png`
- **Problema:** l. 2930: `else{dc=0x1a0a20;dop=.38;}` mete un velo morado oscuro al 38 % sobre las 25 casillas rivales cada vez que falta elixir o hay recarga. La isla pasa de luminosa a «apagada» varias veces por segundo y el efecto se lee como un fallo de iluminación, no como «no puedes disparar».
- **Arreglo:** bajar a `dop=.12` y desaturar con el shader del material (uniform `uDim`) en vez de superponer un plano. El estado «no puedo disparar» ya lo comunica la barra de elixir. Como alternativa, apagar solo el borde de la isla.

### A18 · MEDIO · Los avisos sobre mi isla son planos y sin calidad
- **Captura:** `pra_warn.png`
- **Problema:** el aviso es el plano `dec` en rojo `0xff1030` a .75 más una `⚠️` emoji como sprite y un anillo blanco. Es muy legible, pero se ve plano, como una baldosa de debug, y depende de la fuente emoji del sistema.
- **Arreglo:** usar una textura de canvas propia (rayas diagonales rojas y amarillas tipo «peligro», con borde redondeado y alfa en el centro) desplazada en el tiempo, y una cuenta atrás radial que se llena (ya existe `ringGeo`). Añadir una sombra del proyectil que se agranda sobre las casillas objetivo según se acerca el impacto (círculo negro de .3 a 1 de escala, del 10 % al 40 % de opacidad). Es el lenguaje de Brawl Stars para el área de impacto.

### A19 · MEDIO · Partículas cuadradas en todo el juego
- **Captura:** `pra_myimpact.png`, `65_impacto.png`
- **Problema:** `burst()` (l. 2850) usa `PointsMaterial` sin `map`: con tamaños de .12 a .18 los puntos son cuadrados. Se usan en la estela, el impacto, la recogida de objetos y el K.O.
- **Arreglo:** un `map` circular compartido (`glowTex()`), `alphaTest:.01`, `AdditiveBlending` para las chispas y normal para los restos. Atributo de tamaño por partícula con `onBeforeCompile`: `gl_PointSize *= aSize*(1.-vLife)`. Coste mínimo.

### A20 · MEDIO · No hay partículas ambientales: el escenario se siente muerto
- **Captura:** `63_partida.png`
- **Problema:** lo único que se mueve en reposo son el balanceo de los árboles (±0,025 rad) y unas rayas blancas en el agua. Los juegos de Supercell siempre tienen motas, hojas o polen en el aire.
- **Arreglo:** un único `Points` con 40-60 partículas por tema (Pradera: pétalos o polen; Volcán: ascuas que suben; Trono: chispas mágicas; Olimpo: destellos dorados), animado en el vertex shader con `uTime`, así que la CPU no hace nada. 1 draw call.

### A21 · MEDIO · Bosque sin props y arenas poco diferenciadas
- **Captura:** no capturada (requiere 100-249 trofeos); se deduce de `PSET` (l. 2661)
- **Problema:** `PSET` no tiene `bosque`, así que esa arena solo muestra el GLB horneado. Pradera y Bosque comparten árboles del GLB y la misma textura de casillas con un verde un poco distinto.
- **Arreglo:** reutilizar `pino`/`arbol`/`rocas` con otra escala, más densidad y un tinte (`mat.color=0x7fbf8a`) para crear `PSET.bosque`. Darle a Bosque `fog` verdosa y partículas de hojas. Sin arte nuevo.

### A22 · MEDIO · Props de cartón frontal: se nota que son planos
- **Captura:** `63_partida.png` (árboles grandes al fondo)
- **Problema:** `addProps` (l. 2692) orienta las cartas por completo a la cámara (*billboard* esférico). Con la cámara inclinada a ~50°, los árboles se inclinan hacia atrás y sus bases «flotan» sobre la sombra (en la captura la sombra se ve desplazada). El balanceo es una rotación z de la carta entera, sin deformar la copa.
- **Arreglo:** *billboard* cilíndrico (solo eje Y: `card.rotation.y=atan2(cam.x-g.x,cam.z-g.z)`), que mantiene los troncos verticales y apoyados. Para el balanceo, aplicar en el vertex shader `pos.x+=sin(t+seed)*.04*uv.y²`, de modo que solo se mueva la copa. Usar sombra con textura radial (igual que A5).

### A23 · MEDIO · Barra superior: corazones pequeños y contadores sin jerarquía
- **Captura:** `63_partida.png`, `pra_ko.png`
- **Problema:** `.g3hud .hearts i{font-size:15px}` (l. 616) se reduce hasta 10,5 px con 8 vidas. Los corazones vacíos (`#1a1f45` al 55 %) se confunden con el fondo azul del panel. Las estrellas de la ronda (`.stars .off #2a2f55`) son casi invisibles bajo el reloj. El retrato del rival repite el del propio jugador cuando ambos usan el mismo héroe (`pra_ko`: Brasa contra Brasa) y nada distingue los bandos salvo el color del panel.
- **Arreglo:**
  - Corazones a 20 px fijos. Si hay más de 5, usar el formato «❤ ×6» o una barra segmentada.
  - Corazones vacíos con contorno blanco al 40 % y relleno `#0b0a1f`.
  - Pérdida de corazón con animación (`scale 1.6→1` y fragmentos con `burst` HTML).
  - Estrellas con fondo de cápsula oscura `rgba(0,0,0,.35)` y tamaño de 20 px.
  - Retratos: aro de color de equipo de 3 px y volteo horizontal del rival (`transform:scaleX(-1)`) para que se miren.

### A24 · MEDIO · Banner de estado ancho, en dos líneas y cambiante
- **Captura:** `68_amago_armado.png` (dos líneas y casi 100 % de ancho), `63_partida.png`
- **Problema:** `.status span` (l. 155 y 449) con 17 px y color de fondo distinto según el estado (`warn`, `bad`, `good`, `decoy`). Con textos largos ocupa dos líneas y empuja el hueco del tablero. Como `fitCamera` mide `.status`, la cámara salta al cambiar el texto. Los colores `good` (`#0f4a33`) y `warn` (`#5b3608`) son oscuros y apagados frente al estilo del resto del HUD.
- **Arreglo:** limitar a una línea (`white-space:nowrap;max-width:92vw;text-overflow:ellipsis`), acortar los textos y fijar una altura reservada en `fitCamera` (por ejemplo siempre 44 px) para que la cámara no salte. Paleta saturada con biselado como los botones: verde `linear-gradient(#3ee08a,#13a35a)`, ámbar `#ffb02e→#e07800`, rojo `#ff5a6e→#c4162d` y morado como `.amagob`. Cada cambio de estado con un `pop` de 180 ms.

### A25 · MEDIO · Barra de elixir genérica, sin efecto al recargar ni al gastar
- **Captura:** `63_partida.png`, `62_escondete.png`
- **Problema:** `.esegs i b` (l. 278) es un degradado azul plano. El segmento de coste lleva un borde dorado que se confunde con la selección. No hay brillo al completar un segmento ni un vaciado animado al gastar. En Clash Royale, la barra de elixir es el centro emocional del HUD: rosa, con brillo y con la cifra en una gota.
- **Arreglo:**
  - Color del elixir con reflejo: `linear-gradient(#d68bff,#9b3ce0)` con una franja blanca `inset 0 3px 0 rgba(255,255,255,.5)`, o el azul actual más saturado.
  - Destello al completar: añadir la clase `.full` 200 ms después de que `width` llegue al 100 %, con `@keyframes` de brillo.
  - Al gastar: los segmentos consumidos se vacían de derecha a izquierda con `transition:width .25s`.
  - La cifra `elxn` dentro de una gota de 40 px.
  - Las marcas de coste como muesca con un icono de habilidad encima del segmento y no como borde.

### A26 · MEDIO · Botones de acción que no parecen botones
- **Captura:** `63_partida.png` (fila inferior)
- **Problema:** `.gbottom .acts .act:not(.amagob)` (l. 717) son cápsulas `rgba(8,12,40,.62)` de 14 px que solo informan del coste (👟1, bola de fuego 5). El único botón real es «amago». La fila desperdicia ~60 px del borde inferior, la zona más cómoda para el pulgar. El `background:linear-gradient(transparent,rgba(11,10,31,.6) 35%)` de `.gbottom` ensucia la última fila de casillas.
- **Arreglo:** convertir la fila en una «mano» de 2-3 cartas grandes, como en Clash Royale: 64×74 px con el icono del patrón (`patIcon`), el coste en una gota en la esquina y un estado «listo» con brillo. La de ataque puede indicar que se toca la isla. Quitar el degradado oscuro de `.gbottom` o reducirlo a 20 px.

### A27 · MEDIO · Los textos flotantes (−1, AGUA, TOCADO) no se leen
- **Captura:** `66_aviso.png` («−1» sobre el pecho de Brasa, casi invisible), `65_impacto.png`
- **Problema:** `.ftxt` (l. 187): 26 px, color `--foe` sobre un héroe rojo y sin contorno grueso. Aparece justo en la posición del héroe (`heroScreen` con y=.8), así que queda detrás o encima del personaje con poco contraste.
- **Arreglo:** salir 40 px por encima de la cabeza (`heroScreen` con `y=h+.3`). Fuente de 34-44 px con `-webkit-text-stroke:3px var(--ink)` y `paint-order:stroke`. Animación en tres tiempos: *pop* de 0,6→1,25→1 en 150 ms, subida y desvanecido. Daño recibido en blanco con contorno rojo, daño hecho en amarillo. Añadir un pequeño rebote lateral aleatorio para que no se apilen.

### A28 · MEDIO · El amago armado oscurece toda mi isla con un morado sucio
- **Captura:** `68_amago_armado.png`
- **Problema:** l. 2950: con `G.decoyArm`, cada casilla menos la mía recibe un velo `0xb06bff` al 28-40 % con pulso. Sobre un verde saturado, el resultado es un gris verdoso apagado y no transmite «modo especial».
- **Arreglo:** mantener las casillas a plena luz y marcar las seleccionables con un borde morado brillante animado (anillo `ringGeo[20]` en `0xd08bff` con opacidad pulsante) y una huella fantasma 🎭 al 35 % sobre cada una. Oscurecer solo el resto de la escena con un plano negro al 25 % sobre la isla rival, para enfocar.

### A29 · BAJO · No hay pantalla VS dentro de la arena
- **Captura:** `61_vs.png`, `pra_vs.png` (ya se ve la arena y el texto «Escóndete»)
- **Problema:** la tarjeta VS (`vssheet`, l. 3876) es un modal HTML que dura poco. La partida empieza sin presentación de los héroes en el escenario. En Brawl Stars, cada partida empieza con un barrido de cámara y los luchadores en pose.
- **Arreglo:** durante `R.paused` (la «preparación»), hacer en B3 un *dolly* de 1,2 s desde arriba (`cam fov 50→40`, posición de `d+6` a `d`) con el héroe en animación `win` y un anillo de aparición (`shock` grande), más un `banner` «¡ESCÓNDETE!» con *pop*. Usa solo `update()` y `fitCamera()`.

### A30 · BAJO · Animación de caminar: el héroe se desliza
- **Captura:** se ve en movimiento (código l. 2888-2891)
- **Problema:** el héroe avanza en línea recta a velocidad constante (`spd=1/Hm.step*1.05`) sin aceleración ni frenada y gira con `dt*12`. Con 10 fotogramas de `walk` a 15 fps, los pies resbalan.
- **Arreglo:** usar *ease-out* en el tramo (`mv=Math.min(dist,spd*dt*(.6+.8*Math.min(1,dist)))`), un pequeño salto parabólico por casilla (`hero.position.y=sin(progreso·π)*.12`) y aplastar y estirar al aterrizar. Es el estilo de movimiento por casillas de Clash o Squad Busters y oculta el deslizamiento.

### A31 · BAJO · Iconos sobre casillas con emoji del sistema (💧 ⚡ 👁 ⚠️)
- **Captura:** `63_partida.png` (gotas), `pra_warn.png` (ojo y ⚠️)
- **Problema:** `iconTex()` (l. 2577) dibuja emojis con la fuente del sistema. En iOS se verán como Apple Emoji y en Android de otra forma, sin el contorno grueso del estilo del juego y mezclados con los iconos 3D de `ui/*.webp`.
- **Arreglo:** cuando exista un `ui/<nombre>.webp`, cargarlo como textura. Si no, dibujar en el canvas un contorno de pegatina: `g.shadowColor='#0b0a1f'` con 8 trazos desplazados 3 px antes del emoji, o `strokeText` en `--ink`. Añadir un disco de fondo claro bajo el icono para separarlo de la casilla.

### A32 · BAJO · Anillos de selección y héroe finos y planos
- **Captura:** `63_partida.png` (anillo azul bajo Brasa, anillos amarillos de objetos)
- **Problema:** `RingGeometry(.32,.42)` en `MeshBasicMaterial` plano. Con la perspectiva, el anillo queda tapado casi por completo por el propio héroe. Los anillos amarillos de los objetos, tipo cuenta atrás, son del mismo grosor y compiten con él.
- **Arreglo:** usar un disco con textura degradada (borde brillante, centro transparente al 25 %) para el héroe, y para el rival el mismo en rojo con un giro lento de rayas. Los anillos de cuenta atrás de los objetos, con un grosor de .05 para jerarquizarlos.

### A33 · BAJO · `prWatch` baja la resolución pero no los efectos
- **Captura:** no aplica (rendimiento)
- **Problema:** l. 2788: la única palanca de calidad es el `pixelRatio`, hasta 1,5. Las sombras PCFSoft de 2048² (l. 2539) se recalculan cada fotograma aunque solo se mueven 2 héroes y no proyectan sombra (`castShadow` no se activa en las cartas). Es coste sin beneficio, y el presupuesto liberado podría ir a los VFX de A9-A11 y A20.
- **Arreglo:** `rnd3.shadowMap.autoUpdate=false` y `needsUpdate=true` solo al construir. Mejor aún, desactivar `shadowMap` en la arena (la luz ya está horneada en el GLB) y usar sombras de contacto falsas (A5 y A22). Añadir niveles de calidad: con `prNow<=1.5`, reducir partículas ambientales y estelas a la mitad.

---

## Top 10 de mayor impacto (calidad percibida por esfuerzo)

1. **A1 + A2. Tone mapping ACES y luz de escenario** (viñeta en el terreno y contraste cálido/frío). Es un cambio de pocas líneas que lo arregla todo a la vez: color, profundidad y foco en el tablero.
2. **A10. Impactos con *game feel*** (*hitstop*, destello, doble onda de choque, partículas redondas, rebote de casillas en cadena). Es lo que más separa un juego hecho a mano de uno de Supercell.
3. **A11. Secuencia de K.O. con cámara** (*zoom*, atenuación de la escena y explosión de estrellas). Es el momento más memorable de la partida y ahora no existe.
4. **A4. Reencuadrar la cámara** (más cenital, `fov` más cerrado y centrada en la isla rival). Las casillas que se tocan crecen ~20 % y la isla vacía deja de dominar la pantalla.
5. **A9. Proyectiles con estela de cinta y capas aditivas.** Hace que cada disparo se lea y se disfrute.
6. **A5 + A6 + A7. Anclar a los héroes** (sombra radial, *depth test*, tamaño 1.0 con contorno de equipo y sin opacidad del 50 %).
7. **A8. Quitar el lavado rojo de pantalla completa** en muerte súbita y peligro, y pasar el ambiente al 3D (cielo, luz, ascuas).
8. **A3 + A16. Casillas con volumen real** (Standard con env, menos emisivo) y la misma familia de material en las dos islas, con un tablero de ajedrez legible.
9. **A25 + A26. Barra de elixir y «mano» de acciones al estilo Clash Royale**, con brillo al completar y botones grandes de pulgar.
10. **A12 + A13 + A14 + A20. Entorno vivo** (agua con shader de dos capas y profundidad, espuma en bandas animadas, `scene.fog` real y partículas ambientales por tema en 1 draw call).

## Notas de rendimiento

- Todo lo propuesto se hace sin posprocesado: sprites aditivos, shaders en `onBeforeCompile` y una textura de canvas por efecto.
- Lo que se ahorra quitando la actualización de `shadowMap` por fotograma (A33) y el `filter` CSS del canvas (A1) paga de sobra las partículas ambientales y las estelas.
- Mantener el límite de `prWatch` y añadir un nivel de calidad «bajo» que reduzca a la mitad las partículas.
