# AMAGO · Auditoría S: servidor, anticheat, emparejamiento, seguridad, privacidad y cumplimiento de tiendas

Fecha: 6 nov 2026. Auditoría de solo lectura (no se ha modificado ningún archivo del repositorio).
Pruebas hechas con el servidor arrancado en local (`PORT=8099`, almacenamiento en archivos, `ws`/`pg` instalados en el scratchpad) y scripts propios:
`scratchpad/audit/t1.js` (API HTTP), `t2.js` (autoemparejamiento), `t3.js` (validación en partida contra el bot). El servidor que arranqué se paró con su PID.

Numeración de líneas: `server/server.js`, `server/api.js`, `server/store.js`, `server/stats.js` tal como están en la rama actual.

## Resumen

| id | sev. | título |
|---|---|---|
| S1 | alto | Trofeos inflables con `/api/save` (+40 por guardado, +20 por cada 45 s de ausencia) |
| S2 | alto (crítico antes de cobrar) | Economía, héroes desbloqueados y gemas «de pago» los decide el cliente |
| S3 | alto | Autoemparejamiento: una cuenta se empareja consigo misma y farmea trofeos |
| S4 | alto | `pg.Pool` sin manejador de `error`: una caída de Postgres tumba el proceso |
| S5 | alto | El bloqueo por contraseñas fallidas nunca se activa (bug de contador) |
| S6 | alto | Falta la revocación de Sign in with Apple (sin clave .p8) y la política dice que se hace |
| S7 | alto | Falta `NSPhotoLibraryAddUsageDescription`: «Guardar vídeo» en la hoja de compartir cierra la app |
| S8 | medio | Límites por IP basados en `X-Real-IP`, que puede venir del cliente |
| S9 | medio | Contaminación de prototipo (`Object.prototype`) desde `/api/ev` al abrir `/stats` |
| S10 | medio | `/api/ev` sin autenticación: suplantar uid, envenenar métricas y llenar la base de datos |
| S11 | medio | Borrado de cuenta incompleto y no atómico (eventos anónimos, invitados huérfanos, resurrección) |
| S12 | medio | Carreras lectura-modificación-escritura: se pierden guardados y trofeos |
| S13 | medio | Sin red de seguridad global ni cierre ordenado: cada despliegue corta todas las partidas |
| S14 | medio | Si Postgres falla al arrancar, se usa en silencio almacenamiento efímero |
| S15 | medio | Cuentas de correo sin verificación ni recuperación; enumeración de correos |
| S16 | medio | Bots del modo Online presentados como personas sin aviso |
| S17 | medio | Filtro de nombres eludible, con falsos positivos y sin denunciar/bloquear (1.2) |
| S18 | medio | Menores: <13 pueden registrar correo; analítica activa por defecto; edad solo en cliente |
| S19 | bajo | `/stats`: clave en la URL, comparación no constante, sin límite y clave por defecto `local` |
| S20 | bajo | CORS `*` y ninguna cabecera de seguridad (CSP, nosniff, HSTS, frame-ancestors) |
| S21 | bajo | Postgres: falta índice `events(uid)`, purga sin índice, TLS sin verificar, escrituras innecesarias |
| S22 | bajo | Android: `allowBackup=true` copia el secreto de la cuenta; falta la URL web de borrado que pide Google Play |
| S23 | bajo | Código de traspaso: toma la cuenta sin contraseña, vive en memoria y se puede adivinar si se salta el límite por IP |
| S24 | bajo | Sesiones eternas, secreto de invitado vigente tras registrarse, refresh token de Apple en claro, se pide un correo que no se usa |
| S25 | bajo | Esquivar rival sin penalización y congelar la partida del rival con desconexiones |
| S26 | bajo | Ficha y política inexactas (9 héroes, correo de Apple, revocación); URLs legales en el dominio del servidor de juego |

Verificado correcto (sin hallazgo): el motor es autoritativo (sin elixir no se dispara, el enfriamiento se respeta y las coordenadas fuera del tablero se ignoran), el rival oculto llega como `x:-9,y:-9`, `unl`/`tro` del `hello` se ignoran con base de datos, los nombres se escapan con `esc()` en todos los `innerHTML` revisados, el nonce de Apple se valida y se impide repetir el token, y scrypt con sal y `timingSafeEqual`.

---

## S1 · alto · Trofeos inflables con `/api/save`

