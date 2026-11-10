import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

# =========================================================
# Raster-Modell: Quelle -> mehrere Quadrat-Raster -> Würfel -> Kugel
# ---------------------------------------------------------
# Mathematisch saubere 3D-Geometrie:
# - Punktquelle links
# - 5 Raster-Ebenen mit abnehmender Größe
# - jede Ebene hat ein 5x5 Raster
# - Strahlen verbinden Quelle -> Rasterpunkte -> Würfel -> Kugel
# =========================================================

# -----------------------------
# Einstellungen
# -----------------------------
GRID_N = 5              # 5x5 Raster pro Ebene
NUM_PLANES = 5          # Anzahl Quadrat-Ebenen
SOURCE = np.array([0.0, 0.0, 0.0])

PLANE_X_START = 2.0
PLANE_SPACING = 1.0
PLANE_SIZE_START = 5.0
PLANE_SIZE_DECAY = 0.72

CUBE_CENTER = np.array([8.2, 0.0, 0.0])
CUBE_SIZE = 2.8

SPHERE_CENTER = np.array([12.0, 0.0, 0.0])
SPHERE_RADIUS = 1.7


# -----------------------------
# Hilfsfunktionen
# -----------------------------
def draw_line(ax, p1, p2, color="black", lw=1.0, alpha=1.0, ls="-"):
    ax.plot(
        [p1[0], p2[0]],
        [p1[1], p2[1]],
        [p1[2], p2[2]],
        color=color,
        linewidth=lw,
        alpha=alpha,
        linestyle=ls,
    )


def normalize(v):
    n = np.linalg.norm(v)
    if n < 1e-12:
        return v
    return v / n


def make_grid_plane(x, size, n):
    """Quadrat-Raster in der yz-Ebene bei Position x."""
    ys = np.linspace(-size / 2, size / 2, n)
    zs = np.linspace(-size / 2, size / 2, n)
    points = []
    for y in ys:
        for z in zs:
            points.append(np.array([x, y, z], dtype=float))
    return points, ys, zs


def draw_grid_plane(ax, x, size, n, color="gray", alpha=0.45):
    points, ys, zs = make_grid_plane(x, size, n)

    # horizontale Rasterlinien
    for y in ys:
        p1 = np.array([x, y, -size / 2])
        p2 = np.array([x, y,  size / 2])
        draw_line(ax, p1, p2, color=color, lw=0.7, alpha=alpha)

    # vertikale Rasterlinien
    for z in zs:
        p1 = np.array([x, -size / 2, z])
        p2 = np.array([x,  size / 2, z])
        draw_line(ax, p1, p2, color=color, lw=0.7, alpha=alpha)

    # Rand stärker
    corners = [
        np.array([x, -size/2, -size/2]),
        np.array([x,  size/2, -size/2]),
        np.array([x,  size/2,  size/2]),
        np.array([x, -size/2,  size/2]),
    ]
    for i in range(4):
        draw_line(ax, corners[i], corners[(i + 1) % 4], color="black", lw=1.2, alpha=0.8)

    return points


def cube_vertices(center, size):
    s = size / 2
    offsets = np.array([
        [-s, -s, -s], [-s, -s,  s],
        [-s,  s, -s], [-s,  s,  s],
        [ s, -s, -s], [ s, -s,  s],
        [ s,  s, -s], [ s,  s,  s],
    ])
    return center + offsets


def draw_cube(ax, center, size):
    verts = cube_vertices(center, size)
    edges = [
        (0,1), (0,2), (0,4),
        (1,3), (1,5),
        (2,3), (2,6),
        (3,7),
        (4,5), (4,6),
        (5,7),
        (6,7),
    ]
    for i, j in edges:
        draw_line(ax, verts[i], verts[j], color="royalblue", lw=1.5, alpha=0.95)
    return verts


def draw_sphere(ax, center, radius):
    u = np.linspace(0, 2 * np.pi, 60)
    v = np.linspace(0, np.pi, 35)
    x = center[0] + radius * np.outer(np.cos(u), np.sin(v))
    y = center[1] + radius * np.outer(np.sin(u), np.sin(v))
    z = center[2] + radius * np.outer(np.ones_like(u), np.cos(v))
    ax.plot_wireframe(x, y, z, color="darkorange", linewidth=0.6, alpha=0.7)


