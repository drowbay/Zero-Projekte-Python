import random
import math
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401


def star_points_2d(outer_radius=100, inner_radius=40):
    """Erzeugt 10 Punkte eines 5-Zacken-Sterns in 2D."""
    pts = []
    for i in range(10):
        angle_deg = 90 + i * 36  # startet oben
        angle_rad = math.radians(angle_deg)
        r = outer_radius if i % 2 == 0 else inner_radius
        x = r * math.cos(angle_rad)
        y = r * math.sin(angle_rad)
        pts.append((x, y))
    return pts


# Stern-Grundfläche
base_points = star_points_2d(outer_radius=100, inner_radius=40)

# Punkt O "dahinter / darüber" im Raum
O = (0, 0, 120)

# Alle Zielpunkte für das Chaos-Game:
# 10 Sternpunkte unten + 1 Spitze oben
targets = [(x, y, 0) for x, y in base_points] + [O]

# Startpunkt irgendwo im Raum
x, y, z = 0.0, 0.0, 0.0

xs, ys, zs = [], [], []

# Plot vorbereiten
plt.ion()
fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111, projection="3d")

scatter = ax.scatter([], [], [], s=1)

# Zielpunkte sichtbar machen
tx = [p[0] for p in targets]
ty = [p[1] for p in targets]
tz = [p[2] for p in targets]
ax.scatter(tx, ty, tz, s=50)

ax.set_xlim(-120, 120)
ax.set_ylim(-120, 120)
ax.set_zlim(-20, 140)
ax.set_box_aspect((1, 1, 1))

ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")
ax.set_title("3D Stern Chaos Live")

print("3D Live-Plot läuft ... STRG+C zum Beenden")

try:
    for i in range(80000):
        px, py, pz = random.choice(targets)

        # Halbierungs-Prinzip im 3D-Raum
        x = (x + px) / 2
        y = (y + py) / 2
        z = (z + pz) / 2

        xs.append(x)
        ys.append(y)
        zs.append(z)

        # Nur alle paar Schritte neu zeichnen, sonst wird's lahm
        if i % 200 == 0:
            scatter._offsets3d = (xs, ys, zs)
            plt.draw()
            plt.pause(0.001)

except KeyboardInterrupt:
    print("\nBeendet 👋")

plt.ioff()
plt.show()