**Evidencia:** `server/api.js:340-348`. `games` lo manda el cliente (`b.save.games`, hasta 1e6) y el tope de partidas nuevas es `floor((now - saveAt)/45000) + 2`. El trofeo nuevo se acota a `cur + dG*20`.
**Reproducción (`t1.js`):** cuenta nueva y 10 `POST /api/save` seguidos con `{games:1e6, tro:999999}` dan **tro = 400** (+40 por guardado, sin jugar). El límite es de 30 guardados por minuto, así que salen unos 1.200 trofeos por minuto. Además, tras un día sin guardar `dG ≈ 1.922`, y un solo guardado sube **+38.000**.
**Impacto:** los trofeos fijan el emparejamiento online (`hello` → `u.tro`), las arenas, el camino de trofeos (héroes gratis a 40/110/220/320/400), el tope de nivel por arena y la fuerza del bot. Un tramposo sube al instante y destroza el emparejamiento, y cualquier clasificación futura queda contaminada.
**Arreglo:** los trofeos de las partidas contra el bot no deben llegar en el guardado. Una opción es un endpoint `/api/botresult` con un registro de partida que el servidor pueda validar (semilla + entradas que el servidor vuelva a simular con el motor `E`, que ya carga). La otra, si no se quiere simular, es que el bot local no dé trofeos y solo los den las partidas online. Como mínimo: `dG` no puede superar las partidas registradas por el servidor (crear `/api/gamestart` con un token de un solo uso por partida), el tope fijo es de +20 por guardado y no se cuenta el tiempo de ausencia.

## S2 · alto (crítico antes de activar pagos) · Economía y desbloqueos de confianza del cliente

**Evidencia:** `server/api.js:332-353` guarda `b.save` tal cual (solo corrige `tro`). `index.html:1554` define `gemsPaid`, `coins`, `pp`, `unl`, `lv`, `box`, pase, etc., y todo se gana, se cobra y se canjea en el cliente (cofres, regalo diario, calendario, pase, misiones, `grantSku`). `server/server.js:528-530` toma **`u.save.unl`** como héroes disponibles en el online clasificado.
**Reproducción (`t1.js`):** un guardado con `coins:9e9, gemsFree:9e9, unl:[los 9 héroes]` se acepta, y `/api/load` lo devuelve. Al jugar online con esa cuenta, `available()` ofrece los 9 héroes, incluidos los raros que deberían estar bloqueados.
**Impacto:** cualquier premio se puede reclamar infinitas veces (basta editar el `localStorage` o el JSON), y los héroes de pago o de camino se usan en clasificatorias. Si se activan las compras sin cambiar esto, `gemsPaid` y el Pase Premium serían gratis (fraude, y Apple rechaza los bienes consumibles sin entrega verificable).
**Arreglo:** antes de StoreKit, mover al servidor el libro de cuentas: monedas, gemas (gratis y de pago), `unl`, `lv`, pase y cofres como operaciones idempotentes (`/api/claim-daily`, `/api/open-chest`, `/api/buy` con id de operación), con el reloj del servidor y la validación de recibos (`/api/iap` con App Store Server API). El guardado del cliente debe quedar como caché de presentación. En el online, calcular `unl` con lo que el servidor sabe que se ha desbloqueado.

## S3 · alto · Autoemparejamiento y farmeo de trofeos

**Evidencia:** `server/server.js:431-449` (`matchmake`) no comprueba que `a.uid !== b.uid`. `MAX_CONN_PER_IP = 8` permite varias conexiones. En `leave()` (`server.js:500-503`), quien abandona pierde `troLoss(t)` (0 por debajo de 30 trofeos, 2 por debajo de 300) y el rival gana entre 8 y 10.
**Reproducción (`t2.js`):** dos sockets con el mismo `id/secret` hacen `queue`, se emparejan entre sí (diferencia 0) y uno manda `leave` tras 1,5 s. Cinco ciclos de unos 3,5 s cada uno llevan la cuenta de **0 a 39 trofeos** sin jugar ninguna ronda. Con dos cuentas (la secundaria siempre por debajo de 30 trofeos, sin pérdida) el farmeo no tiene coste.
**Impacto:** los trofeos online, que deberían ser los fiables, se fabrican a ritmo de unos 140 por minuto.
**Arreglo:** impedir que un `uid` esté a la vez en cola o en sala (cerrar la conexión anterior al hacer `hello` con el mismo uid) y no emparejar el mismo uid ni la misma IP o dispositivo. Por abandono antes del primer `go`, ninguno gana trofeos (o solo el que se queda, con un máximo diario). Limitar las victorias por abandono contra el mismo rival, y que el que abandona pierda como mínimo lo mismo que gana el otro.

## S4 · alto · `pg.Pool` sin `pool.on('error')`

**Evidencia:** `server/store.js:86` crea el `Pool` y en ningún sitio hay `pool.on("error", …)`. Según la documentación de `node-postgres`, si un cliente inactivo pierde la conexión (reinicio, failover, mantenimiento de Railway o tiempo de espera de la red), el Pool emite `error`. Sin oyente, Node lanza la excepción y **el proceso termina**. Tampoco hay `process.on("uncaughtException")`.
**Impacto:** cualquier mantenimiento del Postgres de Railway mata el servidor: todas las partidas en curso se pierden, con trofeos a medias, y las salas, los códigos de traspaso y los tokens usados se borran de memoria.
**Arreglo:** `pool.on("error", e => console.error("pg idle", e.message))`; `idleTimeoutMillis`/`connectionTimeoutMillis`; reintentos con espera en `get/put`; y `/health` que compruebe `select 1` para que Railway reinicie solo si de verdad no hay base de datos.

