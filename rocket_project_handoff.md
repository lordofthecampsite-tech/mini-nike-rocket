# Mini Nike Sport Rocket — Claude Code Handoff Document

## Context
This document was prepared during a design conversation on Claude.ai (mobile).
Paste this entire file into a Claude Code session in VS Code to continue the project.
The goal is to generate production-ready, 3D-printable STL files for a model rocket
with zero manual CAD work required.

---

## Your First Message to Claude Code

> "I have a rocket design project. Please read this entire handoff document carefully,
> then install the necessary dependencies and generate all STL files as specified.
> I want you to run everything autonomously — install packages, write the code, execute it,
> check the output, fix any issues, and deliver final STL files ready to slice in PrusaSlicer.
> Do not ask me questions unless something is truly ambiguous. Just execute."

---

## Project Summary

Design and generate a fully 3D-printable model rocket inspired by the **Nike Smoke**
silhouette. All components must be printable on a **Prusa Core One** and assemble
without glue — mechanical snap/twist/friction fits only.

---

## Printer Specifications

| Parameter | Value |
|---|---|
| Printer | Prusa Core One |
| Build Volume | 250 × 220 × 270 mm |
| Primary Material | PLA |
| Nozzle Diameter | 0.4mm (standard) |
| Recommended Wall Perimeters | 3 perimeters |
| Recommended Infill | 15–20% gyroid |
| Layer Height | 0.2mm standard |

### Print Orientation Notes
- **Body tube**: print vertically (Z axis) for best layer orientation along stress axis
- **Nose cone**: print tip-up
- **Fins**: print flat (face down on bed)
- **Fin can / motor mount assembly**: print vertically
- All parts must fit within 250 × 220 × 270 mm — body tube at 241mm fits within Z height

---

## Motor Specifications

| Parameter | Value |
|---|---|
| Motor | Estes C6-5 (largest motor this rocket will ever use) |
| Diameter | 18mm |
| Length | 70mm |
| Peak Thrust | 14.1 N |
| Avg Thrust | 4.7 N |
| Burn Time | 1.9 seconds |
| Max Rocket Weight | 4 oz (113g) including motor |

---

## Weight Budget

