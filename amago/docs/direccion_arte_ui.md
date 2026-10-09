# AMAGO — Revisión de UI de menús y spec de rediseño (nivel Supercell)

Revisado: a_home, b_heroes, c_sheet, d_lvup, e_shop/e_shop2, f_road, g_pass, h_missions, i_box0/3/6, z_pick, end_win (after = solo referencia).
CSS revisado: bloque `menús (estilo Supercell)` (líneas 466-723 de `amago/index.html`) + `.sheet/.modal` (l.198-201) + `RAR` (l.969).

---

## 0. Veredicto en una frase

Los **assets** ya están cerca de Supercell (héroes ilustrados, iconos 3D, cofres): lo que está a nivel de prototipo es **todo lo que hay entre ellos**. Los paneles son planos, todo tiene el mismo contorno y la misma sombra, el fondo es el mismo patrón de rayas en todas las pantallas, se mezclan emojis con renders, no hay jerarquía de color (cada sección tiene su arcoíris) y casi todo se mueve a la vez. Parece una plantilla bien hecha, no un juego con dirección de arte.

### Problemas globales (en todas las pantallas)

1. **Fondo genérico.** `.mbg` con rayas diagonales azules en todas las pantallas. No hay mundo, ni suelo, ni luz. Supercell siempre pone un escenario (diorama 3D, arena difuminada) o al menos un fondo temático por pantalla.
2. **Un único material.** Paneles, tarjetas, filas, pastillas y botones comparten borde de 3 px `#0b0a1f` + sombra dura de 4-6 px. Sin brillo interior, sin bisel inferior, sin sombra suave, todo pesa lo mismo y nada destaca. Supercell usa 3 o 4 "materiales": panel oscuro, panel claro (papel/hielo), botón brillante y "joya" premium.
3. **Emojis mezclados con renders 3D.** ⚙️ 🦸 🏠 ⚔️ 👥 ❤️ 💧 👟 💥 🔔 ⚡ 🔒 🎁 ⭐ ✅ 🏆. Se ven distintos en cada sistema operativo, su estilo no casa con los renders y abaratan al instante. Es el problema más barato de arreglar y el que más se nota.
4. **Color sin significado.** El verde se usa a la vez para reclamar, mejorar, el regalo, la rareza Rara, la cinta "Regalo diario" y el botón Tienda. El morado, para Poder, Pase, Épico, la cinta "Cofres" y el nivel. El jugador no aprende qué significa cada color.
5. **Tipografía sin escala.** Lilita aparece en 11, 12, 13, 14, 15, 16, 17, 18, 20, 22, 24, 28, 30, 32, 38, 40 y 50 px. El contorno con 8 `text-shadow` de 2 px deja los bordes dentados. Los textos secundarios en Nunito de 11-13 px, color `#aab2e6`/`#bcd0ff` sobre azul, apenas se leen.
6. **Ruido de movimiento.** Laten a la vez los badges (`badge` infinito), las flechas ↑, los cofres (`hop`), el brillo (`shine`), el botón de luchar (`pulse`) y los rayos. Cuando todo se mueve, nada llama la atención.
7. **Badges rojos por todas partes.** En la home hay 5 o 6 contadores rojos a la vez. Pierden valor como alerta.
8. **Huecos vacíos.** En home, level-up, cofre, pick y victoria queda vacío entre el 25 % y el 40 % inferior, o hay espacios muertos entre bloques. Supercell llena la pantalla con escenario o compone en vertical con intención.

---

## 1. Problemas por pantalla

### a_home (Inicio)
1. **El héroe flota sobre un disco azul cian plano** (parece un `ellipse` CSS) sin sombra de contacto, sin suelo y sin luz. Es lo más barato de toda la pantalla.
2. **Iconos repetidos.** El cofre aparece 4 veces (Tienda lateral, ¡Ábrelo!, cofre de llaves, pestaña Tienda). Tienda y Pase están duplicados entre la columna lateral y la barra de pestañas. Hay demasiadas puertas a los mismos sitios.
3. **Barra de pestañas mixta.** 🦸 y 🏠 son emojis junto a renders 3D. La barra es una franja plana oscura y la pestaña activa es un rectángulo azul sin volumen.
4. **"Pradera Aprendiz" flota como texto suelto** a la derecha. La arena es lo más aspiracional que tienes y está tratada como una etiqueta de depuración. "ver ficha" en la placa del héroe también suena a texto de desarrollo.
5. **El botón JUGAR** tiene texto oscuro sin contorno, el amarillo no tiene brillo y el botón de modo usa el emoji ⚔️. Faltan volumen y el "caramelo" típico de Supercell.
6. **Los ~100 px vacíos** entre la base del pedestal y la placa del héroe, más los rayos casi invisibles, dejan el centro sin composición.

### b_heroes (Colección)
1. **Todas las comunes son el mismo rectángulo azul plano.** La rareza es una franja oscura con texto de 10 px. La rareza debería ser el marco de la carta, no una etiqueta.
2. **El círculo verde ↑ tapa el arte** (la cabeza de Muro, el arco de Flecha) y late sin parar en todas las cartas a la vez.
3. **Las barras de Poder "45/20", "45/10"** están todas llenas y en verde. Repiten la misma información 6 veces y ensucian la carta.
4. **⭐ emoji para "favorito"** y 🔒 emoji en las bloqueadas.
5. **La línea de ayuda** ("Sube de nivel con ⚡ Puntos de Poder y 🪙 monedas") es texto de tutorial fijo. Ocupa sitio y queda apretada.
6. **La barra de pestañas tapa la última fila** (Ojo/Truco cortadas): falta `padding-bottom`.

### c_sheet (Ficha + mejora)
1. **Parece un formulario.** Las filas `.srow` son rectángulos translúcidos con etiquetas emoji (❤️ 💧 👟 💥). Sin iconos reales ni jerarquía, todo con el mismo peso.
2. **Corte duro entre la cabecera de color y el cuerpo azul.** Los rayos de la cabecera están cortados por un rectángulo. El héroe (170 px) es pequeño para ser la pantalla de su ficha.
3. **"+3 % +6 %"** no se entiende a primera vista (¿actual → siguiente?). Faltan flecha y color de "delta".
4. **Dos botones enormes del mismo tamaño** (MEJORAR y Cerrar). Cerrar debería ser una X, no un botón azul de ancho completo.
5. **Las 10 barritas de nivel** (`lvdots`) son diminutas y oscuras. Parecen una barra de carga, no un progreso.
6. **El coste dentro del botón** (⚡20 🪙30) usa una tipografía de 12 px con poco contraste.

