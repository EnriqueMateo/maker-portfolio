# AMAGO: plan de retención y economía (LiveOps)

Fuentes revisadas: `amago/PROGRESO.md`; en `amago/index.html`, `HEROES` (l. 738), `ROAD`/`UPG`/`CHESTS`/`PASS`/`MISSIONS` (l. 983-997), `DEF` y `loadSave` (l. 1012), `ensureDay`, `giveReward`, `rollChest` (l. 2154-2210), tienda (l. 2299-2340), pase y misiones (l. 2366-2387), `startMatch`/`startRound`/`endMatch` (l. 2500-2610), y las capturas de `review/`. Simulé la economía actual con un script (`scratchpad/sim/cur.js`) y la propuesta con otro (`scratchpad/sim/new.js`).

Perfiles de referencia usados en todo el documento:
- **Regular**: 6 partidas al día (unos 30 min), juega 6 días de cada 7, gana el 55 % en Normal y hace las 3 misiones.
- **Casual**: 3 partidas al día, 4 días a la semana, gana el 50 % y hace 2 de cada 3 misiones.
- **Niño en Fácil**: gana el 78 % (el dato de `PROGRESO.md`).

---

## 1. Diagnóstico: por qué se irá la gente

### Lo que el código hace hoy (números reales)

| Sistema | Valor actual | Consecuencia |
|---|---|---|
| Monedas por partida | **0**. Solo llegan monedas desde cofres, el camino de trofeos, el pase y el regalo | La partida en sí no paga: ganar solo da 1/3 de cofre |
| Cofre por llaves (`CHESTS[1]`) | 15-30 monedas y 15-30 ⚡ (media 22) cada 3 victorias | Unas 6 monedas por partida. Un nivel 9 (900 monedas) son unas 150 partidas solo con llaves |
| Trofeos (`endMatch`) | +8 a +10 por victoria y −3 a −4 por derrota, sin depender de la dificultad | En Fácil (78 %) se suben **+6,3 trofeos por partida**; en Difícil (30 %) aún se sube un poco. Nadie tiene motivo para dejar Fácil |
| Nivel del bot (`startRound`, l. 2529) | `lb = min(cap, nivelTuyo ±1)` | **El bot copia tu nivel.** Pasado el tope por trofeos, subir de nivel no da ventaja. La mejora "no se nota", que es justo lo que el pase de pago tendría que vender |
| `lvBonus` | +3 % de elixir por nivel; +1 vida en los niveles 5 y 9 | A nivel 9, Sombra pasa de 2 a 4 vidas (×2). Es mucho poder: cuidado si algún día hay competitivo online |
| Coste de un héroe 1→9 (`UPG`) | 1.035 ⚡ y 2.205 monedas | Las monedas cuestan el doble que los ⚡, pero se ganan en la misma cantidad: **sobran ⚡** (simulación del Regular: 7.475 ⚡ y 6.369 monedas en D30) |
| Pase (`PASS`) | 30 escalones de 100 fichas, 14 días. Misiones de unas 175 fichas al día | El Regular **lo completa el día 10** y el Casual el día 14. Es el mismo pase cada temporada, sin nada exclusivo |
| Cambio de temporada (`ensureDay`) | `S.pass={season,tk:0,got:[]}` | **Los escalones alcanzados y sin cobrar se pierden sin aviso.** Esto genera enfado y abandono |
| Héroes | 8 en total. El camino da Ojo (40), Truco (110), Rayo (220) y Bum (400); el pase da uno en el escalón 15; los cofres tienen un 8/20/50 % de héroe; la tienda los vende por 100-550 | El Regular **tiene los 8 hacia el D8-D10** (simulación: 7 por camino y pase en D7, más unos 3,8 esperados de cofres). Después, cada premio de "héroe" se convierte en 150 monedas sin más |
| Camino de trofeos | Termina en 1.000 (Olimpo) | El Regular en Fácil llega a 1.000 hacia el **D27**. Después no hay ninguna meta |
| Nivel de jugador (`S.xp`) | Solo cosmético | La barra azul de la portada sube sin dar nada |
| `S.hw` (rondas ganadas por héroe) | Se guarda y solo se ve en "🏆 N" | Es un gancho de maestría ya medio hecho que no se aprovecha |
| Amistosos online | Solo dan +15 XP: ni fichas, ni misiones, ni llaves | Jugar con amigos o con los hijos, que es lo que más retiene, no hace progresar |
| Regalo diario | Un Cofre de nivel 1 (unas 22 monedas) | No da ninguna razón para volver mañana |
| Oferta "Cofre grande −30 %" (`offers`) | Sale cada día a 110 tachando 160 | El precio de referencia es falso porque nunca se vende a 160. Ver el apartado ético |

