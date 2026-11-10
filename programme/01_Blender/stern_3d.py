import math
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

# =========================================================
# 3D Stern aus deiner Skizze
# - ein Mittelpunkt
# - ein Quadrat in der Front-Ebene
# - Sternstrahlen vom Mittelpunkt nach außen
# - ein Punkt dahinter im Raum
# - Verbindungen für die 3D-Wirkung
# =========================================================

# -----------------------------
# Einstellungen
# -----------------------------
NUM_ARMS = 12          # Anzahl Sternstrahlen
INNER_RADIUS = 3.5     # Radius des inneren Quadrats / Sternbereichs
OUTER_RADIUS = 8.0     # Länge der äußeren Sternstrahlen
BACK_POINT_Z = -7.0    # Punkt "dahinter" (negatives Z = nach hinten)
BACK_POINT = np.array([0.0, 0.0, BACK_POINT_Z])
SHOW_SIDE_CONNECTIONS = True
SHOW_OUTER_RING = False


# -----------------------------
# Hilfsfunktionen
# -----------------------------
def make_star_points(num_arms=12, radius=8.0, z=0.0):
    """Erzeugt Punkte im Kreis / Stern außen auf der Front-Ebene."""
    pts = []
    for i in range(num_arms):
        angle = 2 * math.pi * i / num_arms
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        pts.append(np.array([x, y, z], dtype=float))
    return pts


def draw_line(ax, p1, p2, color="black", lw=1.5, alpha=1.0, ls="-"):
    ax.plot(
        [p1[0], p2[0]],
        [p1[1], p2[1]],
        [p1[2], p2[2]],
        color=color,
        linewidth=lw,
        alpha=alpha,
        linestyle=ls,
    )


# -----------------------------
# Geometrie aufbauen
# -----------------------------
center = np.array([0.0, 0.0, 0.0])
outer_points = make_star_points(NUM_ARMS, OUTER_RADIUS, z=0.0)

# inneres Quadrat (wie in deiner Skizze)
s = INNER_RADIUS
square_points = [
    np.array([-s, -s, 0.0]),
    np.array([ s, -s, 0.0]),
    np.array([ s,  s, 0.0]),
    np.array([-s,  s, 0.0]),
]

# -----------------------------
# Plot
# -----------------------------
fig = plt.figure(figsize=(9, 9))
ax = fig.add_subplot(111, projection="3d")

# Hintergrund / Stil
fig.patch.set_facecolor("white")
ax.set_facecolor("white")

# Mittelpunkt
ax.scatter(center[0], center[1], center[2], color="red", s=60, label="Mittelpunkt")

# Punkt dahinter
ax.scatter(
    BACK_POINT[0], BACK_POINT[1], BACK_POINT[2],
    color="blue", s=70, label="Punkt dahinter"
)

# Quadrat zeichnen
for i in range(4):
    p1 = square_points[i]
    p2 = square_points[(i + 1) % 4]
    draw_line(ax, p1, p2, color="gray", lw=2.0)

# Quadrat mit Mittelpunkt verbinden
for p in square_points:
    draw_line(ax, center, p, color="gray", lw=1.2, alpha=0.8)
    draw_line(ax, p, BACK_POINT, color="lightgray", lw=1.0, alpha=0.8, ls="--")

# Sternpunkte und Linien
for i, p in enumerate(outer_points):
    # äußerer Punkt
    ax.scatter(p[0], p[1], p[2], color="black", s=18)

    # Linie vom Mittelpunkt nach außen
    draw_line(ax, center, p, color="black", lw=1.5)

    # Verbindung zum hinteren Punkt => 3D-Effekt
    draw_line(ax, p, BACK_POINT, color="royalblue", lw=1.0, alpha=0.65)

    # optional: äußere Punkte seitlich verbinden
    if SHOW_SIDE_CONNECTIONS:
        p_next = outer_points[(i + 1) % len(outer_points)]
        draw_line(ax, p, p_next, color="silver", lw=0.9, alpha=0.55)

# Optional äußerer Ring
if SHOW_OUTER_RING:
    ring_x = [p[0] for p in outer_points] + [outer_points[0][0]]
    ring_y = [p[1] for p in outer_points] + [outer_points[0][1]]
    ring_z = [p[2] for p in outer_points] + [outer_points[0][2]]
    ax.plot(ring_x, ring_y, ring_z, color="orange", linewidth=1.4, alpha=0.8)

# Verbindung Mittelpunkt -> Punkt dahinter
draw_line(ax, center, BACK_POINT, color="red", lw=2.0, alpha=0.85)

# Achsen-Kreuz wie in der Skizze
axis_len = OUTER_RADIUS + 2
ax.plot([-axis_len, axis_len], [0, 0], [0, 0], color="black", lw=1.0, alpha=0.5)
ax.plot([0, 0], [-axis_len, axis_len], [0, 0], color="black", lw=1.0, alpha=0.5)
ax.plot([0, 0], [0, 0], [BACK_POINT_Z - 1, axis_len / 2], color="black", lw=1.0, alpha=0.5)

# Darstellung
limit = OUTER_RADIUS + 3
ax.set_xlim(-limit, limit)
ax.set_ylim(-limit, limit)
ax.set_zlim(BACK_POINT_Z - 2, limit)
ax.set_box_aspect((1, 1, 1))

ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")
ax.set_title("3D-Stern mit Punkt dahinter")

# Schöne Anfangsansicht
ax.view_init(elev=24, azim=38)

# Legende
ax.legend(loc="upper right")

# Tipp-Text
fig.text(
    0.02, 0.02,
    "Mit der Maus kannst du die 3D-Ansicht drehen.\n"
    "Oben im Script kannst du NUM_ARMS, OUTER_RADIUS und BACK_POINT_Z ändern.",
    fontsize=10,
)

plt.tight_layout()
plt.show()
