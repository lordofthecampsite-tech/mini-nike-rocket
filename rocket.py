"""Mini Nike Sport Rocket — parametric generator.

Generates STL files for a 3D-printable model rocket (Estes C6-5, ~381mm tall).
All dimensions in millimeters. Run with the project's venv python.
"""
from __future__ import annotations

import sys, os, math

# build123d ships expecting `py_lib3mf`; the wheel now installs as `lib3mf`.
import lib3mf as _lib3mf
sys.modules.setdefault("py_lib3mf", _lib3mf)

from build123d import (
    BuildPart, BuildSketch, BuildLine, Part, Sketch,
    Cylinder, Box, Circle, Rectangle, Polygon, Polyline, Line,
    Axis, Plane, Location, Pos, Rot,
    Mode, Align, GeomType,
    extrude, revolve, loft, fillet, chamfer, make_face, mirror,
    export_stl,
)

# ---------------------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------------------
# Body tube
BT_OD = 27.94
BT_ID = 25.40
BT_WALL = (BT_OD - BT_ID) / 2  # 1.27 — matches spec (wall ~2.27? spec says 2.27 but OD-ID/2 = 1.27)
# NOTE: spec lists wall=2.27 but OD 27.94 / ID 25.40 implies 1.27mm wall. Trusting OD/ID.
BT_LEN = 241.3

# Nose cone
NC_LEN = 76.2
NC_BASE_OD = BT_OD
NC_WALL = 2.0
NC_SHOULDER_LEN = 15.0
NC_SHOULDER_OD = 25.10  # slides into BT_ID=25.40 with 0.30mm clearance (friction fit)
NC_EYELET_OD = 6.0
NC_EYELET_ID = 2.5
NC_EYELET_THK = 3.0

# Motor / fin can
MOTOR_OD = 18.0
MM_ID = 18.5            # motor mount inner
MM_OD = 21.0
MM_LEN = 72.0
RETAINER_LIP_ID = 16.5  # lip catches motor thrust ring (motor OD=18 so 16.5 grabs 0.75mm on each side)
RETAINER_LIP_THK = 2.0

CR_OD = 25.10           # centering ring OD = fits inside BT_ID
CR_THK = 3.0

FC_SHOULDER_LEN = 25.0  # upper section that slides into body tube
FC_SHOULDER_OD = 25.10  # friction fit into body tube
FC_EXT_OD = BT_OD       # external flush section aft of body tube
FC_EXT_LEN = 8.0        # short aft collar flush with body tube

# Fins
FIN_ROOT = 63.5
FIN_TIP = 31.75
FIN_SPAN = 40.64
FIN_SWEEP = -5.0        # tip LE 5mm forward of root LE
FIN_THK = 3.81
FIN_TAB_DEPTH = 3.0                 # radial depth of main tab
FIN_TAB_LEN = FIN_ROOT              # tab spans full root chord
FIN_TAB_WING_LEN = 8.0              # axial length of wings at aft end of tab
FIN_TAB_WING_EXTRA = 1.5            # per-side extra circumferential width
FIN_TAB_WING_TOP = 1.5              # wings start 1.5mm below root (= ~0.3mm below BT inner wall)
FIN_COUNT = 4

# Fin slot (body tube): aft keyhole to accept wings + narrow channel.
# After inserting, slide fin 8mm forward to move wings under the narrow
# section, capturing them radially.
SLOT_SLIDE = FIN_TAB_WING_LEN                   # 8mm forward slide to lock
SLOT_NARROW_W = FIN_THK + 0.3                   # 4.11mm
SLOT_KEYHOLE_W = FIN_THK + 2 * FIN_TAB_WING_EXTRA + 0.4  # 7.21mm
SLOT_KEYHOLE_LEN = FIN_TAB_WING_LEN             # 8mm at aft
SLOT_NARROW_LEN = FIN_TAB_LEN                   # 63.5mm
SLOT_TOTAL_LEN = SLOT_KEYHOLE_LEN + SLOT_NARROW_LEN  # 71.5mm
SLOT_AFT_OFFSET = 2.0                           # slot starts 2mm above aft edge

