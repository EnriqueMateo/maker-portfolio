# AMAGO · Monetización: Pase Premium, gemas y tienda

Spec lista para implementar. Basada en el código actual de `amago/index.html` (`UPG`, `CHESTS`, `ROAD`, `PASS`, `MISSIONS`, `offers()`, `showShop`, `endMatch`, `giveReward`, `rollChest`, `ensureDay`) y en `PROGRESO.md`. Mercado: España/UE, iOS/Android (Capacitor) y web. Público: niños y adultos casuales.

Principios que mandan sobre todo lo demás:

1. **Nada aleatorio a cambio de dinero.** Nada que se pague directa o indirectamente con dinero real (gemas, o monedas compradas con gemas) da contenido aleatorio. Los cofres de pago o de la tienda tienen **contenido fijo y visible antes de comprar**. Los cofres que se ganan jugando pueden seguir siendo aleatorios, con las probabilidades a la vista.
2. **Pagar acelera, no decide.** Con el tope de nivel por arena (sección 3.5), quien paga no puede llevar a una arena un héroe por encima del nivel que tiene allí un jugador gratuito activo.
3. **El precio en euros siempre a la vista**, también junto a los precios en gemas (≈ €).
4. **Nunca se vende tras una derrota**, ni en las 3 primeras partidas, ni durante una partida. Como mucho, una ventana de oferta al día.

---

## 0. Diagnóstico rápido de la economía actual (afecta al diseño)

| Dato | Valor actual | Consecuencia |
|---|---|---|
| Coste de subir un héroe del 1 al 9 (`UPG`) | 1.035 ⚡ + 2.205 monedas | Las **monedas** son el cuello de botella (proporción 2,1:1 frente a lo que se gana, ~1:1). Las ofertas de monedas venderán más que las de ⚡. |
| Coste de los 8 héroes al máximo | 8.280 ⚡ + 17.640 monedas | Un F2P activo tarda ~6 meses. Hay margen para acelerar sin agotar el contenido. |
| `lvBonus` | +3 % de recarga de elixir por nivel (+24 % a nivel 9), +1 vida a nivel 5 y 9 | El nivel pesa mucho en la partida, así que **hace falta tope por arena** (3.5) antes de vender ⚡. |
| Bot (`startRound`) | nivel del bot ≈ nivel de tu héroe, con tope `1+floor(tro/90)` | Hoy un jugador de nivel 9 con 0 trofeos aplasta a bots de nivel 1. Si se venden ⚡ sin tope, se compra la victoria contra el bot. |
| Pase (`PASS`) | 30 × 100 fichas, temporadas de 14 días | Un jugador activo (~250 fichas/día) lo acaba en 12 días. 14 días es poco para cobrar un pase (4,99 € cada 14 días = ~10 €/mes, demasiado para niños). |
| Cambio de temporada (`ensureDay`) | `S.pass={season,tk:0,got:[]}` | **Bug de ética:** se pierden los premios alcanzados y no reclamados. Con un pase de pago esto da reembolsos y reseñas de 1 estrella. Hay que corregirlo (5.4). |
| Icono ⚡ | Cristal morado | Las gemas necesitan **otra forma y otro color** (diamante turquesa/verde) para no confundirlas con los ⚡. |

**Decisión:** temporadas de **28 días** y `PASS_STEP` de **200 fichas**. Ritmos:
- Activo (5 partidas y 3 misiones al día, ~250 fichas): escalón 30 hacia el día 24, y luego la bóveda.
- Casual (3 partidas y 2 misiones, ~170 fichas/día): escalón ~23–24.
- Muy casual (3 días por semana): escalón ~10–12.

Con Premium, el Pase Plus o unos pocos saltos de escalón, el casual también llega al 30.

*(Si se quiere mantener 14 días: Premium a 2,99 €, Plus a 5,99 €, 15 escalones en la tabla. No es lo recomendado.)*

---

## 1. Moneda premium: Gemas 💎

### 1.1 Cómo se ganan gratis (pocas, pero siempre algunas)

| Fuente | Cantidad | Frecuencia | Gemas/temporada (activo) |
|---|---|---|---|
| Pase gratuito, escalones 8, 18 y 28 | 10 cada uno | por temporada | 30 |
| «Semana completa»: cobrar las 3 misiones del día en 5 días de una semana (lun–dom) | 10 | semanal | 40 |
| Nivel de jugador (`level()`), cada 5 niveles | 10 | ~1 vez cada 2–3 semanas | ~10 |
| Arena nueva (nodos `arena` de `ROAD`: Bosque, Volcán, Trono, Olimpo) | 25 | una vez cada una | (100 en total, una sola vez) |
| Primera victoria de la historia y poner nombre | 10 + 10 | una vez | (20 una vez) |
| **Recurrente** | | | **~80 por temporada** |

Un F2P activo puede comprar el Pase Premium con gemas (450) más o menos cada 5–6 temporadas. Es una meta de ahorro que fideliza, igual que en Brawl Stars.

### 1.2 Packs de gemas (precios de las tiendas, IVA incluido)

Apple y Google publican precios fijos por país con el IVA ya incluido, así que en la UE los precios que se muestran ya son finales. Usamos los escalones estándar en EUR.

| SKU | Gemas | Precio | Gemas/€ | Extra frente al pack base | Etiqueta |
|---|---|---|---|---|---|
| `amago.gems_80` | 80 | 0,99 € | 81 | – | – |
| `amago.gems_450` | 450 | 4,99 € | 90 | +12 % | «Justo para el Pase» |
| `amago.gems_1000` | 1.000 | 9,99 € | 100 | +24 % | «Popular» |
| `amago.gems_2200` | 2.200 | 19,99 € | 110 | +36 % | – |
| `amago.gems_6000` | 6.000 | 49,99 € | 120 | +48 % | – |

