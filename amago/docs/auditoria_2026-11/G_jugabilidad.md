# AMAGO: auditoría de jugabilidad, sensación de juego y corrección del motor

Área: reglas del motor, kits de héroe, bot, tutorial, ritmo, entrada táctil, feedback, casos límite, online y reglas de arena.
Auditoría de solo lectura: no se ha tocado ningún fichero del repositorio.

## Método

- Lectura completa del motor (`index.html:1109-1441`, entre `ENGINE-START` y `ENGINE-END`), del cliente de partida (`index.html:2800-2990`, `3950-4750`) y de `server/server.js`.
- Simulación en Node con el motor extraído igual que lo hace el servidor (`new Function(bloque ENGINE)`). Para enfrentar bot contra bot añadí una copia en espejo de `botUpdate` que juega como "p". Scripts en `/tmp/claude-0/-home-user-maker-portfolio/89a0f5ca-c3e1-53ff-85f7-17ada0218752/scratchpad/gsim/` (`eng.js`, `duel.js`, `demos.js`, `curve.js`, `noelx.js`, `cam.js`).
- Las cifras de duelo salen de 600 a 2.500 rondas por caso, con el bot "Normal" en los dos lados salvo que se diga otra cosa. La línea base del espejo Flecha contra Flecha da 51,9 % / 47,8 %, así que hay un margen de ruido de unos ±2 puntos.

## Resumen

| id | sev. | título |
|---|---|---|
| G1 | crítico | Online: salir un momento de la app (iOS) acaba en derrota: `resume` falla si el servidor aún no ha visto el corte |
| G2 | alto | La ruta en L es aleatoria y decide si esquivas un golpe |
| G3 | alto | En táctil no se ve el área del ataque antes de disparar; además el 2×2 está anclado arriba a la izquierda |
| G4 | alto | Enfrentamientos de 88/12 con la elección a ciegas (Sombra frente a Brasa, Muro y Mira) |
| G5 | alto | Curva de dificultad: de Fácil a Normal la victoria por ronda cae del 45 % al 11 %, y Fácil deja de dar trofeos a 300 |
| G6 | alto | El amago de Mira se distingue: su huella falsa dura 2 s y la real 4 s |
| G7 | medio | Rayo no puede elegir la diagonal: 19 de 25 casillas dan la misma |
| G8 | medio | Truco y Sombra: el cliente pinta su huella como exacta y dice «disparó desde ahí» |
| G9 | medio | El bot no entiende a Truco: Truco gana un 58 % contra el bot y un 41 % contra un bot que sí lo entiende |
| G10 | medio | En Volcán, Trono y Olimpo el bot ignora la lava, la estatua y el viento: es más fácil justo donde debería apretar |
| G11 | medio | El texto de muerte súbita dice «Ataques sin aviso», pero el motor mantiene el aviso |
| G12 | medio | El amago sigue armado después de disparar: el toque siguiente pone una huella en vez de moverte |
| G13 | medio | En partida no hay pausa, salir ni rendirse; al volver de segundo plano no hay cuenta atrás |
| G14 | medio | Online: la cuenta atrás del cliente no coincide con la del servidor (rondas 2 y siguientes, y cargas lentas) |
| G15 | medio | Online: no hay bloqueo ni respuesta local al disparar; un segundo toque gasta otro disparo |
| G16 | medio | El bot enseña su héroe de la ronda 1 antes de que elijas (y online siempre enseña a Truco) |
| G17 | medio | Tutorial: el reloj corre mientras espera tus acciones (muerte súbita a los 45 s, empate a los 75 s) |
| G18 | medio | Casillas pequeñas en la isla roja (~38×26 pt en iPhone 14, ~28×19 en SE) y disparo inmediato al apoyar el dedo |
| G19 | bajo | Tutorial, ronda 2: si el amago queda en tu columna, Ojo no dispara pero dice «¡Ha picado!» |
| G20 | bajo | Cuando el bot se queda sin elixir, al jugador le sale «Sin elixir» y su barra tiembla |
| G21 | bajo | El bot aprende de los resultados de sus propios amagos (información que un humano no tiene) |
| G22 | bajo | Un aviso que cae sobre tu casilla nunca es un amago (el amago evita al rival) |
| G23 | bajo | Las acciones bloqueadas no dan respuesta (enfriamiento del disparo y toques en pausa o cuenta atrás) |
| G24 | bajo | Subir de nivel apenas se nota en partida (+1 % de elixir por nivel) y PROGRESO.md lo describe mal |
| G25 | mejora | Memoria de disparos en la isla roja (mapa que se apaga poco a poco) |
| G26 | mejora | Coste del camino a la vista y destinos a los que no llegas |
| G27 | mejora | Rastro del rival al final de cada ronda, no solo en la decisiva por K.O. |
| G28 | mejora | Indicador de viento que dure los 6 s y aviso previo de la ráfaga |