### D1: el jugador no vuelve mañana
1. **Nada pide volver mañana.** El único gancho diario es un cofre de unas 22 monedas y 3 misiones que solo dan fichas. No hay calendario, ni bonus de primera victoria, ni nada que avance por entrar.
2. **La primera sesión no tiene una mejora guiada:** `DEF.coins=0`. La primera mejora llega en cuanto se cobran los premios del camino (30 monedas a 10 trofeos), pero nadie la señala. Se abren 6 premios a la vez (captura `a_home`: insignias "6" y "2") sin guion.
3. Las misiones y el pase se ven antes de entender el juego. Sin desbloqueo escalonado, la portada parece igual el D0 y el D1.

### D7: la colección se agota y la mejora no se nota
1. Hacia el D7-D10 el Regular ya tiene casi todos los héroes. Se pierde el mejor premio, el "¡NUEVO HÉROE!", y la tienda de héroes desaparece.
2. Las mejoras no se notan porque el bot copia tu nivel. El jugador gasta 900 monedas en el nivel 9 y la partida sigue igual de difícil.
3. **Corte de temporada en el D14:** quien terminó el pase el D10 pasa 4 días sin nada que hacer, y quien no cobró escalones los pierde.
4. Fácil da los mismos premios que Difícil, así que no hay ninguna escalera de habilidad a la que aspirar.

### D30: se acaban las metas
1. El camino termina en 1.000 trofeos (Regular hacia el D27). Los trofeos nunca bajan ni se reinician.
2. El pase se repite idéntico cada 14 días: mismos premios y ningún cosmético.
3. No hay contenido rotativo: ni modos, ni eventos, ni héroes nuevos.
4. Sin social: los amistosos no cuentan, no hay clasificación entre amigos y no hay motivo para invitar.
5. Las monedas solo sirven para subir niveles, y con todo comprado eso es lo único. Hacia el D90-D100 el Regular lo tiene todo al máximo.

---

## 2. Las 10 funciones por impacto/esfuerzo

Esfuerzo: S = menos de 1 día, M = 2-4 días, L = 1-2 semanas o más (incluye arte).
Los valores ya usan la economía revisada del apartado 4.

### 1. Primera victoria del día + monedas por victoria (impacto muy alto, esfuerzo S)
**Mecánica**
- **Primera victoria del día:** +30 monedas, +20 ⚡ y **llave doble** (esa victoria da 2 llaves). Se reinicia a medianoche local con `today()`.
- **Monedas por victoria contra el bot:** Fácil 5, Normal 8, Difícil 12. **Tope diario de 100 monedas por victorias.** El tope también ayuda a que los niños no alarguen la sesión; al llegar se muestra "Has ganado todas las monedas de hoy. ¡Mañana más!".
- Derrota: 0 monedas, pero sí fichas del pase (como ahora).

**Datos en `S`:** `fw: -1` (día de la última primera victoria), `wc: {day:-1, n:0}` (monedas por victoria ganadas hoy).

**Dónde se ve**
- En portada, una píldora sobre JUGAR: "🎁 1.ª victoria: x2 llaves +30🪙".
- En el final de partida, una fila nueva `endrow` "Monedas +8" y, si toca, la fila "¡Primera victoria del día!" con animación de llave doble.

**Código:** en `endMatch`, antes de `save()`.

### 2. Calendario de 7 días sin castigo (impacto muy alto, esfuerzo S)
**Mecánica:** un día del calendario por cada día que entras. **Si fallas un día, no se reinicia**: simplemente se cobra el siguiente al volver. Es un calendario, no una racha, y evita la presión de las rachas que se pierden, sobre todo en niños.

| Día | Semana 1 (primer ciclo) | Semana 2 en adelante |
|---|---|---|
| 1 | 60 monedas | 40 monedas |
| 2 | Cofre | Cofre |
| 3 | 50 ⚡ | 40 ⚡ |
| 4 | 100 monedas | 80 monedas |
| 5 | Cofre grande | Cofre grande |
| 6 | 80 ⚡ | 60 ⚡ |
| 7 | **Elige un héroe raro** (Ojo o Truco que no tengas; si ya los tienes, Megacofre) | Megacofre |