# Rail guides — 1010-T-slot-compatible dimensions.
# 1010 T-slot: 6.40mm surface opening, 8.26mm interior cavity, ~6.48mm deep.
RAIL_BTN_STEM_D = 5.0
RAIL_BTN_STEM_H = 2.0
RAIL_BTN_HEAD_D = 7.5
RAIL_BTN_HEAD_H = 2.5
RAIL_BTN_PAD_W = 10.0   # reinforcement pad around stem at tube wall
RAIL_BTN_PAD_L = 14.0
RAIL_BTN_PAD_H = 1.8
# Position along body tube (measured from aft end). Aft button is moved
# forward of the fin slot region (slots end near z ≈ 2 + FIN_ROOT = 65.8mm).
RAIL_POS_AFT = 85.0
RAIL_POS_FWD = 175.0
# Angular offset 45° — sits between fins, never on a fin slot.
RAIL_ANGLE_DEG = 45.0

# Material
PLA_DENSITY = 1.24      # g/cm³

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def ogive_profile(length: float, base_radius: float, n: int = 48) -> list[tuple[float, float]]:
    """Tangent ogive profile points from tip (0,0) to base (length, base_radius).
    Returns list of (x, y) with x along axis, y = radius."""
    L, R = length, base_radius
    rho = (R * R + L * L) / (2.0 * R)  # ogive radius
    pts = []
    for i in range(n + 1):
        x = L * i / n
        # distance from tip along axis; in standard tangent-ogive formula:
        # y(x) = sqrt(rho^2 - (L - x)^2) + R - rho
        y = math.sqrt(rho * rho - (L - x) * (L - x)) + R - rho
        y = max(y, 0.0)
        pts.append((x, y))
    return pts


def _volume_cm3(part: Part) -> float:
    return part.volume / 1000.0


def _weight_g(part: Part) -> float:
    return _volume_cm3(part) * PLA_DENSITY


# ---------------------------------------------------------------------------
# Nose cone
# ---------------------------------------------------------------------------
def _ogive_face_points(length: float, base_radius: float, n: int = 64) -> list[tuple[float, float]]:
    """Closed 2D profile (r, z) for a solid ogive sitting with base at z=0,
    tip at z=length. Walk: axis-base -> base-edge -> along ogive to tip -> close."""
    prof = ogive_profile(length, base_radius, n)  # (axial_from_tip, radius), tip->base
    pts: list[tuple[float, float]] = [(0.0, 0.0), (base_radius, 0.0)]
    # Walk from base corner up the ogive to the tip.
    # reversed(prof) goes base (axial=L, r=base_r) -> tip (axial=0, r=0).
    # world z = length - axial_from_tip.
    for (axial, r) in reversed(prof):
        z = length - axial
        pts.append((r, z))
    pts.append((0.0, 0.0))  # close back along axis
    return pts


def build_nose_cone() -> Part:
    """Hollow tangent ogive with shoulder and internal shock-cord eyelet.
    Tip at z=+NC_LEN, base at z=0, shoulder hangs below from z=-NC_SHOULDER_LEN to z=0."""
    with BuildPart() as nc:
        # Outer ogive solid (revolve closed profile about Z).
        with BuildSketch(Plane.XZ):
            with BuildLine():
                Polyline(*_ogive_face_points(NC_LEN, NC_BASE_OD / 2.0))
            make_face()
        revolve(axis=Axis.Z)

        # Shoulder collar (solid cylinder below base).
        with BuildSketch(Plane.XY.offset(-NC_SHOULDER_LEN)):
            Circle(NC_SHOULDER_OD / 2.0)
        extrude(amount=NC_SHOULDER_LEN)

        # Hollow interior of the cone (leave NC_WALL thickness).
        # Use a slightly-shorter ogive offset inward by NC_WALL.
        inner_len = NC_LEN - NC_WALL
        inner_r = NC_BASE_OD / 2.0 - NC_WALL
        with BuildSketch(Plane.XZ):
            with BuildLine():
                Polyline(*_ogive_face_points(inner_len, inner_r))
            make_face()
        revolve(axis=Axis.Z, mode=Mode.SUBTRACT)

        # Hollow the shoulder (open at the aft face so the shock cord can pass through).
        with BuildSketch(Plane.XY.offset(-NC_SHOULDER_LEN)):
            Circle(NC_SHOULDER_OD / 2.0 - NC_WALL)
        extrude(amount=NC_SHOULDER_LEN, mode=Mode.SUBTRACT)

        # Internal shock-cord eyelet: a bridge across the interior at z≈3mm
        # with a through-hole for the cord.
        bridge_z = 3.0
        bridge_w = BT_ID - 2.0
        bridge_d = 5.0
        with BuildSketch(Plane.XY.offset(bridge_z)):
            Rectangle(bridge_w, bridge_d)
        extrude(amount=NC_EYELET_THK)
        with BuildSketch(Plane.XY.offset(bridge_z + NC_EYELET_THK / 2.0)):
            Circle(NC_EYELET_ID / 2.0)
        extrude(amount=NC_EYELET_THK * 2, both=True, mode=Mode.SUBTRACT)

    return nc.part


