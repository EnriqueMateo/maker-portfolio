# AMAGO: auditoría de UX, flujo, primera experiencia, retención, accesibilidad e i18n

Área: U (UX). Auditoría de solo lectura de `amago/index.html` (los números de línea son del commit 486d05f).
Método: lectura del código y Playwright (Chromium con swiftshader, móvil táctil) a 375×667 (iPhone SE) en inglés (`amago-lang=en`), con jugador nuevo (entrenamiento completo hasta la primera partida), jugador veterano (12 partidas) y modo sin conexión. Capturas en
`/tmp/claude-0/-home-user-maker-portfolio/89a0f5ca-c3e1-53ff-85f7-17ada0218752/scratchpad/audit/ux_shots/` (abajo se citan por nombre de fichero).
Las capturas son anteriores al commit 486d05f; los hallazgos afectados por ese commit se han vuelto a comprobar en el código.

Escala: **crítico** (bloquea o hace perder progreso / pasa a muchos jugadores en los 5 primeros minutos), **alto**, **medio**, **bajo**.

## Resumen

| Id | Sev. | Título |
|---|---|---|
| U1 | alto | En el entrenamiento, la burbuja del Entrenador tapa al rival justo cuando te pide dispararle (iPhone SE) |
| U2 | alto | El consejo «¡Nuevo: AMAGO!» se pisa al instante con el de controles y no vuelve a salir nunca |
| U3 | alto | Inicio en 375×667: el aviso de 1.ª victoria tapa «Diario» y se corta; el botón JUGAR queda debajo de la barra de pestañas |
| U4 | alto | Pantalla de fin: el cofre recién ganado y los avisos quedan ocultos tras los botones fijos |
| U5 | alto | Formulario de cuenta: cualquier error borra correo y contraseña, y sin conexión muestra «Failed to fetch» |
| U6 | alto | No hay «He olvidado mi contraseña»: cuenta de correo perdida = progreso perdido |
| U7 | alto | Iniciar sesión con correo sustituye la partida de invitado sin confirmar (con Apple sí se pregunta) |
| U8 | alto | «Reducir movimiento» corta todas las esperas a 60 ms: los carteles de ronda y de muerte súbita desaparecen sin poder leerse |
| U9 | alto | Decenas de textos y etiquetas en español en el modo inglés (lista completa al final), incluido el nombre por defecto «JugadorNNNN» |
| U10 | medio | Instrucciones contradictorias en el entrenamiento: el estado dice «¡Rival a la vista! Dispara» mientras el Entrenador dice «¡Escapa!» |
| U11 | medio | El «Entrenador Ojo» es un búho, pero en la partida juega con Brasa y Muro |
| U12 | medio | Exceso de avisos rojos; el del camino de trofeos sale duplicado y el de Héroes «↑» no se apaga nunca |
| U13 | medio | Primer inicio tras el entrenamiento: cinco llamadas de atención compitiendo (cofre, Diario, cuenta, bloqueos, entrenador) |
| U14 | medio | Aviso de invitado demasiado pronto e insistente, y mensajes contradictorios sobre si el progreso se guarda |
| U15 | medio | Sin salida, pausa ni ajustes una vez empezada la partida (elección de héroe y arena son callejones sin salida) |
| U16 | medio | «Ya sé jugar»: sin nombre, sin primer cofre, y la primera partida real sigue en modo tutorial con la mano |
| U17 | medio | Tienda bloqueada que muestra un «Regalo diario GRATIS» que no se puede coger |
| U18 | medio | La dificultad (Fácil por defecto) cambia trofeos ×0,7 y se corta en 300, pero el selector solo enseña monedas |
| U19 | medio | Objetivos táctiles por debajo de 44 pt (recursos, «¡VALE!», cambiar misión, enlaces, botones pequeños) |
| U20 | medio | Texto de 10-11 px con contraste bajo (pestañas, «MODO», subtítulos sobre azul, enlaces oscuros sobre fondo oscuro) |
| U21 | medio | Identidad de color incoherente (tu isla tiene borde azul pero el texto dice «verde»; «toca el ROJO») y dependencia del color |
| U22 | medio | En la ficha de héroe, MEJORAR (acción principal) queda fuera de pantalla en iPhone SE |
| U23 | medio | Los corazones del HUD se cortan y el nombre se trunca («Jugado…») |
| U24 | medio | Popups uno detrás de otro en las primeras visitas al inicio (novedad, invitado, calendario, temporada, pack) |
| U25 | bajo | Pantalla de fin: «Trofeos · 40» muestra los trofeos de antes, no los de ahora; «×2» sin explicar |
| U26 | bajo | Camino de trofeos: el relleno del raíl no coincide con los nodos y la barra superior desaparece al abrirlo |
| U27 | bajo | Iconos sobrecargados: estrella = fichas, rondas y velocidad; corona = pase, amigos, héroe raro; trofeo = trofeos y victorias del héroe |
| U28 | bajo | Ventanas de resultado con «VOLVER AL INICIO» tras crear cuenta/iniciar sesión; desconexión sin «Reintentar» |
| U29 | bajo | El modal de traspaso remite a «Ajustes → Pasar mi progreso → Tengo un código», pero el ajuste se llama distinto |
| U30 | bajo | «Cómo se juega» no explica el AMAGO ni la muerte súbita, y habla de «3 rondas» cuando es al mejor de 2 (hasta 5 con empates) |
| U31 | bajo | Inglés mejorable: «ROUND TO YOU!», «It was here!», «Password (6 or more)» en el login, AMAGO traducido como FEINT |
| U32 | bajo | Sin zoom (`user-scalable=no`), sin tamaño de texto ni «reducir movimiento» propios en Ajustes, y la caja del cofre no es un botón para VoiceOver |
| U33 | bajo | Desbordes de 1-7 px en 375 px: el «+» de gemas y el sello «−30 % HOY» se salen por la derecha |
| U34 | bajo | Ajustes sin «Ayuda/Contacto» ni identificador de jugador para soporte |
| U35 | bajo | Copia de Apple ID visible fuera de iPhone y placeholders con letra espaciada que se leen mal |