def sphere_hit_from_point(point):
    """Punkt auf Kugeloberfläche in Richtung eines gegebenen Punkts."""
    direction = normalize(point - SPHERE_CENTER)
    return SPHERE_CENTER + direction * SPHERE_RADIUS


# -----------------------------
# Szene zeichnen
# -----------------------------
fig = plt.figure(figsize=(11, 8))
ax = fig.add_subplot(111, projection="3d")

fig.patch.set_facecolor("white")
ax.set_facecolor("white")

# Quelle
ax.scatter(SOURCE[0], SOURCE[1], SOURCE[2], color="crimson", s=75, label="Quelle")

# Raster-Ebenen
all_planes = []
for i in range(NUM_PLANES):
    x = PLANE_X_START + i * PLANE_SPACING
    size = PLANE_SIZE_START * (PLANE_SIZE_DECAY ** i)
    pts = draw_grid_plane(ax, x, size, GRID_N, color="gray", alpha=0.38)
    all_planes.append(pts)

# Strahlen von Quelle zur ersten Rasterebene
first_plane = all_planes[0]
for p in first_plane:
    draw_line(ax, SOURCE, p, color="black", lw=0.55, alpha=0.45)

# Verbindung gleiche Raster-Indizes zwischen Ebenen
for a in range(NUM_PLANES - 1):
    for p1, p2 in zip(all_planes[a], all_planes[a + 1]):
        draw_line(ax, p1, p2, color="black", lw=0.45, alpha=0.35)

# Würfel
cube_verts = draw_cube(ax, CUBE_CENTER, CUBE_SIZE)

# letzte Rasterebene -> vordere Würfelfläche
last_plane = all_planes[-1]
front_ids = np.argsort(cube_verts[:, 0])[:4]
front_face = cube_verts[front_ids]

# Zielpunkte auf der Würfelfront als 5x5 Raster innerhalb der Frontfläche
cube_front_x = np.min(cube_verts[:, 0])
cube_grid, _, _ = make_grid_plane(cube_front_x, CUBE_SIZE, GRID_N)
cube_grid = [p + np.array([0, CUBE_CENTER[1], CUBE_CENTER[2]]) for p in cube_grid]

for p1, p2 in zip(last_plane, cube_grid):
    draw_line(ax, p1, p2, color="seagreen", lw=0.65, alpha=0.65)

# Kugel
draw_sphere(ax, SPHERE_CENTER, SPHERE_RADIUS)
ax.scatter(SPHERE_CENTER[0], SPHERE_CENTER[1], SPHERE_CENTER[2],
           color="darkorange", s=45, label="Kugelzentrum")

# Würfelrückseite -> Kugel
back_x = np.max(cube_verts[:, 0])
back_grid, _, _ = make_grid_plane(back_x, CUBE_SIZE, GRID_N)
back_grid = [p + np.array([0, CUBE_CENTER[1], CUBE_CENTER[2]]) for p in back_grid]

for p in back_grid:
    hit = sphere_hit_from_point(p)
    draw_line(ax, p, hit, color="darkorange", lw=0.65, alpha=0.55)

# Mittelachse
draw_line(ax, SOURCE, SPHERE_CENTER, color="red", lw=1.2, alpha=0.35, ls="--")

# Achsen / View
ax.set_title("Raster-Modell: Quelle -> Quadrat-Raster -> Würfel -> Kugel", pad=16)
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")

ax.set_xlim(-0.5, 14.5)
ax.set_ylim(-4.5, 4.5)
ax.set_zlim(-4.5, 4.5)
ax.set_box_aspect((1.7, 1, 1))
ax.view_init(elev=18, azim=-63)

fig.text(
    0.02, 0.02,
    f"Raster: {GRID_N}x{GRID_N} pro Ebene | Ebenen: {NUM_PLANES} | "
    "Quelle -> abnehmende Raster -> Volumen -> Kugelhülle",
    fontsize=10,
)

ax.legend()
plt.tight_layout()
plt.show()