## S5 · alto · El bloqueo por intentos fallidos no funciona

**Evidencia:** `server/api.js:266-267`:
```js
const n = (f && f.until > Date.now() - 15 * 60000 ? f.n : 0) + 1;
failed.set(email, { n, until: n >= 8 ? Date.now() + 15 * 60000 : 0 });
```
Mientras `n < 8`, `until` vale 0, así que en el siguiente fallo `f.until > now-15min` es falso y `n` vuelve a 1. **Nunca llega a 8.** Además, la limpieza (`api.js:26`) borra cada minuto las entradas con `until = 0`.
**Reproducción (`t1.js`):** 8 contraseñas erróneas para `victima@gmail.com` no producen ningún 429, y el inicio de sesión correcto sigue entrando.
**Impacto:** la única defensa contra la fuerza bruta es el límite de 10 por minuto y por IP, que S8 permite saltar. Con contraseñas de mínimo 6 caracteres y sin listas de contraseñas comunes, una cuenta se puede atacar con diccionario.
**Arreglo:** guardar `{n, first}` y bloquear cuando `n >= 8` dentro de la ventana; aumentar el retardo con cada fallo; añadir un límite global por cuenta independiente de la IP; exigir 8 caracteres o más y rechazar las contraseñas más comunes. Para que no sirva para bloquear a terceros (DoS), aplicar al bloqueo por correo un retardo progresivo en lugar de un bloqueo total, o un CAPTCHA o código por correo.

## S6 · alto · Revocación de Sign in with Apple no configurada

**Evidencia:** `server/api.js:155,166,180-198`: sin `APPLE_TEAM_ID/APPLE_KEY_ID/APPLE_PRIVATE_KEY`, `appleRevoke` devuelve `false` y `appleRefreshToken` no guarda nada. `PROGRESO.md` lo apunta como «pendiente del usuario (opcional): clave .p8». El cliente (`index.html:1686-1690`) incluso pide un `authorizationCode` nuevo al borrar, pero el servidor no puede usarlo.
**Impacto:** la guía 5.1.1(v) y la nota técnica de Apple (desde junio de 2022) exigen revocar los tokens de usuario al borrar una cuenta creada con Sign in with Apple. Es motivo de rechazo en cuanto el revisor lo pruebe. La política de privacidad afirma «si entraste con Apple revocamos el acceso» y «guardamos un token de Apple», lo cual hoy es falso.
**Arreglo:** crear la clave de Sign in with Apple en developer.apple.com y cargar las tres variables en Railway. Si falla `appleRevoke`, apuntarlo en una cola de reintentos (tabla `pending_revokes`) en lugar de ignorarlo. Opcional: el endpoint de notificaciones servidor a servidor de Apple (`consent-revoked`, `account-delete`).

## S7 · alto · Falta `NSPhotoLibraryAddUsageDescription`

**Evidencia:** `index.html:4228` comparte el clip de la repetición con `Cap.Share.share({files:[uri]})` (vídeo en `CACHE`). La hoja nativa de iOS (UIActivityViewController) ofrece «Guardar vídeo». `app/ios/App/App/Info.plist` no tiene `NSPhotoLibraryAddUsageDescription`.
**Impacto:** iOS mata la app («attempted to access privacy-sensitive data without a usage description») cuando el usuario toca «Guardar vídeo». Es un cierre visible en una función que la ficha anuncia («comparte el clip») y que el revisor puede probar. Comprobar en un dispositivo real.
**Arreglo:** añadir `NSPhotoLibraryAddUsageDescription` («AMAGO guarda en tus fotos los clips de repetición que decidas guardar.») y su traducción al inglés en `InfoPlist.strings`. Revisar también `CFBundleLocalizations` (es, en), porque la app tiene interfaz en inglés.

## S8 · medio · Límites por IP basados en una cabecera del cliente

**Evidencia:** `server/server.js:73-78` usa `x-real-ip` si viene y, si no, el último valor de `x-forwarded-for`. Todos los límites (`MAX_CONN_PER_IP`, creación de salas, códigos erróneos y todos los `limited()` del API) dependen de él.
**Reproducción (`t1.js`, en local):** 40 `POST /api/acc` con `X-Real-IP` distinta dan **40/40 aceptados** (el límite es 10/min). Sin la cabecera, 9/20.
**Impacto:** si el proxy de Railway no sobrescribe un `X-Real-IP` que mande el cliente, se pueden saltar todos los límites: crear cuentas sin fin, fuerza bruta de contraseñas (S5), de códigos de traspaso (S23) y de salas, abrir más de 8 conexiones o llenar la base de datos (S10).
**Arreglo:** probar contra producción con `curl -H 'X-Real-IP: 1.2.3.4'` y comparar con lo que registra el servidor. Si Railway la pasa tal cual, usar solo el último salto de `X-Forwarded-For` que añade Railway (o `req.socket.remoteAddress` si no hay proxy). Añadir también límites por cuenta, no solo por IP.