**Datos en `S`:** `cal: {day:-1, i:0, cyc:0}`. `day` es el último día cobrado, `i` es el día del ciclo (0-6) y `cyc` cuenta los ciclos completados.

**Dónde se ve**
- Hoja modal automática **la primera vez que se vuelve a la portada cada día** (nunca antes de la primera partida del D0).
- Se muestran los 7 días, el de hoy brilla y el del día 7 se ve grande. Debajo pone "Mañana: Cofre", que es el gancho para volver.
- En portada, botón lateral "Diario" con una insignia mientras queda algo por cobrar.

### 3. Pase reparado y vía premium (impacto muy alto para retención e ingresos, esfuerzo M)
**Arreglos obligatorios**
- **Cobro automático al cambiar de temporada:** en `ensureDay`, antes de reiniciar, se entregan los escalones pendientes y se avisa con "Te guardamos 3 premios del Pase". Tampoco se pierde nada al comprar el premium tarde.
- **Temporada de 28 días** en lugar de 14 (`SEASON_DAYS=28`) y **40 escalones de 200 fichas** (8.000 fichas). Un pase de pago de 14 días se siente caro y además ahora lo termina todo el mundo.
- **Recuperación** para quien llega tarde o falta días: si el escalón actual es menor que `0,8 × 40 × díaDeTemporada / 28`, las fichas de las partidas cuentan doble. En el final de partida aparece "Fichas x2 (recuperación)".
- **Premio extra tras el escalón 40:** cada 300 fichas, un Cofre, con un máximo de 10 por temporada. Así siempre se avanza algo.
- **Misiones semanales:** 3 por semana, de 250 fichas cada una. Por ejemplo "Gana 12 partidas", "Gana 6 rondas con 3 héroes distintos" o "Juega 1 amistoso" (ver la función 5).
- **1 cambio de misión diaria gratis** (botón ↻).

**Contenido por temporada (28 días)**

| | Vía gratis | Vía premium (4,99 €) |
|---|---|---|
| Monedas (incluidos cofres) | 1.400 | +3.600 |
| ⚡ (incluidos cofres) | 900 | +2.240 |
| Héroe nuevo de la temporada | Escalón 20 | **Escalón 1** (acceso anticipado unas 2 semanas) |
| Cosméticos | 1 marco de avatar | 1 **aspecto** de héroe exclusivo de temporada (escalón 1), 1 aspecto en el escalón 40, 3 emotes, marco animado, título |
| Comodidad | — | +1 cambio de misión al día; las mismas fichas que la vía gratis (nada de multiplicador de fichas) |

Reglas:
- La vía premium se puede comprar en cualquier momento y entrega de golpe lo ya alcanzado.
- El precio se muestra en euros, sin moneda intermedia.
- No se venden escalones sueltos en la versión 1. Para el público infantil es la venta más agresiva; se puede valorar después.

**Datos en `S`:** `pass: {season, tk, got:[], pgot:[], prem:false, bonus:0}` y `mis.wk: {week, list:[]}`, `mis.rr: 0` (cambios usados hoy).

**Dónde se ve**
- Pantalla del pase con dos columnas (gratis | premium bloqueada con candado y precio).
- Tras completar el escalón 5, una vez por temporada, un aviso suave: "Con el Pase Premium tendrías +X🪙 ya". Ese número se calcula de verdad con los escalones alcanzados.

### 4. La dificultad y el nivel cuentan: bot por trofeos, ligas por dificultad y rachas (impacto alto, esfuerzo S)
**Mecánica**
- **Nivel del bot según los trofeos, no según tu nivel** (l. 2529):
  `base = 1 + floor(tro/110)`, con +1 en Difícil y −1 en Fácil, y nunca más de un nivel por encima del tuyo: `lb = clamp(1, 9, min(base, lp+1))`.
  Así, mejorar por delante de tus trofeos da una ventaja real (que es lo que vende el pase) e ir por detrás solo cuesta un nivel. Hay que ver el efecto con `simbot.js` antes de publicar.
- **Trofeos según la dificultad:**
  - Victorias: Fácil ×0,7, Normal ×1, Difícil ×1,4 (sobre 8-10).
  - Derrotas: −2 por debajo de 300, −4 entre 300 y 600, −6 por encima de 600.
  - **Fácil deja de dar trofeos a partir de 300**, aunque sigue dando monedas, llaves y fichas. El aviso dice: "Para subir más trofeos, prueba Normal". Es honesto y un niño puede quedarse en Fácil para siempre sin perder premios.
