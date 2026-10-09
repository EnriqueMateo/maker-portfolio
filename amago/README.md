# AMAGO: prototipo jugable

Hundir la flota con héroes que se mueven. Encuéntralos antes de que te encuentren.

Todo el juego está en un solo archivo HTML sin dependencias (solo carga dos fuentes de Google Fonts). Abre `index.html` en el navegador del móvil o del ordenador.

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