- **Sin pack de 99,99 €.** El público incluye niños, así que el máximo es 49,99 €.
- **Sin «x2 en la primera compra».** Infla el valor percibido y las autoridades de consumo de la UE lo miran con lupa.
- **Las gemas no caducan.** En el guardado se separan las gemas de pago (`gemsPaid`) de las gratuitas (`gemsFree`). Se gastan primero las gratuitas, salvo en lo que exija gemas de pago (nada, de momento). Esta separación se usa en reembolsos y contabilidad.
- **Equivalencia en euros:** cada precio en gemas lleva al lado «≈ X €», calculado con la tarifa **más cara** (pack de 0,99 €, 1,24 céntimos por gema), redondeado a 0,05 €. Ejemplo: «450 💎 (≈ 5,55 €)». Por eso es más honesto vender el Pase también en € directos.
- **Paquetes alineados con los precios.** Lo más caro que se compra con gemas (el Pase, 450) cabe exacto en un pack. Los artículos de 30–60 gemas caben en el pack de 80. Así nadie tiene que comprar más gemas de las que necesita (principio de la red CPC de 2025).

### 1.3 Qué compran las gemas

| Artículo | Gemas | Límite | Notas |
|---|---|---|---|
| Pase Premium de la temporada | 450 | 1 por temporada | Alternativa al pago directo de 4,99 € |
| Salto de 1 escalón del pase | 30 | hasta el escalón 30 | Sección 2.5 |
| Salto de 5 escalones | 135 (−10 %) | hasta el escalón 30 | |
| Salto de 10 escalones | 240 (−20 %) | hasta el escalón 30 | |
| Bolsa de monedas: 300 🪙 | 40 | 3 al día | Acelerador |
| Saco de monedas: 1.500 🪙 | 180 | 1 al día | Acelerador |
| Frasco de poder: 120 ⚡ | 50 | 2 al día | Acelerador |
| Barril de poder: 600 ⚡ | 220 | 1 al día | Acelerador |
| Megacofre a la vista (contenido fijo) | 220 | 1 al día | 250 🪙 + 250 ⚡ + el siguiente héroe bloqueado si queda alguno; si no, +150 🪙. **Contenido mostrado antes de comprar.** |
| Héroe bloqueado, al momento | 30 / 60 / 110 / 180 (común/raro/épico/legendario) | – | También se compran con monedas (`PRICE`), así que no es exclusivo. |
| Skin con tinte (variante de color) | 150 | – | Cosmético |
| Skin ilustrada | 400 | – | Cosmético |
| Pin (emote) | 60 | – | Cosmético |
| Marco de perfil | 100 | – | Cosmético |
| Huellas o estela | 120 | – | Cosmético (la huella sigue siendo igual de legible) |

**Regla de oro:** con gemas **no** se compran cofres aleatorios. Además, los cofres de la tienda que hoy se pagan con monedas (`buyBox`) pasan a ser **«cofres a la vista»** de contenido fijo, porque las monedas se pueden comprar con gemas y eso los convertiría en cajas de botín de pago indirectas (criterio de la Comisión de Juego de Bélgica). Se dejan aleatorios, con probabilidades publicadas, solo los cofres que se **ganan jugando**: llaves, regalo diario, camino de trofeos y pase gratuito.

---

## 2. «Pase AMAGO Premium»

### 2.1 Precios

| Producto | SKU | Precio | Contenido |
|---|---|---|---|
| **Pase Premium** | `amago.pass_premium` | **4,99 €** (o 450 💎) | Desbloquea la pista Premium de la temporada en curso, con efecto retroactivo |
| **Pase Plus** | `amago.pass_plus` | **9,99 €** | Premium + **10 escalones al momento** (2.000 fichas) + skin exclusiva Plus «Muro Rey de Feria» + marco «Plus» animado + **+20 % de fichas en partidas** toda la temporada (no en misiones) |
| Mejora de Premium a Plus | `amago.pass_plus_upgrade` | 4,99 € | La diferencia, para quien ya tiene Premium |

Valor percibido del Plus: 4,99 € + 10 saltos (300 💎 ≈ 3,70 €) + skin (≈ 5 €) + marco ≈ 14 €. Se paga 9,99 €.

### 2.2 Las dos pistas: 30 escalones (temporada 1, «Feria de Sombras»)

Leyenda:
- `chest1`, `chest2` y `chest3` son los cofres de `CHESTS`, aleatorios con probabilidades a la vista. Solo aparecen en la pista **gratuita**.
- `chest2F` y `chest3F` son **cofres fijos**, sin azar. `chest2F` = 65 🪙 + 65 ⚡; `chest3F` = 200 🪙 + 200 ⚡. Son los únicos cofres de la pista Premium, porque es de pago.
- `hero` = el siguiente héroe bloqueado (comportamiento actual, determinista). `hero:eco` = héroe de temporada.

| Esc. | Gratis | Premium |
|---|---|---|
| 1 | 40 monedas | **Héroe de temporada «Eco»** (murciélago, épico)* |
| 2 | 30 ⚡ | 10 💎 |
| 3 | Cofre (`chest1`) | 200 monedas |
| 4 | 50 monedas | 100 ⚡ |
| 5 | Cofre grande (`chest2`) | Skin con tinte «Flecha Otoño» |
| 6 | 45 ⚡ | Cofre grande fijo (`chest2F`: 65 🪙 + 65 ⚡) |
| 7 | Pin «GG» | 250 monedas |
| 8 | **10 💎** | Pin «¡Uy!» |
| 9 | 55 ⚡ | 130 ⚡ |
| 10 | Megacofre (`chest3`) | 15 💎 |
| 11 | 70 monedas | Estela «Chispas» (proyectiles) |
| 12 | 65 ⚡ | 300 monedas |
| 13 | Cofre (`chest1`) | 150 ⚡ |
| 14 | 80 monedas | Megacofre fijo (`chest3F`: 200 🪙 + 200 ⚡) |
| 15 | **Héroe** (siguiente bloqueado; si no queda, 150 🪙) | Skin ilustrada «Brasa Glacial» |
| 16 | 80 ⚡ | 10 💎 |
| 17 | Cofre (`chest1`) | 350 monedas |
| 18 | **10 💎** | Pin animado «¿Dónde estás?» |
| 19 | 100 monedas | 180 ⚡ |
| 20 | Megacofre (`chest3`) | Marco «Feria» (plata) |
| 21 | 95 ⚡ | 400 monedas |
| 22 | Pin «¡Te pillé!» | Megacofre fijo (`chest3F`) |
| 23 | 110 monedas | 220 ⚡ |
| 24 | 110 ⚡ | 10 💎 |
| 25 | Cofre grande (`chest2`) | Huellas «Estrellitas» |
| 26 | 120 monedas | 450 monedas |
| 27 | 125 ⚡ | 250 ⚡ |
| 28 | **10 💎** | 15 💎 |
| 29 | Cofre grande (`chest2`) | Megacofre fijo (`chest3F`) |
| 30 | **Héroe «Eco»*** (si ya lo tienes: Megacofre `chest3`) | Skin legendaria animada «Sombra Eclipse» |

