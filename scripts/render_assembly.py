"""Render a full-assembly view of the rocket from the four part STLs.

Places the nose cone on top, fin can in the body tube aft end, and four fins
radially inserted and slid forward to their locked position.
"""
import os, struct, math, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import rocket as R


def load_stl(path: str) -> np.ndarray:
    with open(path, "rb") as f:
        f.read(80)
        (n,) = struct.unpack("<I", f.read(4))
        data = np.frombuffer(f.read(n * 50), dtype=np.uint8)
    tris = np.zeros((n, 3, 3), dtype=np.float32)
    for i in range(n):
        off = i * 50 + 12
        tris[i] = np.frombuffer(data[off:off + 36].tobytes(), dtype=np.float32).reshape(3, 3)
    return tris


def transform(tris: np.ndarray, *, translate=(0, 0, 0), rotate_z_deg=0.0,
              rotate_x_deg=0.0) -> np.ndarray:
    out = tris.copy()
    if rotate_x_deg:
        a = math.radians(rotate_x_deg)
        c, s = math.cos(a), math.sin(a)
        Rx = np.array([[1, 0, 0], [0, c, -s], [0, s, c]], dtype=np.float32)
        out = out @ Rx.T
    if rotate_z_deg:
        a = math.radians(rotate_z_deg)
        c, s = math.cos(a), math.sin(a)
        Rz = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]], dtype=np.float32)
        out = out @ Rz.T
    out = out + np.array(translate, dtype=np.float32)
    return out


def build_assembly() -> list[tuple[np.ndarray, np.ndarray]]:
    """Return list of (triangles, rgb_color) for each placed sub-part."""
    stl = "/workspace/stl"
    bt_orange = np.array([0.95, 0.45, 0.20])
    nc_orange = np.array([0.98, 0.55, 0.22])
    fc_gray   = np.array([0.55, 0.55, 0.60])
    fin_white = np.array([0.92, 0.92, 0.92])

    parts = []
    # Body tube at origin.
    parts.append((load_stl(f"{stl}/body_tube.stl"), bt_orange))
    # Nose cone sits with its aft face (z=0 in its local frame) at top of body tube.
    nc = load_stl(f"{stl}/nose_cone.stl")
    nc = transform(nc, translate=(0, 0, R.BT_LEN))
    parts.append((nc, nc_orange))
    # Fin can sits inside body tube, aft end flush with body tube aft end.
    # In its local frame the fin can's aft face is at z=-RETAINER_LIP_THK.
    fc = load_stl(f"{stl}/fin_can.stl")
    fc = transform(fc, translate=(0, 0, R.RETAINER_LIP_THK))
    parts.append((fc, fc_gray))
    # Four fins: fin was printed flat (thickness in Z). Orient vertical,
    # slide forward to locked position (wings fully under narrow slot).
    # Locked root position on body tube: z in [keyhole_z1, keyhole_z1+FIN_ROOT]
    root_z0 = R.SLOT_AFT_OFFSET + R.SLOT_KEYHOLE_LEN
    for i in range(R.FIN_COUNT):
        fin = load_stl(f"{stl}/fin.stl")
        # In fin local frame:
        #   x = chord (0..FIN_ROOT at root)
        #   y = span (−tab_depth..+FIN_SPAN)
        #   z = thickness (−wing..FIN_THK+wing)
        # Target placement: fin lies radially outward from body tube, root on
        # the outer surface at body tube azimuth = i*90°.
        # Step 1: rotate about X by −90° so +Y in fin becomes +Z outward...
        # Actually we want fin chord along rocket Z axis and fin span along
        # rocket radial (+X before azimuth rotation). So:
        #   fin x (chord)    → rocket +Z  (axial)
        #   fin y (span/tab) → rocket +X  (radial out) for y>0, −X for tab y<0
        #   fin z (thick)    → rocket ±Y  (tangential)
        # Apply: swap axes via rotation. Rotate +90° about Y axis so fin x→z.
        #   After rotation: new_z = old_x, new_x = -old_z (approximately)
        # Simpler: construct explicit mapping matrix.
        t = fin
        # Remap: (x, y, z) -> (y, z, x) i.e. rocket(X,Y,Z) = fin(y, z, x).
        t = t[:, :, [1, 2, 0]]
        # Translate fin chord origin (now in Z) to root_z0, and span origin
        # so root (y=0) aligns with body tube outer surface (rocket X = BT_OD/2).
        t = t + np.array([R.BT_OD / 2.0, 0.0, root_z0], dtype=np.float32)
        # Rotate azimuthally.
        t = transform(t, rotate_z_deg=i * 90.0)
        parts.append((t, fin_white))
    return parts


def render(parts, out_path: str, title: str, elev=12, azim=-55, figsize=(7, 10)):
    fig = plt.figure(figsize=figsize, dpi=130)
    ax = fig.add_subplot(111, projection="3d")

    light = np.array([0.3, 0.4, 0.9], dtype=np.float32)
    light /= np.linalg.norm(light)

    all_pts = []
    for tris, base in parts:
        v0, v1, v2 = tris[:, 0], tris[:, 1], tris[:, 2]
        normals = np.cross(v1 - v0, v2 - v0)
        lengths = np.linalg.norm(normals, axis=1, keepdims=True)
        lengths[lengths == 0] = 1.0
        normals = normals / lengths
        shade = np.clip(0.4 + 0.7 * (normals @ light), 0.35, 1.0)
        fc = np.clip(base[None, :] * shade[:, None], 0, 1)
        fc = np.concatenate([fc, np.ones((len(tris), 1), dtype=np.float32)], axis=1)
        coll = Poly3DCollection(tris, facecolors=fc, edgecolors="none", linewidths=0)
        ax.add_collection3d(coll)
        all_pts.append(tris.reshape(-1, 3))

    pts = np.concatenate(all_pts, axis=0)
    mins, maxs = pts.min(axis=0), pts.max(axis=0)
    center = (mins + maxs) / 2
    size = (maxs - mins).max() / 2 * 1.05
    ax.set_xlim(center[0] - size, center[0] + size)
    ax.set_ylim(center[1] - size, center[1] + size)
    ax.set_zlim(center[2] - size, center[2] + size)
    try:
        ax.set_box_aspect((1, 1, 1))
    except Exception:
        pass

    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    ax.set_title(title, fontsize=14, pad=10, color="#e8e8e8")
    fig.patch.set_facecolor("#101418")
    ax.set_facecolor("#101418")
    plt.tight_layout()
    fig.savefig(out_path, facecolor=fig.get_facecolor(), dpi=130)
    plt.close(fig)
    print(f"  {out_path}")


def main():
    parts = build_assembly()
    os.makedirs("/workspace/images", exist_ok=True)
    render(parts, "/workspace/images/assembly.png",
           "Mini Nike Sport Rocket — assembled",
           elev=12, azim=-55)
    render(parts, "/workspace/images/assembly_side.png",
           "Assembled — side view",
           elev=0, azim=0, figsize=(5, 10))


if __name__ == "__main__":
    main()
