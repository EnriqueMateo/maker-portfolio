# Arte para los 5 héroes nuevos y las arenas 3–5

Los héroes ya funcionan en el motor (ocultos con `live:false`). Solo falta su arte.
Cuando tengas cada imagen, pásamela y hago el recorte, el contorno, el retrato y las animaciones con la misma cadena que los 8 actuales.

## Cómo pedirlas a Gemini

Pega primero esta base y luego la línea de cada héroe. Pide **una imagen por héroe**.

> Personaje para un juego móvil estilo Brawl Stars / Clash Royale. Render 3D estilizado, cabeza grande, proporciones chibi, materiales brillantes y suaves, colores saturados, contorno limpio. Cuerpo entero, de frente, ligeramente girado a la izquierda, pose de acción amistosa. Fondo blanco liso, sin sombras en el suelo, un solo personaje, sin texto. Mismo estilo que [adjunta `art/concepts/brasa.jpg` y `ojo.jpg` como referencia].

| Héroe | Rol | Prompt (añadir a la base) | Colores |
|---|---|---|---|
| **Mina** | Topo | Topo minero simpático con casco de minero con linterna, gafas redondas sobre la frente, mono marrón con bolsillos, lleva una mina redonda con mecha en una mano y una pala pequeña a la espalda. | marrón `#b07a3a`, crema |
| **Salto** | Rana | Rana atlética y traviesa, piernas largas y musculosas, cinta de ninja en la frente, muñequeras, sonrisa enorme, a punto de saltar con la lengua un poco fuera. | verde `#3ad06a`, amarillo |
| **Savia** | Hada | Hada de bosque pequeña con alas de hoja translúcidas, vestido de pétalos, pelo de enredadera con flores, sostiene una varita de espina con una gota brillante. | rosa `#e05ab0`, verde hoja |
| **Mira** | Lince | Lince francotirador serio y elegante, orejas con pinceles, capa corta, ballesta larga con mira telescópica dorada, un ojo entrecerrado apuntando. | amarillo dorado `#f0c030`, gris |
| **Eco** | Murciélago | Murciélago misterioso con alas grandes como capa, auriculares, ondas de sonido saliendo de la boca, ojos brillantes violeta. | violeta `#5a4ad8`, negro |

Para cada héroe, guarda la imagen como `art/concepts/<id>.jpg` (`mina`, `salto`, `savia`, `mira`, `eco`).

## Arenas 3–5 (props, igual que Pradera)

Misma base de estilo, pero **objeto suelto**, fondo blanco, sin personaje. Guárdalos en `art/props_src/`.

- **Volcán:** roca volcánica con grietas de lava brillante · géiser de lava pequeño · árbol quemado · bandera de humo.
- **Trono:** estatua de piedra de un héroe con escudo (será la estatua que para un golpe) · columna rota · antorcha · alfombra roja enrollada.
- **Olimpo:** nube esponjosa con borde dorado · columna griega dorada · laurel · veleta dorada (para el viento).

## Cuándo sacarlos

Uno cada 2–3 semanas como **novedad**:

1. Sale en la ventana del día como **pack fijo** (héroe + aspecto exclusivo + gemas), contenido a la vista, sin azar.
2. Se puede conseguir **jugando** en el camino de trofeos o en el pase.

Orden recomendado (de más fácil de entender a más raro): Mira → Salto → Mina → Savia → Eco.

## Aspectos de verdad (sustituyen al filtro de color actual)

Ahora un aspecto es el mismo dibujo con otro tono (`SKINS` en `index.html`, campo `f`). Para que se vendan, cada aspecto necesita **su propia ilustración**: otra ropa, otros accesorios y otra paleta, misma silueta para que se reconozca al héroe.
Usa la misma base de estilo y adjunta la imagen del héroe original como referencia («el mismo personaje, misma pose y proporciones, pero con este aspecto»). Guarda cada uno como `art/concepts/<héroe>_<aspecto>.jpg`.

**Los 5 que ya existen en la tienda (prioridad):**

| Aspecto | Prompt |
|---|---|
| Brasa Glacial (`brasa_glacial`) | Dragón de hielo: escamas azul claro translúcidas, cuernos de carámbano, su llama de la cola es fuego azul helado, bufanda de lana blanca. |
| Muro Magma (`muro_magma`) | Gólem de roca volcánica negra con grietas de lava naranja brillante, humo saliendo de los hombros, puños incandescentes. |
| Sombra Carmesí (`sombra_carmesi`) | Ninja con traje rojo intenso y negro, máscara de demonio oni, bufanda larga roja ondeando, shurikens dorados. |
| Truco Ártico (`truco_artico`) | Zorro ártico blanco con pelaje esponjoso, gorro de lana azul con pompón, guantes, aliento visible de frío. |
| Ojo Nevado (`ojo_nevado`) | Búho nival blanco con manchas grises, gafas de aviador de esquí, orejeras, catalejo plateado. |

**Ideas para los siguientes (de temporada, 2 por héroe):**

- Flecha: «Flecha Pirata» (sombrero de tricornio, parche, arco de madera de barco) · «Flecha Neón» (traje futurista con luces cian, arco holográfico).
- Brasa: «Brasa Dorada» (escamas de oro, corona pequeña) · «Brasa Robot» (dragón mecánico con remaches y llama azul de propulsor).
- Rayo: «Rayo Galáctico» (túnica con estrellas, báculo con planeta) · «Rayo Halloween» (sombrero de bruja con calabaza).
- Bum: «Bum Fiesta» (bomba con confeti y gorro de fiesta) · «Bum Pingüino».
- Muro: «Muro Jardín» (musgo, flores y setas por el cuerpo).

Precio orientativo: aspectos normales 150 gemas; de temporada o con efectos, 300 gemas. Siempre se ve el aspecto antes de comprarlo (nada al azar).