- **Racha de victorias:** con 2, 3, 4 y 5 o más victorias seguidas se suman +1, +2, +3 y +4 trofeos. Se ve una llama 🔥 con el número en la portada y en el final.
- **Escudo tras 2 derrotas seguidas:** la siguiente derrota cuesta 0 trofeos y el bot juega un poco más flojo (en `botParams`, `react +0,1`). Es la red de seguridad contra la frustración.

**Datos en `S`:** `ws: 0` (racha de victorias), `ls: 0` (racha de derrotas), `troMax: 0`.

### 5. Los amistosos cuentan y misiones sociales (impacto alto en niños y familias, esfuerzo S)
**Mecánica**
- Los amistosos online dan fichas (victoria 25 y derrota 10, las **5 primeras partidas del día**), cuentan para las misiones diarias y dan XP como contra el bot (40/20 en lugar de 15). No dan trofeos ni monedas por victoria, para que no se pueda abusar entre dos cuentas.
- Misión semanal fija: "Juega 1 amistoso" (250 fichas).
- En los avisos: "Reta a [nombre]: tu código es ABCD".

**Datos en `S`:** `fr: {day:-1, n:0}`.

**Dónde se ve:** en el final del amistoso (`onlineMatchEnd`), filas de fichas y XP, y "Revancha" como ahora.

### 6. Maestría por héroe (impacto alto para D30+, esfuerzo M)
**Mecánica:** usa el `S.hw` que ya existe (rondas ganadas con cada héroe).

| Rondas ganadas | Rango | Premio |
|---|---|---|
| 3 | Bronce | 40 monedas |
| 10 | Plata | 40 ⚡ |
| 25 | Oro | Cofre grande |
| 50 | Experto | Título "<Héroe> Experto" + marco de avatar del color del héroe |
| 100 | Maestro | 300 monedas + 200 ⚡ |
| 200 | Leyenda | Variante dorada del sprite (solo cosmética) + emote |

Por héroe suma unas 420 monedas y 260 ⚡ durante meses; con 8 héroes, unas 3.360 monedas y 2.080 ⚡. Además empuja a usar todo el plantel, porque cada partida obliga a usar 3 héroes.

**Datos en `S`:** `mgot: {id: [3,10,...]}`.

**Dónde se ve**
- En la ficha del héroe (`heroSheet`), una barra de maestría.
- En la placa de la portada, el "🏆 N · ver ficha" pasa a mostrar el rango.
- En `roundBanner`, "+1 maestría".

### 7. Premios de regreso y notificaciones (impacto medio-alto, esfuerzo S)
**Mecánica** (se mide con `S.seen`, el último día que entró):

| Ausencia | Premio de bienvenida |
|---|---|
| 3-9 días | Cofre grande + **fichas x2 en las 5 próximas partidas** |
| 10-29 días | Megacofre + fichas x2 en 10 partidas + "Novedades desde que te fuiste" |
| 30 días o más | Megacofre + **un héroe a elegir** que no tengas (si los tiene todos, 500 monedas) + 1.000 fichas del pase en curso |

**Datos en `S`:** `seen: -1`, `back: {n:0}` (partidas con bonus que quedan).

**Notificaciones** (solo con Capacitor y notificaciones locales):
- Siempre opcionales y desactivadas por defecto en menores.
- **Como máximo 1 al día**, nunca entre las 21:00 y las 9:00, y ninguna a partir del día 30 sin abrir.
- Textos:
  - D+1, 18:00: "Tu Cofre del día 2 te espera 🎁"
  - Calendario día 7: "¡Hoy toca el Megacofre!"
  - Pase a punto de acabar con premios sin cobrar: "Quedan 2 días de temporada y tienes 3 premios por cobrar". Solo si es cierto.
  - Amigo: "¿Una revancha? Crea sala y pásale el código".
- Prohibido: textos de culpa ("Tu héroe está triste"), urgencias falsas o contadores inventados.

### 8. Desafío del día con modo rotativo (impacto alto, esfuerzo M)
**Mecánica:** cada día (semilla `today()`, como las misiones) se activa un modificador del motor:
- **Niebla:** sin huellas al disparar.
- **Elixir loco:** recarga ×2.
- **Lluvia de cebos:** objetos cada 8 s.
- **Espejo:** los dos con el mismo héroe cada ronda.
- **Gigantes:** +2 vidas a todos.
- **Muerte súbita:** desde el segundo 0.
- **Tablero 4×4.**

