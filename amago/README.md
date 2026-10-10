# AMAGO: prototipo jugable

Hundir la flota con héroes que se mueven. Encuéntralos antes de que te encuentren.

El juego está en un solo archivo HTML. Usa Three.js (incluido en `vendor/three.min.js`, licencia MIT en `vendor/THREE-LICENSE.txt`) para la arena y los héroes en 3D, y carga dos fuentes de Google Fonts. Abre `index.html` en el navegador del móvil o del ordenador para jugar contra el bot.

## Modo online

Hay dos modos online:
- **Online:** cola de emparejamiento. El servidor te junta con un rival real de trofeos parecidos (empieza en ±80 y el rango se abre 40 trofeos por segundo de espera). Da trofeos y las recompensas de la dificultad Normal. Si tras 25 s no hay nadie, el juego ofrece jugar contra el bot. Si el rival abandona, ganas tú.
- **Con amigos:** sala privada con código de 4 letras, con revancha.

El modo online necesita el servidor de `server/`. El servidor sirve el propio juego y gestiona las partidas con WebSocket. Es autoritativo: simula la partida y a cada jugador solo le envía lo que puede ver, así que nadie puede saber dónde está el rival mirando el código.

El motor de reglas vive una sola vez, dentro de `index.html`, entre los comentarios `ENGINE-START` y `ENGINE-END`. El servidor lo lee de ahí al arrancar, así que el juego contra el bot y el online siempre usan las mismas reglas.

### Probarlo en tu ordenador

```bash
cd amago
npm install
npm start
```

Abre `http://localhost:8080` en dos pestañas (o en el móvil, con la IP de tu ordenador en la misma wifi). En las dos: **Modo → Online → Jugar**. Para salas privadas: **Con amigos → Crear sala** en una y el código en la otra.

### Publicarlo en Railway

La configuración ya está en `amago/railway.json` (arranque y comprobación de salud en `/health`) y `amago/package.json`.

1. Entra en [railway.com](https://railway.com) con tu cuenta de GitHub.
2. **New Project → Deploy from GitHub repo** y elige este repositorio.
3. En el servicio: **Settings → Source → Root Directory:** `amago`. Elige la rama que quieras desplegar.
4. **Settings → Networking → Generate Domain.** Railway te dará una dirección tipo `https://amago-production.up.railway.app`.
5. Ábrela en el móvil. Cada `git push` a esa rama vuelve a desplegar el juego solo.

`/health` muestra cuántos jugadores hay conectados, las salas abiertas y la gente en cola.

Railway no duerme el servidor, pero tiene un consumo mínimo mensual de pago tras la prueba gratuita. Las partidas online usan muy poca CPU.

### Mensajes del protocolo

Cliente → servidor: `hello`, `queue`, `create`, `join {code}`, `pick {hero}`, `move {x,y}`, `fire {x,y}`, `rematch`, `leave`.
Servidor → cliente: `queued`, `room {code}`, `matched {opp, ranked}`, `pickPhase`, `oppPicked`, `roundStart {you, opp, view}`, `go`, `view {v}` (10 veces por segundo), `ev` (disparos, impactos, objetos), `roundEnd`, `matchEnd`, `rematchAsk`, `oppLeft`, `error`.

## Reglas (versión 4: tiempo real con elixir)

- **1 contra 1, sin turnos.** Cada jugador tiene un solo héroe escondido en su tablero de 5×5.
- **3 rondas, 3 héroes:** antes de cada ronda eliges héroe y no puedes repetirlo. Gana quien se lleve 2 rondas.
- **Todo cuesta elixir** (máximo 10, se recarga 1 por segundo): moverse cuesta según el héroe y disparar según su ataque.
- Toca tu tablero para moverte (el héroe camina casilla a casilla) y el tablero rojo para disparar.
- **Disparar te delata:** el rival ve una huella 👣 durante 2 s (Sombra no deja huella; la de Truco sale en una casilla falsa).
- **Aviso o sin aviso:** los ataques con aviso marcan la zona en rojo en el tablero del rival y se pueden esquivar; Sombra y Rayo pegan casi al instante.
- **Objetos cebo:** salen en la misma casilla en los dos tableros, con su tiempo de vida visible. Si el rival lo coge, desaparece y sabes dónde está.
  - 💧 +4 elixir · ⚡ elixir al doble 6 s · 👁 ves al rival 2,5 s · 🛡️ para el próximo golpe
- **¡CERCA! 🔥** si fallas por una casilla.
- Ronda de 90 s. Desde el segundo 60, muerte súbita: os veis cada 5 s y el elixir va más rápido. Si se acaba el tiempo, gana quien tenga más vida.

## Héroes

| Héroe | Rareza | Vida | Velocidad | Ataque | Coste | Daño | Aviso |
|---|---|---|---|---|---|---|---|
| Flecha (Arquera) | Común | 3 | Rápida | Línea de 3 | 3 | 1 | Sí |
| Brasa (Dragón) | Común | 4 | Lenta | 2×2 | 5 | 2 | Sí |
| Sombra (Ninja) | Común | 2 | Muy rápida | 1 casilla, sin huella | 3 | 1 | No |
| Muro (Gólem) | Común | 6 | Lenta | Columna de 3 | 4 | 1 | Sí |
| Ojo (Búho) | Raro | 2 | Rápida | 1 casilla; oye los pasos del rival | 2 | 1 | Sí |
| Truco (Zorro) | Raro | 3 | Rápida | Línea de 3; huella falsa | 3 | 1 | Sí |
| Rayo (Mago) | Épico | 3 | Normal | Diagonal de 3 | 4 | 2 | No |
| Bum (Bomba) | Legendario | 3 | Normal | Cruz de 5 | 6 | 2 | Sí |

## Menús

- **Inicio** al estilo de los juegos de héroes para móvil: perfil con nivel, trofeos, héroe de portada en un pedestal, selector de modo (contra bot o con amigos) y botón JUGAR.
- **Héroes:** colección con tarjetas por rareza (común, raro, épico, legendario), victorias por héroe y ficha con sus estadísticas. Puedes elegir el héroe de portada.
- **Camino de trofeos:** premios cada pocos trofeos (cofres y héroes garantizados) que se reclaman con un botón.
- Los héroes tienen arte nuevo: manos, pies, sombreado y parpadeo.

## Lo que lo hace adictivo

- Inicio con tus héroes en escena, trofeos y arenas con barra de progreso.
- Búsqueda de rival con pantalla VS.
- Proyectiles, explosiones, partículas, temblor de pantalla, textos flotantes y sonido sintetizado (Web Audio), con vibración en Android.
- Rachas, cofres con apertura en tres toques y héroes desbloqueables por rareza.
- Consejos en contexto la primera vez que pasa cada cosa, en lugar de un tutorial largo.
- El jugador tiene ventaja sin que se note: primera partida contra un bot muy flojo, protección de trofeos para novatos, radar que se carga al perder héroes, aviso de ¡CERCA! y un bot que comete más errores cuando va ganando.

## Bot

Lleva en tiempo real un mapa de probabilidad de dónde está tu héroe (huellas, objetos que coges, aciertos, fallos, avisos de cerca y lo rápido que te mueves), dispara cuando cree que va a acertar, tiende emboscadas en los objetos, esquiva los ataques con aviso tras un tiempo de reacción y se aparta después de disparar. Cuando va ganando reacciona más lento y apunta peor.

El progreso (trofeos, cofres, héroes) se guarda en el navegador con `localStorage`.