---

## Hallazgos

### U1 · alto · En el entrenamiento, la burbuja del Entrenador tapa al rival justo cuando te pide dispararle
- **Evidencia:** `index.html:735` (`.tcoach{… top:calc(118px + safe-area)}`, con `.ingame`), guion en `TUT.r1` (≈ l. 4100-4140). Capturas `04_tut_shoot.png`, `05_tut_escape.png`, `06_tut_counter.png`: en 375×667 la burbuja ocupa de y≈118 a y≈230 (en puntos) y tapa las dos filas superiores de la isla roja; el rival «chivado» solo asoma los pies y la mano apunta al borde de la burbuja. En el paso de contraataque la burbuja (con botón) tapa tres filas.
- **Impacto:** es el momento clave del aprendizaje («¡tócalo para disparar!») y el jugador no ve a quién dispara. En un SE el paso puede parecer roto: abandono en el minuto 1.
- **Arreglo:** en partida, poner la burbuja abajo, sobre la barra de elixir (la isla propia ya está señalada por la mano), o calcular su posición para que no cruce la caja de pantalla del objetivo (`B3.screenPos`). Alternativa: burbuja compacta de una línea en alturas < 700 px.

### U2 · alto · El consejo «¡Nuevo: AMAGO!» se pisa al instante y no vuelve a salir
- **Evidencia:** `startRound`, `index.html:4010-4013`: primero `toast("amagonew", …)` y, en la misma pasada, `else toast("controls", …)`. `toast()` (`l. ≈4557`) marca la clave como vista (`S.tips[k]=1`) y borra el aviso anterior, así que en la primera partida real (`S.games` 1-3) el de AMAGO se marca como visto y desaparece en el mismo fotograma.
- **Impacto:** la mecánica que da nombre al juego no se explica nunca a quien se saltó el entrenamiento, y quien lo hizo pierde el recordatorio. Más partidas sin entender la profundidad = peor retención D1.
- **Arreglo:** una cola de avisos (mostrar el siguiente al cerrar o caducar el anterior) o encadenar: «controls» en la ronda 1 y «amagonew» en la ronda 2. No marcar `S.tips[k]` hasta que el aviso se haya visto al menos 2 s.

### U3 · alto · Inicio en 375×667: elementos que se tapan y se cortan
- **Evidencia:** capturas `v_home_clean.png`, `m_home_after.png`, `tb_home1.png`. `showHome` (`l. 3358-3390`): la pastilla `.firstwin` (`l. 3379`, CSS `l. 799`, `width:max-content`) cruza toda la pantalla, tapa el botón lateral «Diario» (solo asoma su «!») y su texto se corta por la derecha («and +20 [frasco]» fuera). La fila MODO/JUGAR queda parcialmente debajo de la barra de pestañas (Playwright: `clip: gbtn xl play2 «PLAY»`). No hay ninguna regla CSS para alturas pequeñas salvo la de la pantalla final (`l. 644`).
- **Impacto:** el botón más importante del juego se ve cortado y el calendario (retención diaria) queda escondido justo en el móvil más pequeño que soporta iOS 17/18.
- **Arreglo:** `@media (max-height:700px)` que reduzca `.hstage` (héroe más pequeño), convierta la 1.ª victoria en una línea corta («1.ª victoria: ×2 🔑») con `max-width:calc(100% - 140px)` centrada entre las columnas laterales, y reserve `padding-bottom` = altura real de `.tabs` + safe-area para `.playrow2`.

