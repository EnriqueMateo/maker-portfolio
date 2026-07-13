# PET Filament Recycler — Turning Bottles Into 3D-Printing Filament

> A machine that closes the loop on 3D printing: cut plastic bottles into strips, pull them through a **modified hotend**, and pull out usable filament to print with.

<!-- ![Filament recycler](./images/01-overview.jpg) -->
<!-- Photos to be added -->

---

## The idea

3D-printing filament is bought new and thrown away as failed prints and supports. **PET bottles** are everywhere and are the same family of plastic used in some filaments. I wanted to build a machine that **recycles PET bottles directly into printable filament.**

## How it works

1. **Cut** — A plastic bottle is sliced into one long, continuous **strip** of even width.
2. **Pull** — The strip is fed through the machine and pulled from the other side by a **motor** (driven by a **drill** as the power source).
3. **Melt & reshape** — In the middle sits a **modified 3D-printer hotend**, opened up / reworked to size the plastic to roughly **~5 mm** as the strip passes through the heated zone.
4. **Filament out** — What comes out the other side is a continuous filament I can then load and **print PET parts** with.

So the flow is:

```
PET bottle  →  cut into strip  →  [ modified hotend, heated ]  →  pulled by drill/motor  →  usable filament  →  3D printer
```

## What I designed and built

- A **cutting method** to turn a bottle into a uniform continuous strip.
- A **modified hotend**: reworked a standard 3D-printer hotend so a bottle strip (not 1.75 mm filament) can pass through and be reshaped by heat to ~5 mm.
- A **pulling drivetrain** using a drill/motor to draw the strip through the hot zone at a controlled, steady rate.

## What I learned

- **Thermal control matters.** Pull too fast and it doesn't melt/reshape; too slow and it degrades. Getting a steady feed rate is the whole game.
- **Reusing tools creatively** — a drill makes a perfectly good, torquey motor when you don't want to buy one.
- **Sustainability by design** — recycling a waste material back into a useful engineering input.

## Media

Photos and short muted clips will live in [`images/`](./images) and [`videos/`](./videos).

> **Note:** I couldn't locate the filament-recycler photos/videos yet — see the message in chat. Drop them in and I'll slot them straight into this section.
