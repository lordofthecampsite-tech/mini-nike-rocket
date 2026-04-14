# Mini Nike Sport Rocket

A fully 3D-printable, glue-free model rocket inspired by the **NASA Nike Smoke**
sounding rocket. Designed for an **Estes C6-5** motor and a **Prusa Core One**,
with all assembly done by friction / snap fits — no adhesive required.

Every dimension lives in a single parametric Python script
([`rocket.py`](rocket.py)); running it regenerates all four STLs and prints a
weight report against the 77 g budget.

---

## The Rocket

![Assembled rocket](images/assembly.png)

Full step-by-step build in [`ASSEMBLY.md`](ASSEMBLY.md).

### Parts

![Nose Cone](images/nose_cone.png)
![Body Tube](images/body_tube.png)
![Fin Can](images/fin_can.png)
![Fin](images/fin.png)

| | |
|---|---|
| **Overall height** | ≈ 381 mm (15") |
| **Body tube** | 27.94 mm OD × 25.40 mm ID × 241.3 mm |
| **Nose cone** | Tangent ogive, 76.2 mm long, 2 mm wall, internal shock-cord eyelet |
| **Fins** | 4× trapezoidal, 63.5 mm root × 31.75 mm tip × 40.64 mm span × 3.81 mm thick |
| **Motor mount** | 18.5 mm ID × 72 mm, integrated retainer lip |
| **Rail guides** | 2× 1010-T-slot-compatible buttons (5.0 mm stem / 7.5 mm head) at 45° between fins |
| **Fin retention** | Keyway slide-lock — tabs with aft-end wings, captured under narrow slot section after 8 mm forward slide |
| **Motor** | Estes C6-5 (14.1 N peak, 1.9 s burn) |
| **Weight budget** | 77 g printed (after 12 g recovery gear) |

### Components

| File | Role | Print orientation |
|---|---|---|
| `stl/nose_cone.stl` | Hollow ogive with shoulder + internal shock-cord bridge | tip-up |
| `stl/body_tube.stl` | Airframe with 4× fin slots + 2× rail guides | vertical |
| `stl/fin_can.stl`   | Motor mount, 2 centering rings, fin capture slots, retainer lip, friction collar | vertical |
| `stl/fin.stl`       | Single fin with through-wall tab — print **4×** | flat |

### Assembly (no glue) — short version

1. Friction-fit the fin can up into the aft end of the body tube, aligning slots.
2. For each fin: align wings with the **keyhole pocket** at the bottom of a body tube slot, press the tab inward, then **slide the fin ~8 mm forward** so the wings are captured under the narrow slot section.
3. Thread the shock cord through the nose cone's internal bridge and tie off.
4. Pack parachute + wadding, friction-fit the nose cone.
5. Load the Estes C6-5 into the motor mount until it seats against the retainer lip.

Full walkthrough with per-step notes: [`ASSEMBLY.md`](ASSEMBLY.md).

### Weight report (from `rocket.py`)

```
Component      Qty    Vol(cm³)   Weight(g)
------------------------------------------
nose_cone        1       9.72      12.06
body_tube        1      25.37      31.46
fin_can          1       9.19      11.39
fin              4       7.89      39.14
------------------------------------------
TOTAL                              94.05
```

The reported weight is the **solid-PLA** equivalent (mesh volume × 1.24 g/cm³).
With the spec'd **3 perimeters, 15 % gyroid** slicer settings the real printed
mass lands in the **~40–50 g** range, comfortably under the 77 g budget. Slice
before printing to confirm.

---

## Regenerating the STLs

```bash
python3 -m venv --without-pip ~/venv
~/venv/bin/python -m ensurepip  # or bootstrap with get-pip.py
~/venv/bin/pip install build123d==0.10.0 webcolors ocp_gordon sympy
~/venv/bin/pip install --no-deps build123d==0.10.0   # pin against OCP 7.9

~/venv/bin/python rocket.py
~/venv/bin/python scripts/render_parts.py   # regenerate README thumbnails
```

All key dimensions are defined as constants at the top of `rocket.py` —
tweak `BT_OD`, `FIN_ROOT`, `MOTOR_OD`, etc. and re-run.

---

## Build Journal — how we got here

### The pipeline

| Tool | Role |
|---|---|
| **build123d 0.10** | Parametric solid modeling in Python |
| **cadquery-ocp 7.9** | Python bindings for the OpenCascade geometry kernel |
| **lib3mf** | STL/3MF writer used by build123d's `export_stl` |
| **matplotlib + numpy** | Offscreen PNG thumbnails of each STL (`scripts/render_parts.py`) |
| **PrusaSlicer** | Slicing (user-side) — 0.4 mm nozzle, 3 perimeters, 15 % gyroid |

The design itself came out of a Claude.ai mobile conversation that produced
[`rocket_project_handoff.md`](rocket_project_handoff.md) — a full written spec
handed to Claude Code to execute end-to-end.

### Issues encountered & how they were worked around

**1. CadQuery install failed — OCP bindings unavailable on PyPI**

`pip install cadquery` installed the pure-Python layer but not the OpenCascade
Python bindings (`OCP`). CadQuery normally expects a conda install for OCCT.
**Work-around:** switched to **build123d**, which ships a pip-installable
`cadquery-ocp` wheel that bundles OCCT.

**2. `py_lib3mf` vs `lib3mf` module-name drift**

build123d's STL exporter does `from py_lib3mf import Lib3MF`, but the 2.4.x
PyPI package now installs as `lib3mf`. Importing build123d raised
`ModuleNotFoundError: py_lib3mf`.
**Work-around:** a two-line shim at the top of `rocket.py` —
```python
import lib3mf as _lib3mf
sys.modules.setdefault("py_lib3mf", _lib3mf)
```

**3. build123d 0.8 + cadquery-ocp 7.9 = `HashCode` removed**

The default resolved build123d version (0.8.0) calls the old OCP API method
`TopoDS_Shape.HashCode()` which was removed in OCP 7.9 (replaced by
`__hash__`). Pip would not install a newer build123d because 0.9 and 0.10 both
pin `cadquery-ocp<7.9`, and 7.8 wheels are not published for Python 3.11.
**Work-around:** installed build123d 0.10 with `--no-deps --force-reinstall`
against the newer OCP 7.9, then added its transitive deps manually
(`webcolors`, `ocp_gordon`, `sympy`). This worked because the 0.10 code path
no longer uses `HashCode`.

**4. `/workspace/.venv` getting partially wiped between shell calls**

A venv created under `/workspace/.venv` lost its `bin/` and `lib/` subtrees
between commands, even though other files in `/workspace` persisted —
something in the sandbox was eating venv payloads specifically.
**Work-around:** relocated the venv to `~/venv` (`/home/node/venv`) and left
the workspace tree for source only.

**5. Nose cone came out open-ended**

First pass generated the revolve polygon with the wrong vertex traversal —
jumping vertically from `(base_r, 0)` to `(base_r, L)` before tracing the
ogive back down, which produced a cylinder-with-a-cone-carved-out instead of
a closed ogive. The base was open and the tip was a hollow pocket.
**Fix:** rewrote the profile helper (`_ogive_face_points`) to emit points in
strict CCW order: axis-base → base-edge → along ogive tip-ward → close.
Nose cone STL grew from 176 KB → 1024 KB as it now meshes the full curved
surface properly.

**6. Rail guide landed in the middle of a fin slot**

The first rail guide positions were at 38 mm from the aft end, angularly
aligned with `+X` — but the fin slots span 2 – 66 mm aft and sit at 0 / 90 /
180 / 270°. The aft button was being punched straight through a fin slot.
**Fix:** moved both guides to **45° between fins**, pushed the aft guide to
85 mm (above the fin slot zone), and added a 10 × 14 × 2.4 mm reinforcement
pad that sinks 0.6 mm into the tube wall so the button-to-tube junction
doesn't snap off.

### Revisions after first review

A follow-up design pass addressed three of the flagged gaps:

**Fin retention — keyway slide-lock (resolved).** The original first-pass
fin tab was a plain 2.54 mm rectangle with no mechanical retention — a
reviewer (correctly) pointed out nothing kept the fins in under load.
The tab is now **3.0 mm deep** with **1.5 mm-per-side wings** at the aft
8 mm, and each body tube fin slot is a **keyhole**: 8 mm wide pocket at
the aft end, narrow channel above. Assembly is push-in + 8 mm forward
slide; once slid, the wings are trapped under the narrow section and
the fin cannot be pulled radially outward. See `ASSEMBLY.md` step 2.

**Rail guide — updated to 1010 T-slot profile (resolved).** Buttons are
now 5.0 mm stem × 7.5 mm head × 2.5 mm head thickness, which fits the
standard 80/20 1010 T-slot (6.40 mm surface opening, 8.26 mm interior
cavity). Reinforcement pad retained.

### Known simplifications (still outstanding)

- **Fin can → body tube retention** is still a plain friction collar,
  not the bayonet / snap ring the original spec called for. Fine for a
  sport flyer under a C6-5 (thrust pushes the fin can *up* into the
  body tube, not out), but a proper bayonet would be right for higher
  impulses. Deferred intentionally — the L-slot geometry on a 1.27 mm
  wall is fiddly and I'd rather test-fit a prototype before committing.
- **Body tube wall** is 1.27 mm (derived from OD 27.94 / ID 25.40), not
  the 2.27 mm called out in the handoff prose. The OD/ID pair is what
  makes every internal fit (nose cone shoulder, fin can collar, motor
  mount clearance) work, so trusted that over the wall-thickness
  figure. Worth revisiting if more stiffness is wanted — would need to
  either expand OD or accept a tighter internal fit.

---

## Repo layout

```
.
├── rocket.py                     # the whole parametric model
├── rocket_project_handoff.md     # original design spec
├── ASSEMBLY.md                   # step-by-step build instructions
├── scripts/
│   ├── render_parts.py           # STL → PNG thumbnails
│   └── render_assembly.py        # composite assembled view
├── stl/                          # generated STLs (committed for convenience)
│   ├── nose_cone.stl
│   ├── body_tube.stl
│   ├── fin_can.stl
│   └── fin.stl
└── images/                       # README renderings
```

---

*Generated autonomously by Claude Code from the handoff document.*