### d_lvup (Subida de nivel)
1. **Momento de recompensa sin celebración.** Héroe pequeño, hexágono plano, título y "Toca para seguir". El 40 % inferior está vacío.
2. **No hay comparación antes → después** de las estadísticas. "+6 %" sin contexto.
3. **Los rayos casi no se ven.** No hay partículas persistentes, ni foco detrás del héroe, ni cinta de "¡NIVEL SUPERADO!".
4. **El hexágono de nivel no "cambia"** (no hay animación de 2 → 3), solo aparece.

### e_shop / e_shop2 (Tienda)
1. **Arcoíris de cintas.** Verde (Regalo), naranja (Ofertas), morada (Cofres) y azul (Héroes). Cada cabecera tiene un color distinto y se parecen a botones.
2. **Tarjetas de colores planos sin marco interior.** Morado/azul/naranja y verde/azul/naranja seguidos: ninguna destaca porque todas gritan.
3. **El botón de precio desactivado (gris)** parece roto ("390 ~~550~~" ilegible). Supercell mantiene el botón y pinta el número en rojo.
4. **El banner de regalo**, con el botón verde GRATIS sobre fondo verde, tiene poco contraste y ocupa 110 px para un cofre pequeño.
5. **Sin oferta destacada.** Todas las tarjetas miden lo mismo. Falta un "hero offer" grande arriba con temporizador, que es la base de toda tienda de Supercell.
6. **Etiquetas `.tag` de 10 px** ("OFERTA", "-30 %") pegadas al borde superior. Se leen como una franja y no como un sello.

### f_road (Camino de trofeos)
1. **Parece una lista de ajustes**: filas navy idénticas. No se ve como un camino ni como un viaje.
2. **7 botones RECLAMAR verdes idénticos seguidos.** Es ruido y trabajo para el jugador. Falta "Reclamar todo".
3. **El raíl de progreso es una línea oscura de 10 px** sin relleno visible ni marcador de "estás aquí" (avatar).
4. **Los hitos de arena son una fila naranja más.** Deberían ser el clímax visual (banner grande con el render de la arena).
5. **🔒 emoji gris diminuto.** Los textos largos se parten en 2 líneas ("40 Puntos de / Poder").

### g_pass (Pase)
1. **Mismo componente que el camino de trofeos.** No se distingue de f_road, salvo por el título que queda fuera de pantalla.
2. **30 filas casi iguales con candado.** Nada da ganas de llegar al final ni hay recompensa de clímax en el escalón 30.
3. **Sin pista premium.** Todo el valor de monetización del pase está sin usar (ver sección 5).
4. **Recompensas repetitivas** (PP, monedas, cofre) y con el mismo tamaño en todos los escalones.

### h_missions (Misiones diarias)
1. **El CTA principal es CERRAR** (amarillo enorme). La jerarquía está invertida: el amarillo debe ser para acciones de valor.
2. **Filas sin icono de tipo de misión.** Solo texto, una barra oscura con "0/4" de 10 px dentro y la recompensa a la derecha.
3. **El panel azul claro** sobre el fondo oscuro del Pase no casa con ningún otro modal (`.sheet` usa `--panel2`).
4. **Sin recompensa por completar las 3** (cofre bonus) y sin estado visual de "lista para cobrar" en la fila.

### i_box0 / i_box3 / i_box6 (Apertura de cofre)
1. **El fondo es un degradado navy con rayos muy tenues.** Falta un foco de luz detrás del cofre y un suelo donde se apoye.
2. **"Toca para abrir · 2"** en 14 px amarillo: el contador de toques no es visual (faltan pips o grietas de luz).
3. **La recompensa aparece encima de un cofre más pequeño** que "baja". La lectura es rara: el objeto debería salir del cofre y el cofre quedarse anclado abajo.
4. **No hay tarjeta de recompensa** (marco, rareza o brillo detrás del icono) ni cuenta numérica (+30 aparece de golpe).
5. **El contador de "objetos restantes"** (arriba derecha, cofre 40 px + "1") pasa desapercibido. El tercio inferior está vacío.
6. **Halo/flecos blancos** en el contorno del cofre en i_box0. Hay que revisar el matte o alpha de los `.webp` (premultiplicado / *edge bleed*).

### z_pick (Elegir héroe)
1. **El botón ¡A LUCHAR! es rosa-rojo**, un color nuevo para el CTA principal que en Inicio es amarillo. Rompe el sistema.
2. **El consejo es una caja blanca de sistema** con emoji 🦸, ajena a la paleta. Debajo del botón quedan ~170 px vacíos.
3. **Los chips de héroe (56 px) son pequeños** y la selección se marca solo con un borde amarillo. Las estrellas de ronda de las esquinas casi no se ven.
4. **Las estadísticas repiten la ficha** con emojis (⚡ ❤️ 👟 💥 🔔). Debería ser el mismo componente de "stat tiles" que la ficha.

### end_win (Victoria)
1. **"¡VICTORIA!" es amarillo plano** con contorno fino: sin degradado, sin cinta y sin entrada animada.
2. **Los héroes flotan sin suelo ni foco.**
3. **4 botones apilados** (cofre, "🎁 Premios en el camino", JUGAR OTRA, Volver al inicio): demasiadas opciones.
4. **Iconos confusos.** La estrella amarilla (XP) y la estrella cian (fichas del pase) se confunden. "84 +9" no anima el conteo.
5. **Las filas de recompensa** son una tabla. Deberían ser fichas de recompensa que "caen" una a una.

---

## 2. Sistema de diseño

### 2.1 Paleta (tokens)

```css
:root{
  /* tinta y contorno */
  --ink:#0E0B2A;           /* contorno de todo */
  --ink-soft:rgba(8,6,32,.45);

  /* fondo / mundo */
  --sky-1:#3A7BFF; --sky-2:#1D46C8; --sky-3:#0E1F72; --abyss:#060A2E;

  /* panel oscuro (material 1) */
  --pnl-hi:#3343B8; --pnl-1:#26329A; --pnl-2:#1B2477; --pnl-lo:#121957; --pnl-edge:#5A6CF0;
  /* panel claro "hielo" (material 2: cuerpos de modal, filas de stats) */
  --ice-1:#EAF2FF; --ice-2:#C7D8FF; --ice-edge:#FFFFFF; --ice-ink:#1B2363;
  /* hueco/pozo (barras, slots vacíos) */
  --well:#0A0F3A;

  /* acciones (solo por función) */
  --y-1:#FFE95C; --y-2:#FFC21A; --y-lip:#D88700;     /* PRIMARIO: jugar, comprar */
  --g-1:#8CFF6E; --g-2:#2FCB45; --g-lip:#178A2B;     /* POSITIVO: reclamar, mejorar, gratis */
  --b-1:#6FD3FF; --b-2:#2A8BF2; --b-lip:#1656B0;     /* SECUNDARIO: info, cambiar, ver */
  --r-1:#FF7E6E; --r-2:#EC3A44; --r-lip:#9E1E2A;     /* DESTRUCTIVO / alerta */
  --d-1:#B7BDD8; --d-2:#8A91B4; --d-lip:#5C6386;     /* DESACTIVADO */

  /* premium */
  --gold-1:#FFF6B8; --gold-2:#FFD34A; --gold-3:#F3A01B; --gold-lip:#A65A00; --velvet-1:#3A1466; --velvet-2:#16062E;

  /* rareza (marco de carta + luz) */
  --rar-com:#7FA8D9; --rar-com-d:#3E5C97;
  --rar-raro:#41D97A; --rar-raro-d:#167A45;
  --rar-epi:#B566FF; --rar-epi-d:#5C1FB0;
  --rar-leg:#FFC21A; --rar-leg-d:#C46A00;

  /* monedas del juego: un color = una moneda, nunca otra cosa */
  --coin:#FFC21A; --power:#C46BFF; --trophy:#FFAE1F; --token:#3EE6FF; --xp:#7CFFB2;

  /* texto */
  --tx-1:#FFFFFF; --tx-2:#CFDAFF; --tx-3:#93A2DE; --tx-up:#7CFF8A; --tx-dn:#FF6B78; --tx-hl:#FFE45C;
}
```

