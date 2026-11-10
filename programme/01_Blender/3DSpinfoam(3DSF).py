import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# ==========================================
# MS / MSM – animierte 3D-Sinnform (vorwärts)
# ==========================================

# ----------------------------
# SETTINGS
# ----------------------------
SEED = 7
FRAMES = 220
INTERVAL = 70

POINT_COUNT = 180
SHOW_LABELS = False

ETA_DENSITY = 1.0
PSI_STRENGTH = 1.0
DELTA_STRENGTH = 1.0

# ----------------------------
# RNG
# ----------------------------
rng = np.random.default_rng(SEED)

# ----------------------------
# HELPERS
# ----------------------------
def rot_z(a):
    return np.array([
        [np.cos(a), -np.sin(a), 0],
        [np.sin(a),  np.cos(a), 0],
        [0, 0, 1]
    ])

def rot_y(a):
    return np.array([
        [ np.cos(a), 0, np.sin(a)],
        [0, 1, 0],
        [-np.sin(a), 0, np.cos(a)]
    ])

def make_triangle(center, size=0.4, yaw=0.0, tilt=0.0):
    """
    Erzeugt ein kleines 3D-Dreieck (wedge).
    """
    base = np.array([
        [0.0,  1.0, 0.0],
        [-0.85, -0.75, 0.0],
        [0.85, -0.75, 0.0]
    ]) * size

    R = rot_z(yaw) @ rot_y(tilt)
    pts = base @ R.T
    pts += np.array(center)
    return pts

def make_wire_triangle(center, size=0.7, yaw=0.0, tilt=0.0):
    pts = make_triangle(center, size=size, yaw=yaw, tilt=tilt)
    loop = np.vstack([pts, pts[0]])
    return loop

def cloud_points(n, xlim, ylim, zlim):
    xs = rng.uniform(xlim[0], xlim[1], n)
    ys = rng.uniform(ylim[0], ylim[1], n)
    zs = rng.uniform(zlim[0], zlim[1], n)
    return np.column_stack([xs, ys, zs])

# ----------------------------
# STATIC STRUCTURE
# ----------------------------
# Vertex / Ursprungsknoten
vertex = np.array([0.0, 0.0, 0.0])

# Hintergrundpunkte = eta
eta_points = cloud_points(
    POINT_COUNT,
    xlim=(-2.5, 8.0),
    ylim=(-1.6, 5.2),
    zlim=(-1.8, 3.8)
)

# face-Flächen als 3D-Polygone
face_top = np.array([
    [1.2, 3.7, 2.2],
    [6.8, 4.4, 2.9],
    [7.7, 2.2, 1.2],
    [3.0, 1.5, 0.9],
    [0.9, 2.4, 1.4]
])

face_mid = np.array([
    [0.7, 1.0, 0.4],
    [5.8, 1.6, 1.0],
    [6.8, 0.2, 0.1],
    [3.6, -0.7, -0.6],
    [1.2, -0.1, -0.2]
])

# feste Bezugspunkte / kleine g-Punkte
g1 = np.array([0.35, 0.95, 0.55])
g2 = np.array([0.45, -0.75, -0.35])

# ----------------------------
# FIGURE
# ----------------------------
fig = plt.figure(figsize=(8.2, 8.8))
ax = fig.add_subplot(111, projection="3d")
fig.patch.set_facecolor("white")
ax.set_facecolor("white")

# ----------------------------
# DRAW STATIC BASE
# ----------------------------
# face-Flächen
poly_top = Poly3DCollection([face_top], facecolors="0.95", edgecolors="black", linewidths=1.5, alpha=1.0)
poly_mid = Poly3DCollection([face_mid], facecolors="0.88", edgecolors="black", linewidths=1.5, alpha=1.0)
ax.add_collection3d(poly_top)
ax.add_collection3d(poly_mid)

# eta cloud
eta_scatter = ax.scatter(
    eta_points[:, 0], eta_points[:, 1], eta_points[:, 2],
    s=14, facecolors="none", edgecolors="0.4", linewidths=0.7, alpha=0.75
)

# vertex und g-punkte
ax.scatter([vertex[0]], [vertex[1]], [vertex[2]], s=40, color="black")
ax.scatter([g1[0], g2[0]], [g1[1], g2[1]], [g1[2], g2[2]], s=18, color="black")

# Kanten vom Vertex
ax.plot([vertex[0], g1[0]], [vertex[1], g1[1]], [vertex[2], g1[2]], color="black", lw=1.3)
ax.plot([vertex[0], g2[0]], [vertex[1], g2[1]], [vertex[2], g2[2]], color="black", lw=1.3)

# Platzhalter für dynamische Objekte
wedge_polys = []
wire_lines = []
link_lines = []