---

## Hallazgos

### G1 · crítico · Online: salir un momento de la app (iOS) acaba en derrota

**Evidencia**
- `index.html:1712` y `4749`: al pasar a segundo plano el cliente solo vacía analíticas y reinicia `lastT`. No avisa al servidor ni cierra el socket.
- `server/server.js:700-710`: el servidor solo detecta un socket muerto con el ping cada 20 s, así que tarda entre 20 y 40 s. Mientras tanto la ronda **no se pausa** (`onClose` en `477` no llega a ejecutarse) y el rival dispara a un objetivo quieto.
- Peor aún, `server.js:620-623`: al volver, el cliente ve el socket cerrado (`onclose` → `netLost` → `netResume`) y manda `resume`. Si el servidor aún no ha cerrado el socket viejo, `r.away[s]` no existe y responde `resumeFail`. El cliente entonces llama a `netGiveUp()` (`index.html:4393`) y muestra «No se pudo volver a la partida… cuenta como derrota».
- El socket viejo muere después por el ping, entra en `onClose`, espera 15 s de gracia y llama a `leave` con `rankedResult(ws,"lose")`. Resultado: derrota y pérdida de trofeos.

**Impacto en el jugador**
Una llamada, una notificación o un cambio rápido de app en una partida clasificatoria acaba casi siempre en derrota. Además, el rival pasa hasta 40 s disparando a un objetivo que no se mueve.

**Arreglo**
1. Cliente: añadir `document.addEventListener("visibilitychange",()=>{if(document.hidden&&G&&G.online&&NET.ws){NET.ws.close(4000,"bg");}})`, sin marcar `NET.closing`, para que dispare `netResume` al volver. Así el servidor pausa en milisegundos.
2. Servidor, `resume`: si el token es válido y `r.players[s]!==ws`, aceptar aunque no haya `away`. Hacer `const old=r.players[s]; old.room=null; old.terminate();`, borrar `r.away[s]` si existe, y seguir con el flujo actual. Hay que hacerlo antes de `onClose(old)` o marcar `old.replaced=true` para que su `onClose` no cuente como abandono.
3. Bajar el ping a 5 s solo con partida en marcha (`ws.room` en estado `play`): ping cada 5 s y `terminate` a los 10 s.

### G2 · alto · La ruta en L es aleatoria y decide si esquivas

**Evidencia**
`index.html:1174-1180` (`pathTo`): `if(Math.random()<.5){stepX();stepY();}else{stepY();stepX();}`.
En `demos.js`, al ir de (2,2) a (3,3) el primer paso se queda en la fila 2 el **50,0 %** de las veces (10.000 pruebas). Ejemplo: un Flechazo `row3` cubre la fila y=2 y el defensor toca (3,3) para escapar. Si va primero en X, pasa 0,27 s más en zona de peligro (`step` 0,27) y con un vuelo de 0,55 y una reacción de unos 0,3 s le dan. Si va primero en Y, se salva. Con el mismo toque, el resultado lo decide una moneda al aire.
Online además el cliente predice una ruta (`moveTo` local, `4730`) y el servidor sortea otra, así que el héroe corrige su trayectoria con tirones.

**Impacto en el jugador**
Una esquiva bien hecha falla al azar. Es frustrante y enseña al jugador que su decisión no importa. También deja de cumplirse «los mismos datos dan el mismo resultado» entre cliente y servidor.

**Arreglo**
Hacer `pathTo` determinista y que salga primero del peligro. Recibir `R` y `s`, calcular las casillas peligrosas (`R.projs.filter(p=>p.d===s).flatMap(p=>p.cells)`) y elegir el orden (X o Y primero) que pase menos pasos en casillas peligrosas. Si empatan, ir primero por el eje con más distancia, y si siguen empatados, X primero. El cliente debe usar exactamente la misma función para predecir. Coste: unas 6 líneas.

### G3 · alto · En táctil no se ve el área del ataque antes de disparar

**Evidencia**
- `index.html:2812`: `function onMove(ev){if(ev.pointerType==="touch")return;…}`. La previsualización (`hoverCells`, `2903`) solo existe con ratón.
- `index.html:2811`: `onDown` dispara en el mismo `pointerdown`.
- `index.html:1164`: `sq2` usa la casilla tocada como esquina superior izquierda. Por ejemplo, tocar (2,2) cubre (2,2), (3,2), (2,3) y (3,3) (`demos.js`). En la isla roja, y+1 es la fila más cercana a ti, así que el 2×2 de Brasa siempre se extiende a la derecha y hacia abajo.
- `cross5` pierde casillas en los bordes, y `row3` se ajusta a los bordes. El jugador en móvil no ve nada de esto antes de gastar 3 a 8 de elixir.