**Reglas de color**
- Amarillo = la acción principal de la pantalla (máximo uno por pantalla). Verde = obtener o mejorar. Azul = secundario. Rojo solo para alertas y badges. Gris solo para "imposible ahora".
- El morado deja de ser color de UI: queda solo para Poder (moneda) y rareza Épica. El Pase pasa a cian (fichas) y oro (premium).
- Cabeceras de sección: siempre la misma cinta (ver 2.3), sin colores distintos por sección.

### 2.2 Tipografía

| Estilo | Fuente | Tamaño / interlineado | Tratamiento |
|---|---|---|---|
| `t-hero` (VICTORIA, NIVEL 3) | Lilita | 56/1 | relleno con degradado + contorno de 7 px + sombra 0 5 px |
| `t-h1` (título de pantalla) | Lilita | 32/1 | blanco, contorno de 5 px, sombra 0 3 px |
| `t-h2` (cinta, nombre en carta grande) | Lilita | 22/1 | blanco, contorno de 4 px |
| `t-btn-l` (JUGAR) | Lilita | 40/1 | blanco, contorno de 5 px y sombra en el color del labio del botón |
| `t-btn` | Lilita | 20/1 | blanco, contorno de 4 px |
| `t-num` (cifras, precios) | Lilita | 18/1 | blanco, contorno de 3 px, `font-variant-numeric:tabular-nums` |
| `t-label` | Nunito 900 | 13/1.2 | `--tx-2`, sin contorno, `text-shadow:0 1px 0 var(--ink-soft)` |
| `t-small` | Nunito 800 | 12/1.2 | `--tx-3` (mínimo absoluto 12 px) |

Solo estos 8 tamaños: 12, 13, 18, 20, 22, 32, 40 y 56. Lilita solo para títulos, números y botones. Nunito para todo lo descriptivo. En mayúsculas: solo botones y cintas.

**Contorno limpio** (sustituye `.out` y sus 8 sombras):

```css
/* contorno real: duplicamos el texto con data-t para que el trazo quede detrás del relleno */
.stroke{position:relative;color:#fff;z-index:0}
.stroke::before{content:attr(data-t);position:absolute;inset:0;z-index:-1;
  -webkit-text-stroke:var(--sw,5px) var(--ink);color:var(--ink);
  text-shadow:0 var(--sd,3px) 0 var(--ink)}
/* título con relleno de degradado (VICTORIA) */
.t-hero{font:56px/1 var(--f-game);--sw:8px;--sd:6px}
.t-hero>span{background:linear-gradient(#FFF7B0 0%,#FFD84A 45%,#FF9E1A 100%);
  -webkit-background-clip:text;background-clip:text;color:transparent}
/* uso: <h1 class="stroke t-hero" data-t="¡VICTORIA!"><span>¡VICTORIA!</span></h1> */
```
(Alternativa en navegadores modernos: `-webkit-text-stroke:5px var(--ink); paint-order:stroke fill;`. Hay que probarla en iOS Safari antes de adoptarla.)

### 2.3 Paneles y tarjetas

```css
/* MATERIAL 1: panel oscuro con volumen */
.pnl{position:relative;border-radius:18px;border:3px solid var(--ink);
  background:linear-gradient(180deg,var(--pnl-hi) 0%,var(--pnl-1) 30%,var(--pnl-2) 100%);
  box-shadow:inset 0 2px 0 rgba(255,255,255,.22),     /* luz superior */
             inset 0 0 0 1px rgba(120,140,255,.25),    /* filo interior */
             inset 0 -5px 0 rgba(0,0,0,.22),           /* bisel inferior */
             0 4px 0 var(--ink),                       /* espesor */
             0 12px 20px -6px rgba(0,0,30,.55)}        /* sombra suave al suelo */
.pnl::before{content:"";position:absolute;inset:3px 3px 55% 3px;border-radius:14px 14px 50% 50%/14px 14px 18px 18px;
  background:linear-gradient(rgba(255,255,255,.12),rgba(255,255,255,0));pointer-events:none}

/* MATERIAL 2: panel claro "hielo" (cuerpos de modal, tiles de stats) */
.ice{border-radius:14px;border:3px solid var(--ink);color:var(--ice-ink);
  background:linear-gradient(180deg,var(--ice-1),var(--ice-2));
  box-shadow:inset 0 2px 0 #fff,inset 0 -4px 0 rgba(27,35,99,.15),0 3px 0 var(--ink)}

/* POZO (barras, slots vacíos) */
.well{background:var(--well);border:2px solid var(--ink);border-radius:8px;
  box-shadow:inset 0 3px 0 rgba(0,0,0,.45)}

/* barra de progreso con brillo */
.bar{height:14px}.bar>u{display:block;height:100%;border-radius:6px;
  background:linear-gradient(180deg,rgba(255,255,255,.55) 0 35%,transparent 36%),linear-gradient(90deg,var(--c1,#3EE6FF),var(--c2,#1F8BF2))}

/* CINTA de sección (una sola para toda la app) */
.ribbon{position:relative;margin:14px auto 8px;padding:6px 26px;width:max-content;
  font:22px/1 var(--f-game);color:#fff;background:linear-gradient(#2E3DAE,#1A2278);
  border:3px solid var(--ink);border-radius:6px;box-shadow:0 3px 0 var(--ink)}
.ribbon::before,.ribbon::after{content:"";position:absolute;top:6px;width:18px;height:100%;z-index:-1;
  background:#121957;border:3px solid var(--ink)}
.ribbon::before{left:-14px;clip-path:polygon(0 0,100% 0,100% 100%,0 100%,40% 50%)}
.ribbon::after{right:-14px;clip-path:polygon(0 0,100% 0,60% 50%,100% 100%,0 100%)}

/* CARTA con marco de rareza (héroes, ofertas) */
.card{--rc:var(--rar-com);--rd:var(--rar-com-d);position:relative;border-radius:16px;
  border:3px solid var(--ink);padding:4px;background:linear-gradient(var(--rc),var(--rd));
  box-shadow:inset 0 2px 0 rgba(255,255,255,.5),0 4px 0 var(--ink),0 10px 16px -6px rgba(0,0,30,.5)}
.card .art{position:relative;border-radius:11px;height:120px;overflow:visible;
  background:radial-gradient(70% 60% at 50% 40%,color-mix(in srgb,var(--rc) 60%,#fff) 0%,var(--rd) 75%,#0E1450 120%);
  box-shadow:inset 0 0 0 2px rgba(0,0,0,.25)}
.card .art img{position:absolute;left:50%;bottom:0;height:136px;transform:translateX(-50%);   /* el arte se sale por arriba */
  filter:drop-shadow(0 6px 0 rgba(0,0,0,.25))}
.card .plate{margin-top:4px;border-radius:9px;background:linear-gradient(#1F2A85,#141B5E);padding:4px 6px}
.card.raro{--rc:var(--rar-raro);--rd:var(--rar-raro-d)}
.card.epi{--rc:var(--rar-epi);--rd:var(--rar-epi-d)}
.card.leg{--rc:var(--rar-leg);--rd:var(--rar-leg-d)}
```

