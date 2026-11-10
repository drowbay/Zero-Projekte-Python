import random
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401


# =========================================================
# Hilfsfunktionen
# =========================================================
def growth_factor(step, max_steps, start=0.15, end=1.0):
    """Sanftes Wachstum des verfügbaren Raums."""
    t = min(step / max_steps, 1.0)
    return start + (end - start) * (1 - math.exp(-5 * t)) / (1 - math.exp(-5))


def energy_metric(x, y, z):
    """Spielerische Energie-Metrik = Abstand vom Ursprung."""
    return math.sqrt(x * x + y * y + z * z)


def voxel_index(x, y, z, voxel_size):
    return (
        int(x // voxel_size),
        int(y // voxel_size),
        int(z // voxel_size),
    )


def random_spherical_point(radius):
    """Zufälliger Punkt in alle Richtungen, ungefähr kugelförmig."""
    theta = random.uniform(0, 2 * math.pi)
    phi = math.acos(random.uniform(-1, 1))
    r = radius * (random.random() ** (1 / 3))  # volumetrisch verteilt

    x = r * math.sin(phi) * math.cos(theta)
    y = r * math.sin(phi) * math.sin(theta)
    z = r * math.cos(phi)
    return x, y, z


def random_stretched_point(radius, stretch=(1.6, 1.2, 1.0)):
    """
    Zufälliger Punkt in alle Richtungen, aber gedehnt.
    stretch=(sx,sy,sz) erzeugt anisotrope Ausdehnung.
    """
    x, y, z = random_spherical_point(radius)
    return x * stretch[0], y * stretch[1], z * stretch[2]


# =========================================================
# Farben / Teilchentypen
# =========================================================
PARTICLE_COLORS = {
    "anchor_1": "#FFFFFF",   # weiß
    "anchor_2": "#FFD700",   # gold
    "field": "#00E5FF",      # cyan
    "drift": "#1E88E5",      # blau
    "quantum": "#EC407A",    # pink
    "plasma": "#FF7043",     # orange
    "memory": "#AB47BC",     # lila
    "echo": "#26A69A",       # türkis
    "noise": "#BDBDBD",      # grau
    "shadow": "#5C6BC0",     # indigo
}

PARTICLE_ORDER = list(PARTICLE_COLORS.keys())


# =========================================================
# Parameter
# =========================================================
TOTAL_STEPS = 100000

SPACE_RADIUS = 120
USE_GROWTH = True

# Dehnung in alle Richtungen, aber gern etwas länger auf X/Y/Z
STRETCH = (1.8, 1.4, 1.2)

# 1 oder 2 Fixpunkte
USE_SECOND_ANCHOR = True
ANCHOR_1 = (0, 0, 0)
ANCHOR_2 = (55, -35, 30)

# Gewichtung der Zielarten
ANCHOR_WEIGHT_1 = 3
ANCHOR_WEIGHT_2 = 2
FIELD_WEIGHT = 6
DRIFT_WEIGHT = 4
QUANTUM_WEIGHT = 2
MEMORY_WEIGHT = 2

# Schneller / lebendiger:
# kleinerer Faktor -> aggressiverer Zug
FACTOR_CHOICES = [1.55, 1.7, 1.85, 2.0]

VOXEL_SIZE = 10
DRAW_EVERY = 300
POINT_SIZE = 2


# =========================================================
# Plot
# =========================================================
plt.ion()
fig = plt.figure(figsize=(13, 9))
ax = fig.add_subplot(111, projection="3d")

scatter = ax.scatter([], [], [], s=POINT_SIZE)
target_scatter = ax.scatter([], [], [], s=40, alpha=0.95)

limit = SPACE_RADIUS * max(STRETCH) * 1.2
ax.set_xlim(-limit, limit)
ax.set_ylim(-limit, limit)
ax.set_zlim(-limit, limit)
ax.set_box_aspect((1, 1, 1))
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")
ax.set_title("Freies 3D-Feld mit Fixpunkten")

theory_text = fig.text(
    0.015,
    0.96,
    "",
    fontsize=10,
    verticalalignment="top",
    family="monospace",
)

legend_handles = [
    Line2D([0], [0], marker='o', color='w', label=name,
           markerfacecolor=color, markersize=8)
    for name, color in PARTICLE_COLORS.items()
]
ax.legend(
    handles=legend_handles,
    loc="upper right",
    bbox_to_anchor=(1.22, 1.0),
    title="Teilchentypen"
)


# =========================================================
# Datencontainer
# =========================================================
x, y, z = 0.0, 0.0, 0.0
xs, ys, zs = [], [], []
point_colors = []

occupied_voxels = set()
field_counter = {}
particle_counter = {name: 0 for name in PARTICLE_ORDER}
energy_values = []

history_points = []


# =========================================================
# Ziele bauen
# =========================================================
def build_targets(g, history_points):
    radius = SPACE_RADIUS * g
    targets = []

    # Fixpunkte / Anker
    for _ in range(ANCHOR_WEIGHT_1):
        targets.append((*ANCHOR_1, "anchor_1"))

    if USE_SECOND_ANCHOR:
        scaled_anchor_2 = tuple(a * g for a in ANCHOR_2)
        for _ in range(ANCHOR_WEIGHT_2):
            targets.append((*scaled_anchor_2, "anchor_2"))

    # Freie Feldpunkte
    for _ in range(FIELD_WEIGHT):
        fx, fy, fz = random_stretched_point(radius, stretch=STRETCH)
        targets.append((fx, fy, fz, "field"))

    # Drift-Partikel: weiter außen, mehr Expansion
    for _ in range(DRIFT_WEIGHT):
        dx, dy, dz = random_stretched_point(radius * 1.25, stretch=STRETCH)
        targets.append((dx, dy, dz, "drift"))

    # Quantum-Partikel: kleine unruhige Wolke um den Ursprung
    for _ in range(QUANTUM_WEIGHT):
        qx = random.uniform(-15, 15) * g
        qy = random.uniform(-15, 15) * g
        qz = random.uniform(-15, 15) * g
        targets.append((qx, qy, qz, "quantum"))

    # Memory-Partikel aus der Vergangenheit
    if len(history_points) > 30:
        sample_count = min(8, len(history_points))
        samples = random.sample(history_points, sample_count)
        for hx, hy, hz in samples:
            targets.append((hx, hy, hz, "memory"))

    # Echo / Noise / Shadow / Plasma
    ex, ey, ez = random_stretched_point(radius * 0.7, stretch=STRETCH)
    targets.append((ex, ey, ez, "echo"))

    nx, ny, nz = random_stretched_point(radius * 0.4, stretch=(2.0, 2.0, 0.8))
    targets.append((nx, ny, nz, "noise"))

    sx, sy, sz = random_stretched_point(radius * 0.5, stretch=(1.2, 1.2, 0.5))
    targets.append((sx, sy, -abs(sz), "shadow"))

    px, py, pz = random_stretched_point(radius * 0.9, stretch=(1.0, 1.0, 1.6))
    targets.append((px, py, pz, "plasma"))

    # Sichtbare Ziele ohne exakte Duplikate
    visible_targets = []
    seen = set()
    for t in targets:
        key = (round(t[0], 3), round(t[1], 3), round(t[2], 3), t[3])
        if key not in seen:
            visible_targets.append(t)
            seen.add(key)

    return targets, visible_targets


# =========================================================
# Simulation
# =========================================================
print("Freies Feld mit 1–2 Fixpunkten läuft ... STRG+C zum Beenden")

try:
    for i in range(TOTAL_STEPS):
        g = growth_factor(i, TOTAL_STEPS) if USE_GROWTH else 1.0
        targets, visible_targets = build_targets(g, history_points)

        px, py, pz, particle_type = random.choice(targets)
        factor = random.choice(FACTOR_CHOICES)

        # Bewegung: schneller, freier, wachsend
        x = (x + px) / factor
        y = (y + py) / factor
        z = (z + pz) / factor

        # leichte Zusatzdehnung / Drift
        x *= 1.0015
        y *= 1.0012
        z *= 1.0010

        xs.append(x)
        ys.append(y)
        zs.append(z)
        point_colors.append(PARTICLE_COLORS[particle_type])
        particle_counter[particle_type] += 1

        energy = energy_metric(x, y, z)
        energy_values.append(energy)

        vox = voxel_index(x, y, z, VOXEL_SIZE)
        occupied_voxels.add(vox)
        field_counter[vox] = field_counter.get(vox, 0) + 1

        if i % 150 == 0:
            history_points.append((x, y, z))
            if len(history_points) > 600:
                history_points.pop(0)

        if i % DRAW_EVERY == 0 and i > 0:
            scatter._offsets3d = (xs, ys, zs)
            scatter.set_color(point_colors)

            tx = [p[0] for p in visible_targets]
            ty = [p[1] for p in visible_targets]
            tz = [p[2] for p in visible_targets]
            tc = [PARTICLE_COLORS[p[3]] for p in visible_targets]
            target_scatter._offsets3d = (tx, ty, tz)
            target_scatter.set_color(tc)

            avg_energy = float(np.mean(energy_values[-1000:])) if energy_values else 0.0
            density = len(xs) / max(len(occupied_voxels), 1)
            dominant_voxel = max(field_counter, key=field_counter.get)

            dominant_particle = max(particle_counter, key=particle_counter.get)

            theory_text.set_text(
                "Freies Feld\n"
                "-----------\n"
                f"Energie     : {avg_energy:8.2f}\n"
                f"Lage        : ({x:7.2f}, {y:7.2f}, {z:7.2f})\n"
                f"Feld        : {len(occupied_voxels):8d} Voxel\n"
                f"Emergenz    : Expansion / Cluster / Drift\n"
                f"Information : {len(occupied_voxels):8d}\n"
                f"Ordnung     : {density:8.2f}\n"
                f"Wachstum    : {g:8.2f}\n"
                f"TopPartikel : {dominant_particle}\n"
                f"DominantVox : {dominant_voxel}"
            )

            ax.set_title(
                f"Freies 3D-Feld | Schritt {i} | Wachstum {g:.2f} | Ordnung {density:.2f}"
            )

            plt.draw()
            plt.pause(0.001)

except KeyboardInterrupt:
    print("\nBeendet 👋")


# =========================================================
# Abschluss
# =========================================================
avg_energy_total = float(np.mean(energy_values)) if energy_values else 0.0
density_final = len(xs) / max(len(occupied_voxels), 1)
dominant_voxel = max(field_counter, key=field_counter.get) if field_counter else None

print("\n--- Abschlussanalyse ---")
print(f"Gesamtpunkte : {len(xs)}")
print(f"Belegte Voxel: {len(occupied_voxels)}")
print(f"Ordnung      : {density_final:.2f}")
print(f"Energie Ø    : {avg_energy_total:.2f}")
print(f"Dominant Vox : {dominant_voxel}")

print("\n--- Teilchenzählung ---")
for name in PARTICLE_ORDER:
    print(f"{name:>10}: {particle_counter[name]}")

plt.ioff()
plt.show()