\* **Héroe de temporada sin pago para ganar.** Con Premium se consigue en el escalón 1 (acceso anticipado). Gratis, en el escalón 30 de la misma temporada, y desde la temporada siguiente se vende en la tienda por monedas (`PRICE[2]` = 320). Tiene que cumplir la misma franja de equilibrio que los demás (44–55 % de victorias en `simbot.js`). Si la temporada no trae héroe nuevo (hace falta arte), Premium 1 = skin ilustrada «Bum Petardo» y Gratis 30 = Megacofre.

**Totales por temporada** (valor esperado de los cofres aleatorios según `CHESTS`):

| | Monedas | ⚡ | 💎 | Héroes | Cosméticos |
|---|---|---|---|---|---|
| Pista gratis | ~1.225 | ~1.270 | 30 | 2 (escalones 15 y 30) | 2 pines |
| Pista Premium | 2.615 | 1.695 | 60 | Eco anticipado | 3 skins, 2 pines, estela, huellas, marco |
| Fin de temporada Premium | – | – | 40 | – | marco oro animado |

Un jugador Premium avanza unas **1,8 veces más rápido en recursos** que un F2P activo (el F2P gana ~90 🪙 y ~90 ⚡ al día sumando todo, y el Premium ~185 🪙 y ~150 ⚡). El tope por arena (3.5) impide convertir esa ventaja en superioridad dentro de la partida. Premium recupera 100 de sus 450 💎 (22 %): incentivo para acabar el pase y volver a comprarlo, sin regalarlo.

### 2.3 Compra a mitad de temporada: desbloqueo retroactivo (clave para convertir)

- Al comprar Premium (o Plus), **todos los escalones Premium ya alcanzados quedan reclamables al momento**.
- La animación de confirmación muestra la cascada: «¡Premium activado! Tienes **N premios** listos: X monedas, Y ⚡, Z 💎, Eco…», con un botón **«RECOGER TODO»** que los entrega en secuencia rápida (los cofres fijos se suman sin animación de toques).
- La cabecera del pase, para quien no tiene Premium, muestra siempre el valor acumulado: «**7 premios Premium** esperándote (incluye a Eco)». Es honesto (son premios que ya se han ganado jugando) y es el mayor motor de conversión del género.
- Pase Plus: los 10 escalones se suman **antes** de calcular lo retroactivo, así que se ve todo junto.

**Protección de compra tardía:** si se compra con **3 días o menos** para el final y el ritmo actual no llega al escalón 30, el diálogo previo lo dice («A tu ritmo llegarás al escalón ~19 antes de que acabe»). Ofrece además **aplicar Premium a la temporada siguiente** (`S.pass.nextPrem=true`) en vez de a la actual. Evita compras de las que el jugador se arrepienta y los reembolsos.

### 2.4 Fin de temporada

1. **Reclamo automático**: al cambiar de temporada, todo lo alcanzado y sin reclamar (gratis y Premium) se entrega en el modal «Resumen de la Temporada N». Ya no se pierde nada.
2. **Bonus final por llegar al escalón 30:**
   - Gratis: insignia «Temporada N (bronce)» en el perfil + 1 Megacofre (`chest3`).
   - Premium: insignia «Temporada N (oro)» + marco oro animado + **40 💎**.
3. **Bóveda** (más allá del escalón 30): cada 300 fichas extra, hasta 10 veces:
   - Gratis: 1 Cofre (`chest1`).
   - Premium: +40 🪙 y +5 💎 (máximo 50 💎 por temporada).
   - Los saltos de escalón **no** sirven en la bóveda.
4. Las fichas no pasan de una temporada a otra. Las insignias y los cosméticos se quedan para siempre. Las skins de pase **no vuelven a la venta durante 12 meses**: se dice claramente, sin «nunca jamás» que meta presión.

### 2.5 Saltos de escalón

- 1 escalón = 30 💎 (≈ 0,35 €); 5 = 135 💎; 10 = 240 💎.
- Solo hasta el escalón 30 y **solo si tienes Premium o Plus**. Para un F2P el único motivo de saltar escalones es adelantar recursos, y eso ya lo cubren las ofertas limitadas de recursos.
- Antes de pagar se muestra la previsión: «Vas a ritmo de llegar al escalón 27. Con 3 saltos llegas al 30». Se sugiere el **número mínimo** de saltos, nunca el pack más grande.

---

## 3. Tienda

### 3.1 Orden de la tienda (de arriba abajo)

1. **Regalo diario gratis** (como ahora, el primero: buena voluntad).
2. **Destacado** (una sola tarjeta grande, se elige por prioridad):
   1. Pack de Inicio, si está disponible y no se ha comprado.
   2. Pase Premium, si no se tiene: «Temporada 1 · 4,99 € · 7 premios esperándote».
   3. Oferta destacada de la semana.