### U4 · alto · Pantalla de fin: el cofre ganado queda oculto tras los botones fijos
- **Evidencia:** `endMatch` (`l. 4335-4353`) y `.endbtns{position:sticky}` (`l. 643`). Capturas `m_end.png` / `m_end_full.png`: el contenido mide 853 px en una pantalla de 667; la tarjeta «¡3 llaves: cofre! Toca para abrirlo» queda justo detrás de «JUGAR OTRA» y la pastilla «¡Premios en el camino de trofeos!» queda por debajo. En el entrenamiento (`tb_end.png`) quedan ocultas las filas «Regalo de bienvenida» y «¡Premio del entrenamiento: tu primer cofre!».
- **Impacto:** el momento de mayor recompensa (cofre) es invisible; el jugador pulsa JUGAR OTRA sin saber que tenía un cofre. Rompe el bucle «gano → abro» que sostiene la retención.
- **Arreglo:** priorizar: si hay cofre, mostrar `endchest` arriba (sustituyendo el podio en alturas < 750 px) o convertir el botón principal en «ABRIR COFRE»; quitar el podio en pantallas bajas; limitar a 3 filas y agrupar el resto en «+2 premios más».

### U5 · alto · El formulario de cuenta borra lo escrito en cada error y muestra errores técnicos
- **Evidencia:** `accSubmit` (`l. 1629-1653`): en cada error se hace `renderModal()`, que vuelve a crear los `<input>` vacíos (`l. ≈3800`). Sin conexión, `M.err=e.message` muestra el texto del navegador: captura `m_offline_reg.png` → «Failed to fetch» (en Safari sería «Load failed»). Los errores del servidor llegan en español (`server/api.js:243-390`, p. ej. «Cuenta no encontrada.», «Ese código no existe o ha caducado.», «espera») y algunos no están en `I18N_EN`.
- **Impacto:** un fallo de contraseña o una mala conexión obliga a reescribir correo y contraseña; en móvil, con teclado, es frustrante y reduce la conversión de invitado a cuenta (que protege la retención a largo plazo).
- **Arreglo:** guardar `email` en `UI.modal` y rellenar el campo al re-renderizar (la contraseña se puede conservar en memoria); mapear `TypeError`/fallos de red a «Sin conexión. Comprueba internet y vuelve a probar.»; que el servidor devuelva códigos (`bad_pass`, `rate`, `not_found`) y el cliente los traduzca.

### U6 · alto · No hay recuperación de contraseña
- **Evidencia:** `renderModal` cuenta (`l. ≈3800-3815`): solo correo, contraseña, ENTRAR y «No tengo cuenta». `grep` sin resultados de «olvid/forgot/reset» en `index.html` y `server/api.js`. Además, desde 486d05f el servidor bloquea tras 8 contraseñas fallidas.
- **Impacto:** quien olvida la contraseña pierde su cuenta para siempre (y con ella héroes y compras futuras). Además de soporte, es un riesgo de reseñas de 1 estrella.
- **Arreglo:** «¿Olvidaste la contraseña?» con código de 6 dígitos por correo (o enlace mágico), y mientras tanto ofrecer Sign in with Apple como opción principal en iOS y un correo de soporte visible.

### U7 · alto · Iniciar sesión con correo sustituye la partida de invitado sin confirmación
- **Evidencia:** `accSubmit` rama login (`l. ≈1644`): `if(r.j.save)restoreSave(r.j.save)` directamente; solo hay una nota pequeña «Ojo: la partida de invitado de este móvil se sustituye…» (captura `v_m_acclogin.png`). En cambio, con Apple sí hay `confirmAsk("¿Usar la partida de tu cuenta?" …)` (`l. ≈1685`).
- **Impacto:** un jugador que entra por error en una cuenta vieja (o en la de un hermano) pierde su partida de invitado actual sin vuelta atrás.
- **Arreglo:** usar el mismo `confirmAsk` que en Apple cuando `isGuest()&&S.games>0`, mostrando trofeos/héroes de ambas partidas; guardar una copia local de la partida de invitado durante 7 días para poder recuperarla.

### U8 · alto · «Reducir movimiento» se come la información, no solo la animación
- **Evidencia:** `const sleep=ms=>…setTimeout(r,REDUCED?Math.min(ms,60):ms)` (`l. 1554`) y `banner()` (`l. 1820`) usa `sleep(dur)`. Con la preferencia del sistema activada: «¡MUERTE SÚBITA! · Golpes más rápidos…» (`l. 4606`), «¡RONDA PARA TI!», «Se acabó el tiempo: vida X % contra Y %» (`roundBanner`, `l. 4262`), la cuenta atrás 3-2-1 y el VS duran 60 ms. `revealFoe` («¡Estaba aquí!», 2 s) también pasa a 60 ms. Además, el CSS global (`l. 250`) reduce todas las animaciones a 0,01 s, incluida la de la mano del tutorial y la barra de carga.
- **Impacto:** los jugadores con sensibilidad al movimiento (y quien tiene activado «Reducir movimiento» por batería) no se enteran de por qué ganaron/perdieron la ronda ni de que empieza la muerte súbita. Es justo lo contrario de lo que pide la preferencia.
- **Arreglo:** separar `sleep` (lógica/lectura, nunca recortar) de `animMs` (duración de animación); en modo reducido, mantener los carteles el mismo tiempo pero sin escalado/temblor (solo fundido). Revisar también que `B3.shake` (`l. ≈2891`) respete `REDUCED` (ahora no lo comprueba).

