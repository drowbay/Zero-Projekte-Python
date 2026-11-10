import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

# ==========================================
# MS / MSM – Sinnformbild (Spin-Foam inspiriert)
# Statische Visualisierung
# ==========================================

# ----------------------------
# SETTINGS
# ----------------------------
SEED = 7
POINT_COUNT = 220
SHOW_LABELS = True
SHOW_GRID_POINTS = True

# Einfluss des Modells
ETA_DENSITY = 1.0     # Grundstruktur
PSI_STRENGTH = 1.0    # Richtungsdynamik
DELTA_STRENGTH = 1.0  # sichtbare Differenz

# ----------------------------
# HELPERS
# ----------------------------
rng = np.random.default_rng(SEED)

def draw_triangle(ax, center, size=0.45, angle=0.0,
                  facecolor="0.25", edgecolor="black",
                  alpha=1.0, linewidth=1.2):
    """
    Zeichnet ein kleines gerichtetes Dreieck (wedge marker).
    """
    cx, cy = center
    base = np.array([
        [0.0, 1.0],
        [-0.85, -0.75],
        [0.85, -0.75]
    ]) * size

    rot = np.array([
        [np.cos(angle), -np.sin(angle)],
        [np.sin(angle),  np.cos(angle)]
    ])

    pts = base @ rot.T
    pts[:, 0] += cx
    pts[:, 1] += cy

    tri = Polygon(
        pts,
        closed=True,
        facecolor=facecolor,
        edgecolor=edgecolor,
        alpha=alpha,
        linewidth=linewidth
    )
    ax.add_patch(tri)
    return pts

def draw_wire_triangle(ax, center, size=0.75, angle=0.0,
                       color="0.5", linewidth=1.0, alpha=0.65):
    """
    Zeichnet ein transparentes Hilfsdreieck hinter dem dunklen Keil.
    """
    cx, cy = center
    base = np.array([
        [0.0, 1.0],
        [-0.85, -0.75],
        [0.85, -0.75]
    ]) * size

    rot = np.array([
        [np.cos(angle), -np.sin(angle)],
        [np.sin(angle),  np.cos(angle)]
    ])

    pts = base @ rot.T
    pts[:, 0] += cx
    pts[:, 1] += cy

    pts_loop = np.vstack([pts, pts[0]])
    ax.plot(pts_loop[:, 0], pts_loop[:, 1], color=color, lw=linewidth, alpha=alpha)

def noisy_points_in_region(xmin, xmax, ymin, ymax, count):
    xs = rng.uniform(xmin, xmax, count)
    ys = rng.uniform(ymin, ymax, count)
    return xs, ys

# ----------------------------
# FIGURE
# ----------------------------
fig, ax = plt.subplots(figsize=(8, 10))
fig.patch.set_facecolor("white")
ax.set_facecolor("white")

# ----------------------------
# META-FLÄCHEN (face / wedge area)
# ----------------------------
# Große obere face
face_poly = np.array([
    [2.1, 8.6],
    [7.8, 9.5],
    [8.7, 5.3],
    [3.4, 4.5],
    [1.5, 6.1]
])

# Mittlerer wedge / Sinnkeil
wedge_poly = np.array([
    [1.4, 5.5],
    [6.9, 6.2],
    [7.9, 3.8],
    [4.5, 2.7],
    [2.0, 3.6]
])

face_patch = Polygon(face_poly, closed=True, facecolor="0.95", edgecolor="black", linewidth=1.8)
wedge_patch = Polygon(wedge_poly, closed=True, facecolor="0.88", edgecolor="black", linewidth=1.8)

ax.add_patch(face_patch)
ax.add_patch(wedge_patch)

# ----------------------------
# ETA = symmetrische Grundstruktur
# -> Hintergrundpunkte
# ----------------------------
if SHOW_GRID_POINTS:
    # obere Fläche
    xs1, ys1 = noisy_points_in_region(2.2, 8.4, 4.9, 9.1, int(POINT_COUNT * ETA_DENSITY))
    ax.scatter(xs1, ys1, s=10, facecolors="none", edgecolors="0.4", linewidths=0.8, alpha=0.75)

    # untere / rechte Fläche
    xs2, ys2 = noisy_points_in_region(3.2, 9.2, 0.8, 5.0, int(POINT_COUNT * 0.75 * ETA_DENSITY))
    ax.scatter(xs2, ys2, s=10, facecolors="none", edgecolors="0.4", linewidths=0.8, alpha=0.75)