for _ in range(4):
    poly = Poly3DCollection([np.zeros((3, 3))], facecolors="0.2", edgecolors="black", linewidths=1.0, alpha=1.0)
    ax.add_collection3d(poly)
    wedge_polys.append(poly)

    line, = ax.plot([], [], [], color="0.5", lw=1.0, alpha=0.7)
    wire_lines.append(line)

for _ in range(3):
    line, = ax.plot([], [], [], color="0.25", lw=1.2)
    link_lines.append(line)

# ----------------------------
# LABELS
# ----------------------------
if SHOW_LABELS:
    ax.text(7.0, 3.2, 2.5, "spin foam face", fontsize=12)
    ax.text(3.7, 0.6, 0.4, "wedge", fontsize=12)
    ax.text(-0.55, 0.0, 0.0, "vertex", fontsize=12)
    ax.text(7.0, -0.6, -0.5, "edge", fontsize=12)

title = ax.set_title("MS / MSM – animierte 3D-Sinnform (vorwärts)", fontsize=13)

# ----------------------------
# AXIS STYLE
# ----------------------------
ax.set_xlim(-1.2, 8.4)
ax.set_ylim(-2.2, 5.3)
ax.set_zlim(-2.2, 4.0)

ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")

ax.view_init(elev=24, azim=-64)

# ----------------------------
# ANIMATION
# ----------------------------
def update(frame):
    t = frame * 0.055

    # leichte Vorwärtsbewegung des Gesamteindrucks
    drift = np.array([0.020 * frame, 0.0, 0.0])

    # vier dynamische wedge-Zentren
    centers = [
        np.array([2.2 + 0.35*np.sin(1.2*t),  2.2 + 0.15*np.cos(t),     1.3 + 0.25*np.sin(0.8*t)]),
        np.array([2.8 + 0.30*np.cos(0.9*t),  0.2 + 0.22*np.sin(1.1*t), 0.2 + 0.18*np.cos(1.3*t)]),
        np.array([6.6 + 0.18*np.sin(1.0*t), -1.1 + 0.18*np.cos(0.7*t), -0.8 + 0.20*np.sin(0.9*t)]),
        np.array([6.5 + 0.25*np.cos(0.8*t),  3.7 + 0.20*np.sin(0.9*t),  2.7 + 0.15*np.cos(1.0*t)]),
    ]

    yaws = [
        -0.55 + 0.30*np.sin(t),
        -0.35 + 0.25*np.cos(1.2*t),
         0.95 + 0.25*np.sin(0.9*t),
         0.75 + 0.22*np.cos(1.1*t),
    ]

    tilts = [
        0.35*np.sin(0.7*t),
        0.25*np.cos(0.9*t),
        0.40*np.sin(0.8*t),
        0.28*np.cos(0.85*t),
    ]

    sizes = [
        0.42 + 0.05*np.sin(t),
        0.48 + 0.05*np.cos(1.1*t),
        0.54 + 0.04*np.sin(0.8*t),
        0.52 + 0.04*np.cos(0.9*t),
    ]

    # dynamische Wedges
    for i in range(4):
        c = centers[i] + drift * 0.02
        tri = make_triangle(c, size=sizes[i] * PSI_STRENGTH, yaw=yaws[i], tilt=tilts[i])
        wire = make_wire_triangle(c, size=(sizes[i] + 0.28), yaw=yaws[i], tilt=tilts[i])

        wedge_polys[i].set_verts([tri])
        wire_lines[i].set_data(wire[:, 0], wire[:, 1])
        wire_lines[i].set_3d_properties(wire[:, 2])

    # Links / Delta
    link_targets = [
        centers[1] + np.array([-0.35, 0.1, 0.0]),
        centers[0] + np.array([-0.25, -0.1, 0.0]),
        centers[2] + np.array([-0.45, 0.0, 0.1]),
    ]

    starts = [vertex, g1, g2]

    for i in range(3):
        p0 = starts[i]
        p1 = link_targets[i] + drift * 0.02
        xs = [p0[0], p1[0]]
        ys = [p0[1], p1[1]]
        zs = [p0[2], p1[2]]
        link_lines[i].set_data(xs, ys)
        link_lines[i].set_3d_properties(zs)
        link_lines[i].set_linewidth(1.1 + 0.4 * DELTA_STRENGTH)

    # leichte Kameradrehung = Vorwärtsgefühl
    ax.view_init(elev=24 + 2*np.sin(0.3*t), azim=-64 + 8*np.sin(0.18*t))

    title.set_text(f"MS / MSM – animierte 3D-Sinnform (vorwärts) | t = {t:.2f}")

    artists = wedge_polys + wire_lines + link_lines
    return artists

ani = FuncAnimation(fig, update, frames=FRAMES, interval=INTERVAL, blit=False)

plt.tight_layout()
plt.show()