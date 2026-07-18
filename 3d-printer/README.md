# CoreXY 3D Printer — Built From Scratch on a €120 Budget

> Designing a complete 3D printer from a blank sheet of paper: new CoreXY kinematics, a moving heated bed on twin Z lead-screws, a recycled Creality mainboard reflashed to fit, and a chassis that went from all-plastic to a full aluminium-extrusion frame after the first version flexed too much.

![Hand-drawn design](./1000012100.JPEG)
*The starting point: the whole machine sketched by hand on graph paper — frame, CoreXY gantry, belt path and Z bed.*

---

## The idea

I wanted to build a 3D printer **from scratch** — not assemble a kit — to really understand motion systems, firmware and machine design. The rules I set myself:

- **Hard budget: under €120.** Recycle and reuse as much as possible.
- **Reuse the electronics** from my old Creality printer (its **Creality 4.2.7 silent mainboard**) instead of buying a new controller.
- **Different kinematics from what I knew.** My old Creality was a "bed-slinger" (the bed moves on Y). I wanted a **CoreXY** system, where the toolhead moves in X and Y via two belts and two fixed motors, and the **heated bed moves up and down on Z**.

## From sketch to CAD

Every part was modelled in **Fusion 360** before printing. I designed the frame, the CoreXY gantry, the motor mounts and the Z bed carriage from scratch.

<table>
<tr>
<td align="center"><img src="./1000012371.JPEG" width="250"><br><sub>NEMA stepper mount — CAD next to the real motor to check the fit</sub></td>
<td align="center"><img src="./1000012381.JPEG" width="380"><br><sub>Z bed carriage on twin lead-screws, driven by two steppers — modelled in Fusion 360</sub></td>
</tr>
</table>

## The printed chassis (v1 — all plastic)

The first full chassis was **entirely 3D-printed** in yellow PLA — frame legs, base shell and brackets. It worked, but under load the printed frame flexed more than I wanted.

<table>
<tr>
<td align="center"><img src="./1000012870.JPEG" width="230"><br><sub>A printed structural column with its threaded rod</sub></td>
<td align="center"><img src="./1000013172.JPEG" width="230"><br><sub>Printed base panels + black reinforcement brackets</sub></td>
<td align="center"><img src="./1000013188.JPEG" width="230"><br><sub>Printed base/enclosure shell with vents</sub></td>
</tr>
</table>

![Printed chassis v1](./1000013997.JPEG)
*Version 1 assembled: fully 3D-printed base and uprights, with a NEMA stepper and Z lead-screw fitted.*

### The key iteration

Version 1 taught me the most important lesson: **a fully printed frame isn't stiff enough.** So I rebuilt the whole machine around a **full aluminium-extrusion frame with 3D-printed reinforcements** — the project I call **KMI 2.0**.

---

## KMI 2.0 — the aluminium reconstruction

This is the version I'm proudest of. I kept everything that worked from v1 (the CoreXY concept, the recycled electronics, the Z-bed idea) and rebuilt the entire structure in **2020 aluminium extrusion**, using 3D-printed parts only where they add value: corner gussets, motor mounts, the toolhead and belt tensioners. Aluminium carries the loads; plastic does the clever geometry.

### Print the new machine on the old one

Before swapping anything, I printed all the new structural brackets on my **old Ender-3 Pro** — the same printer whose mainboard would later become the brain of the new one. The donor building its own successor.

<table>
<tr>
<td align="center"><img src="./1000012382.JPEG" width="240"><br><sub>The new twin-Z bed carriage, redesigned in Fusion 360</sub></td>
<td align="center"><img src="./1000012964.JPEG" width="430"><br><sub>Printing the new structural brackets on my old Ender-3 Pro before the rebuild</sub></td>
</tr>
</table>

### The new frame

<table>
<tr>
<td align="center"><img src="./IMG_9549.jpg" width="300"><br><sub>The v2 frame: 2020 aluminium extrusion with custom 3D-printed corner gussets and twin-Z lead-screws. Rigid where v1 flexed.</sub></td>
<td align="center"><img src="./IMG_9569.jpg" width="300"><br><sub>Old and new side by side: the donor Ender-3 next to the aluminium machine it's becoming</sub></td>
</tr>
</table>

### Assembly

<table>
<tr>
<td align="center"><img src="./DSC04213.JPG" width="300"><br><sub>Mid-assembly: MGN linear rails, printed + metal corner brackets, twin lead-screws and the Kingroon bed dropping in</sub></td>
<td align="center"><img src="./DSC04245.JPG" width="430"><br><sub>Toolhead, part-cooling fan and bed, coming together on the aluminium frame</sub></td>
</tr>
</table>

### Electronics — same brain, new body

- **Controller:** recycled **Creality 4.2.7** board from the Ender-3.
- **Firmware:** reflashed and reconfigured for **CoreXY kinematics** — new axis directions, steps/mm, endstop positions and a moving-Z heated bed. Nothing like the stock Creality config.
- **Power:** a dedicated mains PSU feeding the bed and electronics.

<table>
<tr>
<td align="center"><img src="./DSC04220.JPG" width="300"><br><sub>Recycled Creality 4.2.7 board, mains PSU and the Ender LCD wired into the new machine</sub></td>
<td align="center"><img src="./DSC04240.JPG" width="300"><br><sub>PSU and the two Z steppers driving the bed on twin lead-screws</sub></td>
</tr>
</table>

### The finished machine

![KMI 2.0 finished](./DSC04210.JPG)
*KMI 2.0 assembled and running: the CoreXY gantry on a rigid aluminium frame, LED-lit, with the recycled electronics underneath.*

<table>
<tr>
<td align="center"><img src="./DSC04230.JPG" width="300"><br><sub>Detail: toolhead, Kingroon bed and the twin-Z lead-screws with anti-backlash nuts</sub></td>
<td align="center"><img src="./DSC04250.JPG" width="300"><br><sub>Mechanical Z endstop and the part-cooling fan up close</sub></td>
</tr>
</table>

### Gallery

<table>
<tr>
<td align="center"><img src="./DSC04222.JPG" width="300"></td>
<td align="center"><img src="./DSC04211.JPG" width="300"></td>
</tr>
<tr>
<td align="center"><img src="./DSC04238.JPG" width="300"></td>
<td align="center"><img src="./DSC04244.JPG" width="300"></td>
</tr>
</table>

![Detail](./DSC04248.JPG)

---

## Specs at a glance

| Item | Detail |
|---|---|
| Motion system | CoreXY (X/Y), heated bed on twin-Z lead-screws |
| Controller | Creality 4.2.7 (recycled from an Ender-3) + custom firmware config |
| Frame | v1: fully 3D-printed → **KMI 2.0: 2020 aluminium extrusion + printed reinforcements** |
| Motion hardware | MGN linear rails, steel rods + bearings, GT2 belts & pulleys |
| Bed | Kingroon 180 × 180 mm heated bed |
| Endstops | Mechanical limit switches |
| Power | Dedicated mains PSU |
| CAD | Fusion 360 |
| Budget | **< €120** |

## What I learned

- How **CoreXY kinematics** actually work, and how to configure firmware for a motion system from zero (axis mapping, steps/mm, homing, endstops).
- **Structural stiffness matters more than part count** — the jump from a printed frame to aluminium was the difference between "moves" and "prints well."
- How to plan a **rebuild without waste**: reuse the electronics, print the new parts on the old machine, and only buy what the budget truly needs.
- Safe integration of **mains power** into a machine.

## Media

All photos in this folder are at full resolution — feel free to edit them.
