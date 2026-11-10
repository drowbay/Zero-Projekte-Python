import random
import math
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401


# =========================================================
# PARAMETER
# =========================================================
TOTAL_STEPS = 120000

BASE_RADIUS = 120

# Pulsgeschwindigkeit
PULSE_SPEED = 0.002
SECOND_PULSE = 0.0007  # zweiter Rhythmus (macht es organischer)

# Drift Stärke
DRIFT_STRENGTH = 0.002

# Kontraktion / Expansion
FACTOR_BASE = 1.6
FACTOR_VARIATION = 0.6

# Darstellung
POINT_SIZE = 2
DRAW_EVERY = 300


# =========================================================
# HILFSFUNKTIONEN
# =========================================================
def random_point(radius):
    theta = random.uniform(0, 2 * math.pi)
    phi = math.acos(random.uniform(-1, 1))
    r = radius * (random.random() ** (1/3))

    x = r * math.sin(phi) * math.cos(theta)
    y = r * math.sin(phi) * math.sin(theta)
    z = r * math.cos(phi)
    return x, y, z


def energy(x, y, z):
    return math.sqrt(x*x + y*y + z*z)


# =========================================================
# PLOT SETUP
# =========================================================
plt.ion()
fig = plt.figure(figsize=(11, 9))
ax = fig.add_subplot(111, projection='3d')

scatter = ax.scatter([], [], [], s=POINT_SIZE)

limit = BASE_RADIUS * 1.8
ax.set_xlim(-limit, limit)
ax.set_ylim(-limit, limit)
ax.set_zlim(-limit, limit)
ax.set_box_aspect((1, 1, 1))

ax.set_title("Breathing Field 3D 🌌")


# Text Anzeige
info_text = fig.text(
    0.02, 0.95, "",
    fontsize=10,
    family="monospace",
    verticalalignment="top"
)


# =========================================================
# START
# =========================================================
x, y, z = 0.0, 0.0, 0.0
xs, ys, zs = [], [], []
colors = []

energy_values = []

print("🔥 Breathing Field läuft... STRG+C zum Beenden")

# =========================================================
# LOOP
# =========================================================
try:
    for i in range(TOTAL_STEPS):

        # =================================================
        # 🧠 1. PULS (deine Idee!)
        # =================================================
        t = i * PULSE_SPEED
        t2 = i * SECOND_PULSE

        state = math.sin(t) + 0.5 * math.sin(t2)

        # normalisieren auf -1 bis +1
        state = max(-1, min(1, state))

        # =================================================
        # 🌌 2. RADIUS (Expansion / Kompression)
        # =================================================
        radius = BASE_RADIUS * (1 + state * 0.5)

        # =================================================
        # ⚛️ 3. ZIELPUNKT
        # =================================================
        px, py, pz = random_point(radius)

        # =================================================
        # 🔧 4. FAKTOR (zieht zusammen)
        # =================================================
        factor = FACTOR_BASE + (state + 1) * FACTOR_VARIATION

        # =================================================
        # 🚀 5. BEWEGUNG
        # =================================================
        x = (x + px) / factor
        y = (y + py) / factor
        z = (z + pz) / factor

        # =================================================
        # 🌊 6. DRIFT (leichtes "Wachsen")
        # =================================================
        drift = 1 + state * DRIFT_STRENGTH
        x *= drift
        y *= drift
        z *= drift

        xs.append(x)
        ys.append(y)
        zs.append(z)

        # =================================================
        # 🎨 7. FARBE (Zustand sichtbar machen)
        # =================================================
        e = energy(x, y, z)
        energy_values.append(e)

        # state -> Farbe (0 bis 1)
        c = (state + 1) / 2

        colors.append(c)

        # =================================================
        # 🖥️ 8. UPDATE
        # =================================================
        if i % DRAW_EVERY == 0 and i > 0:

            scatter._offsets3d = (xs, ys, zs)
            scatter.set_array(np.array(colors))
            scatter.set_cmap("turbo")

            avg_e = float(np.mean(energy_values[-1000:]))

            info_text.set_text(
                "Breathing Field\n"
                "----------------\n"
                f"State       : {state:8.3f}\n"
                f"Radius      : {radius:8.2f}\n"
                f"Energy(avg) : {avg_e:8.2f}\n"
                f"Points      : {len(xs):8d}"
            )

            ax.set_title(
                f"Breathing Field 🌌 | Schritt {i} | State {state:.2f}"
            )

            plt.draw()
            plt.pause(0.001)

except KeyboardInterrupt:
    print("\n👋 Beendet")


# =========================================================
# ENDE
# =========================================================
plt.ioff()
plt.show()