## S9 · medio · Contaminación de prototipo desde `/api/ev` al abrir `/stats`

**Evidencia:** `server/stats.js:62-69`:
```js
const h = r.d.hero; … H[h] = H[h] || { n: 0, w: 0 }; H[h].n++; if (r.d.win) H[h].w++;
```
Con `hero:"__proto__"`, `H["__proto__"]` es `Object.prototype` y se le añaden `n` y `w`.
**Reproducción:** `POST /api/ev {ev:[{k:"round_end",d:{hero:"__proto__",win:true}}]}` sin autenticación. Al abrir `/stats`, en el mismo proceso `({}).n === NaN` y `({}).w === NaN` (comprobado llamando a `statsPage` con ese evento). `modes[m.d.mode]` tiene el mismo patrón.
**Impacto:** todo objeto del servidor hereda `n`/`w`. Hoy no he encontrado una ruta de explotación directa, pero es una base clásica para saltarse comprobaciones (`if (obj.n)`) y estropea el panel. Lo dispara cualquiera, sin cuenta.
**Arreglo:** `const H = Object.create(null)` y `modes = Object.create(null)` (o `Map`); validar `d.hero` contra `heroIds` y `d.mode` contra una lista en `/api/ev`.

## S10 · medio · `/api/ev` sin autenticación

**Evidencia:** `server/api.js:391-406`: el `uid` es el `b.id` que mande el cliente, sin secreto; se aceptan 60 eventos por petición y 40 peticiones por minuto, y cada `d` puede ocupar hasta 400 B. `stats.js:10` y `store.js:128-131` cargan 60 días de eventos en memoria por cada visita a `/stats`.
**Impacto:** (a) cualquiera atribuye eventos a la cuenta de otro (el id viaja en claro, por ejemplo en capturas), lo que ensucia los datos personales de ese usuario (RGPD, exactitud); (b) se envenenan las métricas de retención y embudo con uids inventados; (c) unas 2.400 filas, alrededor de 1 MB por minuto y por IP (sin límite combinado con S8), llenan Postgres y hacen que `/stats` agote la memoria.
**Arreglo:** exigir `id`+`secret` (o un HMAC de sesión) o aceptar solo eventos sin uid; validar `k` contra una lista cerrada y `d` con un esquema; poner un límite diario de eventos por cuenta; precalcular las métricas (tabla diaria agregada) en vez de cargarlo todo; y tope o particiones de `events`.

## S11 · medio · Borrado de cuenta incompleto y no atómico

**Evidencia:**
- `index.html:1706`: sin cuenta (`ACC`), los eventos van con un id anónimo `amago-uid` de `localStorage`. `store.del()` (`store.js:101-105`) solo borra `events where uid = <id de cuenta>`, así que esos eventos se quedan.
- Al iniciar sesión con correo o Apple en otro móvil, o al hacer `accLogout` (`index.html:1696-1699`, `CLOUD.init()` crea otro invitado), las cuentas de invitado anteriores quedan huérfanas con su guardado y sus eventos hasta la purga de 24 meses. «Borrar cuenta» no las toca.
- Los tres `DELETE` van sin transacción: si falla el segundo, quedan eventos o logins sueltos y el cliente ya ha dado el borrado por hecho si respondió 200 (en realidad el error termina en 400, pero las filas borradas antes no se recuperan).
- Resurrección: `store.put` es un *upsert*. Un `/api/save` o `/api/load` que haya pasado `auth()` justo antes del borrado vuelve a crear el usuario después (`api.js:236-238`, `353`).
- Las conexiones WS abiertas y los `links` de traspaso de esa cuenta siguen vivos en memoria.
**Impacto:** la política promete «se eliminan … junto con tus estadísticas», y el borrado no es completo (art. 17 RGPD; Apple 5.1.1(v) pide borrar los datos asociados).
**Arreglo:** que el cliente mande también su `amago-uid` y la lista de ids de invitado que haya usado ese dispositivo, y borrarlos. Al convertir o iniciar sesión, fusionar o borrar el invitado anterior. Hacer el borrado en una transacción, poner una marca `deleted` (tumba) que `put` respete (`update … where not deleted`), cerrar las conexiones WS de ese uid y borrar sus `links`.

## S12 · medio · Carreras lectura-modificación-escritura