Reglas del desafío:
- Consiste en **ganar 3 partidas antes de perder 3**.
- Premios por victoria: 1 da 20 monedas, 2 dan 30 ⚡ y 3 dan Cofre grande + 100 fichas.
- Se puede reintentar gratis una vez al día. **No se venden reintentos**: pagar por otra oportunidad con premio variable roza el juego de azar.
- Se desbloquea tras 10 partidas.

**Datos en `S`:** `ev: {day:-1, w:0, l:0, tries:0, got:[]}`.

**Dónde se ve**
- Tarjeta en portada sobre el botón de modo ("Hoy: Niebla 🌫️ · 1/3 ✓").
- El selector de modo (`setdiff`) añade el modo "Desafío".

### 9. Temporadas de liga y camino infinito (impacto alto para D30+, esfuerzo M)
**Mecánica**
- Al terminar cada temporada de 28 días (la misma del pase), **los trofeos por encima de 500 se reducen a la mitad del exceso**. Por ejemplo, 900 pasa a 700.
- Las arenas desbloqueadas dependen de `troMax` y no se pierden nunca.
- Premio de fin de liga según el pico de la temporada:

| Pico | Premio |
|---|---|
| 300 o más | 100 monedas |
| 500 o más | 200 monedas + 100 ⚡ |
| 700 o más | 350 monedas + 200 ⚡ + marco |
| 900 o más | Megacofre + 200 monedas + título "Olímpico T#" |

- **Camino infinito a partir de 1.000:** cada 100 trofeos un Cofre grande y cada 500 un Megacofre. Los nodos se generan en `ROAD`.

**Datos en `S`:** `troMax`, `lg: {season, peak, got:false}`.

**Dónde se ve:** el camino de trofeos muestra "Liga termina en N días". Al cambiar de temporada aparece una pantalla de resumen antes del cofre automático del pase.

### 10. Cadencia de héroes nuevos y colección que no se agota (impacto muy alto a largo plazo, esfuerzo L)
**Mecánica**
- **1 héroe nuevo cada temporada de 28 días**: escalón 20 del pase gratis, escalón 1 del premium y, después de la temporada, en la tienda por monedas al precio de su rareza.
- Ritmo de rarezas: rara, épica, rara, legendaria.
- Al tenerlos todos, los premios de "héroe" se convierten en **un cofre del nivel equivalente** (rara: Cofre grande; épica y legendaria: Megacofre) en lugar de 150 monedas fijas.
- Primeros héroes posibles con mecánicas que el motor ya tiene: "Eco", que deja una huella falsa al moverse, y "Gancho", que atrae cebos.
- **Aspectos** como segundo gasto de monedas, que `PROGRESO.md` ya menciona: 600 monedas por un recolor y 1.200 por un aspecto. Solo por monedas o premium, nunca aleatorios.

**Datos en `S`:** `skins: {id: "def"}`, `own: []`. `IDS` sigue funcionando.

**Dónde se ve:** en el pase (escalón 20 marcado como héroe), en la tienda en la sección "Nuevo" y en una ventana de novedades al empezar la temporada.

### Mejoras rápidas que no entran en el top 10 (esfuerzo XS)
- **Recompensa por nivel de jugador:** cada nivel da 20 ⚡ y cada 5 niveles un marco o emote. Da sentido a la barra de XP de la portada.
- **Primera mejora guiada en el D0**, en el apartado 3.
- **Probabilidad de héroe visible** en los cofres ("8 % héroe nuevo") y **garantía**: el 10.º cofre grande o megacofre seguido sin héroe trae uno. Va en `S.pity`.

### Límites éticos y legales (España y UE)

