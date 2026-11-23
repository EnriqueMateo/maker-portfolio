# Compras dentro de la app: lo que hay que crear en App Store Connect

La app ya tiene el componente de compras (StoreKit 2, `StorePlugin.swift`) y el servidor verifica cada compra con la firma de Apple.
**Las compras se activan solas** en cuanto Apple devuelve estos productos: mientras no existan, la tienda sigue sin compras con dinero.

## 1. Antes de nada (solo tú)
1. App Store Connect → **Acuerdos, impuestos y banca** → firmar el **Acuerdo de apps de pago** y rellenar datos bancarios y fiscales.
2. App → **Información general** → «URL de notificaciones del servidor de App Store» (producción **y** sandbox), versión 2:
   `https://maker-portfolio-production-7712.up.railway.app/api/asn`

## 2. Productos (App → Monetización → Compras dentro de la app → «+»)
Todos son **Consumibles**. El ID tiene que ser exactamente este. Precio: el de la tabla en España (Apple calcula el resto de países).

| ID del producto | Nombre de referencia | Precio | Nombre visible (es / en) | Descripción (es / en) |
|---|---|---|---|---|
| `amago.gems_80` | Gemas 80 | 0,99 € | 80 gemas / 80 gems | Un puñado de gemas. / A handful of gems. |
| `amago.gems_450` | Gemas 450 | 4,99 € | 450 gemas / 450 gems | Justo para el Pase Premium. / Just right for the Premium Pass. |
| `amago.gems_1000` | Gemas 1000 | 9,99 € | 1.000 gemas / 1,000 gems | Bolsa de gemas. / Bag of gems. |
| `amago.gems_2200` | Gemas 2200 | 19,99 € | 2.200 gemas / 2,200 gems | Cofre de gemas. / Chest of gems. |
| `amago.gems_6000` | Gemas 6000 | 49,99 € | 6.000 gemas / 6,000 gems | Montaña de gemas. / Mountain of gems. |
| `amago.pass_premium` | Pase Premium | 4,99 € | Pase Premium / Premium Pass | Premios dorados en cada escalón de esta temporada. / Golden rewards on every tier this season. |
| `amago.pass_plus` | Pase Plus | 9,99 € | Pase Plus / Plus Pass | Pase Premium + 10 escalones y un marco. / Premium Pass + 10 tiers and a frame. |
| `amago.pass_plus_upgrade` | Mejora a Plus | 4,99 € | Mejora a Pase Plus / Plus Pass upgrade | Para quien ya tiene el Premium. / For Premium Pass owners. |
| `amago.starter` | Pack de Inicio | 1,99 € | Pack de Inicio / Starter Pack | 200 gemas, monedas, Poder y un aspecto. Una vez por cuenta. / 200 gems, coins, Power and a skin. Once per account. |
| `amago.bundle_power` | Lote de Poder | 4,99 € | Lote de Poder / Power Bundle | Monedas, Poder y 100 gemas. Uno por semana. / Coins, Power and 100 gems. One per week. |

Cada producto pide una **captura de revisión** (la tienda del juego vale: `store/capturas`) y una nota para el revisor, por ejemplo:
> Consumable. Granted after server-side verification of the StoreKit 2 signed transaction. Test with the review account in the review notes.

## 3. Probar sin cobrar
- **TestFlight:** las compras usan el entorno de pruebas de Apple (no se cobra). El servidor acepta transacciones de prueba («Sandbox»).
- Comprueba: comprar 80 gemas, cerrar la app a mitad de compra y volver (se entrega al abrir), y pedir un reembolso de prueba (las gemas desaparecen).

## 4. Qué se ha cuidado
- Nada aleatorio por dinero; precio de Apple en la moneda del jugador; menores de 13 sin compras; 13-17 con tope de 30 €/mes.
- Una compra nunca se entrega dos veces ni en dos cuentas; si se corta la conexión, se entrega al volver; los reembolsos quitan lo entregado.
