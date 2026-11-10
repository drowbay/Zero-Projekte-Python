# zero_qubit_bloch_sim.py
# Pydroid 3
#
# Zero Qubit Bloch Simulation
#
# Modell:
# Q = (x, y, z, t, w)
#
# x,y,z = Punkt auf der Bloch-Sphere
# t     = Zeit / Verlauf
# w     = Layer / Zusatzphase / Einbettungsspur
#
# Physikalisch:
# Ein Qubit-Zustand:
# |psi> = cos(theta/2)|0> + e^(i phi) sin(theta/2)|1>
#
# Bloch-Kugel:
# x = sin(theta) cos(phi)
# y = sin(theta) sin(phi)
# z = cos(theta)
#
# Modell-Erweiterung:
# w(t) = A sin(phi(t))
#
# Penta-Sprung:
# 0 -> 2 -> 4 -> 1 -> 3

import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


# Farben aus unserem Zero/Smile-System
BLUE = "#1f77b4"
MAGENTA = "#b23a78"
BLACK = "#111111"
GRAY = "#777777"
LIGHT_BLUE = "#8ecae6"
LIGHT_MAGENTA = "#e07aa8"
BACKGROUND = "#f7fbff"


# Einstellungen
FRAMES = 900
TRAIL_LENGTH = 160

# Qubit-Winkel
THETA_BASE = math.pi / 2.4       # Neigung auf der Kugel
PHI_SPEED = 0.035                # Drehgeschwindigkeit

# w-Layer
W_AMP = 0.65
W_TO_Z = 0.55                    # w wird sichtbar als Zusatzhöhe

# Penta-Orbit
PENTA = [0, 2, 4, 1, 3]
PENTA_RADIUS = 1.08


def bloch_xyz(theta, phi):
    """
    Bloch-Kugel-Koordinaten.
    """
    x = math.sin(theta) * math.cos(phi)
    y = math.sin(theta) * math.sin(phi)
    z = math.cos(theta)
    return np.array([x, y, z], dtype=float)


def zero_qubit_state(t):
    """
    Unser Zustand:
    Q(t) = (x(t), y(t), z(t), t, w(t))
    """

    # theta darf leicht atmen, damit es lebendig aussieht
    theta = THETA_BASE + 0.28 * math.sin(t * 0.65)

    # phi dreht um die Kugel
    phi = t

    xyz = bloch_xyz(theta, phi)

    # w ist Zusatzphase/Layer
    w = W_AMP * math.sin(phi * 1.5)

    return xyz[0], xyz[1], xyz[2], t, w, theta, phi


def sphere_wireframe():
    """
    Erzeugt Linien für eine einfache Bloch-Sphere.
    """
    lines = []

    # Längenkreise
    for a in np.linspace(0, 2 * math.pi, 9):
        pts = []
        for u in np.linspace(0, 2 * math.pi, 160):
            x = math.sin(u) * math.cos(a)
            y = math.sin(u) * math.sin(a)
            z = math.cos(u)
            pts.append([x, y, z])
        lines.append(np.array(pts))

    # Breitenkreise
    for z in np.linspace(-0.75, 0.75, 5):
        r = math.sqrt(max(0, 1 - z*z))
        pts = []
        for a in np.linspace(0, 2 * math.pi, 160):
            x = r * math.cos(a)
            y = r * math.sin(a)
            pts.append([x, y, z])
        lines.append(np.array(pts))

    return lines


def penta_points(theta):
    """
    Fünf Phasenpunkte auf der Bloch-Sphere nach Penta-Reihenfolge.
    """
    pts = []
    labels = []

    for p in PENTA:
        phi = 2 * math.pi * p / 5
        xyz = bloch_xyz(theta, phi)
        pts.append(xyz)
        labels.append(str(p))

    return np.array(pts), labels


# Plot vorbereiten
fig = plt.figure(figsize=(10, 8))
fig.patch.set_facecolor(BACKGROUND)

ax = fig.add_subplot(111, projection="3d")
ax.set_facecolor(BACKGROUND)

fig.suptitle(
    "Zero Qubit Bloch Simulation — Q=(x,y,z,t,w)",
    color=BLACK,
    fontsize=13
)

ax.set_xlim(-1.45, 1.45)
ax.set_ylim(-1.45, 1.45)
ax.set_zlim(-1.45, 1.45)

ax.set_xlabel("x", color=BLACK)
ax.set_ylabel("y", color=BLACK)
ax.set_zlabel("z + w-Projektion", color=BLACK)

ax.view_init(elev=25, azim=45)

# Bloch-Sphere Linien
for line in sphere_wireframe():
    ax.plot(
        line[:, 0], line[:, 1], line[:, 2],
        color=GRAY,
        alpha=0.18,
        linewidth=0.8
    )