**Impacto en el jugador**
El jugador apunta a ciegas con ataques que no son de una sola casilla: Brasa, Bum, Rayo, Muro y Flecha en los bordes. Los fallos parecen «injustos» y no se aprende la forma de cada ataque.

**Arreglo**
Apuntar manteniendo el dedo. En `pointerdown` sobre la isla roja guardar `aim={x,y}` y pintar `areaOf` en blanco (como `hoverCells`). En `pointermove` actualizar `aim` (quitar el `return` para táctil). En `pointerup` disparar si sigue sobre una casilla roja, y cancelar si el dedo sale del tablero. Un toque rápido (menos de 120 ms) dispara igual que ahora, para no ralentizar a los expertos.
Para `sq2`, usar `hits[0].uv` del raycast para elegir el cuadrante: si `uv.x<.5` el bloque empieza en `x-1`, y lo mismo con `uv.y`. Así el 2×2 queda centrado donde toca el dedo.

### G4 · alto · Enfrentamientos de 88/12 con la elección a ciegas

**Evidencia** (`duel.js`, 800 rondas por lado, bot Normal en los dos lados; los dos órdenes coinciden)

| A contra B | gana A |
|---|---|
| Sombra contra Brasa | 11,0 % (al revés, 87,5 %) |
| Sombra contra Muro | 11,3 % (Muro contra Sombra, 90,0 %) |
| Sombra contra Mira | 85,4 % (Mira contra Sombra, 14,8 %) |
| Rayo contra Flecha | 30,5 % (al revés, 70,3 %) |
| Muro contra Brasa | 41,9 % |

Sombra tiene 2 de vida (`1120`), así que cae de un golpe ante cualquier ataque de 2 (Brasa, Rayo, Bum, Mira). Muro, con su columna entera y 6 de vida, la castiga.
PROGRESO.md habla de un 44-56 % por héroe en total, pero el formato es «elige a ciegas, no repitas», así que cada ronda la decide sobre todo el emparejamiento.

**Impacto en el jugador**
Muchas rondas están decididas antes de empezar. Con Sombra se pierde 9 de cada 10 veces contra Muro sin poder hacer nada. Es la sensación de «no depende de mí» que más rápido hace abandonar un juego.

**Arreglo** (probar por simulación con estos valores de partida)
- Sombra: `hp:3`, `step:.22` y `cost:3`; o mantener `hp:2` y dar a su sigilo un «primer golpe de cada ronda bloqueado» (`shieldUntil` de 1 golpe al empezar).
- Muro: `col5` → `col3` centrado en el toque (ya existe `col3` en `areaOf`), o `cost:4`.
- Mira contra Sombra: subir `travel` de Mira a 1,3, o que Sombra sea inmune al tiro que no avisa durante 0,5 s tras moverse.
- Añadir un objetivo al simulador: ningún emparejamiento fuera del 35-65 %, y comprobar la matriz entera (8×8), no solo la media de cada héroe.

### G5 · alto · Curva de dificultad: de Fácil a Normal la victoria cae del 45 % al 11 %

**Evidencia**
`index.html:3951-3955` (`DIFFS`) y `curve.js` (600 rondas, jugador simulado con los parámetros del propio bot):

| jugador | contra Fácil | contra Normal | contra Difícil |
|---|---|---|---|
| nivel «Fácil» | 45,5 % | **11,3 %** | 2,7 % |
| nivel «Normal» | 88,5 % | 50,5 % | 16,0 % |

Ganar el 11 % de las rondas supone ganar alrededor del 3 % de las partidas al mejor de 3. Además, `4285` hace que a partir de 300 trofeos Fácil dé 0 trofeos, lo que obliga a pasar a Normal justo en ese salto. El online (`server.js:183-192`) ya interpola los parámetros por trofeos (`lerp`), pero el modo contra el bot no.

**Impacto en el jugador**
Hay un muro entre 250 y 300 trofeos, justo al llegar al Volcán. Encadenar derrotas ahí es la causa típica de abandono en la primera semana.

**Arreglo**
Interpolar dentro de cada dificultad con `k=clamp((S.tro-base)/rango)`, como en el online: en Fácil, de los valores de `facil` (0 trofeos) a un punto medio (`think:.8, dodge:.45, eps:.4, gap:3.2, thr:1.35, moveP:.55`) a los 300. O bien añadir «Media» con esos valores y hacer que Fácil dé trofeos hasta 400 con `TRO_MULT` reducido.
Objetivo medible con `curve.js`: un jugador de nivel Fácil debería ganar cerca del 30 % de las rondas contra el siguiente escalón.