**Evidencia:** `get` → modificar → `put` del documento JSON entero, sin control de versión en SQL: `/api/load` (`api.js:236-238`, escribe en **cada** carga para actualizar `last`), `/api/save`, `/api/login`, `/api/apple` y `rankedResult` (`server.js:357-368`).
**Impacto:** si `/api/load` (al abrir la app) y `/api/save` (al pasar a segundo plano) se cruzan, o dos móviles de la misma cuenta, o un `rankedResult` con un guardado, la segunda escritura pisa la primera: se pierde el guardado (y vuelve un `rev` anterior), los trofeos online o una sesión nueva (`shs`).
**Arreglo:** actualizaciones atómicas en SQL (`update users set data = jsonb_set(...)`, `data->'tro'` sumado en la consulta) o bloqueo optimista (`update … where (data->>'rev')::int = $old`). `last` en su propia columna, actualizada sin reescribir el JSON.

## S13 · medio · Sin red de seguridad global ni cierre ordenado

**Evidencia:** el bucle de partida (`server.js:284-301`), los temporizadores de elección y fin de ronda (`156`, `332`, `398`) y los `setTimeout` del bot no tienen `try/catch`. Solo `handle()` lo tiene (`server.js:682-686`). No hay `process.on("uncaughtException"|"unhandledRejection")` ni manejador de `SIGTERM`. Según `PROGRESO.md`, cada push a la rama despliega.
**Impacto:** un solo fallo del motor en `E.tick`/`botUpdate` (por ejemplo, con un héroe nuevo con `live:true`) tumba todas las salas. Cada despliegue mata las partidas sin avisar: `resume` responde `resumeFail` porque las salas vivían en memoria, y los trofeos de esas partidas quedan sin resolver. Los códigos de traspaso, `usedTokens` de Apple y los contadores de límites se reinician.
**Arreglo:** envolver cada `tick` en `try/catch` y, si falla, cerrar esa sala sola como empate. Con `SIGTERM`: dejar de aceptar colas, avisar a los clientes y esperar a que terminen las rondas (Railway da un tiempo de gracia configurable con `RAILWAY_DEPLOYMENT_DRAINING_SECONDS`). Desplegar desde una rama de producción y no desde la de trabajo. Si algún día hay más de una instancia, el estado efímero importante (links, tokens usados) debe ir a Postgres o Redis.

## S14 · medio · Si Postgres falla al arrancar, se usan archivos efímeros sin avisar

**Evidencia:** `server/store.js:139-151`: si `pgStore()` lanza (Postgres arrancando, credenciales rotadas, red), se registra un error y se usa `fileStore` en el disco efímero de Railway. El servidor arranca normal y `/health` responde `ok`.
**Impacto:** durante ese despliegue, todas las cuentas nuevas, los guardados, los registros y los borrados van a un disco que se pierde en el siguiente despliegue. Los jugadores existentes reciben 401, el cliente crea cuentas nuevas y luego no las encuentra. Además, un borrado de cuenta hecho en ese periodo no se aplica a Postgres: el cliente lo da por bueno y la cuenta sigue en la base de datos real (incumplimiento de borrado).
**Arreglo:** en producción (`RAILWAY_ENVIRONMENT` o `DATABASE_URL` definidos), no usar archivos: reintentar con espera creciente y, si no se puede, salir con código ≠ 0 para que Railway reintente. `/health` debe reflejar el estado de la base de datos.

## S15 · medio · Cuentas de correo sin verificación ni recuperación; enumeración

**Evidencia:** `server/api.js:241-257` registra cualquier correo sin confirmarlo. No hay ruta para restablecer ni cambiar la contraseña. `409 "Ya hay una cuenta con ese correo"` revela si un correo existe. `/api/login` solo ejecuta scrypt (unos 50 ms) si el correo existe (`api.js:263-265`): otra forma de enumerar, por tiempo.
**Reproducción (`t1.js`):** registro de `victima@gmail.com` con contraseña `123456` aceptado. Un segundo intento con otra cuenta recibe 409, lo que confirma que el correo existe.
**Impacto:** alguien puede ocupar el correo de otra persona y el dueño real ya no puede registrarse. Quien olvide la contraseña pierde la cuenta, salvo con un código de traspaso del móvil viejo, y lo único que queda es el correo de soporte, sin forma de verificar la identidad. El correo que se guarda puede no ser de quien juega, lo que también es un problema de exactitud (RGPD).
**Arreglo:** enviar un enlace o código de verificación por correo (Postmark, SES…) antes de dar la cuenta por creada, añadir «He olvidado mi contraseña» y unificar las respuestas («Si el correo es válido, te hemos enviado un código»). En el login, ejecutar scrypt contra un hash ficticio cuando el correo no exista.

## S16 · medio · Bots del modo Online presentados como personas

