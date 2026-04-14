"""Render each STL as a PNG thumbnail for the README.

Uses matplotlib's 3D Poly3DCollection. No external viewer or GPU required.
Loads binary STL directly (no trimesh dep).
"""
import os, struct, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


def load_stl(path: str) -> np.ndarray:
    """Return (N, 3, 3) array of triangle vertices from a binary STL."""
    with open(path, "rb") as f:
        header = f.read(80)
        (n_tri,) = struct.unpack("<I", f.read(4))
        data = np.frombuffer(f.read(n_tri * 50), dtype=np.uint8)
    tris = np.zeros((n_tri, 3, 3), dtype=np.float32)
    for i in range(n_tri):
        off = i * 50 + 12  # skip normal
        verts = np.frombuffer(data[off:off + 36].tobytes(), dtype=np.float32).reshape(3, 3)
        tris[i] = verts
    return tris


def render(stl_path: str, out_path: str, title: str, elev=20, azim=-60):
    tris = load_stl(stl_path)
    fig = plt.figure(figsize=(6, 6), dpi=120)
    ax = fig.add_subplot(111, projection="3d")

    # Lighting: shade faces by normal·light direction
    v0, v1, v2 = tris[:, 0], tris[:, 1], tris[:, 2]
    normals = np.cross(v1 - v0, v2 - v0)
    lengths = np.linalg.norm(normals, axis=1, keepdims=True)
    lengths[lengths == 0] = 1.0
    normals = normals / lengths
    light = np.array([0.3, 0.4, 0.9])
    light /= np.linalg.norm(light)
    shade = np.clip(0.4 + 0.7 * (normals @ light), 0.35, 1.0)
    base_rgb = np.array([0.95, 0.45, 0.20])  # rocket orange
    face_colors = np.clip(base_rgb[None, :] * shade[:, None], 0, 1)
    face_colors = np.concatenate([face_colors, np.ones((len(tris), 1))], axis=1)

    coll = Poly3DCollection(tris, facecolors=face_colors, edgecolors="none", linewidths=0)
    ax.add_collection3d(coll)

    mins = tris.reshape(-1, 3).min(axis=0)
    maxs = tris.reshape(-1, 3).max(axis=0)
    center = (mins + maxs) / 2
    size = (maxs - mins).max() / 2 * 1.1
    ax.set_xlim(center[0] - size, center[0] + size)
    ax.set_ylim(center[1] - size, center[1] + size)
    ax.set_zlim(center[2] - size, center[2] + size)
    try:
        ax.set_box_aspect((1, 1, 1))
    except Exception:
        pass

    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    ax.set_title(title, fontsize=13, pad=10, color="#e8e8e8")
    fig.patch.set_facecolor("#101418")
    ax.set_facecolor("#101418")
    plt.tight_layout()
    fig.savefig(out_path, facecolor=fig.get_facecolor(), dpi=120)
    plt.close(fig)
    print(f"  {out_path}")


def main():
    stl_dir = "/workspace/stl"
    img_dir = "/workspace/images"
    os.makedirs(img_dir, exist_ok=True)
    renders = [
        ("nose_cone",  "Nose Cone (tangent ogive, hollow)",       20, -60),
        ("body_tube",  "Body Tube (fin slots + rail guides)",     15, -70),
        ("fin_can",    "Fin Can (motor mount + centering rings)", 20, -60),
        ("fin",        "Fin (trapezoidal, through-wall tab)",     25, -55),
    ]
    for name, title, elev, azim in renders:
        render(os.path.join(stl_dir, f"{name}.stl"),
               os.path.join(img_dir, f"{name}.png"),
               title, elev=elev, azim=azim)


if __name__ == "__main__":
    main()
