# ============================================================
# TIRXY-RADAR v1
# ------------------------------------------------------------
# Zero + Lumi
# Emergenz / Zustandsfeld / Raumprojektion
#
# Idee:
# - Zentrum S0
# - 6 Raumrichtungen (+/-x, +/-y, +/-z)
# - jede Achse trägt Energie + Phase
# - Phasen koppeln sich
# - daraus entstehen Resonanzmuster
# - Rotation + Emergenz werden sichtbar
#
# BENÖTIGT:
# pip install numpy matplotlib
# ============================================================

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# ============================================================
# PARAMETER
# ============================================================

c = 1.0

time_speed = 0.05

# 6 Richtungsvektoren
directions = np.array([
    [ 1, 0, 0],   # +x
    [-1, 0, 0],   # -x
    [ 0, 1, 0],   # +y
    [ 0,-1, 0],   # -y
    [ 0, 0, 1],   # +z
    [ 0, 0,-1],   # -z
])

# Startphasen
phases = np.linspace(0, 2*np.pi, 6, endpoint=False)

# Frequenzen pro Achse
freqs = np.array([1.0, 1.2, 0.9, 1.1, 1.4, 1.3])

# ============================================================
# FIGUR
# ============================================================

fig = plt.figure(figsize=(9,9))
ax = fig.add_subplot(111, projection='3d')

# ============================================================
# UPDATE
# ============================================================

def update(frame):

    ax.clear()

    # Achsenbereich
    ax.set_xlim(-2,2)
    ax.set_ylim(-2,2)
    ax.set_zlim(-2,2)

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")

    ax.set_title("TIRXY-RADAR v1  |  Emergenz-Zustandsfeld")

    # --------------------------------------------------------
    # Zentrum S0
    # --------------------------------------------------------

    ax.scatter(0,0,0, s=180)

    # --------------------------------------------------------
    # Resonanzfeld sammeln
    # --------------------------------------------------------

    field_x = []
    field_y = []
    field_z = []

    # --------------------------------------------------------
    # 6 Richtungsachsen
    # --------------------------------------------------------

    for i, d in enumerate(directions):

        # Phase
        theta = phases[i] + frame * time_speed * freqs[i]

        # Energie / Amplitude
        amplitude = c**2 * (0.6 + 0.4*np.sin(theta))

        # Endpunkt
        endpoint = d * amplitude

        # Achsenlinie
        ax.plot(
            [0, endpoint[0]],
            [0, endpoint[1]],
            [0, endpoint[2]],
            linewidth=3
        )

        # Endpunkt markieren
        ax.scatter(
            endpoint[0],
            endpoint[1],
            endpoint[2],
            s=80
        )

        # Spiral-/Resonanzpunkte
        t = np.linspace(0, amplitude, 80)

        spiral_x = d[0] * t + 0.08*np.sin(6*t + theta)
        spiral_y = d[1] * t + 0.08*np.cos(6*t + theta)
        spiral_z = d[2] * t + 0.08*np.sin(6*t + theta)

        field_x.extend(spiral_x)
        field_y.extend(spiral_y)
        field_z.extend(spiral_z)

    # --------------------------------------------------------
    # Emergenzfeld darstellen
    # --------------------------------------------------------

    ax.scatter(
        field_x,
        field_y,
        field_z,
        s=3,
        alpha=0.45
    )

    # --------------------------------------------------------
    # Kugelsymmetrie andeuten
    # --------------------------------------------------------

    u = np.linspace(0, 2*np.pi, 30)
    v = np.linspace(0, np.pi, 20)

    r = 1.2

    x = r * np.outer(np.cos(u), np.sin(v))
    y = r * np.outer(np.sin(u), np.sin(v))
    z = r * np.outer(np.ones(np.size(u)), np.cos(v))

    ax.plot_wireframe(
        x, y, z,
        linewidth=0.3,
        alpha=0.2
    )

# ============================================================
# ANIMATION
# ============================================================

ani = FuncAnimation(
    fig,
    update,
    frames=1000,
    interval=40
)

plt.show()