| Idea | Valoración |
|---|---|
| Cofres aleatorios **comprados con monedas** (`buyBox`, oferta Cofre grande o Megacofre) | Hoy es aceptable porque las monedas no se compran con dinero. **En cuanto el pase premium dé monedas, comprar cofres aleatorios con ellas es una caja de botín pagada indirectamente.** Propuesta: la tienda vende **lotes de contenido fijo** ("Lote de poder: 120 monedas → 100 ⚡") y los cofres solo se ganan jugando. Afecta al anteproyecto español de mecanismos aleatorios de recompensa, a la postura de Bélgica y Países Bajos y a las normas de App Store y Google Play sobre probabilidades. **Hay que cambiarlo antes de lanzar el premium.** |
| "Cofre grande −30 %" diario tachando 160 | Precio de referencia ficticio (patrón engañoso). Con dinero real chocaría con la directiva Ómnibus (art. 6 bis de la Directiva 98/6/CE: el descuento se calcula sobre el precio más bajo de los 30 días anteriores). Hay que quitar el tachado o hacer que la rebaja rote de verdad. |
| Rachas que se reinician al faltar un día | Se descartan; se usa el calendario sin castigo. |
| Héroe de temporada adelantado en el premium | Es una ventaja leve que solo cuenta contra bots, porque los amistosos van a nivel 1. Se acepta, pero hay que mantener los amistosos normalizados y, **si llega el competitivo online, emparejar por nivel o normalizarlo.** |
| Exclusivos de temporada (miedo a perdérselo) | Moderado. Mitigación: los aspectos de pases antiguos vuelven a la tienda por monedas al cabo de 6 meses, y se anuncia desde el principio. |
| Monedas o gemas de pago, venta de escalones, reintentos de pago, anuncios con premio para menores | No se hacen en la versión 1. Hay que seguir los "Key principles on in-game virtual currencies" de la red CPC (2025): precios en euros, sin moneda intermedia opaca. |
| Topes diarios de monedas | Son a favor del jugador: limitan las sesiones largas sin quitar el progreso diario. |

(Antes de lanzar en tiendas, que lo revise un asesor legal. El anteproyecto español no estaba aprobado según mi información.)

---

## 3. Primera semana día a día (D0-D7)

**Desbloqueo escalonado.** Todo existe desde el principio, pero se muestra en este orden:
1. Partida 1: tutorial.
2. Partida 2: misiones.
3. Partida 3: pase.
4. Partida 5: amistosos.
5. Partida 10: desafío del día.
6. D2: misiones semanales.
7. 3 rondas ganadas con un héroe: maestría.
8. 300 trofeos: ligas.

### D0 (primera sesión, unos 20-25 min)
1. Partida tutorial (`G.tutorial`). Al terminar se pide el nombre, que está pendiente en `PROGRESO.md`.
2. **Bono de bienvenida: 60 monedas y 40 ⚡**, con mejora guiada de Flecha al nivel 2 (40 monedas y 25 ⚡) y la animación `lvup`. Es el primer "subo".
3. Partidas 2-4: el camino en 10 trofeos da 50 monedas, en 20 da 40 ⚡ y en 30 un Cofre. Las misiones aparecen tras la partida 2, con la primera ya casi hecha ("Juega 3 partidas" en 2/3).
4. Partida 3 o 4: tercera llave y el **primer Cofre**. El pase aparece y ya está en el escalón 1 (bono de 200 fichas al desbloquearlo).
5. Hacia la partida 5-6 (40 trofeos): **Ojo**, el primer héroe nuevo.
6. Primera victoria del día ya cobrada y calendario día 1 (60 monedas), que se muestra al volver a la portada tras la partida 1.
7. Al cerrar la sesión: "Mañana: 🎁 Cofre (día 2) · llave doble · misiones nuevas".

### D1
- Calendario día 2 (Cofre) y primera victoria con llave doble.
- 3 misiones nuevas y regalo de la tienda.
- Objetivo de la sesión: **Flecha o Brasa al nivel 3** y unos 70 trofeos (cofre grande del camino).

### D2
- Calendario día 3 (50 ⚡). Aparecen las **misiones semanales** (3 × 250 fichas).
- Desafío del día desbloqueado (ya van unas 10 partidas). Primer modo, por ejemplo Niebla.

### D3
- Calendario día 4 (100 monedas).
- **Truco** (110 trofeos) y arena **Bosque** (100 trofeos): primer cambio de escenario.
- Si va bien en Normal, la racha 🔥 aparece por primera vez.

### D4
- Calendario día 5 (**Cofre grande**).
- Primer rango de maestría (Bronce con el héroe más usado).
- Pase hacia el escalón 9-10. Primer aviso suave del premium con números reales.

### D5
- Calendario día 6 (80 ⚡).
- **Momento clave: el primer héroe llega al nivel 5 (+1 vida)**. La economía del apartado 4 está calculada para que pase entre el D4 y el D5.
- Si está en Fácil cerca de 300 trofeos, aparece "prueba Normal".