| Component | Weight |
|---|---|
| C6-5 Motor | 24g (0.85oz) |
| 12" parachute + shroud lines | ~6g |
| Shock cord (~18" elastic) | ~4g |
| Recovery wadding | ~2g |
| Recovery gear subtotal | ~12g |
| **Available for printed rocket** | **~77g max** |

The CadQuery script must calculate and print estimated PLA weight
(PLA density = 1.24 g/cm³) for all components combined so we know
before slicing whether we're within budget.

---

## Overall Rocket Dimensions

| Parameter | Value |
|---|---|
| Total height | ~381mm (15 inches) |
| Body tube OD | 27.94mm (1.1") |
| Body tube ID | 25.40mm (1.0") |
| Aesthetic inspiration | NASA Nike Smoke sounding rocket |

---

## Component Specifications

### 1. Nose Cone
- **Shape**: Tangent ogive
- **Length**: 76.2mm (3.0")
- **Base diameter**: 27.94mm OD (matches body tube)
- **Shoulder**: 15mm long, ~25.1mm OD (friction fit into body tube ID)
- **Wall thickness**: 2.0mm
- **Interior**: Hollow to save weight
- **Shock cord attachment**: Internal printed eyelet/lug boss at the base
  interior — a simple loop anchor the shock cord can be tied through.
  No glue. No swivel needed.
- **Fit**: Friction fit shoulder — tight enough to stay during flight,
  pops off cleanly on ejection charge

### 2. Body Tube
- **OD**: 27.94mm
- **ID**: 25.40mm
- **Wall thickness**: 2.27mm
- **Length**: 241.3mm (9.5")
- **Features**:
  - 4× fin slots cut through wall at aft end, equally spaced at 90°
  - Each slot sized to accept fin through-wall tabs
  - Aft end interfaces with fin can via twist-lock or snap ring
  - Forward end is open (nose cone friction fits in)
- **Print**: Vertically, 3 perimeters, 15% gyroid infill

### 3. Fin Can Assembly
This is a single printed sub-assembly that combines:
- Short aft body section
- Motor mount tube
- Two centering rings (printed integral)
- Fin capture slots/locks
- Motor retainer lip

**Motor mount tube**
- ID: 18.5mm (18mm motor slides in with ~0.25mm clearance)
- OD: ~21mm
- Length: 72mm (motor is 70mm, 2mm extra for retainer lip)
- Retainer: small printed lip at aft end catches motor thrust ring

**Centering rings** (printed integral with motor tube)
- OD: 25.1mm (fits inside body tube ID)
- ID: matches motor tube OD
- Thickness: 3mm each
- Position: one forward, one aft of motor tube

**Fin slots**
- 4× slots at 90° spacing
- Sized to capture fin through-wall tabs
- Tabs lock in with a slight interference or quarter-turn lock

**Interface to body tube**
- Fin can slides into aft end of body tube
- Retained by a printed snap ring or bayonet-style quarter-turn lock
- No glue

### 4. Fins (4× identical)
Inspired by the Nike Smoke — large, bold, nearly square trapezoidal shape.
Fins do NOT extend beyond the aft end of the rocket.

| Parameter | Value |
|---|---|
| Root chord | 63.5mm (2.5") |
| Tip chord | 31.75mm (1.25") |
| Span | 40.64mm (1.6") from body surface |
| Leading edge sweep | ~5mm forward sweep (very subtle, nearly square like real Nike) |
| Thickness | 3.81mm (0.15") |
| Through-wall tab depth | 2.54mm (0.1") below root |
| Tab width | matches slot in fin can |
| Quantity | 4, equally spaced at 90° |

### 5. Rail Guides
- Style: Conformal printed-on rail buttons (not separate parts)
- Rail size: 1010 standard launch rail
- Quantity: 2
- Position: One ~38mm from aft end, one ~152mm from aft end (mid-body)
- Design: Low-profile rectangular guide with 1010 slot profile,
  printed as part of body tube or bonded feature —
  sized so rocket slides freely on rail but without slop

---

## Assembly Sequence (No Glue)

1. Slide fins through fin can slots until tabs click/lock
2. Slide fin can into aft end of body tube, twist to lock
3. Feed shock cord through nose cone interior eyelet and tie off
4. Fold parachute, attach to shock cord
5. Pack parachute + wadding into body tube
6. Friction-fit nose cone into forward end of body tube
7. Insert motor into fin can motor tube until it seats against retainer lip
8. Place on 1010 rail via conformal rail guides

---

## Deliverables

Claude Code should produce the following STL files:

| File | Description |
|---|---|
| `nose_cone.stl` | Hollow ogive nose cone with shoulder and internal shock cord lug |
| `body_tube.stl` | Main airframe tube with fin slots and rail guide features |
| `fin_can.stl` | Integrated aft assembly: motor mount + centering rings + fin slots |
| `fin.stl` | Single fin (print 4 copies) |

Optionally, if weight budget is tight:
| `motor_retainer.stl` | Separate snap-on motor retainer clip if integrated lip is insufficient |

All files should be exported in **millimeters**.

---

## Code Requirements

- Use **CadQuery** (install via pip if not present: `pip install cadquery`)
- If CadQuery unavailable, fall back to **build123d** (`pip install build123d`)
- Script should be fully parametric — all key dimensions defined as
  variables at the top of the file so they're easy to tweak
- Script must print to console:
  - Volume of each component in cm³
  - Estimated PLA weight of each component in grams (density = 1.24 g/cm³)
  - Total estimated rocket weight in grams
  - Pass/fail against 77g weight budget
- Export each component as a separate STL file
- STL files should be watertight / manifold (suitable for slicing)

---

## Key Constraints Summary

1. **No glue** — all joints are mechanical (friction, snap, twist-lock)
2. **18mm motor** — ID must accept Estes 18mm motors including C6-5
3. **Motor length** — 70mm, retainer lip at aft end
4. **Weight limit** — printed rocket under 77g total
5. **Bed size** — all parts fit within 250 × 220 × 270mm
6. **Fin profile** — Nike Smoke style, fins stay within body length, minimal sweep
7. **Nose cone** — hollow, internal shock cord anchor, friction fit shoulder
8. **Rail guides** — conformal 1010 rail buttons, printed on body tube
9. **PLA on Prusa Core One** — standard 0.4mm nozzle, 3 perimeters, 15-20% gyroid

---

## Aesthetic Notes

- Overall silhouette: stubby and aggressive, like the NASA Nike Smoke sounding rocket
- Fins: large, bold, nearly square trapezoidal — the defining visual feature
- Nose cone: relatively short ogive, not needle-thin
- This is a sport flyer, not a scale model — proportions can be optimized
  for printability and strength over strict scale accuracy

---

*Document prepared April 2026. Continue this project in Claude Code / VS Code.*
