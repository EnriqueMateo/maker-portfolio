# AMAGO en portales de juegos web (gratis, sin mantenimiento)

La misma partida que en el móvil, jugable en el navegador. Los portales ya tienen el tráfico: tú solo subes el .zip una vez. En la versión web sale un botón «Móvil» (y, tras algunas victorias, un aviso al final) que lleva a la App Store.

## 1. Preparar el .zip

**Recomendado: el .zip que se actualiza solo** (`app/portal/amago-web-itch-embed.zip`, 1 KB). Abre dentro del portal el juego del servidor, así que cada mejora que subo llega sola al portal: lo subes una vez y te olvidas.
```
cd amago/app
AMAGO_SERVER=https://maker-portfolio-production-7712.up.railway.app node scripts/build-portal.js itch --embed
```
Única pega: en Safari, el progreso de quien juega como invitado dentro del portal puede borrarse; con cuenta (Apple o correo) se guarda siempre.

Alternativa con todos los archivos dentro (no se actualiza sola, hay que volver a subirla):
```
cd amago/app
AMAGO_SERVER=https://maker-portfolio-production-7712.up.railway.app node scripts/build-portal.js itch
```
Sale `app/portal/amago-web-itch.zip` (~45 MB). Para CrazyGames: el mismo comando con `crazygames` (allí el botón de la App Store va apagado porque no permiten enlaces a otras tiendas).

## 2. itch.io (empieza aquí: aprueban al momento)
1. Crea la cuenta en itch.io (gratis) → «Upload new project».
2. **Kind of project:** HTML. Sube el .zip y marca «This file will be played in the browser».
3. **Viewport:** 400 × 780, marca «Mobile friendly» (vertical) y «Fullscreen button».
4. **Título:** `AMAGO: Blind Duel` · **Precio:** gratis · **Género:** Strategy · **Tags:** `pvp, 1v1, multiplayer, strategy, hide-and-seek, bluffing, cute, mobile, browser, real-time`.
5. **Descripción** (en inglés, el público de itch es internacional):
   > Real-time 1v1 blind duels. Your hero hides on your island, your rival's on theirs: nobody sees anybody. Move, read the footprints and strike first, or leave a FEINT so they shoot where you are not. 9 heroes, a 5-world campaign with bosses, online matches and private rooms. Free, no ads. Also on the App Store.
6. Capturas: usa las de `store/capturas/en` y una portada de 630×500.

## 3. CrazyGames (más tráfico, revisan el juego)
1. developer.crazygames.com → «Submit game» con el .zip de `crazygames`.
2. Primero lo ponen en «Basic launch» (unos días de prueba con tráfico real). Si los jugadores vuelven y juegan rato, pasa a «Full launch» y les reparte el juego a millones de visitas al mes.

## Qué esperar (realista)
- itch.io: 3-15 jugadores al día al principio, que bajan si no se actualiza.
- CrazyGames: si supera el «Basic launch», decenas o cientos de jugadores al día; si no, casi nada.
- De la web a la App Store pasa poca gente (1-3 %), pero los jugadores web cuentan como jugadores (rellenan el online y suben las métricas).

## El enlace de reto (lo que más puede crecer solo)
En «Con amigos» → crear sala, ahora hay un botón **ENVIAR RETO**. Manda un enlace (`…/s/ABCD`) por WhatsApp o donde sea: tu amigo lo abre y juega contra ti en el navegador al momento, sin instalar nada. Desde la app de iPhone el enlace también funciona. Al compartir una jugada, el texto lleva otro enlace (`…/j`) que manda a la App Store desde iPhone y al juego web desde lo demás.

Consejo: en Railway puedes cambiar gratis la dirección por una más corta (Settings → Networking → editar el dominio, p. ej. `amago.up.railway.app`). Si lo haces, avísame y cambio la dirección del servidor en la app.