3. **Ofertas del día** (4 huecos): los 3 actuales en monedas (`offers()`, con contenido fijo) + **1 hueco en gemas** que rota (Frasco de poder −20 % = 40 💎, Bolsa de monedas ×2 = 80 💎 por 600 🪙, o el Megacofre a la vista).
4. **Recursos** (gemas → monedas y ⚡, con los límites diarios de 1.3).
5. **Cofres a la vista** (en monedas, contenido fijo mostrado): Cofre 60, Cofre grande 160, Megacofre 420. Antes de comprar se muestra el contenido exacto, sacado de la tirada del día con una semilla `today()+tier`.
6. **Héroes** (como ahora, en monedas o en gemas).
7. **Cosméticos** (skins con tinte, pines, marcos, huellas y estelas fuera de temporada).
8. **Gemas** (los 5 packs). También se abre tocando el contador 💎 de la barra superior.
9. Pie: «Precios con IVA incluido · Información de compras y probabilidades · Restaurar compras».

### 3.2 Pack de Inicio (una sola vez)

- SKU `amago.starter` · **1,99 €**
- Contiene: **200 💎 + 600 🪙 + 300 ⚡ + Cofre grande fijo (65/65) + skin con tinte exclusiva «Flecha Aprendiz»**. Valor de referencia ≈ 9 €, con etiqueta «×4 de valor».
- **Disponibilidad ética, sin cuenta atrás:** aparece tras la 6.ª partida o al desbloquear la arena Bosque (100 trofeos), lo que pase antes. Sigue disponible hasta que el jugador llegue a 250 trofeos (Volcán). La caducidad depende del progreso, no de un reloj que mete prisa.

### 3.3 Oferta destacada semanal (rotación de 4 semanas, compra directa en €)

| Semana | SKU | Precio | Contenido |
|---|---|---|---|
| 1 | `amago.bundle_hero` | 4,99 € | Skin ilustrada de un héroe del catálogo + 300 ⚡ + 800 🪙 |
| 2 | `amago.bundle_cosmetic` | 2,99 € | Skin con tinte + pin + marco (tema común) |
| 3 | `amago.bundle_power` | 4,99 € | 1.200 🪙 + 600 ⚡ + 100 💎 (como mucho una vez por semana) |
| 4 | `amago.bundle_hero` (otro héroe) | 4,99 € | ídem semana 1 |

Cada uno, una compra por semana como máximo. Fuera de la rotación, nunca más de **una** oferta en € en pantalla aparte de los packs de gemas.

### 3.4 Progreso de pago ético: aceleradores y límites

- Lo que se puede acelerar con dinero: monedas, ⚡, escalones del pase y héroes que también se consiguen gratis.
- Lo que **no** se compra nunca: trofeos, llaves, victorias, nivel de jugador, ventaja en la partida (los boosts de partida, `BOOSTS`, siguen siendo solo cebos del tablero).
- Límites diarios de recursos (1.3) y de ofertas: el gasto máximo diario posible en aceleradores es de ~550 💎 (≈ 5,50 €). Para comprar poder sin límite habría que comprar héroes al nivel máximo, y eso no existe.
- **Topes de gasto para menores** (franja de edad declarada en 6):
  - Menos de 13 años: compras con dinero real **desactivadas en la versión web**. En las tiendas dependen del control parental de la plataforma (Ask to Buy / Family Link) y de nuestro tope.
  - De 13 a 17: tope de **30 € al mes** en el cliente (`S.purch.month`). Al llegar al tope: «Has llegado al límite mensual de compras. Vuelve a estar disponible el día 1».
  - Para todos: aviso suave a los 50 € en un mes («Llevas 52,93 € este mes») con enlace a «Gestionar gastos».

### 3.5 Tope de nivel por arena (el seguro contra el pago para ganar)

`LV_CAP = [3, 5, 7, 8, 9]` para Pradera, Bosque, Volcán, Trono y Olimpo. Nivel efectivo en partida = `min(S.lv[id], LV_CAP[arena])`. Se puede subir por encima del tope (y se guarda para más adelante), pero en la partida se juega con el tope. La ficha del héroe lo indica: «Nivel 7 · en Bosque juegas a nivel 5». Un F2P activo llega a esos topes de forma natural más o menos cuando alcanza cada arena, así que comprar ⚡ adelanta el progreso dentro de tu arena sin romperla. Para el futuro modo online con trofeos, el emparejamiento se hace por trofeos con el mismo tope (los amistosos siguen a nivel 1).

---

## 4. Momentos de conversión

**Reglas globales del gestor (`maybeOffer(evt)`):**
- Nunca en las 3 primeras partidas (`S.games<3`).
- Nunca tras una derrota ni durante una partida.
- Como mucho **1 ventana (modal) de oferta al día** (`S.offerSeen.day`).
- El mismo mensaje, como mucho cada 3 días.
- Menores de 13: ningún modal de venta, solo la tienda y la pantalla del pase.
- Sin notificaciones push de ofertas.
- **Textos sin exhortación directa a comprar** (en España, la Ley de Competencia Desleal prohíbe exhortar directamente a los niños a comprar): se informa del contenido y del precio, y los botones son «Ver…», «Desbloquear · 4,99 €» o «Ahora no».