### D6
- Desafío con otro modo (Espejo).
- Misión semanal de amistoso: "Reta a alguien de casa".
- Pase hacia el escalón 13-14.

### D7
- Calendario día 7: **elige un héroe raro** (o Megacofre si ya los tiene).
- Pantalla "Semana 1 completada": partidas, héroes, nivel máximo y siguiente objetivo (Rayo a 220 trofeos, nivel 6 o el héroe de temporada en el escalón 20).
- Se renuevan las misiones semanales y empieza la semana 2 del calendario.

---

## 4. Ajuste de la economía

### Objetivos
- **X = unas 4 semanas** para que un jugador **Regular gratis** lleve un héroe del nivel 1 al 9 concentrándose en él (unas 12 semanas para el trío que exige cada partida y unas 33 para los 8).
- **Y = unas 2,5 semanas** para el mismo jugador **con el pase premium** (unas 7,5 semanas para el trío). Es 1,6 veces más rápido, sin que el pago sea imprescindible.
- Casual: unas 7,5 semanas gratis y unas 4,6 con pase.

### UPG nuevo (coste para subir **a** cada nivel)

| Nivel | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | **Total** |
|---|---|---|---|---|---|---|---|---|---|
| ⚡ | 25 | 55 | 100 | 180 | 310 | 510 | 890 | 1.530 | **3.600** (antes 1.035) |
| Monedas | 40 | 90 | 170 | 300 | 520 | 850 | 1.480 | 2.550 | **6.000** (antes 2.205) |

```js
const UPG=[null,null,{pp:25,c:40},{pp:55,c:90},{pp:100,c:170},{pp:180,c:300},{pp:310,c:520},{pp:510,c:850},{pp:890,c:1480},{pp:1530,c:2550}];
```

La curva es barata al principio (nivel 5 = 600 monedas y 360 ⚡, unos 3 días) y lenta al final. Los ⚡ se acercan a la mitad de las monedas, igual que su ritmo de ingreso, así que dejan de sobrar.

### CHESTS nuevos (solo se ganan jugando; se muestra la probabilidad de héroe)

```js
const CHESTS={1:{n:"Cofre",coins:[20,30],pp:[15,25],hero:.06,taps:1},
              2:{n:"Cofre grande",coins:[70,90],pp:[50,70],hero:.15,taps:2},
              3:{n:"Megacofre",coins:[220,280],pp:[160,200],hero:.35,taps:3}};
```

- Medias: 25/20, 80/60 y 250/180.
- Se baja la probabilidad de héroe porque ahora los héroes llegan de forma fija (camino, calendario, pase y tienda). Hay garantía en el 10.º cofre grande o mega.
- Se quita `price`: la tienda vende lotes fijos ("120 ⚡ por 150 monedas", "Lote de nivel: 300 monedas + 150 ⚡ por 400 monedas" una vez al día).
- Héroes en tienda: `PRICE=[150,300,600,1000]`. Antes eran 100-550, que es poco frente a la nueva escala de monedas.

### ROAD (ajuste de monedas a la nueva escala; mismos hitos)
- Los premios de monedas pasan de 30/60/100/150/300 a **50/100/180/280/500**.
- Los de ⚡ pasan de 25/40/60/100/150/200/300 a **40/60/100/160/240/320/480**.
- A partir de 1.000, camino infinito (función 9).
- Total del camino: unas 3.200 monedas y 2.900 ⚡ de golpe en las 3-5 primeras semanas. Por eso el primer héroe llega antes de las 4 semanas en la práctica: unas 3 semanas para un Regular nuevo.

### Fichas y pase

| Fuente | Fichas |
|---|---|
| Partida contra el bot | Victoria 25 · empate 15 · derrota 10 (sin cambios) |
| Amistoso | Igual, en las 5 primeras partidas del día |
| Misiones diarias | 3 al día, unas 175 de media (sin cambios) |
| Misiones semanales | 3 × 250 = 750 a la semana |
| Pase | 40 escalones × 200 = **8.000** en 28 días |

Comprobación:
- Regular: 6 × (0,55 × 25 + 0,45 × 10) = 110 por partidas, más 175 de misiones, son 285 al día. Por 6 días son 1.710, más 750 semanales: **2.457 a la semana**. Completa el pase en unas **3,3 semanas (D23)**, con 5 días de margen.
- Casual: unas 1.182 a la semana, lo que da el escalón 23 de 40 el día 28. Con la recuperación ×2 sube al escalón 27-28. Llega al héroe de temporada (escalón 20) en unos 17 días.