# ---------------------------------------------------------------------------
# Body tube
# ---------------------------------------------------------------------------
def build_body_tube() -> Part:
    with BuildPart() as bt:
        # Outer cylinder
        with BuildSketch(Plane.XY):
            Circle(BT_OD / 2.0)
        extrude(amount=BT_LEN)
        # Bore
        with BuildSketch(Plane.XY):
            Circle(BT_ID / 2.0)
        extrude(amount=BT_LEN, mode=Mode.SUBTRACT)

        # Fin slots through aft wall — 4 slots at 90°
        # Slot is a rectangle through the wall: width = FIN_THK + 0.3mm clearance,
        # length = FIN_ROOT + 0.3mm, positioned near aft end with a small offset.
        slot_w = FIN_THK + 0.3
        slot_l = FIN_ROOT + 0.3
        slot_aft_offset = 2.0  # mm above aft end
        for i in range(FIN_COUNT):
            angle = i * 360.0 / FIN_COUNT
            # Build a box aligned radially, then rotate; easier: rotate sketch plane
            loc = Location((0, 0, slot_aft_offset + slot_l / 2.0)) * Rot(Z=angle)
            with BuildPart(mode=Mode.SUBTRACT) as _s:
                with BuildSketch(Plane.YZ):
                    Rectangle(slot_w, slot_l)
                extrude(amount=BT_OD)  # punch through both walls? extends in +X
                # Actually we only want to cut one wall — move origin so the box
                # starts at x=BT_ID/2-0.5 and extends outward.
            # The above isn't location-aware inside the existing context.
        # Simpler: subtract slots with explicit loft / box at known position
    # Fin slots: keyhole at aft + narrow channel that captures the wings.
    bt_part = bt.part
    radial_cut_depth = 4.0  # punch well through the 1.27mm wall
    keyhole_z0 = SLOT_AFT_OFFSET
    keyhole_z1 = SLOT_AFT_OFFSET + SLOT_KEYHOLE_LEN
    narrow_z0 = keyhole_z1
    narrow_z1 = narrow_z0 + SLOT_NARROW_LEN

    for i in range(FIN_COUNT):
        angle = i * 360.0 / FIN_COUNT
        # Keyhole section (wider): z=[keyhole_z0, keyhole_z1]
        with BuildPart() as key:
            Box(radial_cut_depth, SLOT_KEYHOLE_W, SLOT_KEYHOLE_LEN)
        key_placed = Pos(BT_OD / 2.0, 0, (keyhole_z0 + keyhole_z1) / 2.0) * key.part
        key_placed = key_placed.rotate(Axis.Z, angle)
        bt_part = bt_part - key_placed

        # Narrow channel: z=[narrow_z0, narrow_z1]
        with BuildPart() as narrow:
            Box(radial_cut_depth, SLOT_NARROW_W, SLOT_NARROW_LEN)
        narrow_placed = Pos(BT_OD / 2.0, 0, (narrow_z0 + narrow_z1) / 2.0) * narrow.part
        narrow_placed = narrow_placed.rotate(Axis.Z, angle)
        bt_part = bt_part - narrow_placed

    # Rail guides: reinforced mushroom button on a reinforcement pad,
    # placed at 45° between fins so they never land on a fin slot.
    for z_pos in (RAIL_POS_AFT, RAIL_POS_FWD):
        with BuildPart() as guide:
            # Reinforcement pad — an oval-ish slab bonded to the tube surface.
            # Built with its inner face straddling the tube wall so it fuses cleanly.
            with BuildSketch(Plane.YZ):
                Rectangle(RAIL_BTN_PAD_W, RAIL_BTN_PAD_L)
            extrude(amount=RAIL_BTN_PAD_H + 0.6)  # +X; 0.6mm sinks into wall
            # Stem
            with BuildSketch(Plane.YZ.offset(RAIL_BTN_PAD_H + 0.6)):
                Circle(RAIL_BTN_STEM_D / 2.0)
            extrude(amount=RAIL_BTN_STEM_H)
            # Head
            with BuildSketch(Plane.YZ.offset(RAIL_BTN_PAD_H + 0.6 + RAIL_BTN_STEM_H)):
                Circle(RAIL_BTN_HEAD_D / 2.0)
            extrude(amount=RAIL_BTN_HEAD_H)
        # Offset along tube surface; sink pad 0.6mm into wall for a solid weld.
        placed = Pos(BT_OD / 2.0 - 0.6, 0, z_pos) * guide.part
        placed = placed.rotate(Axis.Z, RAIL_ANGLE_DEG)
        bt_part = bt_part + placed

    return bt_part