Radios: 22 px en modales, 18 px en paneles, 16 px en cartas y botones grandes, 12 px en botones pequeños y pastillas, 8 px en pozos y barras. Contorno: siempre 3 px (2 px solo en elementos de menos de 32 px).

### 2.4 Botones

```css
.btn{--t:var(--y-1);--b:var(--y-2);--l:var(--y-lip);
  position:relative;display:inline-flex;align-items:center;justify-content:center;gap:6px;
  font:20px/1 var(--f-game);color:#fff;padding:12px 20px 16px;border-radius:16px;
  border:3px solid var(--ink);cursor:pointer;overflow:hidden;
  background:linear-gradient(180deg,var(--t) 0%,var(--b) 70%);
  box-shadow:inset 0 -6px 0 var(--l),inset 0 2px 0 rgba(255,255,255,.7),
             0 4px 0 var(--ink),0 10px 14px -4px rgba(0,0,30,.45);
  transition:transform 80ms ease-out,box-shadow 80ms ease-out}
.btn::before{content:"";position:absolute;left:6px;right:6px;top:3px;height:42%;border-radius:12px 12px 6px 6px;
  background:linear-gradient(rgba(255,255,255,.6),rgba(255,255,255,.1));pointer-events:none}
.btn:active{transform:translateY(3px) scale(.98);
  box-shadow:inset 0 -3px 0 var(--l),inset 0 2px 0 rgba(255,255,255,.7),0 1px 0 var(--ink),0 4px 8px -4px rgba(0,0,30,.45)}
.btn.green{--t:var(--g-1);--b:var(--g-2);--l:var(--g-lip)}
.btn.blue {--t:var(--b-1);--b:var(--b-2);--l:var(--b-lip)}
.btn.red  {--t:var(--r-1);--b:var(--r-2);--l:var(--r-lip)}
.btn:disabled,.btn.off{--t:var(--d-1);--b:var(--d-2);--l:var(--d-lip);cursor:default}
.btn:disabled:active{transform:none}
.btn.xl{font-size:40px;padding:16px 24px 22px;border-radius:20px}  /* JUGAR */
.btn.sm{font-size:16px;padding:7px 12px 10px;border-radius:12px}
/* texto del botón: blanco con contorno en el color del labio, no texto oscuro */
.btn>b{-webkit-text-stroke:0;text-shadow:0 2px 0 var(--l),0 0 2px var(--ink),0 3px 0 var(--ink)}

/* PREMIUM: oro + destello */
.btn.premium{--t:var(--gold-1);--b:var(--gold-3);--l:var(--gold-lip);
  background:linear-gradient(180deg,var(--gold-1) 0%,var(--gold-2) 40%,var(--gold-3) 100%)}
.btn.premium::after{content:"";position:absolute;top:-30%;bottom:-30%;width:28%;left:-40%;
  background:linear-gradient(100deg,transparent,rgba(255,255,255,.85),transparent);transform:skewX(-20deg);
  animation:sheen 3.2s 1s cubic-bezier(.6,0,.2,1) infinite}
@keyframes sheen{0%,70%{left:-40%}100%{left:130%}}

/* precio sin dinero suficiente: el botón sigue igual y el número pasa a rojo */
.btn .price.short{color:var(--tx-dn)}

/* botón cerrar redondo (sustituye a "Cerrar"/"CERRAR") */
.x{position:absolute;top:-12px;right:-12px;width:40px;height:40px;border-radius:50%;
  border:3px solid var(--ink);background:linear-gradient(var(--r-1),var(--r-2));
  box-shadow:inset 0 -4px 0 var(--r-lip),inset 0 2px 0 rgba(255,255,255,.6),0 3px 0 var(--ink)}
```

Jerarquía por pantalla: **1 primario** (amarillo o verde), como mucho **1 secundario** (azul, más pequeño) y el resto pasa a iconos o enlaces. "Cerrar" siempre como `.x` o con tap fuera, nunca como botón grande.

### 2.5 Iconografía
- **Cero emojis en la UI.** Todo icono es un render 3D (`ui/*.webp`) o un SVG con el mismo lenguaje: contorno de 3 px `--ink`, relleno con degradado vertical (claro arriba), brillo blanco elíptico arriba a la izquierda y sombra interior abajo.
- Tamaños fijos: 20 (inline en texto), 28 (pastillas, costes), 40 (filas), 56 (botones laterales), 96-140 (recompensa).
- **Un concepto = un icono.** Cofre = recompensa. Tienda = bolsa o puesto, no un cofre. Fichas del pase ≠ XP ≠ favorito (hoy hay 3 estrellas distintas).
- Los iconos inline nunca se desaturan con `grayscale` para indicar "no tienes". Se usa el pozo vacío o un número rojo.
- Badges: rojo con número solo para "acción pendiente". Verde "GRATIS" solo para el regalo. Máximo 3 badges visibles por pantalla.