| # | Evento → lugar | Texto (ES) | Frecuencia |
|---|---|---|---|
| M1 | Primera apertura de una temporada nueva (en `ensureDay`, tras el «Resumen de temporada») → modal a pantalla completa | **Título:** «¡Empieza la Temporada 2: Feria de Sombras!» · **Cuerpo:** «30 escalones de premios gratis. El Pase Premium añade un premio extra en cada escalón y el héroe Eco desde el primer día.» · **Botones:** «VER EL PASE» / «Ahora no» | 1 por temporada |
| M2 | Pantalla del pase, siempre (cabecera de la pista Premium bloqueada) | «Pase Premium · 4,99 € · **{N} premios** ya alcanzados esperándote» · botón «DESBLOQUEAR · 4,99 €» · enlace «¿Qué incluye?» | siempre |
| M3 | Al reclamar un premio gratis cuyo premio Premium está bloqueado → aviso pequeño bajo el escalón (no es modal) | «Con Premium, este escalón también da: **250 monedas**.» | 1 al día |
| M4 | Pantalla de fin **tras una victoria** que cruza los escalones 5, 10 o 20 → `pillbtn` como el de «Premios en el camino» | «⭐ Escalón 10: hay **10 premios Premium** guardados para ti» → abre el pase | 1 cada 3 días |
| M5 | Pack de Inicio: tras la 6.ª partida (si es una victoria) o al desbloquear Bosque, en la pantalla de inicio después de la celebración de arena → modal | **Título:** «Pack de Inicio · solo una vez» · **Cuerpo:** «200 gemas, 600 monedas, 300 de Poder, un Cofre grande y la skin Flecha Aprendiz. Disponible hasta que llegues al Volcán.» · **Botones:** «VER PACK · 1,99 €» / «Ahora no» | 1 sola vez como modal; después, solo en la tienda |
| M6 | Hoja de subir de nivel con monedas o ⚡ insuficientes (hoy hay `toast("coins","Te faltan monedas…")`) | «Te faltan **120 monedas**. Se consiguen en cofres, el camino de trofeos y el pase.» Si `S.gems≥40`: botón «Usar 40 💎 (≈ 0,50 €)». Si no, enlace «Ir a la tienda». | cada vez (no es modal) |
| M7 | Pase, últimos 5 días, sin Premium y escalón ≥ 15 → banda en la cabecera | «Quedan 5 días. Si activas Premium ahora recibes al momento los **18 premios** de los escalones que ya has alcanzado.» | en la pantalla del pase |
| M8 | Después de comprar (Premium o Plus) → cascada retroactiva | «¡Premium activado! **{N} premios** listos: {X} monedas, {Y} de Poder, {Z} gemas y más.» · «RECOGER TODO» | al comprar |
| M9 | Escalón 30 alcanzado sin Premium → aviso en el escalón | «¡Pase completo! Con Premium sumarías **30 premios más** y 40 gemas de bonus.» | 1 por temporada |
| M10 | Saltos de escalón: pase con Premium, últimos 3 días y escalón previsto < 30 | «A tu ritmo llegarás al escalón 27. Con **3 saltos (90 💎)** llegas a la skin Sombra Eclipse.» | 1 al día |
| M11 | Contador 💎 de la barra superior (siempre) → abre la sección de gemas | Rótulo de la sección: «Gemas · precios con IVA incluido» | – |

Hoja de confirmación de **cualquier** gasto en gemas: «¿Usar **180 💎** (≈ 2,25 €) en Saco de monedas (1.500 🪙)? Te quedarán 270 💎.» · «CONFIRMAR» / «Cancelar». Si el gasto es menor de 50 💎 y ya se ha confirmado alguno ese día, se puede omitir con un ajuste «No volver a preguntar hoy». Para menores de 18, siempre se pregunta.

---

## 5. Plan de implementación

### 5.1 Constantes nuevas o que cambian

```js
const SEASON_DAYS=28, PASS_STEP=200, PASS_N=30, VAULT_STEP=300, VAULT_MAX=10;
const SEASON0_V2=<día de lanzamiento>, SEASON_BASE=<nº de temporada al migrar>;  // la temporada en curso se cierra sin pérdidas
const LV_CAP=[3,5,7,8,9];                           // por índice de ARENAS
const GEM_EUR=0.99/80;                              // para mostrar «≈ €»
const FIXED={2:{coins:65,pp:65},3:{coins:200,pp:200}};
const PASS_F=[/* 30 objetos de la tabla 2.2 */], PASS_P=[/* 30 */];
// tipos de premio nuevos: {r:"gems",n}, {r:"chest",tier,fixed:true}, {r:"skin",id}, {r:"pin",id},
//                         {r:"frame",id}, {r:"trail",id}, {r:"prints",id}, {r:"tokens",n}
const COSM={ skin:{flecha_otono:{hero:"flecha",kind:"tint",hue:-25,n:"Flecha Otoño"}, brasa_glacial:{hero:"brasa",kind:"art",n:"Brasa Glacial"}, …},
             pin:{gg:{t:"GG"}, uy:{t:"¡Uy!"}, donde:{t:"¿Dónde estás?",anim:1}, tepille:{t:"¡Te pillé!"}},
             frame:{feria_plata:{…}, plus:{…}, s1_oro:{…}}, trail:{chispas:{…}}, prints:{estrellitas:{…}} };
const GEM_SHOP=[{id:"coins300",gems:40,r:{r:"coins",n:300},lim:3},{id:"coins1500",gems:180,r:{r:"coins",n:1500},lim:1},
                {id:"pp120",gems:50,r:{r:"pp",n:120},lim:2},{id:"pp600",gems:220,r:{r:"pp",n:600},lim:1},
                {id:"mega",gems:220,r:{r:"chest",tier:3,fixed:"mega"},lim:1}];
const SKIP={1:30,5:135,10:240};
```

Las skins con tinte se pintan con un filtro de color sobre el sprite actual (`hue-rotate` y saturación en el material del cartón de `spriteHero`). Son baratas de producir. Las skins ilustradas son un `.webp` nuevo en `sprites/<id>_<skin>.webp`, con el mismo `RIG2D`.

### 5.2 Campos nuevos en `S` (añadir a `DEF`, con migración en `loadSave`)