# Achsen
ax.plot([-1.25, 1.25], [0, 0], [0, 0], color=BLACK, alpha=0.45)
ax.plot([0, 0], [-1.25, 1.25], [0, 0], color=BLACK, alpha=0.45)
ax.plot([0, 0], [0, 0], [-1.25, 1.25], color=BLACK, alpha=0.45)

ax.text(1.32, 0, 0, "x", color=BLACK)
ax.text(0, 1.32, 0, "y", color=BLACK)
ax.text(0, 0, 1.32, "|0>", color=BLUE)
ax.text(0, 0, -1.32, "|1>", color=MAGENTA)

# Penta-Punkte
penta_pts, penta_labels = penta_points(THETA_BASE)
ax.plot(
    penta_pts[:, 0],
    penta_pts[:, 1],
    penta_pts[:, 2],
    color=MAGENTA,
    linewidth=1.8,
    alpha=0.65,
    linestyle="--"
)

for i, label in enumerate(penta_labels):
    ax.scatter(
        [penta_pts[i, 0]],
        [penta_pts[i, 1]],
        [penta_pts[i, 2]],
        s=35,
        color=BLUE if i % 2 == 0 else MAGENTA
    )
    ax.text(
        penta_pts[i, 0] * 1.08,
        penta_pts[i, 1] * 1.08,
        penta_pts[i, 2] * 1.08,
        label,
        color=BLACK
    )

# Bewegter Zustand
state_dot = ax.scatter([], [], [], s=95, color=BLUE, label="Qubit-Zustand")
state_vector, = ax.plot([], [], [], color=BLUE, linewidth=2.5, label="Zustandsvektor")
w_line, = ax.plot([], [], [], color=MAGENTA, linewidth=1.6, alpha=0.75, label="w-Layer-Spur")
trail_line, = ax.plot([], [], [], color=LIGHT_BLUE, linewidth=2.0, alpha=0.75, label="Zeitspur")

info = ax.text2D(0.02, 0.95, "", transform=ax.transAxes, color=BLACK)
legend = ax.text2D(0.66, 0.95, "", transform=ax.transAxes, color=BLACK)

ax.legend(loc="lower left", fontsize=8)

trail = []


def update(frame):
    global trail

    t = frame * PHI_SPEED * 2 * math.pi

    x, y, z, time_value, w, theta, phi = zero_qubit_state(t)

    # w sichtbar machen: Zusatzhöhe
    z_visual = z + W_TO_Z * w

    # Punkt setzen
    state_dot._offsets3d = ([x], [y], [z_visual])

    # Vektor vom Ursprung
    state_vector.set_data([0, x], [0, y])
    state_vector.set_3d_properties([0, z_visual])

    # w-Linie: von eigentlichem Bloch-Punkt zur w-Projektion
    w_line.set_data([x, x], [y, y])
    w_line.set_3d_properties([z, z_visual])

    # Trail
    trail.append([x, y, z_visual])
    trail = trail[-TRAIL_LENGTH:]

    arr = np.array(trail)
    trail_line.set_data(arr[:, 0], arr[:, 1])
    trail_line.set_3d_properties(arr[:, 2])

    # Wahrscheinlichkeiten
    prob_0 = math.cos(theta / 2) ** 2
    prob_1 = math.sin(theta / 2) ** 2

    info.set_text(
        "ZERO-QUBIT\n\n"
        "Q(t) = (x,y,z,t,w)\n\n"
        f"x = {x:.3f}\n"
        f"y = {y:.3f}\n"
        f"z = {z:.3f}\n"
        f"t = {time_value:.3f}\n"
        f"w = {w:.3f}\n\n"
        f"theta = {theta:.3f}\n"
        f"phi   = {phi:.3f}\n\n"
        f"P(0) = |alpha|² = {prob_0:.3f}\n"
        f"P(1) = |beta|²  = {prob_1:.3f}\n\n"
        "Penta:\n"
        "0 → 2 → 4 → 1 → 3"
    )

    legend.set_text(
        "LEGENDE\n\n"
        "Kugel = Bloch-Sphere\n"
        "Blau = Qubit-Zustand\n"
        "Magenta = w-Layer\n"
        "Grau = Koordinaten / Hilfslinien\n\n"
        "Mathe:\n"
        "x²+y²+z² = 1\n"
        "|psi> = α|0> + β|1>\n"
        "|α|²+|β|² = 1\n\n"
        "Merksatz:\n"
        "x,y,z zeigen Zustand\n"
        "t zeigt Verlauf\n"
        "w zeigt Schicht"
    )

    ax.view_init(
        elev=25 + 4 * math.sin(t * 0.15),
        azim=45 + frame * 0.12
    )

    return state_dot, state_vector, w_line, trail_line, info, legend


ani = FuncAnimation(
    fig,
    update,
    frames=FRAMES,
    interval=40,
    blit=False
)

plt.show()