### U9 · alto · Textos en español en el modo inglés
- **Evidencia:** escaneo estático (traductor `TR` reproducido en Node contra `I18N_EN`) y recogida de nodos de texto visibles en Playwright. Ejemplos visibles: nombre por defecto «Jugador4822» en el HUD y para el rival online (`loadSave`, `l. 1569`; captura `02_tut_coach1.png`), «👤 Invitado» en Ajustes (`l. 3822`, `v_m_settings.png`), «With 3 keys you get a **cofre**» (`l. 3744`, `v_m_keysinfo.png`), «Te hemos guardado un regalo por volver.» (`l. 3785`, `v_m_comeback5.png`), «Quedan 3 hoy ·» en la tienda (`l. 3510`), «Cofre grande fijo» en el pase (`l. 3235`), «vida/velocidad» en el consejo de elegir héroe (`l. 3997`), «CÓDIGO» como placeholder, los textos nuevos de 486d05f («👣 Huella falsa: allí NO está», «Golpes más rápidos · os veréis cada 5 s», «🎭 Lejos de ti»…). Lista completa al final.
- **Impacto:** en el mercado anglosajón (el grueso de las 50k descargas posibles) el juego parece a medio traducir; también rompe VoiceOver en inglés (etiquetas `aria-label` en español).
- **Arreglo:** (1) generar el nombre por defecto según idioma («Player4822») o pedir nombre antes; (2) no partir frases con plantillas que dejan fragmentos vacíos (los patrones `#` exigen al menos un carácter: «…por volver#.» no casa si el hueco está vacío); (3) añadir las claves que faltan; (4) añadir un test que recorra todas las pantallas en inglés y falle si queda texto con `[áéíóúñ¿¡]` o palabras españolas frecuentes; (5) traducir los mensajes del servidor por código.

### U10 · medio · Instrucciones contradictorias en el entrenamiento
- **Evidencia:** captura `05_tut_escape.png`: la píldora de estado (`renderStatus`, `l. 4531+`) dice «👀 Rival spotted! Shoot» mientras la burbuja dice «Hit! … Run!» y la mano señala tu propia isla. En `06_tut_counter.png` el estado dice «⏳ Get ready!» con el juego en pausa.
- **Impacto:** el novato recibe dos órdenes opuestas en el segundo 20 de su vida en el juego.
- **Arreglo:** mientras `G.tut` tenga un paso activo, ocultar o sustituir la píldora de estado por el texto del paso (o atenuarla).

### U11 · medio · El Entrenador Ojo es un búho pero juega con un dragón y un gólem
- **Evidencia:** `TUT.match` (`l. 4046`): `opp:{name:"Entrenador Ojo"}`, `oppPool:["brasa","muro"]`. Capturas `02_tut_coach1.png` (bienvenida con el búho, HUD rival «Coach Ojo» con la cara de Brasa) y `tb_r2_amago.png` (Muro).
- **Impacto:** confunde quién es quién en el primer combate; además Ojo aparece luego como héroe bloqueado (40 trofeos), lo que podría ser un buen gancho que ahora se pierde.
- **Arreglo:** que el entrenador juegue con Ojo (vida 3, sin disparar salvo guion) o llamar al rival «Muñeco de práctica de Ojo». Al final: «¡Desbloquea a Ojo a los 40 trofeos!».

### U12 · medio · Exceso de avisos rojos, uno duplicado y otro permanente
- **Evidencia:** `nav()` (`l. 3333`) y `roadBar()`; capturas `v_home_clean.png` y `m_home_after.png`: hasta 6 puntos rojos a la vez (Tienda «!», Héroes «↑», Trofeos «4», barra de trofeos «4», cofre «1», Diario «!»). El número del camino aparece dos veces. «↑» en Héroes depende de `anyUp()` (hay recursos para mejorar algún héroe): con economía normal está casi siempre encendido y no se apaga al visitar la pestaña. El «!» de la Tienda es el regalo diario: sale cada día aunque el jugador no compre nunca.
- **Impacto:** ceguera a los avisos: cuando hay algo realmente importante (cofre, misión), ya no destaca. Brawl/Clash limitan los rojos a acciones cobrables.
- **Arreglo:** jerarquía: rojo solo para cosas cobrables ahora (cofre, misión completa, camino, regalo); «↑» en verde/amarillo y solo la primera vez que una mejora es posible (apagar al visitar Héroes, `S.seenUp`); un solo indicador para el camino (quitar el de la barra o el de la pestaña).

### U13 · medio · Primer inicio tras el entrenamiento: demasiadas llamadas de atención
- **Evidencia:** `tb_home1.png` / `tb_home2.png`: a la vez el Entrenador («¡Tu primer cofre!»), la mano, el cofre que bota, el calendario «Diario» con «!» (aparece con `S.games>=1`, `l. 3373`), la barra amarilla de invitado (`l. 3382`, `S.games>=1`), Misiones y Pase con candado. La burbuja del entrenador tapa la ficha del héroe y la barra de invitado.
- **Impacto:** en el minuto 3 el jugador no sabe qué es importante; el bucle que se quiere enseñar (cofre → JUGAR) compite con 3 cosas más.
- **Arreglo:** hasta terminar la primera partida real (`S.games<2`): ocultar Diario, barra de invitado y botones bloqueados (o mostrarlos atenuados sin candado), y revelarlos con una pequeña animación «¡Nuevo!» cuando se desbloquean (`UNLOCK`, `l. 3200`).

### U14 · medio · El aviso de invitado llega demasiado pronto y los mensajes se contradicen
- **Evidencia:** barra permanente desde la 1.ª partida (`l. 3382`), modal `guestnag` a las 3, 10, 25 y 60 partidas (`homeEvents`, `l. 3393+`), «Ajustes → Invitado», y el modal de traspaso que dice «Tu progreso se guarda solo en la nube ✅» (`l. 3791`, captura `m_offline_cloud.png`, que además muestra a la vez «✅» y «No connection.»).
- **Impacto:** a un jugador de 3 minutos se le pide una cuenta antes de enganchar; y al mismo tiempo se le dice que su progreso ya está en la nube y que no lo está. Pierde credibilidad.
- **Arreglo:** primer aviso tras la 1.ª subida de arena o 5 partidas, y en un momento positivo (después de abrir un cofre). Barra del inicio solo tras ese momento y con «✕» (posponer 3 días). Texto del traspaso para invitados: «Tu progreso está en este móvil. Crea una cuenta para no perderlo».

### U15 · medio · No hay salida, pausa ni ajustes una vez dentro de la partida
- **Evidencia:** `showPick` (`l. 3983`) y `buildArena` (`l. ≈4500`) no tienen botón de volver ni de ajustes; la acción `home` existe (`l. 4639`) pero no hay ningún botón que la lance en esas pantallas. Tampoco se puede silenciar el sonido en partida ni salir del entrenamiento una vez empezado.
- **Impacto:** si entras sin querer (o suena el móvil en el bus), solo puedes cerrar la app. Sin silenciar en partida, en público se cierra la app.
- **Arreglo:** botón ⚙ pequeño en el HUD con: sonido, vibración y «Abandonar» (con confirmación que explique que cuenta como derrota); en la elección de héroe, «‹» que vuelva al inicio en partidas contra el bot.

### U16 · medio · «Ya sé jugar» deja una primera experiencia a medias
- **Evidencia:** `case "tutskip"` (`l. 4632`): `S.tutDone=1` y `showHome()`. Sin nombre (queda «JugadorNNNN»), sin el primer cofre del entrenamiento ni el paso «Pulsa JUGAR». Después, `startMatch` (`l. 3971`) pone `tutorial:S.games===0`: la primera partida real sigue siendo «tutorial» (mano que señala, sin botón AMAGO, bot nivel 1).
- **Impacto:** el jugador experto recibe justo lo que quería evitar (mano y tutorial), y el que sabe jugar no recibe el regalo inicial: peor sensación de recompensa.
- **Arreglo:** al saltar: pedir nombre, dar el mismo cofre y poner `S.games` a un valor que no active `G.tutorial`, o usar `S.tutDone` en lugar de `S.games===0` para decidir.

### U17 · medio · Tienda bloqueada que enseña un regalo gratis que no se puede coger
- **Evidencia:** `showShop` (`l. ≈3488`) pinta el «Regalo diario · GRATIS» aunque `!unlocked("shop")`; `lockNow` (`l. 3205`) y `LOCK_FREE` (`l. 3212`) bloquean el toque con «🔒 Se desbloquea al jugar N partidas más». Las pastillas de monedas de la barra superior llevan a la tienda (`l. 3341+`).
- **Impacto:** frustración («me dice GRATIS y no me deja»); sensación de trampa.
- **Arreglo:** con la tienda bloqueada, mostrar una vista previa con el regalo como «Disponible tras 3 partidas» (gris), o desbloquear el regalo diario desde la primera partida (es una buena razón para volver mañana).

### U18 · medio · La dificultad afecta a los trofeos, pero no se dice
- **Evidencia:** `TRO_MULT={facil:.7,normal:1,dificil:1.4}` (`l. ≈1501`), «En Fácil ya no se suben trofeos» a partir de 300 (`endMatch`, `l. 4283+`). El selector (`v_m_mode.png`) solo muestra «+5/+8/+12 monedas». El modo por defecto es Fácil.
- **Impacto:** el jugador avanza un 30 % más lento por el camino de trofeos sin saberlo, y a los 300 trofeos se encuentra con un muro explicado solo a posteriori.
- **Arreglo:** mostrar «🏆 ×0,7 / ×1 / ×1,4» en cada chip; sugerir Normal automáticamente tras 3 victorias seguidas en Fácil («¿Subes a Normal? +40 % trofeos»).

### U19 · medio · Objetivos táctiles pequeños
- **Evidencia (Playwright, 375×667):** pastillas de monedas/poder/gemas 54-68×30 (`.rpill`, `l. 571`), «¡VALE!» del entrenador 57×39, «Cambiar misión ↻» 30×30 (`.reroll`, `l. 951`) pegado a la recompensa, enlaces «Ya sé jugar»/«Ya tengo cuenta» 197-213×40, «Iniciar sesión/crear una» 305×35, botones `gbtn sm` de la tienda 36-39 de alto, botón de misiones del pase 56×39 sin texto, «Volver» de la cola online 73×42.
- **Impacto:** toques fallidos en un juego para pulgares; el ↻ se puede pulsar por error y gasta el único cambio diario sin confirmación.
- **Arreglo:** mínimo 44×44 pt de área táctil (se puede ampliar con `::after` sin cambiar el dibujo); ↻ con confirmación o deshacer; texto «Misiones» en el botón del pase.

### U20 · medio · Texto pequeño y con poco contraste
- **Evidencia:** etiquetas de pestañas 11 px con `opacity:.8` (`l. 584`); «MODO» 10 px en `--tx-3 #93A2DE` sobre panel azul `#2f6fe0` → contraste 1,9:1 (`l. 804`); «Cambiar» 11 px; `.sub` `#CFDAFF` sobre `#2f6fe0` → 3,4:1 a 13 px; enlaces `.linkbtn.dk` color tinta al 75 % sobre la hoja azul oscura (`l. 753`) prácticamente invisibles (captura `v_m_acc.png`, «I have an account: sign in»); sellos «GRATIS/−30 % HOY» a 10 px; «4/9» en Héroes.
- **Impacto:** ilegible al sol o con vista cansada; WCAG pide 4,5:1 para texto normal.
- **Arreglo:** suelo de 12 px (13 px en etiquetas de pestañas) y 4,5:1; `.linkbtn.dk` en blanco/amarillo sobre fondos oscuros; quitar la opacidad de las etiquetas.

### U21 · medio · Identidad de color incoherente y dependencia del color
- **Evidencia:** la isla propia tiene borde y banderas azules y tu nombre va en azul (`--me:#34c6ff`, `l. 16`), pero los textos dicen «tu isla **verde**» (entrenador, `l. 4120`) y «toca el **ROJO**» (`toast("controls")`, `l. 4013`). Los avisos de impacto sí llevan ⚠️ además del rojo (bien), pero «huella» (amarillo) y «cerca» (naranja) en la isla rival se distinguen sobre todo por color.
- **Impacto:** para ~8 % de los chicos (daltonismo rojo-verde) «verde/rojo» como única referencia no sirve; y el mensaje «verde» no coincide con lo que se ve.
- **Arreglo:** hablar de «tu isla (abajo)» y «la isla rival (arriba)»; etiquetas «TÚ»/«RIVAL» sobre cada isla en las primeras partidas; unificar a azul (tú) / rojo (rival) en todo; iconos distintos para huella/cerca (ya hay 🔥, reforzar con forma).

### U22 · medio · Ficha de héroe: MEJORAR fuera de pantalla
- **Evidencia:** `heroPage` (`l. ≈3426-3452`), captura `v_m_heropage.png`: en 375×667 la ilustración ocupa ~45 % de la altura y el botón MEJORAR y «PONER EN PORTADA» quedan por debajo; solo se ve Maestría.
- **Impacto:** la acción principal de progresión no se ve; la notificación «↑» lleva a una pantalla donde no aparece el botón.
- **Arreglo:** botón MEJORAR fijo (sticky) abajo, o escenario del héroe de 160 px en pantallas bajas.

### U23 · medio · HUD: corazones cortados y nombre truncado
- **Evidencia:** capturas del entrenamiento: el panel del jugador muestra «Jugado…» y el 5.º corazón partido (en el entrenamiento la vida es +3, `TUT.setup`); con niveles 5/9 (+1 vida) pasa también en partidas normales.
- **Impacto:** la vida es la información más importante del HUD y no se ve completa.
- **Arreglo:** con más de 4 corazones, mostrar «♥ ×7» o dos filas; nombre con `max-width` pero sin quitar espacio a la vida.

### U24 · medio · Popups encadenados en las primeras visitas al inicio
- **Evidencia:** `showHome` abre `news` (héroe nuevo) a las 3 partidas (`l. ≈3362`); `homeEvents` (`l. 3393`) abre, en visitas sucesivas, `comeback`, sesión caducada, `guestnag` (3 partidas), `calendar` (≥2 partidas, una vez al día) y `maybeOffer` (`l. 3402`: `seasonnew` a las 3 partidas, `starter` a las 6). Cada vuelta del fin de partida al inicio entre las partidas 2 y 6 puede abrir una ventana nueva.
- **Impacto:** está bien que haya solo una por visita, pero se vive como «cada vez que vuelvo me salta algo»: típico motivo de desinstalación en los primeros días.
- **Arreglo:** presupuesto global de 1 popup no solicitado por sesión (no por visita), y nunca en la 1.ª-3.ª partida salvo el calendario; mover «héroe nuevo» a la tienda (banner) para jugadores con < 5 partidas.

### U25 · bajo · Fin de partida: «Trofeos · 40» confunde
- **Evidencia:** `l. 4335`: `<small>Trofeos · ${before}</small>`; captura `m_end.png` («+6 · Trophies · 40» con 46 de total). «Pass tokens ×2» sin explicar (recuperación por ir con retraso).
- **Impacto:** el jugador cree que tiene 40 o duda de si se sumaron.
- **Arreglo:** animar «40 → 46» (ya existe `countUp`); «×2: vas con retraso en el pase» como tooltip o fila.

### U26 · bajo · Camino de trofeos: raíl desalineado y barra superior oculta
- **Evidencia:** `showRoad` (`l. 3543-3560`): `frac=S.tro/top` sobre un raíl de nodos equiespaciados (`min-height:112px`), así que con 40 trofeos el relleno llega entre 10 y 20 (captura `v_road.png`). `scrollIntoView` desplaza la página y la barra de recursos queda fuera.
- **Arreglo:** calcular la altura del relleno por interpolación entre los nodos alcanzados; hacer el raíl desplazable dentro de un contenedor y dejar la barra superior fija.

### U27 · bajo · Iconos con varios significados
- **Evidencia:** estrella = fichas del pase (misiones, fin de partida), rondas ganadas (misiones) y velocidad (ficha de héroe); corona = Pase, modo «Con amigos», «Héroe raro» del día 7 del calendario (`v_m_calendar.png`), aspectos y marcos; trofeo = trofeos y victorias con el héroe (`hplate`, «🏆 1» en `m_home_after.png`).
- **Arreglo:** un icono por concepto (zapatilla para velocidad, espadas para victorias de héroe, silueta de héroe para «héroe raro», dos personas para amigos).

### U28 · bajo · Botones de resultado poco adecuados y sin reintento
- **Evidencia:** el modal `info` (`l. 3880`) siempre tiene un solo botón «VOLVER AL INICIO», usado para «¡Cuenta creada!», «¡Hola de nuevo!», «¡Progreso recuperado!» y para las desconexiones (`netGiveUp`, `l. 4401`). La cola online sin conexión sí ofrece «Jugar contra bot» (bien, `m_offline_queue.png`).
- **Arreglo:** «GENIAL»/«SEGUIR» para los éxitos (sin navegar); para errores de red, «REINTENTAR» + «Jugar contra bot».

### U29 · bajo · Traspaso de progreso con nombres que no coinciden
- **Evidencia:** modal `cloud` (`l. 3787`): «abre AMAGO → Ajustes → **Pasar mi progreso** → Tengo un código», pero en Ajustes el botón dice «☁️ Pasar mi partida a otro móvil» (`l. ≈3829`).
- **Arreglo:** usar exactamente el mismo texto en los dos sitios.

### U30 · bajo · «Cómo se juega» incompleto
- **Evidencia:** `HOW` (`l. 1456`): 5 tarjetas sin el AMAGO, sin la muerte súbita (45 s) ni el empate por vida al acabar el tiempo; «3 rondas, 3 héroes» cuando se gana con 2 y con empates puede haber hasta 5 (`endRound`).
- **Arreglo:** añadir tarjetas «🎭 Amago» y «⚡ Muerte súbita», y «Al mejor de 3 (gana quien llegue a 2)».

### U31 · bajo · Inglés mejorable
- **Evidencia:** «ROUND TO YOU!» / «ROUND TO PIXELKING» (`roundBanner`), «It was here!» (rival → «They were here!»), placeholder «Password (6 or more)» también en el login, «Hit!» como traducción de «¡Tocado!», y el nombre del juego (AMAGO) traducido como «FEINT» en el botón y en el entrenamiento, lo que desconecta marca y mecánica.
- **Arreglo:** «YOU WIN THE ROUND!», «PIXELKING TAKES THE ROUND», «Password (6+ characters)» solo al crear, y valorar mantener «AMAGO» como nombre propio de la mecánica («AMAGO: fake footprint»).

### U32 · bajo · Accesibilidad de sistema
- **Evidencia:** `<meta name="viewport" … maximum-scale=1, user-scalable=no>` (`l. 5`); no se usa Dynamic Type ni hay tamaño de texto en Ajustes; «reducir movimiento» solo se lee del sistema; la apertura de cofres es un `div data-a="boxtap"` sin rol de botón ni texto accesible; el lienzo de la arena tiene `aria-label` en español.
- **Arreglo:** opción «Texto grande» y «Menos efectos» en Ajustes; `role="button"` y `aria-label` en las capas táctiles a pantalla completa.

### U33 · bajo · Pequeños desbordes horizontales en 375 px
- **Evidencia (Playwright):** el «+» de gemas ocupa x=358-382 (se sale 7 px; captura `v_home_clean.png`), el sello «−30 % HOY» llega a x=378 (`v_shop.png`, «30 % TODA»).
- **Arreglo:** `margin-right` en la última pastilla y `overflow:hidden` en `.ocard` para los sellos.

### U34 · bajo · Sin ayuda ni contacto en el juego
- **Evidencia:** Ajustes (`l. ≈3820-3836`, `v_m_settings.png`): no hay «Ayuda/Contacto», ni ID de jugador visible para soporte, ni versión.
- **Arreglo:** fila «💬 Ayuda y contacto» (mailto con el ID y la versión) y el ID copiable en «Tu cuenta».

### U35 · bajo · Textos de cuenta fuera de lugar
- **Evidencia:** «Si tu Apple ID ya tiene una cuenta de AMAGO…» se muestra aunque `APPLE_OK` sea falso (Android/web) (`v_m_acc.png`). Placeholders con `letter-spacing` enorme («E m a i l»).
- **Arreglo:** condicionar esa frase a `APPLE_OK`; letter-spacing normal en `.inp` (salvo campos de código).

---

## Ritmo de recompensas y desbloqueos (notas)
- `UNLOCK={cal:1,mis:2,pass:3,shop:3,mastery:10}` (`l. 3200`): el ritmo es razonable, pero los menús bloqueados se ven desde el minuto 2 con candado (ver U13); mejor revelarlos al desbloquearse con una pequeña celebración.
- Camino de trofeos: premios a 10/20/30/40 (Ojo) ≈ cada 1-2 victorias en Fácil; buen ritmo inicial. Bosque (100) ≈ 15 victorias en Fácil (≈ 11 en Normal): conviene sugerir Normal antes (U18).
- La primera partida real no tiene premio «garantizado» propio más allá de las llaves; el entrenamiento ya da cofre, bien.

## Lista de textos sin traducir (modo inglés)

Comprobado reproduciendo `TR` en Node con `I18N_EN` del commit 486d05f y en las pantallas recorridas con Playwright.

**Texto visible**
1. «Jugador####» (nombre por defecto; HUD, VS, rival online) — `l. 1569`
2. «👤 Invitado» (Ajustes) — `l. 3822`
3. «cofre» (en «Con **3 llaves** ganas un **cofre**», modal Llaves) — `l. 3744`
4. «‹Cofre/Cofre grande/Megacofre› fijo» (pase Premium, recompensas fijas) — `rewardName`, `l. 3235`
5. «Quedan N hoy ·» (tienda, recursos, cuando no hay pagos: el patrón espera texto tras «·») — `l. 3510`
6. «vida», «velocidad» (consejo al elegir héroe; las demás piezas sí se traducen) — `l. 3997`
7. «Te faltan », « monedas», «. Se consiguen jugando, en cofres y en el pase.» (ficha de héroe sin recursos) — `l. 3450`
8. «Quedan N días» (cabecera del pase cuando no hay recuperación ×2) — `l. 3588`
9. «Te hemos guardado un regalo por volver.» (regreso tras 3-9 días) — `l. 3785`
10. «(sin conexión ahora mismo)» (modal de traspaso) — `l. 3791`
11. «Tu progreso ya está a salvo con tu Apple ID.» y el sufijo « +20 gemas de regalo.» (cuenta creada) — `l. 1640`, `l. 1677`
12. «Nada aleatorio se vende: … contenido fijo y visible. Las gemas no caducan.» (Compras y probabilidades sin pagos activos; solo existe la variante con IVA) — `l. 3751`
13. «¡TOCADO! −N» y «¡K.O.!» (texto flotante al acertar) — `l. 4586`
14. Nuevos en 486d05f: «👣 Huella falsa: allí NO está», «👣 Huella borrosa: está por esa zona» (`l. 4548`); «Truco deja huellas falsas: allí NO está.», «Sombra deja una huella borrosa: está cerca, no justo ahí» (`l. 4574`); «Golpes más rápidos · os veréis cada 5 s» (`l. 4606`); «🎭 Lejos de ti» (`l. 4733`)
15. Placeholder visible «CÓDIGO» (Con amigos y traspaso) — `l. 3790` y modal de amigos
16. Mensajes del servidor que no están en el diccionario: «Cuenta no encontrada.», «Ese código no existe o ha caducado.», «Prueba otra vez.», y los códigos internos «espera», «cuenta», «datos», «grande», «método» — `server/api.js:220-390`
17. Error técnico del navegador sin traducir ni adaptar: «Failed to fetch» / «Load failed» — `accSubmit`, `l. 1652`
18. Solo con pagos activos: «O CON 💎 450 GEMAS» (página del Pase Premium) — `premiumHTML`

**Atributos (VoiceOver / tooltips)**
19. `aria-label` «Perfil y ajustes», «Puntos de poder» (barra superior, todas las pantallas) — `l. 3341-3343`
20. `aria-label` «Cerrar» (todas las ✕), «Cambiar misión», «Año de nacimiento», «Código de traspaso», «Código de sala», «Nombre»
21. `aria-label` «Arena. Toca tu isla para moverte y la isla roja para atacar», «Amago: huella falsa en tu isla» — `l. 4503+`
22. `title` «Moverte una casilla» y «Poder N» (`pwrHTML`)

**Decisión de producto (no es un error, pero conviene decidir)**
23. Nombres de héroes en español con significado (Flecha, Brasa, Sombra, Muro, Ojo, Truco, Rayo, Bum, Mina, Salto, Savia, Mira, Eco): se dejan tal cual; valorar subtítulo en inglés («Flecha · the Archer» ya aparece en algunas fichas).