### Ingresos semanales en régimen estable (sin camino; `scratchpad/sim/new.js`)

| Fuente (Regular gratis, 6 días) | Monedas | ⚡ |
|---|---|---|
| Monedas por victoria: 3,3 victorias/día × 8 × 6 | 158 | — |
| Primera victoria: 30 / 20 × 6 | 180 | 120 |
| Cofres de llaves: (3,3 + 1 llave extra) × 6 / 3 = 8,6 cofres × 25 / 20 | 215 | 172 |
| Regalo diario (Cofre) × 6 | 150 | 120 |
| Calendario (6/7 de un ciclo de 475 / 360) | 407 | 309 |
| Pase gratis (1.400 / 900 entre 4 semanas) | 350 | 225 |
| **Total gratis** | **unas 1.460** | **unos 950** |
| + Pase premium (3.600 / 2.240 entre 4) | +900 | +560 |
| **Total con pase** | **unas 2.360** | **unos 1.510** |

(La simulación da 1.461/946 y 2.361/1.506. La diferencia con la tabla es redondeo y el calendario con 6 de 7 días.)

**Cálculo de X e Y para un héroe (6.000 monedas y 3.600 ⚡):**
- Gratis: 6.000 / 1.461 = **4,1 semanas**; 3.600 / 946 = 3,8 semanas. **X ≈ 4 semanas**, con las monedas como límite.
- Pase: 6.000 / 2.361 = **2,5 semanas**; 3.600 / 1.506 = 2,4 semanas. **Y ≈ 2,5 semanas**.
- Trío (×3): gratis 12,3 semanas y pase 7,6.
- 8 héroes: gratis unas 33 semanas y pase unas 20. Si se suman la maestría (unas 3.400 monedas en total) y un héroe nuevo cada 4 semanas, siempre hay algo que mejorar más allá del D90.
- Casual (3 partidas, 4 días, 50 %): unas 815 monedas a la semana, así que un héroe tarda **7,4 semanas** gratis y **4,6** con pase.

**El premium visto como compra:** 3.600 monedas y 2.240 ⚡ equivalen a unas 2,5 semanas de juego gratis del Regular, más 2 aspectos, emotes y el héroe adelantado, por 4,99 € cada 28 días. Es fácil de explicar en la pantalla del pase: "El Premium te da lo mismo que ~2 semanas de juego, y además aspectos".

### Comparación rápida con la economía actual (simulación del Regular en Fácil)

| | Actual | Propuesta |
|---|---|---|
| Héroes completos | D8-D10 | Unos 7 en el D7 (con el elegido del calendario), los 8 hacia el D14-D21, y +1 por temporada |
| Primer héroe a nivel 9 | **D10-D12** (2.205 monedas) | **D21-D28** (6.000 monedas, con el camino ayudando al principio) |
| Pase completado | D10 de 14 | D23 de 28 |
| Fin de metas | D27 (camino) y D100 (todo al máximo) | Ligas cada 28 días, camino infinito, maestría (meses) y héroe nuevo cada 28 días |
| ¿Notas la mejora? | No: el bot copia tu nivel | Sí: el bot depende de los trofeos, con un máximo de un nivel por encima del tuyo |

### Orden de implementación sugerido
1. **Sprint 1 (S, sin arte):**
   - Cobro automático del pase al cambiar de temporada.
   - Primera victoria y monedas por victoria.
   - Calendario.
   - Bot según trofeos, trofeos según dificultad y rachas.
   - Nuevos `UPG` y `CHESTS`.
   - Quitar el tachado falso.
   - Amistosos que cuentan.
2. **Sprint 2 (M):**
   - Pase de 28 días y 40 escalones con vía premium y recuperación.
   - Misiones semanales.
   - Lotes de contenido fijo en lugar de cofres en la tienda.
   - Regreso.
   - Maestría.
3. **Sprint 3 (M-L):**
   - Desafío del día con modificadores.
   - Ligas y camino infinito.
   - Primer héroe de temporada y aspectos.

Métricas a instrumentar desde el sprint 1 (hoy no hay telemetría):
- D1, D7 y D30.
- Partidas por día.
- Porcentaje que cobra el calendario.
- Escalón del pase en el día 14 y en el 28.
- Distribución de dificultad.
- Momento de la primera mejora.
- Conversión al premium tras el aviso del escalón 5.