### G6 · alto · El amago de Mira se distingue

**Evidencia**
- Disparo real: `index.html:1250`, `until:R.now+HUELLA_T*(H.loud?2:1)`, es decir 4 s para Mira.
- Amago: `1269`, `until:R.now+HUELLA_T` (2 s fijos).
- `viewFor` (`1422-1423`) envía `until` al rival, y el cliente pinta la opacidad con `(until-now)/HUELLA_T` (`2927`). `demos.js` lo confirma: el rival recibe `[{dur:4},{dur:2}]`.
- La huella real de Mira empieza con opacidad 2 (se ve llena 2 s y luego se apaga). La del amago se apaga desde el principio y desaparece a los 2 s.
- Lo mismo pasa con Eco (oculto): el disparo real deja 2 huellas (`1251`) y el amago solo 1.

**Impacto en el jugador**
Contra Mira, el amago, que es la mecánica que da nombre al juego, se descubre a simple vista. El jugador que lo note lo ignora siempre.

**Arreglo**
En `amago`, usar la misma duración y el mismo número de huellas que un disparo real: `until:R.now+HUELLA_T*(H.loud?2:1)` y, si `H.echo`, una segunda huella con `fakeSpot`.
Mejor aún, crear un `printOf(h,H,x,y,decoy)` común a `fire` y `amago` para que no vuelvan a separarse. Añadir una prueba que compare `viewFor` de un disparo y de un amago para cada héroe (las claves y `until-now` deben ser iguales).

### G7 · medio · Rayo no puede elegir la diagonal

**Evidencia**
`index.html:1161-1163`: prueba primero `[1,1]` y solo usa `[1,-1]` si la primera no cabe. En `demos.js`, 19 de 25 casillas dan la diagonal «\\» y solo 6 esquinas dan «/». La descripción dice «Rayo en diagonal», como si se pudiera elegir.

**Impacto en el jugador**
El héroe más caro (8 de elixir) no puede apuntar la mitad de sus tiros posibles. Esto explica en parte su 30 % contra Flecha (G4).

**Arreglo**
Igual que en G3: elegir la diagonal según el cuadrante del toque (`uv`). Si `(uv.x-.5)*(uv.y-.5)>0`, usar «\\», si no, «/». Pasarlo al motor como un parámetro opcional `fire(R,s,tx,ty,hk,variant)` validado en el servidor (0 o 1). Opción más sencilla: alternar la orientación en cada toque sobre la misma casilla y mostrarla al mantener el dedo.

### G8 · medio · Truco y Sombra: su huella se pinta como exacta

**Evidencia**
- `index.html:2927`: en la isla roja, cualquier `huella` se dibuja con `icon="foot"` y no mira `m.fake` ni `m.blur` (solo en tu isla se usa `foot2`).
- `4566`: el aviso `foeprint` dice «¡El rival disparó desde ahí! Contraataca rápido.».
- `4540`: la barra de estado dice «👣 ¡Ha disparado desde ahí!».
- Para Truco, `fakeSpot` (`1235`) garantiza que la huella **no** está en su casilla. Para Sombra, `blurSpot` la pone en un 3×3.

**Impacto en el jugador**
El juego da instrucciones falsas. Contra Truco, «contraataca ahí» siempre falla, y el novato cree que el juego hace trampas.

**Arreglo**
En `update`, si `top.fake`, usar `icon="foot2"` (morado) con un «?» encima. Si `top.blur`, pintar en `dc` las 9 casillas de alrededor con opacidad 0,2.
Cambiar los textos según el héroe rival: Truco → «👣 Huella falsa: allí NO está»; Sombra → «👣 Huella borrosa: está por esa zona».

### G9 · medio · El bot no entiende a Truco

**Evidencia**
`index.html:1354-1358`: toda `huella` se trata con `setExact(.75)`, aunque `m.fake` sea verdadero.
`duel.js`, Truco contra Flecha (2.000 rondas): **58,3 %** con el bot actual y **40,9 %** con un bot que, ante un Truco, hace `belief[y][x]*=.05` en vez de `setExact` (variante `fakeAware`).

**Impacto en el jugador**
Contra el bot, Truco es una trampa ganadora: el bot persigue cada huella falsa. Eso distorsiona la percepción del equilibrio y la simulación con la que se ajustó.

**Arreglo**
En `botUpdate`, `if(m.t==="huella"&&HF.fake&&!m.decoy){B.belief[m.y][m.x]*=.05;B.belief=normalize(B.belief);}`. Con Sombra, repartir el peso por el 3×3 en vez de usar `.4` en la casilla exacta.
Después, volver a ajustar Truco (con este dato, su huella falsa no compensa sus otras cifras: quizá `step:.27` o `travel:.6`).

