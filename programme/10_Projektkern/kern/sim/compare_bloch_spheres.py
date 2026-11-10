# compare_bloch_spheres.py
# Pydroid 3
#
# Vergleich:
# 1) Normale Bloch-Sphere
# 2) Zero-Bloch-Sphere mit Q=(x,y,z,t,w)
#
# Links:
#   normale Bloch-Sphere
#   x² + y² + z² = 1
#
# Rechts:
#   Zero-Bloch-Sphere
#   Q(t) = (x(t), y(t), z(t), t, w(t))
#   wobei x² + y² + z² = 1 bleibt
#
# Idee:
# - Die normale Bloch-Sphere zeigt nur den Qubit-Zustand.
# - Die Zero-Bloch-Sphere zeigt denselben Zustand
#   plus eine Zusatzspur w.
#
# Wichtig:
# x,y,z sind Zustandskoordinaten, keine Ortskoordinaten.
# w ist hier eine Modell-Erweiterung.

import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# ------------------------------------------------------------
# FARBEN
# ------------------------------------------------------------

BLUE = "#1f77b4"
MAGENTA = "#b23a78"
BLACK = "#111111"
GRAY = "#777777"
LIGHT_BLUE = "#8ecae6"
BACKGROUND = "#f7fbff"

# ------------------------------------------------------------
# EINSTELLUNGEN
# ------------------------------------------------------------

FRAMES = 1000
INTERVAL = 40

THETA_BASE = math.pi / 2.35
THETA_BREATH = 0.24
PHI_SPEED = 0.055

W_AMP = 0.65
W_TO_Z = 0.55

TRAIL_LENGTH = 140


# ------------------------------------------------------------
# MATHE
# ------------------------------------------------------------

def bloch_xyz(theta, phi):
    """
    Offizielle Bloch-Sphere:
    x = sin(theta) cos(phi)
    y = sin(theta) sin(phi)
    z = cos(theta)
    """
    x = math.sin(theta) * math.cos(phi)
    y = math.sin(theta) * math.sin(phi)
    z = math.cos(theta)
    return x, y, z


def zero_state(t):
    """
    Unser erweitertes Modell:
    Q = (x, y, z, t, w)

    x,y,z bleiben auf der Bloch-Sphere.
    """
    theta = THETA_BASE + THETA_BREATH * math.sin(0.55 * t)
    phi = t

    x, y, z = bloch_xyz(theta, phi)

    # w als Zusatzspur / Layer
    w = W_AMP * math.sin(1.45 * phi)

    return x, y, z, t, w, theta, phi


def sphere_mesh(nu=50, nv=26):
    u = np.linspace(0, 2 * np.pi, nu)
    v = np.linspace(0, np.pi, nv)

    xs = np.outer(np.cos(u), np.sin(v))
    ys = np.outer(np.sin(u), np.sin(v))
    zs = np.outer(np.ones_like(u), np.cos(v))

    return xs, ys, zs


# ------------------------------------------------------------
# FIGUR
# ------------------------------------------------------------

fig = plt.figure(figsize=(12, 6))
fig.patch.set_facecolor(BACKGROUND)

ax1 = fig.add_subplot(121, projection="3d")
ax2 = fig.add_subplot(122, projection="3d")

for ax in [ax1, ax2]:
    ax.set_facecolor(BACKGROUND)
    ax.set_xlim(-1.35, 1.35)
    ax.set_ylim(-1.35, 1.35)
    ax.set_zlim(-1.35, 1.35)

    ax.set_xlabel("x", color=BLACK)
    ax.set_ylabel("y", color=BLACK)
    ax.set_zlabel("z", color=BLACK)

    ax.view_init(elev=24, azim=42)

    # Achsen
    ax.plot([-1.25, 1.25], [0, 0], [0, 0], color=BLACK, alpha=0.35, linewidth=1.0)
    ax.plot([0, 0], [-1.25, 1.25], [0, 0], color=BLACK, alpha=0.35, linewidth=1.0)
    ax.plot([0, 0], [0, 0], [-1.25, 1.25], color=BLACK, alpha=0.35, linewidth=1.0)

    ax.text(1.30, 0, 0, "x", color=BLACK)
    ax.text(0, 1.30, 0, "y", color=BLACK)
    ax.text(0, 0, 1.30, "|0⟩", color=BLUE)
    ax.text(0, 0, -1.32, "|1⟩", color=MAGENTA)

# Kugelgitter
xs, ys, zs = sphere_mesh()

ax1.plot_wireframe(xs, ys, zs, color=GRAY, linewidth=0.45, alpha=0.22)
ax2.plot_wireframe(xs, ys, zs, color=GRAY, linewidth=0.45, alpha=0.22)

ax1.set_title("Normale Bloch-Sphere", color=BLACK)
ax2.set_title("Zero-Bloch-Sphere: Q=(x,y,z,t,w)", color=BLACK)

