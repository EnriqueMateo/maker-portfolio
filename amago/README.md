# AMAGO: prototipo jugable

Hundir la flota con personajes que se mueven. Los dos jugadores deciden a la vez y cada ataque deja una huella que delata al atacante.

Este es el primer prototipo: tú contra un bot, todo en un solo archivo HTML sin dependencias. Abre `index.html` en el navegador del ordenador o del móvil.

## Reglas implementadas

- Tableros ocultos de 5×5, 3 personajes por bando y 2 rocas por tablero.
- Antes de cada ronda eliges 3 personajes de 4 ofrecidos al azar.
- Cada turno, cada personaje se mueve una casilla o usa su habilidad. Primero se resuelven los movimientos y después los ataques.
- Atacar deja una huella visible para el rival durante 2 turnos (la Asesina y el Caballero no la dejan).
- Si aciertas ves "¡Tocado!" con el personaje alcanzado.
- Pista inicial: una columna donde hay un personaje rival.
- En el turno 6 el borde del tablero se convierte en lava (1 de daño por turno).
- El último superviviente se mueve hasta 2 casillas.
- Ronda de 10 turnos como máximo. Si nadie gana, gana quien hizo más daño. Partida al mejor de 3.
- Repetición al final de cada ronda con los dos tableros al descubierto.

| Personaje | Vida | Recarga | Habilidad |
|---|---|---|---|
| Arquera | 2 | 1 | Línea de 3 casillas, 1 de daño |
| Monstruo | 3 | 3 | Bola de fuego 2×2, cae el turno siguiente con aviso |
| Asesina | 1 | 2 | 1 casilla, 2 de daño, sin huella |
| Exploradora | 2 | 1 | Revela una zona 2×2 |
| Caballero | 3 | 2 | Escudo para él y los aliados de al lado, sin huella |
| Ilusionista | 2 | 2 | Huella falsa y flecha falsa |

## Pendiente

Agua y niebla en los mapas, modo online con salas privadas, gráficos y sonido.