# ---------------------------------------------------------------------------
# Fin can
# ---------------------------------------------------------------------------
def build_fin_can() -> Part:
    """Integrated fin can: motor mount + 2 centering rings + shoulder that
    slides into body tube + fin capture slots + retainer lip at aft."""
    with BuildPart() as fc:
        # Motor mount tube
        with BuildSketch(Plane.XY):
            Circle(MM_OD / 2.0)
        extrude(amount=MM_LEN)
        with BuildSketch(Plane.XY):
            Circle(MM_ID / 2.0)
        extrude(amount=MM_LEN, mode=Mode.SUBTRACT)

        # Aft centering ring
        with BuildSketch(Plane.XY):
            Circle(CR_OD / 2.0)
            Circle(MM_OD / 2.0, mode=Mode.SUBTRACT)
        extrude(amount=CR_THK)

        # Forward centering ring
        with BuildSketch(Plane.XY.offset(MM_LEN - CR_THK)):
            Circle(CR_OD / 2.0)
            Circle(MM_OD / 2.0, mode=Mode.SUBTRACT)
        extrude(amount=CR_THK)

        # Retainer lip at aft end of motor mount: annular disk with ID smaller
        # than motor OD so it catches the motor's thrust ring. We add it at z=0
        # extending downward. Easier: a thin disk inside the motor tube.
        with BuildSketch(Plane.XY):
            Circle(MM_OD / 2.0)
            Circle(RETAINER_LIP_ID / 2.0, mode=Mode.SUBTRACT)
        extrude(amount=-RETAINER_LIP_THK)  # extends below z=0

        # Shoulder collar: thin-walled tube that slides into body tube ID.
        # Sits above the forward centering ring; OD = CR_OD (=25.1), wall ~1.5.
        shoulder_base_z = MM_LEN
        with BuildSketch(Plane.XY.offset(shoulder_base_z)):
            Circle(FC_SHOULDER_OD / 2.0)
            Circle(FC_SHOULDER_OD / 2.0 - 1.5, mode=Mode.SUBTRACT)
        extrude(amount=FC_SHOULDER_LEN)

        # External flush collar at aft: short section OD=BT_OD flush with body tube
        # sits at z in [-RETAINER_LIP_THK - FC_EXT_LEN, -RETAINER_LIP_THK]? Simpler:
        # make an external ring around the aft centering ring region so the outside
        # is flush with the body tube between the fin slots area.
        # Place it spanning z in [CR_THK, CR_THK + FC_EXT_LEN]
        with BuildSketch(Plane.XY.offset(CR_THK)):
            Circle(BT_OD / 2.0)
            Circle(CR_OD / 2.0, mode=Mode.SUBTRACT)
        extrude(amount=FC_EXT_LEN)

    fc_part = fc.part

    # Fin slots: match body-tube slot axial extent so the tab (with wings)
    # can pass through the centering rings and sit in the fin can.
    # Cut from just outside the motor mount tube to beyond the body tube OD,
    # so the centering rings get keyed for the fin but the motor mount is
    # not breached.
    slot_inner_r = MM_OD / 2.0 + 0.3
    slot_outer_r = BT_OD / 2.0 + 1.0
    slot_radial = slot_outer_r - slot_inner_r
    slot_cx = (slot_inner_r + slot_outer_r) / 2.0
    slot_w = SLOT_KEYHOLE_W  # wide enough for wings
    slot_l = SLOT_TOTAL_LEN + 0.4
    slot_center_z = SLOT_AFT_OFFSET + SLOT_TOTAL_LEN / 2.0

    for i in range(FIN_COUNT):
        with BuildPart() as slot:
            Box(slot_radial, slot_w, slot_l)
        moved = Pos(slot_cx, 0, slot_center_z) * slot.part
        moved = moved.rotate(Axis.Z, i * 360.0 / FIN_COUNT)
        fc_part = fc_part - moved

    return fc_part