### G10 · medio · En las arenas avanzadas el bot ignora las reglas

**Evidencia**
- `botUpdate` (`1338-1405`) no lee `R.lava`, `R.cover` ni `R.wind`. El jugador ve la lava 3 s antes (`R.lava.warnAt`, pintada en `2944`) y puede apartarse; el bot nunca lo hace, así que la erupción lo delata (`1313-1315`).
- Con viento, `fire` desplaza el tiro una casilla (`1247`). El jugador puede compensar, pero el bot no, y falla en todos los tiros de esos 6 s.
- El bot tampoco usa la estatua de Trono.
- Las arenas se aplican desde 250 trofeos (`startRound`, `3999`).

**Impacto en el jugador**
Justo cuando el juego debería ponerse más difícil (Volcán, Trono, Olimpo), las reglas nuevas favorecen al humano. Las reglas parecen un adorno, no una decisión táctica para los dos.

**Arreglo**
En `botUpdate`:
- Si `R.lava&&R.now>=R.lava.warnAt` y el bot está en una casilla de lava, `me.path=[pick(adj fuera de lava)]` (con la misma probabilidad `B.dodge`).
- Al apuntar con viento activo, `t[0]=clampN(t[0]-R.wind.dir)`.
- Con `R.cover` libre, sumar `.1` de preferencia a esa casilla en `relocate`.

### G11 · medio · Muerte súbita: el texto dice «sin aviso»

**Evidencia**
`index.html:4598`: `banner("¡MUERTE SÚBITA!","Ataques sin aviso · os veréis cada 5 s")`. PROGRESO.md también dice «ataques sin aviso». Sin embargo, el motor dice en `1244`: «en muerte súbita el aviso se mantiene, pero el golpe llega antes» (`travel*.6`), y el cliente sigue pintando el aviso (`inc`, `2905`).

**Impacto en el jugador**
El jugador deja de mirar su isla porque cree que no habrá aviso. Además, no sabe que el elixir sube ×1,5 ni que los golpes llegan un 40 % antes.

**Arreglo**
Texto: «Golpes más rápidos · elixir ×1,5 · os veréis cada 5 s». Corregir también el `I18N_EN` (`1516`) y PROGRESO.md.

### G12 · medio · El amago armado sobrevive a un disparo

**Evidencia**
`index.html:4721-4746`: con `G.decoyArm` activo, tocar la isla roja dispara un ataque real sin desarmar el amago. El siguiente toque en tu isla, normalmente para escapar tras disparar (lo que pide el propio aviso `myprint`), entra en `if(b==="p"&&G.decoyArm)` y **coloca una huella falsa en lugar de moverte**.
Además, el motor acepta un amago sobre tu propia casilla (`amago` no lo comprueba), lo que delata tu posición. La interfaz lo atenúa en `2937`, pero no lo impide.

**Impacto en el jugador**
Te quedas quieto sobre tu huella real y el rival te remata. Es un error que el jugador no entiende.

**Arreglo**
En `onTile`, rama `b==="b"`: `if(G.decoyArm){G.decoyArm=false;$("#amagob")?.classList.remove("on");}` antes de disparar.
En la rama de amago: `if(x===me.x&&y===me.y){floatText(…,"🎭 Lejos de ti","miss");return;}`, sin desarmar, para que pueda elegir otra casilla.
En el motor, `amago` debe devolver `"self"` si `x===h.x&&y===h.y`.

### G13 · medio · En partida no hay pausa, salir ni rendirse

**Evidencia**
`buildArena` (`4490-4506`) no tiene ningún botón de salir. `data-a="home"` solo aparece en los modales de error y en el final (`3873`, `4345`), pero se registra `quit_mid` (`4677`), así que el equipo lo esperaba.
Contra el bot, el motor se para con `document.hidden` o `UI.modal` (`4242`). Al volver, sigue al instante sin cuenta atrás, con proyectiles en vuelo.
Bajar el centro de notificaciones de iOS no siempre activa `hidden`, así que la partida sigue corriendo.

**Impacto en el jugador**
Para salir hay que matar la app. Al volver de una interrupción te pueden dar antes de saber dónde estás.

**Arreglo**
Botón ⏸ en `.tbox`:
- Contra el bot: abre un modal «Pausa» (la partida ya se para con `UI.modal`) con «Seguir» y «Rendirse», que cuenta como derrota con `endMatch` y `G.score.b=2`.
- Online: solo «Rendirse», que envía `{t:"leave"}`.
- Al volver de `hidden` o cerrar la pausa: `R.paused=true` y una cuenta 3-2-1 (`banner` ×3) antes de `R.paused=false`. Escuchar también `window.blur` en partida contra el bot.