**Evidencia:** `server/server.js:179-194` (`makeBot`): apodo como el de una persona, trofeos ±55 de los tuyos y retrasos de elección simulados (`174`). `405`: «rival en 8-18 s (como un emparejamiento real)». `PROGRESO.md`: «bot online indistinguible». La ficha dice «ONLINE O CON AMIGOS: rivales de tu nivel en segundos», y solo las notas para Apple mencionan «or a bot».
**Impacto:** con poca población, casi todas las partidas «online» son contra bots, sin que el jugador lo sepa, y dan trofeos «online». Apple (2.3.1: la descripción y la funcionalidad no deben engañar) y la normativa de consumo de la UE (Directiva 2005/29, Digital Fairness y orientaciones de la CPC sobre videojuegos) consideran engañoso hacer creer que se juega contra personas. Si un usuario lo descubre, es un riesgo para la reputación.
**Arreglo:** decir en la ficha y en la pantalla de búsqueda «Si no hay rival en unos segundos, juegas contra un rival de práctica» (puede seguir siendo sutil durante la partida), o marcar al rival como «IA» en la pantalla de resultados. Además: un emparejamiento en dos fases (ampliar el rango antes de recurrir al bot) y métricas del % de partidas con bot por franja horaria.

## S17 · medio · Filtro de nombres eludible y sin denunciar/bloquear

**Evidencia:** `server/server.js:122-140`. `norm()` usa NFD (no NFKD) y elimina todo lo que no sea `a-z`.
**Reproducción:** pasan `"рuta"` (р cirílica), `"ｐｕｔａ"` (ancho completo), `"Ꮲuta"`, `"f*ck"` y `"n!gger"`. Se bloquean nombres legítimos: `"Penélope"`, `"Viola"`, `"Sexto"`, `"Dickens"`, `"Pepe Escoño"`. Se aceptan caracteres invisibles o de control bidi (U+202E, U+200B), que permiten nombres engañosos o en blanco.
**Impacto:** los nombres que escriben los jugadores se ven en las salas con amigos (y en el cliente: VS, banners, «quiere la revancha»). La guía 1.2 de Apple exige, para contenido generado por usuarios, filtrar, permitir denunciar y bloquear, y dar un contacto. El cuestionario de edad declara «Contenido generado por usuarios: No».
**Arreglo:** NFKC más una tabla de confusables (Unicode TR39 *skeleton*), quitar las categorías `Cf`/`Cc` y comprobar las palabras prohibidas sobre texto con y sin signos de puntuación. Usar una lista de excepciones (Scunthorpe) en vez de `includes` a ciegas. En las salas privadas, añadir «Ocultar nombres» y «Denunciar» (aunque sea un `mailto:`), o mostrar solo apodos automáticos también con amigos.

## S18 · medio · Menores: registro y analítica sin restricción por edad

**Evidencia:** la edad se pregunta en el cliente (`index.html:4658`, `S.age.band`) y solo se usa para limitar las compras (`3280-3285`). Quien declara menos de 13 años puede crear una cuenta con correo y contraseña, y la analítica (`EV`) está activa por defecto con un identificador seudónimo. La política (privacidad.html, «Menores») dice «Si eres menor de 14 años, juega online con permiso…» sin ningún mecanismo. La clasificación prevista es 9+.
**Impacto:** COPPA (EE. UU.): recoger el correo y un identificador persistente de menores de 13 sin consentimiento verificable de los padres. RGPD art. 8 / LOPDGDD art. 7: en España se necesita consentimiento parental por debajo de 14 años cuando la base es el consentimiento. La analítica con identificador en el dispositivo podría requerir consentimiento (art. 22.2 LSSI) según el criterio de la AEPD.
**Arreglo:** para `u13` (o `<14` en España), ocultar el registro con correo y el online con nombres libres y desactivar la analítica (o hacerla sin identificador). Mandar la franja de edad al servidor para hacerla cumplir allí. Valorar pedir consentimiento para la analítica en el primer arranque (UE). Ajustar la política al comportamiento real.

## S19 · bajo · Protección de `/stats`

**Evidencia:** `server/api.js:201,209-215`: la clave va en la URL (`?k=`), así que queda en los registros de Railway, el historial del navegador y el `Referer`. La comparación es `!==` (no en tiempo constante) y no hay límite de intentos. Fuera de Railway y sin `STATS_KEY`, la clave es `"local"`. **Reproducción:** `GET /stats?k=local` responde 200 en local, y lo mismo pasaría en Render u otro proveedor sin esa variable.
**Impacto:** quien consiga la clave ve las métricas de negocio. `statsPage` carga además todos los documentos de usuario (con `ph`, `sh`, `appleRt`) en memoria.
**Arreglo:** cabecera `Authorization: Bearer` o autenticación básica, `timingSafeEqual`, `limited(ip,"stats",5)`, ninguna clave por defecto salvo con `NODE_ENV=development`, y en `allUsers` solo las columnas necesarias (`created`, `last`, `email is not null`).

## S20 · bajo · CORS `*` y ninguna cabecera de seguridad