```js
gemsFree:0, gemsPaid:0,                 // S.gems = gemsFree+gemsPaid (getter)
pass:{season, tk:0, got:[], gotP:[], prem:false, plus:false, nextPrem:false, vault:0, done:false},
own:{skin:[], pin:["gg"], frame:[], trail:[], prints:[]},
equip:{skin:{}, pins:["gg"], frame:"", trail:"", prints:""},   // skin por héroe; 4 pines equipables
purch:{
  starter:false, starterSeen:false,
  tx:{},                                // txId → {sku,t,granted:true}: entrega idempotente
  pending:[],                           // compras pagadas pendientes de entregar (por si la app se cierra)
  month:{m:"2026-10", cents:0},         // tope de gasto
  log:[]                                // últimas 50 {sku,t,cents,tx}
},
gemDeals:{day:-1, got:{}},              // límites diarios de GEM_SHOP
weekMis:{wk:-1, days:0, got:false},     // «Semana completa»
age:{band:"", at:0},                    // "u13" | "13-17" | "18+"
offerSeen:{day:-1, keys:{}},            // gestor de frecuencia de ofertas
badges:[],                              // insignias de temporada
gemOnce:{}                              // gemas de una sola vez ya dadas (arenas, primera victoria, nombre)
```

### 5.3 Funciones

| Función | Qué hace |
|---|---|
| `gems()`, `addGems(n,paid)`, `spendGems(n)` | Gasta primero las gratuitas y devuelve `false` si no llega. |
| `eur(gems)` | Texto «≈ 2,25 €». |
| `confirmGems(n,label,onOk)` | Hoja de confirmación de 4 (con el saldo que queda). |
| `giveReward(r)` (ampliar) | Tipos `gems`, `skin`, `pin`, `frame`, `trail`, `prints`, `tokens`, y `chest` con `fixed` (entrega `FIXED[tier]` con `openItems`, sin `rollChest`). |
| `passTier()` (ajustar a `PASS_STEP=200`) y `vaultTier()` | |
| `showPass()` (rediseño) | Dos columnas por escalón (gratis a la izquierda, Premium a la derecha con candado y valor), cabecera M2 y botón «Saltar escalones» si hay Premium. |
| `passClaimP(i)` | Premium: comprueba `S.pass.prem && i<=passTier() && !gotP.includes(i)`. |
| `claimAllPass()` | «RECOGER TODO» (gratis y Premium), con agregado de premios en un solo `openItems`. |
| `activatePremium(plus)` | `prem=true`; si `plus`, suma `tk += 10*PASS_STEP` (sin pasar del escalón 30) y entrega skin y marco; después `retroSummary()` → M8. |
| `buyPassWithGems()` | `confirmGems(450,…)` → `activatePremium(false)`. |
| `skipTiers(n)` | Valida Premium, tope 30 y precio `SKIP[n]`; `S.pass.tk = (passTier()+n)*PASS_STEP`. |
| `seasonRollover(old)` | Se llama desde `ensureDay` **antes** del reset: entrega todo lo alcanzado y no reclamado (gratis y Premium), da los bonus de 2.4 y aplica `nextPrem`. Muestra «Resumen de temporada». |
| `buyGemItem(id)` | Límites de `S.gemDeals`, confirmación y entrega. |
| `shopChestPreview(t)` | Tirada fija del día (semilla `today()*31+t`) que se muestra antes de comprar. `buyBox` entrega exactamente eso. |
| `effLv(id)` | `Math.min(lvOf(id), LV_CAP[arenaIdx()])`. Usarla en `startRound`/`newHero` donde hoy se usa `lvOf`. |
| `maybeOffer(evt)` | Gestor central de 4 (eventos: `season_start`, `end_win`, `arena_unlock`, `games6`, `pass_done`, `low_res`). |
| `buyIAP(sku)` | Comprueba la edad y el tope mensual, llama a `PAY.buy(sku)` y luego `grantSku(sku,res.tx)`. |
| `grantSku(sku,tx)` | **Idempotente**: si `S.purch.tx[tx]` existe, no hace nada. Se guarda (`save()`) **antes** de animar. |
| `revokeSku(sku,tx)` | Para reembolsos: quita las gemas de pago (el saldo puede quedar en negativo y bloquea gastar) y el Premium se queda (no se quitan premios ya reclamados). |
| `showGems()`, `showPurchaseInfo()` | Packs y página legal (precios, probabilidades, reembolsos, contacto). |
| `ageGate()` | Modal neutral tras la 1.ª partida: «¿En qué año naciste?» (rueda, sin valor por defecto «adulto»). |

**Probabilidades en pantalla** (botón «i» de cada cofre gratuito, a partir de `CHESTS`):
- Cofre: monedas 15–30 · ⚡ 15–30 · héroe 8 %.
- Cofre grande: monedas 45–80 · ⚡ 50–80 · héroe 20 %.
- Megacofre: monedas 150–250 · ⚡ 160–240 · héroe 50 %.
- Si sale héroe, el peso por rareza es 6/3/2/1 (común/raro/épico/legendario), solo entre los héroes bloqueados. La pantalla muestra el % calculado en el momento para tu colección.

### 5.4 Corrección necesaria en `ensureDay`

```js
const season=SEASON_BASE+Math.max(0,Math.floor((d-SEASON0_V2)/SEASON_DAYS));
if(S.pass.season!==season){ if(S.pass.season>=0) seasonRollover(S.pass);
  const np=S.pass.nextPrem; S.pass={season,tk:0,got:[],gotP:[],prem:np,plus:false,nextPrem:false,vault:0,done:false}; }
```

### 5.5 Adaptador de pagos `PAY`