# ----------------------------
# VERTEX / Bezugspunkt
# ----------------------------
vertex = np.array([1.4, 4.55])
ax.scatter([vertex[0]], [vertex[1]], s=32, color="black", zorder=5)

# zwei kleine Markierungen an der Kante
g1 = np.array([1.8, 5.25])
g2 = np.array([1.75, 3.75])

ax.plot([vertex[0], g1[0]], [vertex[1], g1[1]], color="black", lw=1.4)
ax.plot([vertex[0], g2[0]], [vertex[1], g2[1]], color="black", lw=1.4)

# kleine g-Marken
ax.text(1.15, 5.3, "g", fontsize=12)
ax.text(1.15, 3.55, "g", fontsize=12)

# ----------------------------
# PSI = gerichtete Dynamik
# -> drei Wedges / gerichtete Keile
# ----------------------------
# oberer Keil
c_top = (4.0, 6.6)
draw_wire_triangle(ax, c_top, size=0.75, angle=-0.35)
draw_triangle(ax, c_top, size=0.42 * PSI_STRENGTH + 0.05, angle=-0.35, facecolor="0.25")

# mittlerer Keil
c_mid = (3.4, 4.0)
draw_wire_triangle(ax, c_mid, size=0.80, angle=-0.55)
draw_triangle(ax, c_mid, size=0.46 * PSI_STRENGTH + 0.05, angle=-0.55, facecolor="0.25")

# unterer rechter Keil
c_low = (7.2, 1.15)
draw_wire_triangle(ax, c_low, size=0.85, angle=0.95)
draw_triangle(ax, c_low, size=0.50 * PSI_STRENGTH + 0.05, angle=0.95, facecolor="0.25")

# oberer rechter Keil
c_top_right = (7.2, 8.95)
draw_wire_triangle(ax, c_top_right, size=0.85, angle=0.85)
draw_triangle(ax, c_top_right, size=0.50 * PSI_STRENGTH + 0.05, angle=0.85, facecolor="0.25")

# ----------------------------
# LINKS / DELTA
# -> sichtbare Verbindungen / Differenzen
# ----------------------------
# Link vom vertex zum mittleren wedge
ax.plot([vertex[0], c_mid[0] - 0.4], [vertex[1], c_mid[1] + 0.2], color="0.2", lw=1.3 * DELTA_STRENGTH)

# zusätzliche feine Verbindungslinien
ax.plot([g1[0], c_top[0] - 0.1], [g1[1], c_top[1] - 0.2], color="0.45", lw=1.0, alpha=0.75)
ax.plot([g2[0], c_mid[0] - 0.1], [g2[1], c_mid[1] - 0.25], color="0.45", lw=1.0, alpha=0.75)

# ----------------------------
# TEXT / BESCHRIFTUNG
# ----------------------------
if SHOW_LABELS:
    ax.text(7.55, 7.35, "spin foam\nface", fontsize=16, ha="center")
    ax.text(4.75, 4.45, "wedge", fontsize=18, ha="center")
    ax.text(4.75, 3.5, "link", fontsize=16, ha="center", rotation=-14)
    ax.text(0.55, 4.45, "vertex", fontsize=16, ha="right")

    ax.text(4.15, 6.05, r"$z=(\pi,\omega)$", fontsize=16)
    ax.text(3.65, 3.25, r"$z=(\pi,\omega)$", fontsize=16)

    ax.text(7.95, 0.7, "edge", fontsize=16, ha="left")

    # MS-Modell-Hinweise
    ax.text(7.15, 9.8, r"$\eta$: symmetrische Grundstruktur", fontsize=11, ha="right")
    ax.text(7.15, 9.45, r"$\psi$: gerichtete Dynamik", fontsize=11, ha="right")
    ax.text(7.15, 9.1, r"$\Delta$: sichtbare Differenz", fontsize=11, ha="right")

# ----------------------------
# LAYOUT
# ----------------------------
ax.set_xlim(0, 10)
ax.set_ylim(0, 10.4)
ax.set_aspect("equal")
ax.axis("off")

plt.tight_layout()
plt.show()