### 2.6 Fondo
- **Inicio:** diorama de la arena actual (render de Blender de la isla del juego, como en `after.png`) a pantalla completa, con *depth-of-field* y tono azulado. Encima, un foco cálido detrás del héroe (`radial-gradient` amarillento con `mix-blend-mode:screen`) y un suelo: pedestal renderizado (isla de hierba con piedra) con sombra de contacto.
- **Resto de menús:** sustituir las rayas por un patrón de **iconos del juego** (estrellas, cofres y coronas en SVG al 5 % de opacidad, en mosaico de 120 px, deriva lenta de 60 s), sobre `radial-gradient(130% 80% at 50% 0%, var(--sky-1), var(--sky-2) 45%, var(--sky-3) 85%, var(--abyss))` y viñeta.
- **Pantallas de recompensa** (cofre, nivel, victoria): fondo propio por tipo (azul para cofre, morado para nivel, oro para victoria) con rayos de 2 capas (lentos y rápidos en sentido contrario), suelo luminoso elíptico y motas flotando.

```css
.bg-menu{position:fixed;inset:0;z-index:-1;background:
  radial-gradient(90% 60% at 50% 35%,rgba(255,255,255,.10),transparent 60%),
  radial-gradient(130% 80% at 50% 0%,var(--sky-1),var(--sky-2) 45%,var(--sky-3) 85%,var(--abyss))}
.bg-menu::before{content:"";position:absolute;inset:-120px;opacity:.06;
  background:url(ui/pattern.svg) 0 0/120px 120px;animation:drift 60s linear infinite}
.bg-menu::after{content:"";position:absolute;inset:0;
  background:radial-gradient(120% 90% at 50% 40%,transparent 55%,rgba(4,6,36,.7))}
@keyframes drift{to{transform:translate(120px,120px)}}
.godrays{position:absolute;width:900px;height:900px;left:50%;top:42%;margin:-450px 0 0 -450px;
  background:repeating-conic-gradient(rgba(255,240,180,.22) 0 6deg,transparent 6deg 15deg);
  -webkit-mask:radial-gradient(closest-side,#000 15%,transparent 95%);mask:radial-gradient(closest-side,#000 15%,transparent 95%);
  animation:spin 30s linear infinite}
.godrays.b{animation-direction:reverse;animation-duration:45s;opacity:.6;filter:blur(2px)}
.floorglow{position:absolute;left:50%;width:300px;height:70px;margin-left:-150px;border-radius:50%;
  background:radial-gradient(closest-side,rgba(255,240,180,.55),transparent)}
```

### 2.7 Movimiento

| Evento | Duración | Curva | Detalle |
|---|---|---|---|
| Pulsar botón | 80 ms bajada | `ease-out` | translateY 3 px, scale .98 |
| Soltar botón | 160 ms | `cubic-bezier(.34,1.56,.64,1)` | rebote hasta 1.0 |
| Entrar pantalla | 220 ms | `cubic-bezier(.2,.8,.2,1)` | contenido de y+16 px con opacidad 0→1; lista escalonada 30 ms por elemento (máximo 8) |
| Abrir modal | 280 ms | `cubic-bezier(.34,1.56,.64,1)` | scale .85→1, fondo 180 ms con fade |
| Cerrar modal | 140 ms | `ease-in` | scale 1→.92, opacidad 0 |
| Recompensa: aparición | 450 ms | anticipación (scale .8, 120 ms) → 1.15 (200 ms) → 1 (130 ms) | más destello blanco de 120 ms |
| Contador numérico | 600-900 ms | `ease-out` (cúbica) | tick sonoro cada ~5 % |
| Moneda vuela a la barra superior | 550 ms | arco bezier | al llegar, *bump* de la pastilla: 180 ms, scale 1.2 |
| Idle de CTA | brillo cada 3.5 s | — | **solo el CTA principal** |
| Badge | bote de 500 ms cada 4 s | `ease-out` | con desfase aleatorio, no latido continuo |
| Cofre en reposo | salto de 1.6 s cada 3 s | — | solo si hay cofre por abrir |

Regla: **como mucho un elemento en loop por pantalla** (el CTA principal). Respetar `prefers-reduced-motion` (quitar rayos, saltos y brillo).

```css
:root{--e-pop:cubic-bezier(.34,1.56,.64,1);--e-out:cubic-bezier(.2,.8,.2,1)}
@keyframes appear{from{opacity:0;transform:translateY(16px)}}
.stagger>*{animation:appear .22s var(--e-out) both;animation-delay:calc(var(--i,0)*30ms)}
@keyframes reward{0%{transform:scale(.3);opacity:0}25%{transform:scale(.8);opacity:1}65%{transform:scale(1.15)}100%{transform:scale(1)}}
@media (prefers-reduced-motion:reduce){*{animation-duration:.01ms!important;animation-iteration-count:1!important}}
```

---

## 3. Rediseño por pantalla (viewport 390×844)

Común: barra superior de 0 a 56 px (margen lateral de 12) y barra de pestañas de 760 a 844 (76 px + safe area). Contenido con `padding-bottom:96px` para que nada quede tapado.

**Barra superior (h 48):** perfil 148×44 (avatar 40 con marco por nivel, nombre `t-label` 14, barra XP de 6 px en `--xp`), pastilla de monedas 96×34 y de poder 84×34 (icono de 40 que sobresale por la izquierda, número `t-num`, "+" verde de 18 px a la derecha para ir a la tienda), botón menú 40×40 con SVG de engranaje o hamburguesa.

**Barra de pestañas:** fondo `.pnl` sin bordes laterales y con borde superior de 3 px. 5 slots de 78 px. Icono de 44 px. Solo la pestaña activa muestra la etiqueta y se eleva: panel claro 86×84 que sobresale 14 px, icono a 56 px y rebote de 160 ms. Las inactivas, al 75 % de brillo.

### Inicio
- **56-96:** fila con el camino de trofeos (230×36: trofeo, 75, barra dorada y siguiente recompensa) y, a la derecha, el **banner de arena** 120×36 con miniatura de la arena y su nombre en dos líneas (`t-small`). Al pulsar, abre el camino.
- **96-600: escenario.** Diorama de fondo y pedestal renderizado (isla de 260×80, con su sombra) centrado en y≈520. Héroe 3D de ~330 px de alto con foco cálido detrás y 2 capas de rayos suaves. Al tocarlo hace una animación de ataque (ya existe).
  - Columna izquierda (x 12, y 110): **Misiones** 64×64 con anillo de progreso (2/3) y **Pase** 64×64 con mini barra de fichas. Se quita Tienda (ya está en las pestañas).
  - Columna derecha (x 314, y 110): **Cofre por abrir** 76×76 con salto y contador. Debajo, **Cofre de llaves**: módulo 76×92 con el cofre y 3 ranuras de llave en pozo (las llaves conseguidas se ven a color con brillo).