```js
/* Interfaz común. Todas las funciones devuelven promesas. */
// PAY.init(): Promise<void>
// PAY.products(): Promise<Array<{sku, title, price:"4,99 €", micros:4990000, currency:"EUR"}>>   ← precio localizado de la tienda
// PAY.buy(sku): Promise<{ok:true, sku, tx, receipt} | {ok:false, reason:"cancel"|"pending"|"unavailable"|"blocked"|"error", msg?}>
// PAY.restore(): Promise<Array<{sku, tx}>>       // obligatorio en iOS
// PAY.finish(tx): Promise<void>                 // confirmar o consumir tras entregar
// PAY.onUpdate(cb)                              // compras diferidas (Ask to Buy) que llegan tarde

const PAY = (window.Capacitor?.isNativePlatform?.() ? PAY_NATIVE
           : (/[?&]paytest=1/.test(location.search) || window.AMAGO_PAY_TEST) ? PAY_TEST
           : PAY_NONE);

const PAY_TEST = {             // web de pruebas: simula, nunca cobra
  async init(){}, 
  async products(){ return SKUS.map(s=>({sku:s.sku,title:s.n,price:fmtEur(s.eur),micros:s.eur*1e6,currency:"EUR"})); },
  buy(sku){ return new Promise(res=>{
    UI.modal={k:"paytest",sku,res};renderModal();          // hoja «COMPRA DE PRUEBA · no se cobra nada» con
  });},                                                    // botones Pagar / Cancelar / Simular pendiente / Simular error
  async restore(){ return Object.entries(S.purch.tx).map(([tx,v])=>({sku:v.sku,tx})); },
  async finish(){}, onUpdate(){}
};  // al pagar: res({ok:true, sku, tx:"test-"+Date.now(), receipt:"TEST"})

const PAY_NONE = { async init(){}, async products(){return [];}, async buy(){return {ok:false,reason:"unavailable"};},
                   async restore(){return [];}, async finish(){}, onUpdate(){} };
// Con PAY_NONE (web de producción o artifact), la UI oculta todo lo que se paga en € y deja lo que se paga en gemas o monedas.
```

**Flujo de `buyIAP`:**
1. `canSpend(cents)`: edad y tope mensual.
2. `PAY.buy(sku)`.
3. Si va bien: `S.purch.pending.push({sku,tx})` y `save()`, después `grantSku`, `PAY.finish(tx)`, y se quita de `pending` y se guarda.
4. Al arrancar, se procesa `pending` (por si la app se cerró a mitad).

**Capacitor (iOS/Android):**
- **Recomendado: RevenueCat** (`@revenuecat/purchases-capacitor`). Valida los recibos en su servidor y gestiona reembolsos (webhooks) y precios localizados. Gratis hasta un volumen de ingresos modesto.
  - Configurar `appUserID` = id anónimo propio guardado en el servidor de AMAGO.
  - Los consumibles (gemas, pase y packs) se entregan cuando el *webhook* del servidor confirma, o en el cliente con `customerInfo` y luego se concilia.
- **Alternativa: `cordova-plugin-purchase` v13** (`CdvPurchase.store`), que funciona en Capacitor, con validador propio o el de iaptic.
- **Tipos de producto:**
  - Gemas, pase de la temporada, Pase Plus y la mejora a Plus: **consumibles**. El pase se aplica a «la temporada actual», así que un único SKU sirve todas las temporadas.
  - `amago.starter`: también consumible, con candado de «una sola vez» en el servidor, para no tener que ofrecer restaurar un producto no consumible.
  - Si Apple pide en la revisión que el pase sea restaurable, se usa una **suscripción no renovable** por temporada (`amago.pass_s{N}`) con restauración por cuenta.
- **Requisito previo a cobrar dinero real: guardado en la nube.** Hoy todo vive en `localStorage` (`SAVE_KEY`), así que reinstalar la app o borrar datos hace perder lo comprado.
  - Mínimo: cuenta anónima en el servidor Node (`server/`), con `POST /save` y `GET /save` firmados por un token del dispositivo y vinculados a Game Center o Play Games para recuperarla.
  - El saldo de gemas de pago y `S.purch.tx` mandan desde el servidor.
- **Validación en el servidor (fase 2):**
  - Endpoint `POST /iap/verify {sku, tx, receipt, platform}`, que valida con App Store Server API (JWS) o Google Play Developer API (`purchases.products.get`), o simplemente recibe el webhook de RevenueCat.
  - Anota `tx` como única y devuelve `{grant}`. El cliente entrega solo lo que devuelve el servidor.
  - Reembolsos: App Store Server Notifications `REFUND` y Google *Voided Purchases API* → `revokeSku`.
- **Web real** (si algún día se cobra en web): Stripe Checkout. El vendedor eres tú, así que hay que cobrar el IVA del país del comprador (régimen OSS de la UE), pedir el consentimiento expreso de renuncia al desistimiento y usar los mismos SKU.
- **Política de las tiendas:** dentro de la app nativa, nada de enlaces a pagar en web (la regla de pagos externos de Apple en la UE tiene sus propias condiciones; no merece la pena para este juego).

### 5.6 Lista de SKU

**Dinero real (tiendas):**

| SKU | Tipo | Precio EUR | Entrega |
|---|---|---|---|
| `amago.gems_80` | consumible | 0,99 | 80 💎 de pago |
| `amago.gems_450` | consumible | 4,99 | 450 💎 |
| `amago.gems_1000` | consumible | 9,99 | 1.000 💎 |
| `amago.gems_2200` | consumible | 19,99 | 2.200 💎 |
| `amago.gems_6000` | consumible | 49,99 | 6.000 💎 |
| `amago.pass_premium` | consumible (1 por temporada en el servidor) | 4,99 | Premium de la temporada actual (o de la siguiente si `nextPrem`) |
| `amago.pass_plus` | consumible (1 por temporada) | 9,99 | Plus |
| `amago.pass_plus_upgrade` | consumible (1 por temporada, requiere Premium) | 4,99 | Premium → Plus |
| `amago.starter` | consumible (1 en total) | 1,99 | Pack de Inicio |
| `amago.bundle_hero` | consumible (1 por semana) | 4,99 | Pack de la semana |
| `amago.bundle_cosmetic` | consumible (1 por semana) | 2,99 | ídem |
| `amago.bundle_power` | consumible (1 por semana) | 4,99 | ídem |

**Internos (gemas, sin tienda):** `g.pass` 450, `g.skip1` 30, `g.skip5` 135, `g.skip10` 240, `g.coins300` 40, `g.coins1500` 180, `g.pp120` 50, `g.pp600` 220, `g.mega` 220, `g.hero.{id}` 30/60/110/180, `g.skin.{id}` 150/400, `g.pin.{id}` 60, `g.frame.{id}` 100, `g.trail.{id}` 120, `g.prints.{id}` 120.