### G14 · medio · Online: la cuenta atrás del cliente no coincide con la del servidor

**Evidencia**
El servidor espera siempre `COUNTDOWN_MS=3300` (`server.js:21`, `275-279`). El cliente, en las rondas 2 y siguientes, hace VS 700 ms + 250 ms y muestra «¡YA!» (`index.html:4171-4173`), es decir al segundo. Durante unos 2,3 s el jugador ve «¡YA!» pero `R.paused` sigue a `true` hasta `go` (`4439`): sus toques se ignoran y la barra dice «⏳ ¡Prepárate!».
En la ronda 1, si `GFX.ensureAnim` tarda (red lenta), las `view` llegan antes de `buildArena`. El filtro `UI.screen==="game"` (`4440`) las descarta y el jugador pierde segundos de partida.
Al reanudar (`server.js:636`), la partida sigue sin cuenta atrás para ninguno de los dos.

**Impacto en el jugador**
El arranque se siente roto («¡YA!» y no responde), y los móviles lentos empiezan con desventaja.

**Arreglo**
El servidor manda `goAt` (milisegundos que quedan) en `roundStart` y `resumed`. El cliente programa el 3-2-1 para que termine exactamente en `goAt`. El servidor espera un `{t:"ready"}` de cada cliente después de `buildArena` (máximo 6 s) antes de empezar los 3,3 s. Tras un `resume`, poner `R.paused=true` y reanudar con un `setTimeout` de 3 s más un evento `go`.

### G15 · medio · Online: disparo sin bloqueo ni respuesta local

**Evidencia**
`index.html:4738-4743`: online solo se comprueba `R.elx.p`, una copia de la última `view` que puede tener hasta 100 ms de antigüedad, y `cdUntil`. No se descuenta elixir ni se marca nada hasta que el servidor responde con `ev fired`, una ida y vuelta de 80 a 300 ms en móvil.
Si el jugador vuelve a tocar porque «no ha pasado nada», y pasan más de 0,45 s (`fire` en `1243`), el servidor acepta un segundo disparo y gasta otros 3 a 8 de elixir.

**Impacto en el jugador**
Disparos dobles sin querer, sensación de retraso y elixir gastado sin entender por qué.

**Arreglo**
Online, al tocar:
- `G.pendFire=R.now`, `R.elx.p-=H.cost` (predicción) y respuesta inmediata: `sfx("shoot")`, `tl.bump` y las casillas `areaOf` en naranja (un `myProjs` fantasma).
- Ignorar los toques en rojo mientras `R.now-G.pendFire<.6` y no haya llegado el `fired` propio.
- La siguiente `view` corrige el elixir.

### G16 · medio · El bot enseña su héroe de la ronda 1 antes de que elijas

**Evidencia**
`index.html:3969`: `UI.modal.oppHero=G.oppPool[0]`, que se pinta en «¡Rival encontrado!» (`3867`). Ese es exactamente el héroe que juega el bot en la ronda 1 (`startRound`, `3993`), y el jugador elige después (`showPick`). Con emparejamientos de 88/12 (G4), es una contraelección gratis.
Online, `matched` no trae `oppHero`, así que se pinta siempre `heroSVG("truco")` (`3867`), un dato falso.

**Impacto en el jugador**
Contra el bot, quien lo descubre gana la ronda 1. Online, el jugador cree que el rival jugará con Truco.

**Arreglo**
En el modal de búsqueda, mostrar un retrato neutro («?» o la silueta del favorito del rival) y no `oppPool[0]`. Si se quiere enseñar algo, que sea un héroe al azar del `oppPool` que no se use en la ronda 1. Online, quitar el valor por defecto `"truco"`.

### G17 · medio · Tutorial: el reloj corre mientras espera

**Evidencia**
En `TUT.r1` (`4086-4130`) solo se pausa en los pasos con botón («¡VALE!» y «¡A POR ÉL!»). Los pasos «mover», «disparar», «escapar» y «contraatacar» esperan con `until(...)` mientras `R.now` avanza. Si un jugador lento pasa de 45 s, aparecen el cartel de muerte súbita y los pings. A los 75 s la ronda termina por tiempo: `timeWinner` con 6/6 contra 3/3 y el mismo daño da **empate**, y la lección de disparo se queda sin terminar.
`TUT.setup` (`4046`) pone `passiveUntil=1e9` en cada ronda. Si se llega a la ronda 3 (el jugador pierde la 2), no hay guion (`go()` solo cubre las rondas 1 y 2) y el bot no ataca nunca.

**Impacto en el jugador**
El primer minuto de juego puede verse confuso o roto justo con los jugadores más lentos, los que más necesitan el tutorial.

