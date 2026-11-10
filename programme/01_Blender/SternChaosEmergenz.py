import random
import math
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401


def star_points_2d(outer_radius=100, inner_radius=40):
    """Erzeugt 10 Punkte eines 5-Zacken-Sterns in 2D."""
    pts = []
    for i in range(10):
        angle_deg = 90 + i * 36
        angle_rad = math.radians(angle_deg)
        r = outer_radius if i % 2 == 0 else inner_radius
        x = r * math.cos(angle_rad)
        y = r * math.sin(angle_rad)
        pts.append((x, y))
    return pts


# -----------------------------
# Geometrie
# -----------------------------
base_points = star_points_2d(outer_radius=100, inner_radius=40)
O = (0, 0, 120)
targets = [(x, y, 0) for x, y in base_points] + [O]
target_names = [f"S{i}" for i in range(10)] + ["O"]

# -----------------------------
# Chaos-Start
# -----------------------------
x, y, z = 0.0, 0.0, 0.0
xs, ys, zs = [], [], []
colors = []
hit_counter = {name: 0 for name in target_names}

# Für Emergenz-Analyse:
# Wir legen ein 3D-Raster über den Raum und zählen, welche Zellen benutzt werden.
voxel_size = 8
occupied_voxels = set()

# -----------------------------
# Plot
# -----------------------------
plt.ion()
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection="3d")

scatter = ax.scatter([], [], [], s=1, c=[], cmap="plasma")

# Zielpunkte anzeigen
tx = [p[0] for p in targets]
ty = [p[1] for p in targets]
tz = [p[2] for p in targets]
ax.scatter(tx, ty, tz, s=60, marker="o")

for name, (px, py, pz) in zip(target_names, targets):
    ax.text(px, py, pz + 4, name, fontsize=8)

ax.set_xlim(-120, 120)
ax.set_ylim(-120, 120)
ax.set_zlim(-20, 140)
ax.set_box_aspect((1, 1, 1))

ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")
ax.set_title("3D Stern Chaos mit Emergenz")

print("3D Emergenz-Plot läuft ... STRG+C zum Beenden")

# -----------------------------
# Simulation
# -----------------------------
try:
    for i in range(100000):
        idx = random.randrange(len(targets))
        px, py, pz = targets[idx]
        hit_counter[target_names[idx]] += 1

        # Halbierungs-Prinzip
        x = (x + px) / 2
        y = (y + py) / 2
        z = (z + pz) / 2

        xs.append(x)
        ys.append(y)
        zs.append(z)
        colors.append(i)

        # belegte Raumzelle merken
        voxel = (
            int(x // voxel_size),
            int(y // voxel_size),
            int(z // voxel_size),
        )
        occupied_voxels.add(voxel)

        if i % 500 == 0 and i > 0:
            scatter._offsets3d = (xs, ys, zs)
            scatter.set_array(np.array(colors))

            # Emergenz-Metriken
            num_points = len(xs)
            num_voxels = len(occupied_voxels)
            compression = num_points / max(num_voxels, 1)

            max_hits = max(hit_counter.values())
            dominant = [k for k, v in hit_counter.items() if v == max_hits]

            print(
                f"Schritt {i:6d} | "
                f"Punkte: {num_points:6d} | "
                f"belegte Voxel: {num_voxels:5d} | "
                f"Verdichtung: {compression:7.2f} | "
                f"dominant: {dominant}"
            )

            plt.draw()
            plt.pause(0.001)

except KeyboardInterrupt:
    print("\nBeendet 👋")

# -----------------------------
# Abschluss-Auswertung
# -----------------------------
total_hits = sum(hit_counter.values())

print("\n--- Abschlussanalyse ---")
print(f"Gesamtpunkte: {len(xs)}")
print(f"Belegte Voxel: {len(occupied_voxels)}")
print(f"Verdichtung: {len(xs) / max(len(occupied_voxels), 1):.2f}")

print("\nTreffer pro Zielpunkt:")
for name in target_names:
    hits = hit_counter[name]
    percent = 100 * hits / total_hits if total_hits else 0
    print(f"  {name:>2}: {hits:6d}  ({percent:5.2f} %)")

plt.ioff()
plt.show()