### 5.7 Orden de trabajo sugerido

1. Tope por arena (`effLv`) y corrección del cambio de temporada. Valen sin monetización.
2. Gemas gratis, `GEM_SHOP`, cofres a la vista y probabilidades.
3. Pase a doble pista con Premium por gemas, `PAY_TEST`, cascada retroactiva y saltos.
4. Cosméticos (tintes primero, ilustradas después).
5. Edad, topes y página «Información de compras».
6. Guardado en la nube, RevenueCat, validación en el servidor y reembolsos. **Solo entonces** se activan los SKU en €.

**Indicadores a vigilar:**
- Conversión a Premium (objetivo 3–6 % de los activos mensuales) y tasa de compra del pack de inicio.
- Escalón medio al final de temporada, F2P frente a Premium. Si el F2P mediano baja del escalón 15, subir las fichas.
- Reembolsos por debajo del 2 %.
- Porcentaje de compras de menores que llegan al tope.

---

## 6. Lista legal y ética (UE y España)

> No es asesoramiento jurídico. Conviene revisarlo con un abogado de consumo y videojuegos antes del lanzamiento, porque varias normas están en tramitación.

**Cajas de botín y azar**
- [ ] Nada aleatorio a cambio de dinero real, gemas ni monedas compradas. Los cofres de la tienda y los de la pista Premium tienen contenido fijo y visible. Esto evita los problemas en Bélgica, donde la Comisión de Juego considera juego de azar las cajas de botín de pago, y en Países Bajos.
- [ ] España: la normativa sobre «mecanismos aleatorios de recompensa» (el anteproyecto de 2022 y el proyecto de ley de protección de menores en entornos digitales, que prevé prohibir a los menores el acceso a ellos) **sigue en tramitación**. Hay que comprobar su estado en la fecha de lanzamiento. Nuestro diseño ya cumple el supuesto más estricto.
- [ ] Probabilidades publicadas de todos los cofres aleatorios gratuitos (botón «i» y página «Información de compras»). Las piden las guías de Apple (3.1.1) y la política de Google Play.
- [ ] Clasificación PEGI 7 o similar con el descriptor «Compras dentro del juego», **no** «(incluye artículos aleatorios)». Revisar la IARC en Google Play.

**Precios y moneda virtual**
- [ ] Precios en € con **IVA incluido**: Directiva 98/6/CE y TRLGDCU (RDL 1/2007). En las tiendas se usa el precio localizado de `PAY.products()`, nunca uno escrito a mano. En la web, «IVA incluido».
- [ ] Equivalencia «≈ €» junto a todo precio en gemas. Packs alineados para no obligar a comprar de más. Sin caducidad. Saldo siempre visible. Esto sigue los principios clave de la red CPC sobre monedas virtuales en juegos (2025).
- [ ] Sin cuentas atrás falsas, sin precios «antes» inventados (el precio tachado tiene que ser real, como `CHESTS.price`), sin avergonzar al que dice que no (siempre «Ahora no», nunca «No, prefiero perder»), sin ofertas personalizadas según la frustración (nada tras derrotas). Directiva 2005/29/CE de prácticas comerciales desleales.
- [ ] Vigilar la propuesta europea de *Digital Fairness Act*, que puede endurecer las reglas de monedas virtuales y de diseño adictivo.

**Menores**
- [ ] **No exhortar directamente a los niños a comprar**: Anexo I, punto 28, de la Directiva 2005/29/CE y art. 30 de la Ley 3/1991 de Competencia Desleal. Los textos describen y dan el precio; los botones son neutros.
- [ ] Pregunta de edad neutral. Menores de 13: sin compras en la web y sin modales de venta. De 13 a 17: tope de 30 €/mes y confirmación siempre.
- [ ] Información para familias: «Cómo activar el control parental» con enlaces a Ask to Buy (Apple) y Family Link (Google).
- [ ] RGPD y LOPDGDD: en España, la edad de consentimiento digital es **14 años**. Por debajo, sin analítica que identifique ni publicidad personalizada. Analítica propia y anónima, o consentimiento parental. Si algún día se publica en la categoría «Niños» de Apple: nada de SDK de terceros de analítica o anuncios y control parental antes de comprar o abrir enlaces.
- [ ] Sin notificaciones push de ofertas. Sin publicidad de terceros en la versión de pago.

**Compras, desistimiento y reembolsos**
- [ ] En las tiendas, Apple y Google son quienes venden y gestionan los reembolsos. AMAGO tiene que procesar sus avisos de reembolso (`revokeSku`) y no penalizar más allá de retirar lo reembolsado.
- [ ] En la web (si se activa): derecho de desistimiento de 14 días en contenido digital (Directiva 2011/83/UE, art. 16 m; TRLGDCU, art. 103 m). Solo se pierde con consentimiento expreso y reconocimiento antes de la entrega inmediata: casilla sin marcar y justificante por email.
- [ ] «Restaurar compras» visible (lo exige Apple). Guardado en la nube antes de cobrar dinero real.
- [ ] Guardar el registro de transacciones (identificador, SKU, fecha, importe) y dar un contacto de soporte para incidencias de compra, en la página «Información de compras» y en la ficha de la tienda.
- [ ] Condiciones de uso y política de privacidad en español, enlazadas desde Ajustes y desde la tienda.

**Juego justo (ética del diseño)**
- [ ] Tope de nivel por arena (`LV_CAP`) activo antes de vender ⚡.
- [ ] El héroe de temporada se consigue gratis en la misma temporada y está equilibrado (44–55 % en la simulación).
- [ ] Nada de poder exclusivo de pago. Lo exclusivo es solo cosmético (skins, pines, marcos, huellas, estelas). Las huellas cosméticas no reducen la legibilidad: se prueba en daltonismo y a baja resolución.
- [ ] Premios alcanzados y no reclamados se entregan al final de la temporada.
- [ ] Revisión trimestral de las métricas de gasto de menores y de los «grandes gastadores», con avisos de gasto (50 €/mes).