**Arreglo**
Con `G.tut`, congelar el reloj de ronda durante el guion: `R.tutFreeze=true` y, en `tick`, `if(R.tutFreeze&&R.now>=SUDDEN_T-5)R.now=SUDDEN_T-5`. Quitarlo en `free1` y `free2`. En la ronda 3 o siguientes del tutorial, `passiveUntil=R.now+3`.

### G18 · medio · Casillas pequeñas en la isla roja y disparo inmediato

**Evidencia**
Proyecté con Three r160 la misma cámara de `fitCamera` (FOV 40, `2762-2780`), suponiendo una interfaz de unos 15 % arriba y unos 22 % abajo (`cam.js`):

| pantalla | fila lejana de la isla roja | fila cercana de la isla roja | tu isla |
|---|---|---|---|
| iPhone 14 (390×844) | ≈38×26 pt | ≈42×31 pt | 44-49 pt |
| iPhone SE (375×667) | ≈28×19 pt | ≈30×23 pt | — |

El mínimo que recomienda Apple es 44×44 pt.
El raycast solo mira las mallas de las casillas (`2808`), así que un toque en el hueco de 0,04 no hace nada, y el disparo sale al apoyar el dedo (`2811`).

**Impacto en el jugador**
Toques que van a la casilla equivocada en la isla donde cada error cuesta 3 a 8 de elixir, sobre todo en el SE y en la fila del fondo.

**Arreglo**
- Raycast contra un plano por isla (o `ray.intersectPlane` con y=0) y redondear a la casilla más cercana, sin huecos muertos.
- Disparar en `pointerup` con la vista previa de G3.
- Dar más tamaño a la isla roja: inclinar la cámara un poco más hacia arriba (`dir=V(0,1,.65)`) o escalar la isla roja ×1,1 en z.

### G19 · bajo · Tutorial, ronda 2: «¡Ha picado!» aunque no dispare

**Evidencia**
`index.html:4145`: `if(m.x!==me.x)AMAGO.fire(R,"b",m.x,m.y,ui);`. Muro dispara en columna, así que si el jugador pone el amago en su propia columna no hay disparo. Aun así, en `4147` el entrenador dice «¡Ha picado! Disparó a tu huella falsa.».

**Impacto en el jugador**
La lección del amago miente justo cuando el jugador no ha seguido la mano.

**Arreglo**
Si `m.x===me.x`: `this.coach("Ponla en otra columna, lejos de ti.")` y volver a esperar otro amago (reiniciar `decoyUntil=0`). O que Ojo dispare a `[m.x,m.y]` con un patrón de una casilla solo en el tutorial.

### G20 · bajo · «Sin elixir» del bot se muestra como tuyo

**Evidencia**
El motor llama a `call(hk,"noElx",s)` para cualquiera de los dos lados (`1206`), pero `ui.noElx()` (`4597`) no mira `s`: hace temblar tu barra, suena «miss» y sale «Sin elixir».
Ocurre en el **2,3 %** de las rondas (`noelx.js`, 1.800 rondas), sobre todo cuando el bot amaga mientras camina.

**Arreglo**
`noElx(s){if(s&&s!=="p")return;…}`.

### G21 · bajo · El bot aprende de sus propios amagos

**Evidencia**
El resultado del amago del bot se guarda como marcas reales «agua» o «cerca» en `R.marks.p` (`1277`, `dud:true`). `botUpdate` (`1353-1361`) no filtra `m.dud`, así que el bot sabe si el jugador estaba al lado de su disparo de pega. Al humano esas marcas se le ocultan (`viewFor`, `1422`; cliente, `2923`). Afecta también al bot del online.
Efecto medido: unos 2-3 puntos (variante `noDudP`: 49,5 % / 50,4 %, frente a la línea base 51,9 % / 47,8 %). Es pequeño pero real.

**Arreglo**
`for(const {m} of ready){if(m.dud)continue;…}` (o `if(m.dud&&m.t!=="huella")continue;`).

### G22 · bajo · Un aviso sobre tu casilla nunca es un amago

**Evidencia**
`index.html:1265-1266`: el disparo de pega se vuelve a sortear hasta 30 veces para no cubrir al defensor. Un jugador atento aprende que si el aviso le toca, es real, y si no le toca, puede ser un amago. Eso le dice que el atacante no le tenía localizado.

**Arreglo**
Que el amago apunte con la misma lógica que un disparo real: un objetivo plausible que puede caer sobre el defensor. Si cae encima, que se resuelva como «¡Uf! Por poco», como ya hace el caso raro de `1281-1282`. Dejar de rehacer el sorteo, o hacerlo solo con un 50 % de probabilidad.

### G23 · bajo · Las acciones bloqueadas no dan respuesta