**Evidencia:** `server/api.js:53` (`access-control-allow-origin: *` en todo el API). `server/server.js:65` y las páginas HTML (juego, privacidad, soporte) no llevan CSP, `X-Content-Type-Options`, `frame-ancestors`/`X-Frame-Options`, HSTS ni `Referrer-Policy`. `index.html` no tiene `<meta http-equiv="Content-Security-Policy">`.
**Impacto:** como la autenticación va en el cuerpo de la petición, el CORS abierto no permite CSRF, pero sí que cualquier web cree cuentas o mande eventos desde el navegador de sus visitantes (S10). Sin CSP, un futuro fallo de `esc()` sería una XSS completa que robaría `id/secret` de `localStorage`. El juego web se puede incrustar en un iframe (clickjacking).
**Arreglo:** permitir solo los orígenes `capacitor://localhost`, `https://localhost` (Android) y el dominio propio. Cabeceras: `Content-Security-Policy: default-src 'self'; connect-src 'self' wss://…; img-src 'self' data: blob:; frame-ancestors 'none'`, `X-Content-Type-Options: nosniff`, `Strict-Transport-Security` y `Referrer-Policy: no-referrer`. En la app, una CSP equivalente en `<meta>`.

## S21 · bajo · Postgres: índices, purga, TLS y escrituras

**Evidencia:** `server/store.js:87-91` solo indexa `events(t)` y `logins(uid)`. `del` hace `delete from events where uid=$1` **sin índice**, recorriendo toda la tabla en cada borrado de cuenta. La purga (`116`) evalúa `(data->>'last')::bigint` sobre todo `users`. `ssl:{rejectUnauthorized:false}` (`86`) acepta cualquier certificado. `max:5` comparte conexiones entre el juego y `/stats` (que hace `select` de tablas enteras). `/api/load` reescribe el JSON entero (hasta 48 KB) en cada apertura.
**Impacto:** el borrado y la purga se vuelven lentos a medida que crece `events`, y una consulta de `/stats` puede ocupar el pool y frenar los guardados. TLS sin verificar permite un ataque de intermediario en la red interna.
**Arreglo:** `create index on events(uid)`; columnas reales `last bigint`, `email text`, `tro int` con índices; purga por lotes; `ssl` con la CA de Railway (o sin TLS si es la red privada `*.railway.internal`); un pool aparte para `/stats` o vistas materializadas; `last` actualizado con un `update` pequeño.

## S22 · bajo · Android: copia de seguridad y borrado exigido por Google Play

**Evidencia:** `app/android/app/src/main/AndroidManifest.xml`: `android:allowBackup="true"` sin `dataExtractionRules`, y el `localStorage` del WebView (con `id`+`secret` de la cuenta) entra en las copias de Google y en `adb backup`. `res/xml/file_paths.xml` declara `external-path "."` (toda la memoria externa compartible con FileProvider). `soporte.html` y la ficha solo explican el borrado dentro de la app.
**Impacto:** restaurar una copia en otro dispositivo clona la sesión, y quien extraiga la copia obtiene la cuenta. La política de datos de usuario de Google Play exige un **enlace web** donde se pueda pedir el borrado de la cuenta sin reinstalar la app (formulario «Data deletion» de Play Console): sin él, se rechaza o se retira la app.
**Arreglo:** `allowBackup="false"` (o reglas que excluyan `app_webview`), limitar `file_paths.xml` a `cache-path`. Añadir en `soporte.html` un apartado «Borrar mi cuenta» con instrucciones y un formulario o correo (con el id de la cuenta o el correo de acceso), y ponerlo en Play Console.

## S23 · bajo · Código de traspaso

**Evidencia:** `server/api.js:356-381`. Con un código de 6 caracteres (32^6 ≈ 1,07·10^9), válido 15 minutos, cualquiera **sin autenticar** obtiene la cuenta (también las registradas con correo o Apple) y se invalidan todas las sesiones del dueño (`u.sh = …; u.shs = []`). El límite es de 6 por minuto y por IP (saltable con S8). Los códigos viven en un `Map` en memoria y se pierden al reiniciar.
**Impacto:** el riesgo de adivinarlo es bajo, pero una captura de pantalla o alguien mirando el móvil basta para robar la cuenta y echar al dueño, que no tiene forma de recuperarla.
**Arreglo:** para las cuentas con correo o Apple, no permitir el traspaso por código (que inicien sesión). Para invitados: 8 caracteres o más, un solo código activo por cuenta, confirmación en el móvil de origen («¿Pasar tu partida a otro móvil?») y aviso al dueño. Guardar los códigos en Postgres.

## S24 · bajo · Sesiones y tokens