- **540-600:** placa del héroe en cinta 230×56: hexágono de poder 44, nombre `t-h2` y, debajo, "🏆" sustituido por icono de trofeo + número. Se quita "ver ficha"; la placa tiene una flecha ▸ SVG.
- **640-736:** fila de juego. Botón de modo 120×80 (`.btn.blue`, icono de modo de 40 px, "Bot fácil" `t-label` y "MODO" pequeño) y **JUGAR** 238×80 (`.btn.xl`, texto blanco con contorno, brillo cada 3.5 s, y un pequeño icono de espadas a la izquierda del texto).
- **Animación:** entrada del héroe (cae al pedestal con *squash*, 400 ms), botones laterales escalonados y "bump" de las pastillas al volver de una recompensa.

### Héroes
- **56-108:** título "Héroes" (`t-h1`), contador 5/8 en pastilla y botón "i" 32×32 que abre la ayuda (se quita la línea de tutorial).
- **Rejilla de 3 columnas:** cartas `.card` de 114×164, gap 10, márgenes laterales 12.
  - Arte 102 de alto con el héroe a 120 px saliéndose por arriba. Fondo radial del color de la rareza.
  - Placa inferior: nombre `t-btn` 16, hexágono de nivel 26 px solapado a la izquierda del arte (abajo izquierda) y barra de PP de 8 px.
  - **Si se puede mejorar:** la placa entera pasa a verde con la flecha SVG ↑ y "MEJORAR" (sin círculo flotante sobre el arte). Solo la carta con mejora más barata hace un bote cada 4 s.
  - Favorito: pin SVG de corona de 22 px en la esquina superior izquierda del marco.
  - Bloqueado: marco gris pizarra, silueta con un 30 % de luz de rareza detrás y chip inferior "🏆 110" con icono de trofeo y candado SVG.
- **Animación:** entrada escalonada de las cartas (30 ms). Al pulsar, la carta se "levanta" (scale 1.04, 120 ms) antes de abrir la ficha.

### Ficha del héroe (pantalla completa, no modal)
- **0-56:** botón atrás 40×40 (flecha SVG), nombre centrado `t-h1` y chip de rareza.
- **56-380:** escenario con rayos del color de la rareza, pedestal, héroe 3D a 280 px (canvas de la home reutilizado) y swipe ◀ ▶ para cambiar de héroe.
- **380-430:** fila de nivel. Hexágono de 56 a la izquierda; a la derecha, una barra de 10 segmentos de 26×12 en pozo (rellenos en morado de poder, el siguiente parpadeando).
- **440-640:** **stat tiles** `.ice` en rejilla 2×2 de 171×88 (Vida, Elixir, Velocidad, Ataque). Cada uno con icono 3D de 36, valor `t-num` 22 en `--ice-ink`, etiqueta `t-small`, y si hay mejora un chip verde "▲ +6 %" en la esquina. La tile de Ataque es ancha (358×88) con el patrón de la cuadrícula y "quita 1 · coste 3".
- **650-680:** descripción del héroe, `t-label`, 2 líneas como máximo.
- **690-760:** **MEJORAR** `.btn.green` 358×72 con dos chips de coste dentro (icono 28 + número; rojo si falta). Si no se puede, el botón queda gris y debajo aparece "Te faltan 12 ⚡" en `t-small`.
- "Poner en portada" pasa a icono de corona 40×40 junto al nombre.
- **Animación:** al pulsar MEJORAR, los chips de coste vuelan al botón, carga de 400 ms (barra que se llena dentro del botón) y transición a Level-up.

### Level-up
- Fondo morado de recompensa con 2 capas de rayos y suelo luminoso.
- **0-90:** cinta dorada "¡NIVEL SUPERADO!" de 300×64 que entra con caída y rebote a 200 ms.
- **110-460:** héroe 320 px que sube desde y+60 con un destello, más partículas en ráfaga.
- **470-560:** hexágono 96 px. El "2" gira 90° y sale como "3" (flip de 300 ms) con 12 chispas SVG.
- **580-720:** **tarjeta de comparación** `.pnl` 330×130 con filas "Vida 3 → 3" y "Elixir +3 % → **+6 %**". El valor nuevo en verde, con conteo y destello sobre la fila que cambia.
- **760:** "Toca para seguir" aparece a los 900 ms, `t-label` con fade.

### Tienda
- **56-100:** título "Tienda".
- **104-300: OFERTA DESTACADA** `.pnl` 366×190. Fondo de rayos del color de la rareza, héroe en oferta a 200 px saliéndose por arriba a la izquierda, a la derecha el nombre `t-h2`, sello "-30 %" (estrella SVG roja de 64 px, rotada -12°), temporizador con icono de reloj y botón de precio `.btn` con el precio antiguo tachado encima.
- **Cinta "Diario"** y una rejilla de 3 cartas de 114×168: **regalo gratis** (primera carta, marco verde, caja de regalo 3D y botón verde "GRATIS"; si ya se cogió, contador "Mañana" sobre el pozo) + 2 ofertas. Las etiquetas pasan a sellos en la esquina (cinta diagonal o chip rotado), no franjas.
- **Cinta "Cofres":** 3 cartas con el cofre a 96 px sobre luz, nombre y "⚡15–30" como chip, y botón de precio amarillo (si no llega, número rojo).
- **Cinta "Héroes":** cartas de héroe con el mismo `.card` de la colección.
- Futuro: "Monedas" con montones de monedas (S/M/L) y "Pase Dorado" fijo arriba (ver sección 5).
- **Animación:** el temporizador hace tic. Al comprar, la carta se "hunde", hay un destello y entra el overlay de recompensa.

### Camino de trofeos
- **Cabecera fija** (56-150) `.pnl`: trofeo 3D de 56, "75" `t-h1`, barra hasta la siguiente recompensa y, a la derecha, **"RECLAMAR (7)"** `.btn.green.sm`, que reclama todo en cascada.
- **Raíl central vertical** de 18 px en pozo, relleno dorado hasta la posición actual y **avatar del jugador** 44 px con marco amarillo en el punto exacto ("Estás aquí"), que va subiendo.
- **Nodos de recompensa en zigzag** a izquierda y derecha del raíl: tiles 120×120 (`.ice` si están reclamados, oscuros si están bloqueados, dorados con glow si son reclamables). Icono de 72, cantidad debajo y número de trofeos en una pastilla pegada al raíl.
  - Tile reclamable: se toca entero para cobrar, con badge "!" y un brillo lento.
  - Tile bloqueado: icono a color al 70 % con candado SVG de 24 en la esquina (nunca en gris).
- **Hito de arena:** banner a ancho completo de 366×150 con el render de la arena, nombre `t-h2` en cinta y "Desbloquea en 🏆100".
- **Animación:** al entrar, el raíl se rellena desde el último punto visto hasta el actual (600 ms) y el avatar se desplaza.

