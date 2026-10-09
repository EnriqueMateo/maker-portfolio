# AMAGO: prototipo jugable

Hundir la flota con héroes que se mueven. Encuéntralos antes de que te encuentren.

Todo el juego está en un solo archivo HTML sin dependencias (solo carga dos fuentes de Google Fonts). Abre `index.html` en el navegador del móvil o del ordenador.

## Reglas (versión 3, simplificada)

- Cada jugador tiene 3 héroes escondidos en un tablero de 5×5.
- **Una jugada por turno:** eliges un héroe y atacas en el tablero rival o lo mueves una casilla. Los dos jugáis a la vez.
- Primero se resuelven los movimientos y después los ataques.
- **Atacar te delata:** el rival ve una huella 👣 donde estás (salvo los héroes sigilosos).
- Si fallas pero había un rival al lado, sale **¡CERCA! 🔥**.
- **Radar 📡:** se carga solo (y más rápido si pierdes un héroe). Revela a un rival.
- La mayoría de héroes cae de un golpe. Ronda de 12 turnos como máximo; en los 3 últimos el radar se carga para los dos. Partida al mejor de 3.

## Héroes

| Héroe | Rareza | Ataque |
|---|---|---|
| Flecha (Arquera) | Común | Línea de 3 en fila |
| Brasa (Dragón) | Común | Fuego 2×2 que cae al turno siguiente (recarga 1) |
| Sombra (Ninja) | Común | 1 casilla, sin huella |
| Muro (Gólem) | Común | Columna de 3. Aguanta 2 golpes |
| Ojo (Búho) | Raro | Revela una zona 2×2, sin huella |
| Truco (Zorro) | Raro | Ataque falso y huella falsa |
| Rayo (Mago) | Épico | Diagonal de 3 |
| Bum (Bomba) | Legendario | Cruz de 5 (recarga 1) |

## Lo que lo hace adictivo

- Inicio con tus héroes en escena, trofeos y arenas con barra de progreso.
- Búsqueda de rival con pantalla VS.
- Proyectiles, explosiones, partículas, temblor de pantalla, textos flotantes y sonido sintetizado (Web Audio), con vibración en Android.
- Rachas, cofres con apertura en tres toques y héroes desbloqueables por rareza.
- Consejos en contexto la primera vez que pasa cada cosa, en lugar de un tutorial largo.
- El jugador tiene ventaja sin que se note: primera partida contra un bot muy flojo, protección de trofeos para novatos, radar que se carga al perder héroes, aviso de ¡CERCA! y un bot que comete más errores cuando va ganando.

## Bot

Lleva un mapa de probabilidad de dónde están tus héroes (huellas, aciertos, fallos, avisos de cerca y movimientos posibles), ataca donde más probable es acertar y huye cuando se delata. En 400 rondas simuladas gana el 94 % contra un bot aleatorio. Para repetirlo, en la consola: `__amagoSim(400, "hard", "easy")`.

El progreso (trofeos, cofres, héroes) se guarda en el navegador con `localStorage`.