**Evidencia:** `server/api.js:59-69`: las sesiones (`sh`, `shs`) no caducan nunca. El secreto de invitado (`sh`) sigue siendo válido después de registrarse, y solo se quita al cerrar sesión (`api.js:324`). `appleRt` (refresh token de Apple) se guarda en claro en el JSON del usuario (`api.js:298,314`). `AppleAuthPlugin.swift:28` pide el permiso `.email`, pero el servidor guarda `"Apple ID"` y lo descarta (`api.js:289,312`), aunque `PrivacyInfo.xcprivacy` declara Email.
**Impacto:** si se filtra un `id/secret` (copia de seguridad, S22), da acceso permanente. Si se filtra la base de datos, se exponen los refresh tokens de Apple. Se pide un dato que no se usa (minimización, art. 5.1.c RGPD).
**Arreglo:** caducidad deslizante (por ejemplo, 180 días) por sesión; al registrarse, cambiar el `sh` por una sesión nueva; cifrar `appleRt` con una clave del entorno (AES-GCM); pedir `requestedScopes = []` si no se va a usar el correo, o usarlo (para recuperación) y declararlo bien; y una opción de «Cerrar sesión en todos los dispositivos».

## S25 · bajo · Esquivar rivales y congelar partidas

**Evidencia:** `server/server.js:500`: `midMatch` exige `state !== "lobby"`. Durante 1,5 s tras `matched` (`server.js:398`) se ven el apodo y los trofeos del rival, y salir no cuesta nada (se puede volver a la cola al momento). `onClose` (`server.js:467-487`) pausa la partida de los dos hasta 15 s por corte y 25 s en total por partida, y el jugador elige cuándo.
**Impacto:** se puede esquivar a los rivales con más trofeos y elegir solo los fáciles (o los bots, si se distinguen). Cortar la conexión en el momento clave congela al rival y da tiempo para pensar o para frenar su racha de elixir.
**Arreglo:** contar como abandono (sin trofeos para nadie, con penalización ligera y espera para volver a la cola) cualquier salida tras `matched`. No enseñar los trofeos exactos del rival hasta `go`. Durante una ausencia, en vez de pausar, dejar al héroe quieto e invulnerable unos segundos, o pausar solo una vez por partida.

## S26 · bajo · Ficha, política y URLs

**Evidencia y arreglo:**
- La ficha dice «8 HÉROES» y `E.IDS` publica 9 (Mira, `live` desde el 15 oct). Corregir el texto (o «9+»).
- La política dice que Apple «nos da… tu correo» y que «guardamos un token de Apple para poder revocar», y ninguna de las dos cosas pasa (S6, S24). Ajustar el texto o el código.
- La política dice «Ajustes → Borrar progreso … junto con tus estadísticas», cuando el borrado es incompleto (S11).
- `PrivacyInfo.xcprivacy` y App Privacy no declaran la franja de edad (se guarda en el guardado de la nube) ni el nombre de jugador como «Otro contenido del usuario». Revisarlo con S18.
- Las URLs de privacidad y soporte están en el servidor de juego (`maker-portfolio-production-7712.up.railway.app`): si cae el servidor o se cambia de proveedor, la ficha queda con enlaces rotos (Apple 5.1.1(i) exige que la URL funcione). Mejor un dominio propio o GitHub Pages.
- Como no hay compras, comprobar que «Restaurar compras» e «Información de compras y probabilidades» no aparecen con `PAY_NONE`: Apple rechaza referencias a compras que no existen (2.1/3.1.1). No lo he podido verificar sin ejecutar el cliente.

---

## Comprobado y correcto (para no repetir trabajo)

- **Elixir y enfriamiento en el servidor:** 25 `fire` seguidos dejan pasar **1** (`t3.js`); `move` a `(99,-3)` se ignora (`inB`).
- **Rival oculto:** `view.heroes.b` llega con `x:-9,y:-9` salvo con Visión; el elixir del rival no se envía; los ids son opacos por sala; los disparos sin aviso no dicen al defensor ni las casillas ni `hitAt`.
- **`hello`:** con base de datos, `tro`/`unl` del mensaje se ignoran (elegir `rayo` sin tenerlo da `flecha` al azar). Un solo `hello` por conexión.
- **Mensajes malformados** (`[]`, `null`, `pick` fuera de sala, `resume` con `__proto__`) no tumban el servidor. `maxPayload` es de 2 KB y hay un límite de 30 mensajes por segundo.
- **XSS:** los nombres pasan por `esc()` en todos los `innerHTML` que los muestran (`index.html:3333, 3867, 3871, 3983-3988, 4258, 4358, 4444, 4446, 4483, 4497-4499`), y el servidor quita `<>&"`.
- **Sign in with Apple:** firma RS256 con JWKS, `iss`, `aud`, `exp`, nonce SHA-256 y un solo uso del token. Las contraseñas usan scrypt (N=16384) con sal y comparación en tiempo constante.
- **iOS:** solo vertical, `UIRequiresFullScreen`, solo iPhone (`TARGETED_DEVICE_FAMILY=1`), ATS por defecto (`build-www.js` exige `https://`), `ITSAppUsesNonExemptEncryption=false` y `NSPrivacyTracking=false`.