# ---------------------------------------------------------------------------
# Fin
# ---------------------------------------------------------------------------
def build_fin() -> Part:
    """Single fin, flat-printable. Trapezoidal with slight forward LE sweep,
    plus a through-wall tab. The tab has 'wings' at its aft end (aft = x=0)
    that extend in the thickness direction; these mate with a keyhole in the
    body tube slot and capture the fin radially after an 8mm slide-forward."""
    with BuildPart() as fin:
        # Main fin body (flat on print bed, extruded in Z = thickness).
        with BuildSketch(Plane.XY):
            Polygon(
                (0.0, 0.0),
                (FIN_ROOT, 0.0),
                (FIN_SWEEP + FIN_TIP, FIN_SPAN),
                (FIN_SWEEP, FIN_SPAN),
                align=(Align.MIN, Align.MIN),
            )
        extrude(amount=FIN_THK)

        # Main tab: full-root-chord rectangle below y=0.
        with BuildSketch(Plane.XY):
            with BuildLine():
                Polyline(
                    (0.0, 0.0),
                    (0.0, -FIN_TAB_DEPTH),
                    (FIN_TAB_LEN, -FIN_TAB_DEPTH),
                    (FIN_TAB_LEN, 0.0),
                    (0.0, 0.0),
                )
            make_face()
        extrude(amount=FIN_THK)

        # Wings: two ears that extend ±Z beyond the fin thickness,
        # sitting at the aft 8mm of the tab and below FIN_TAB_WING_TOP.
        # After the fin is slid forward 8mm, these sit below the narrow
        # portion of the body-tube slot and trap the fin radially.
        wing_y0 = -FIN_TAB_DEPTH
        wing_y1 = -FIN_TAB_WING_TOP
        wing_x0 = 0.0
        wing_x1 = FIN_TAB_WING_LEN

        # Top-side wing (+Z of fin face).
        with BuildSketch(Plane.XY.offset(FIN_THK)):
            with BuildLine():
                Polyline(
                    (wing_x0, wing_y0),
                    (wing_x0, wing_y1),
                    (wing_x1, wing_y1),
                    (wing_x1, wing_y0),
                    (wing_x0, wing_y0),
                )
            make_face()
        extrude(amount=FIN_TAB_WING_EXTRA)

        # Bottom-side wing (−Z of fin face).
        with BuildSketch(Plane.XY):
            with BuildLine():
                Polyline(
                    (wing_x0, wing_y0),
                    (wing_x0, wing_y1),
                    (wing_x1, wing_y1),
                    (wing_x1, wing_y0),
                    (wing_x0, wing_y0),
                )
            make_face()
        extrude(amount=-FIN_TAB_WING_EXTRA)

    return fin.part


# ---------------------------------------------------------------------------
# Build & export
# ---------------------------------------------------------------------------
def main():
    outdir = os.path.dirname(os.path.abspath(__file__))
    stl_dir = os.path.join(outdir, "stl")
    os.makedirs(stl_dir, exist_ok=True)

    components = []

    print("Building nose cone...")
    nc = build_nose_cone()
    components.append(("nose_cone", nc, 1))

    print("Building body tube...")
    bt = build_body_tube()
    components.append(("body_tube", bt, 1))

    print("Building fin can...")
    fc = build_fin_can()
    components.append(("fin_can", fc, 1))

    print("Building fin...")
    fn = build_fin()
    components.append(("fin", fn, FIN_COUNT))

    print()
    print(f"{'Component':<14}{'Qty':>4}{'Vol(cm³)':>12}{'Weight(g)':>12}")
    print("-" * 42)
    total_weight = 0.0
    for name, part, qty in components:
        v = _volume_cm3(part)
        w = _weight_g(part) * qty
        total_weight += w
        print(f"{name:<14}{qty:>4}{v:>12.2f}{w:>12.2f}")
    print("-" * 42)
    print(f"{'TOTAL':<18}{'':>2}{'':>12}{total_weight:>12.2f}")
    budget = 77.0
    status = "PASS" if total_weight <= budget else "FAIL"
    print(f"Weight budget: {budget}g — {status} (margin {budget - total_weight:+.1f}g)")

    print()
    print("Exporting STLs...")
    for name, part, _qty in components:
        path = os.path.join(stl_dir, f"{name}.stl")
        export_stl(part, path, tolerance=0.05, angular_tolerance=0.2)
        print(f"  {path}  ({os.path.getsize(path) // 1024} KB)")

    print("\nDone.")


if __name__ == "__main__":
    main()