### Pase (ver también sección 5)
- **Cabecera** de 366×170: arte de la temporada (héroe con skin de temporada, render), "Temporada 1" `t-h2`, "quedan 6 días" con reloj, barra de escalón con la ficha cian y el botón **Misiones** (icono + badge).
- **Dos pistas** por escalón: Gratis a la izquierda (tile azul 150×110), número de escalón en el raíl central (círculo de 40) y Dorado a la derecha (tile oro 150×110).
- **Recompensas de clímax** cada 5 escalones (tiles más grandes, 150×140) y el escalón 30 como banner especial.
- **Botón fijo** encima de las pestañas: "PASE DORADO" `.btn.premium` 366×64 (oculto si ya se ha comprado).

### Misiones
- **Bottom sheet** (sube desde abajo, 280 ms), altura de unos 420 px, con `.x` arriba a la derecha y el título en cinta.
- Chip "Nuevas en 4 h 45 min" con reloj.
- Filas `.pnl` 350×76: **icono de tipo** 52 (bandera de victoria, corazón roto, trofeo), texto `t-label` 14, barra de 12 px con "0/4" a la derecha fuera de la barra y **chip de recompensa** (ficha cian 28 + 50).
  - Completada: la fila pasa a verde con el botón "COBRAR" `.btn.green.sm`.
  - Cobrada: check SVG y opacidad .6.
- **Fila final:** "Completa las 3" con cofre bonus y 3 pips.
- **Animación:** al cobrar, la ficha vuela a la barra del pase con conteo.

### Apertura de cofre
- Fondo de recompensa (azul o morado según el cofre) con godrays de 2 capas. **Cofre anclado abajo** en y≈560-760, a 240 px, sobre un suelo luminoso con sombra.
- **Arriba:** cinta con el nombre del cofre. **Pips de toque** (3 círculos de 18 px) bajo el cofre.
- **Cada toque:** squash/stretch de 120 ms, sacudida y luz que sale de las juntas (glow amarillo que crece: 30 %, 60 %, 100 %).
- **Apertura:** destello blanco de 120 ms, la tapa salta (cambio a `_open` con scale 1.2→1), haz de luz vertical y los objetos **salen del cofre** en arco hasta y≈250.
- **Recompensa:** tarjeta `.card` de 220×260 (color según tipo: oro las monedas, morado el poder, rareza el héroe) con el icono de 140 rotando ±6°, cantidad `t-hero` 56 con conteo desde 0 y nombre.
- **Contador de restantes:** el cofre de abajo muestra un chip "×2". Arriba a la derecha se elimina.
- **Héroe nuevo:** pantalla aparte con luz de rareza, silueta durante 400 ms → revelado con destello, cinta "¡NUEVO HÉROE!" y nombre.
- **Resumen:** rejilla de cartas 110×130 escalonadas y botón "CONTINUAR" amarillo.

### Elegir héroe
- **0-70:** "RONDA 1" `t-h1` en cinta, con los marcadores de ronda (3 estrellas SVG de 28 px por bando) a cada lado y en tus colores (azul a la izquierda, rojo a la derecha).
- **80-170:** fila de **chips de 76×76** con marco de rareza. El seleccionado se eleva 6 px con marco amarillo y glow. Los usados aparecen oscurecidos con un check verde SVG.
- **180-560:** tarjeta `.pnl`. Héroe 3D a 220 px a la izquierda con pedestal y, a la derecha, nombre `t-h2`, rareza y 4 **stat tiles** compactos (iconos 3D, sin emojis).
- **570-640:** consejo dentro de un panel oscuro con icono de bombilla SVG y la cara del mascota/héroe. Se quita la caja blanca.
- **680-764:** **¡A LUCHAR!** `.btn.xl` amarillo 366×84. El amarillo es "el gran botón" en toda la app.
- **Animación:** al cambiar de chip, el héroe grande hace swap (sale por la izquierda, entra con rebote).

### Victoria
- Fondo dorado de victoria con rayos y confeti inicial.
- **40-130:** "¡VICTORIA!" `t-hero` con degradado y contorno de 8 px, sobre una cinta. Entra con escala 2→1 y sacudida de pantalla.
- **140-360:** los dos héroes sobre un podio con foco: el ganador delante y más grande (220 px), con una animación de celebración.
- **370-500:** **3 fichas de recompensa** de 112×120 (Trofeos, Fichas del pase, XP) que caen una a una (150 ms de desfase), con conteo (84 → 93) y el icono volando después a su destino. La ficha de Trofeos lleva un badge "!" si hay premio en el camino (y se quita el botón "🎁 Premios en el camino").
- **510-600:** llaves (3 ranuras). Si se completan, banner del cofre de llaves 366×90 con "¡ÁBRELO!".
- **680-764:** fila de botones: **INICIO** `.btn.blue` 110×76 (icono de casa) + **JUGAR OTRA** `.btn.xl` 246×76.

---

## 4. Iconos e ilustraciones a producir

**Prioridad A: sustituyen emojis (Blender, 256 px, mismo setup de luz que `ui/`).**
1. Pestaña Héroes: busto/casco de héroe (o la cabeza de Flecha recortada).
2. Pestaña Inicio: casita/castillo de la arena.
3. Pestaña Tienda: bolsa o carrito con monedas (para que deje de ser el mismo cofre de las recompensas).
4. Ajustes: engranaje dorado/azul.
5. Stats: corazón (vida), gota de elixir (recarga), bota alada (velocidad), espada o flecha (ataque), campana (aviso).
6. Candado (dorado para premium y gris acero para normal), check verde y equis roja de cerrar.
7. Modos: espadas cruzadas, cabeza de bot y dos siluetas (amigos).
8. **Ficha del pase** propia (moneda-ticket cian con estrella), distinta de la estrella de XP. XP: orbe verde-menta con "XP" o estrella con alas.
9. Reloj/temporizador e "i" de información.

**Prioridad B: escenario y celebración (Blender).**
10. **Pedestal/isla** para el héroe (hierba + piedra + borde dorado), versiones por arena.
11. **Fondo diorama por arena** (render 1170×2532 desenfocado): Pradera Aprendiz, Bosque Cazador, etc.
12. Miniaturas de arena (para el banner de inicio y los hitos del camino).
13. **Cofre dorado premium** (`chest4`, cerrado/abierto, negro y oro) para el pase.
14. Caja de regalo diaria (lazo verde).
15. Montones de monedas S/M/L y de cristales de poder S/M/L.
16. Iconos de misión: bandera de victoria, corazón roto, trofeo pequeño.
17. Corona (favorito/portada y pase dorado).
18. Skins de temporada de 1 o 2 héroes (la recompensa estrella del pase).