**Evidencia**
- `index.html:4745`: contra el bot, el resultado `"cd"` (0,45 s) no se trata.
- Online, `4742`: `if(R.now<me.cdUntil)return;`.
- Con `R.paused` (cuenta atrás, coach del tutorial, rival desconectado), `onTile` hace `return` sin más (`4722`).

**Arreglo**
Mostrar un `floatText` corto («⏳») y `sfx("nope")` en cada caso. Con `R.paused`: `tl.bump` y el texto «Espera…».

### G24 · bajo · Subir de nivel apenas se nota y PROGRESO.md lo describe mal

**Evidencia**
`index.html:1171`: `lvBonus` da `elx:.01*(lv-1)` y `hp:0`, es decir un +8 % como mucho en el nivel 9, tras 6.000 monedas. PROGRESO.md dice «+3 % de recarga por nivel y +1 vida en los niveles 5 y 9». El documento está desactualizado y la mejora es casi imperceptible en partida: unos 0,4 s menos por cada disparo de 3 de elixir en el nivel 9.

**Arreglo**
Corregir PROGRESO.md. Para que se note sin «comprar victorias», dar en los niveles 3, 6 y 9 algo visible y cosmético-funcional: estela del proyectil, efecto del K.O. o un aspecto de huella. O que cada nivel dé `elx:.02` con tope de arena (`LV_CAP` ya limita).

### G25 · mejora · Memoria de disparos en la isla roja

**Evidencia**
Las marcas «agua» y «cerca» duran `MARK_T=1,3 s` (`1112`, `1277`). Después la isla roja queda limpia y el jugador tiene que recordar de memoria dónde ha disparado, que es la habilidad central del juego.

**Propuesta**
Guardar en el cliente `shotMem[x,y]={t,res}` con cada impacto propio y pintarlo en `dc` con una opacidad de `.25*(1-(now-t)/6)`: azul para «agua» y naranja para «cerca», 6 s. No revela nada que el jugador no haya visto ya, pero convierte la deducción en algo visible y satisfactorio. Ayuda mucho a los novatos (G5).

### G26 · mejora · Coste del camino a la vista

**Evidencia**
Moverse cuesta 1 de elixir por casilla (`mc:1`, `1205-1209`). Tocar una casilla a 4 de distancia con 3 de elixir hace que el héroe se pare a medio camino con «Sin elixir». Además gasta el elixir del siguiente disparo sin aviso. El marcador `dest` (`2936`) no muestra el coste.

**Propuesta**
Dibujar «-N💧» sobre el marcador de destino, con borde rojo si `N>R.elx.p`, y atenuar en tu isla las casillas a más de `floor(elx)` pasos. Tocar una casilla a la que no llegas mueve solo hasta donde llega el elixir, pero lo enseña antes.

### G27 · mejora · Rastro del rival al final de cada ronda

**Evidencia**
La repetición (`playReplay`) solo se ve en la ronda decisiva y si hubo K.O. (`4266`). En el resto, `revealFoe` muestra únicamente la casilla final. `REC.snaps` ya guarda la posición del rival cada 0,08 s (y online `track`, `server.js:285-291`).

**Propuesta**
En todas las rondas, durante los 2 s de `revealFoe`, pintar en la isla roja el camino de los últimos 6 s como huellas que se encienden en orden (de `REC.snaps`), con un rótulo «Aquí esquivó tu disparo» si un `impact` propio cayó a 1 casilla. Es aprendizaje inmediato: el «¿dónde estaba?» que el juego ya usa como gancho para compartir.

### G28 · mejora · Indicador de viento que dure y aviso previo

**Evidencia**
En Olimpo, el viento empieza sin aviso (`1316`) y desplaza 6 s los disparos. El cartel dura 1,3 s (`4600`). Durante el resto del tiempo no hay ninguna pista, y un tiro lanzado justo al empezar se desvía por sorpresa.

**Propuesta**
- Avisar 2 s antes: `R.wind.warnAt=next-2` y una flecha translúcida sobre la isla roja.
- Mostrar en el HUD el icono «💨→ 4 s» durante toda la ráfaga.
- Con la vista previa de G3, enseñar ya desplazada la zona que va a caer.

---

## Notas

- Las cifras de equilibrio enfrentan bot contra bot. Un humano juega distinto (sobre todo con Sombra), pero las diferencias de G4 y G9 son tan grandes que no se explican por el estilo del bot.
- No reproduje G1 con un iPhone real. La cadena (no hay aviso al pasar a segundo plano, el ping es de 20 s y `resume` exige `away`) se deduce del código del cliente y del servidor citado.
- G18 es una estimación: supuse la altura de la interfaz de arriba y de abajo. Medirlo en el dispositivo con `screenPos` en las 4 esquinas de la casilla.