# ------------------------------------------------------------
# OBJEKTE LINKS: NORMALE BLOCH-SPHERE
# ------------------------------------------------------------

dot1 = ax1.scatter([], [], [], s=90, color=BLUE, label="Qubit-Zustand")
vec1, = ax1.plot([], [], [], color=BLUE, linewidth=2.4, label="Zustandsvektor")
trail1, = ax1.plot([], [], [], color=LIGHT_BLUE, linewidth=1.8, alpha=0.80, label="Zeitspur")

info1 = ax1.text2D(0.03, 0.95, "", transform=ax1.transAxes, color=BLACK)

ax1.legend(loc="lower left", fontsize=8)

# ------------------------------------------------------------
# OBJEKTE RECHTS: ZERO-BLOCH
# ------------------------------------------------------------

dot2 = ax2.scatter([], [], [], s=90, color=BLUE, label="Zero-Zustand")
vec2, = ax2.plot([], [], [], color=BLUE, linewidth=2.4, label="Zustandsvektor")
wline2, = ax2.plot([], [], [], color=MAGENTA, linewidth=1.8, alpha=0.85, label="w-Spur")
trail2, = ax2.plot([], [], [], color=LIGHT_BLUE, linewidth=1.8, alpha=0.80, label="Zeitspur")

info2 = ax2.text2D(0.03, 0.95, "", transform=ax2.transAxes, color=BLACK)

ax2.legend(loc="lower left", fontsize=8)

# Spuren
history_left = []
history_right = []


# ------------------------------------------------------------
# ANIMATION
# ------------------------------------------------------------

def update(frame):
    global history_left, history_right

    t = frame * PHI_SPEED * 2 * math.pi

    x, y, z, t_value, w, theta, phi = zero_state(t)

    # ---- LINKS: normale Bloch-Sphere ----
    dot1._offsets3d = ([x], [y], [z])
    vec1.set_data([0, x], [0, y])
    vec1.set_3d_properties([0, z])

    history_left.append([x, y, z])
    history_left = history_left[-TRAIL_LENGTH:]

    arr_left = np.array(history_left)
    trail1.set_data(arr_left[:, 0], arr_left[:, 1])
    trail1.set_3d_properties(arr_left[:, 2])

    # Wahrscheinlichkeiten
    p0 = math.cos(theta / 2) ** 2
    p1 = math.sin(theta / 2) ** 2

    info1.set_text(
        "NORMALE BLOCH-SPHERE\n\n"
        "Zustand:\n"
        "|ψ⟩ = cos(θ/2)|0⟩ + e^(iφ) sin(θ/2)|1⟩\n\n"
        f"x = {x:.3f}\n"
        f"y = {y:.3f}\n"
        f"z = {z:.3f}\n\n"
        f"θ = {theta:.3f}\n"
        f"φ = {phi:.3f}\n\n"
        f"P(0) = {p0:.3f}\n"
        f"P(1) = {p1:.3f}\n\n"
        "Kern:\n"
        "x² + y² + z² = 1"
    )

    # ---- RECHTS: Zero-Bloch ----
    z_visual = z + W_TO_Z * w

    dot2._offsets3d = ([x], [y], [z_visual])
    vec2.set_data([0, x], [0, y])
    vec2.set_3d_properties([0, z_visual])

    # w-Linie zeigt Unterschied zwischen echtem Bloch-Punkt und Zero-Projektion
    wline2.set_data([x, x], [y, y])
    wline2.set_3d_properties([z, z_visual])

    history_right.append([x, y, z_visual])
    history_right = history_right[-TRAIL_LENGTH:]

    arr_right = np.array(history_right)
    trail2.set_data(arr_right[:, 0], arr_right[:, 1])
    trail2.set_3d_properties(arr_right[:, 2])

    info2.set_text(
        "ZERO-BLOCH\n\n"
        "Erweiterung:\n"
        "Q = (x, y, z, t, w)\n\n"
        f"x = {x:.3f}\n"
        f"y = {y:.3f}\n"
        f"z = {z:.3f}\n"
        f"t = {t_value:.3f}\n"
        f"w = {w:.3f}\n\n"
        f"z_vis = z + {W_TO_Z:.2f}·w\n"
        f"      = {z_visual:.3f}\n\n"
        "Kern:\n"
        "x² + y² + z² = 1 bleibt gültig\n\n"
        "Zusatz:\n"
        "t = Verlauf\n"
        "w = Schicht / Zusatzspur"
    )

    # Kamera leicht bewegen
    a = 42 + 0.10 * frame
    e = 24 + 3 * math.sin(0.08 * t)

    ax1.view_init(elev=e, azim=a)
    ax2.view_init(elev=e, azim=a)

    return dot1, vec1, trail1, info1, dot2, vec2, wline2, trail2, info2


ani = FuncAnimation(
    fig,
    update,
    frames=FRAMES,
    interval=INTERVAL,
    blit=False
)

plt.tight_layout()
plt.show()