**Prioridad C: SVG / CSS.**
19. Cinta (banner) en 9-slice: azul, dorada y roja.
20. Sello de oferta (estrella dentada) y cinta diagonal de esquina.
21. Destellos de 4 puntas, chispas, disco de glow y piezas de confeti (estrella, rombo y tira).
22. Flechas atrás/adelante, chevron ▲ verde de mejora y "!" de badge.
23. Patrón de fondo de iconos (estrella, cofre y corona en mosaico de 120 px).
24. Marcadores de ronda (estrella vacía/llena, azul/roja).
25. Marcos de avatar por nivel (bronce, plata, oro).

Además, revisar el alpha de los `.webp` actuales: el cofre de i_box0 muestra un halo claro. Exportar desde Blender con *straight alpha* + *edge padding*, o aplicar *defringe*.

---

## 5. Pase premium (Pase Dorado)

**Objetivo:** que el jugador vea lo que se pierde en cada escalón y que lo premium parezca un material distinto (joya y oro sobre terciopelo), no "lo mismo, pero amarillo".

**En la pantalla del pase:**
- **Dos pistas** con el raíl central. La pista Gratis va en `.pnl` azul. La **pista Dorada** va sobre terciopelo morado-negro (`--velvet-1 → --velvet-2`) con un marco dorado de 3 px, filete interior `--gold-1` y motas doradas flotando lentamente.
- **Las recompensas premium bloqueadas se muestran a todo color**, nunca en gris, con un **candado dorado** de 28 px en la esquina y un brillo diagonal que recorre las tiles en ola (40 ms de desfase entre escalones, cada 6 s). Si están en gris, nadie las desea.
- **Más valor visible:** las recompensas premium son de 1.5 a 2 veces mayores, más variadas (skins, cofre dorado, marcos de avatar, emotes, héroe exclusivo) y cada 5 escalones hay una tile "clímax" de 150×150 con rayos detrás.
- **Escalón 30:** banner a ancho completo con la **skin de temporada** en render y la etiqueta "EXCLUSIVO".
- **Cabecera:** a la derecha del arte de la temporada, una insignia "PASE DORADO" (corona + escudo) y el botón `.btn.premium` "DESBLOQUEAR" con destello. Si se ha comprado, la cabecera entera se vuelve dorada y lleva corona animada.

**Pantalla de compra** (modal a pantalla completa):
- Terciopelo, godrays dorados y la skin de temporada girando sobre un pedestal dorado (canvas 3D).
- Título "PASE DORADO" `t-hero` con degradado dorado.
- 4 o 5 beneficios con check dorado SVG: "+30 recompensas", "Skin exclusiva", "Cofre dorado cada 5 escalones", "+20 % de fichas de misión" y "Marco de avatar dorado".
- Sello "¡x5 de valor!". Botón `.btn.premium` 340×80 con el precio y temporizador de temporada.

**Al comprar:**
- Destello dorado y confeti dorado. El candado de cada tile premium alcanzada salta y se rompe en cascada (60 ms por tile, de abajo hacia arriba).
- Las tiles pasan a "reclamables" con glow. Botón "RECLAMAR TODO" dorado.

```css
.track-gold{background:radial-gradient(120% 60% at 50% 0%,#5A1F9A,var(--velvet-1) 40%,var(--velvet-2));
  border:3px solid var(--ink);border-radius:18px;box-shadow:inset 0 0 0 3px var(--gold-2),inset 0 0 0 5px var(--ink),0 4px 0 var(--ink)}
.tile.premium{position:relative;border-radius:14px;border:3px solid var(--ink);overflow:hidden;
  background:radial-gradient(70% 60% at 50% 40%,#FFF3B0 0%,var(--gold-2) 45%,var(--gold-3) 80%,var(--gold-lip) 100%);
  box-shadow:inset 0 2px 0 #fff,inset 0 -5px 0 rgba(120,50,0,.35),0 3px 0 var(--ink),0 0 18px rgba(255,200,60,.45)}
.tile.premium::after{content:"";position:absolute;top:-40%;bottom:-40%;width:30%;left:-50%;
  background:linear-gradient(100deg,transparent,rgba(255,255,255,.8),transparent);transform:skewX(-20deg);
  animation:sheen 6s calc(var(--i)*40ms) ease-in-out infinite}
.tile.premium .lock{position:absolute;top:4px;right:4px;width:28px;height:28px}  /* candado dorado render */
.tile.premium.locked img{filter:none}  /* nunca desaturar */
```

---

## 6. Los 10 cambios con más impacto (en orden)

1. **Eliminar todos los emojis de la UI** y sustituirlos por renders o SVG de un único estilo (pestañas, ajustes, stats, candados, modo, favorito). Es el mayor salto de calidad percibida por hora de trabajo.
2. **Nuevo material de panel y botón** (`.pnl`, `.btn`: brillo superior, bisel inferior, sombra suave más espesor, texto blanco con contorno). Se cambia en un sitio y mejora todas las pantallas.
3. **Escenario en Inicio:** pedestal renderizado + sombra de contacto + foco + fondo diorama de la arena, en lugar del disco cian sobre rayas.
4. **Sistema de color por función** (amarillo primario, verde obtener, azul secundario, oro premium; morado solo para Poder y Épico) y **una sola cinta de sección**. Se acaba el arcoíris.
5. **Escala tipográfica de 8 tamaños + contorno limpio** (`.stroke` con `data-t`), mínimo de 12 px y contraste de los textos secundarios a `--tx-2`.
6. **Cartas de héroe con marco de rareza y arte que se sale del marco**, rejilla de 3 columnas y estado "mejorable" en la placa (sin círculo latiendo encima del arte).
7. **Secuencias de recompensa con coreografía** (cofre anclado, objetos que salen en arco, tarjeta de recompensa, conteo de números, monedas que vuelan a la barra superior, flip del nivel con comparación de stats). Es lo que hace que algo "se sienta" Supercell.
8. **Camino de trofeos y Pase como viaje** (raíl con avatar "estás aquí", tiles en zigzag, hitos de arena grandes, "Reclamar todo") + **Pase con pista Dorada** visible y deseable.
9. **Jerarquía de botones:** un CTA amarillo por pantalla, "Cerrar" como `.x`, fin de los 4 botones apilados en Victoria y del CERRAR amarillo en Misiones, y ¡A LUCHAR! en amarillo.
10. **Disciplina de movimiento:** quitar los loops infinitos (badges, ↑, pulse), dejar solo el brillo del CTA principal, entradas escalonadas de 220 ms y `prefers-reduced-motion`. A la vez, quitar duplicados en Inicio (Tienda y Pase laterales) y limitar a 3 badges visibles.

**Orden de implementación sugerido (CSS puro primero):** 2 → 4 → 5 → 9 → 10 (un día, sin assets nuevos) · después 1 y 6 (assets de iconos) · después 3, 7 y 8 (renders de escenario y lógica de animación).
