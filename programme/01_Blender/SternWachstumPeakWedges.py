import random
import math
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401


# =========================================================
# Geometrie
# =========================================================
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


def make_peak_wedges(base_points, wedge_length=18, wedge_width=10, z_lift=8):
    """
    Erzeugt für jede äußere Sternspitze 3 Zusatzpunkte:
    - 1 Punkt weiter nach außen
    - 2 seitliche Keilpunkte
    Nur die äußeren Peaks (Index 0,2,4,6,8).
    """
    wedges = []

    for i in range(0, 10, 2):
        x, y = base_points[i]

        length = math.hypot(x, y)
        if length == 0:
            continue

        # Richtung vom Zentrum zur Spitze
        ux, uy = x / length, y / length

        # Senkrechte Richtung für Breite
        px, py = -uy, ux

        # Keilspitze weiter außen
        tip = (x + ux * wedge_length, y + uy * wedge_length, z_lift)

        # Zwei seitliche Punkte
        left = (
            x + ux * (wedge_length * 0.5) + px * wedge_width,
            y + uy * (wedge_length * 0.5) + py * wedge_width,
            z_lift * 0.6,
        )
        right = (
            x + ux * (wedge_length * 0.5) - px * wedge_width,
            y + uy * (wedge_length * 0.5) - py * wedge_width,
            z_lift * 0.6,
        )

        wedges.extend([tip, left, right])

    return wedges


def growth_factor(step, max_steps, start=0.25, end=1.0):
    """Langsames Wachstum der Geometrie."""
    t = min(step / max_steps, 1.0)
    return start + (end - start) * (1 - math.exp(-4 * t)) / (1 - math.exp(-4))


# =========================================================
# Theorie-Ebenen
# =========================================================
def energy_metric(x, y, z):
    """
    Energie hier als Abstand vom Ursprung.
    Kein physikalisch exaktes Modell, sondern ein Spielwert:
    viel Auslenkung = mehr 'Energie'.
    """
    return math.sqrt(x * x + y * y + z * z)


def voxel_index(x, y, z, voxel_size):
    """Ordnet einen Punkt einer Raumzelle zu."""
    return (
        int(x // voxel_size),
        int(y // voxel_size),
        int(z // voxel_size),
    )


# =========================================================
# Parameter
# =========================================================
TOTAL_STEPS = 90000
OUTER_RADIUS = 100
INNER_RADIUS = 40
TOP_HEIGHT = 120

USE_WEDGES = True
USE_GROWTH = True

# Ordnung/Chaos-Regel
# 2 = streng, klar
# >2 = organischer, diffuser
FACTOR_CHOICES = [2, 2, 2.2, 2.5]

# Wedges stärker gewichten?
WEDGE_WEIGHT = 2

# Emergenz-/Feldraster
VOXEL_SIZE = 8

# Update-Geschwindigkeit
DRAW_EVERY = 400


# =========================================================
# Plot
# =========================================================
plt.ion()
fig = plt.figure(figsize=(11, 8))
ax = fig.add_subplot(111, projection="3d")

# Punktewolke
scatter = ax.scatter([], [], [], s=1, c=[], cmap="plasma")

# Zielpunkte-Schicht separat, damit sie sauber neu gezeichnet werden kann
target_scatter = ax.scatter([], [], [], s=25, alpha=0.8)

ax.set_xlim(-140, 140)
ax.set_ylim(-140, 140)
ax.set_zlim(-20, 160)
ax.set_box_aspect((1, 1, 1))
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")
ax.set_title("3D Stern Wachstum + Peak Wedges + Emergenz")

# Theorie-Text links oben
theory_text = fig.text(
    0.02,
    0.95,
    "",
    fontsize=10,
    verticalalignment="top",
    family="monospace",
)


# =========================================================
# Startzustand
# =========================================================
x, y, z = 0.0, 0.0, 0.0
xs, ys, zs = [], [], []
colors = []

occupied_voxels = set()
field_counter = {}

energy_values = []
dominant_voxel = None

print("Wachstumsmodus mit Peak-Wedges + Emergenz läuft ... STRG+C zum Beenden")


# =========================================================
# Simulation
# =========================================================
try:
    for i in range(TOTAL_STEPS):
        g = growth_factor(i, TOTAL_STEPS) if USE_GROWTH else 1.0

        # -------------------------
        # Lage: aktuelle Zielgeometrie
        # -------------------------
        base_points_2d = star_points_2d(
            outer_radius=OUTER_RADIUS * g,
            inner_radius=INNER_RADIUS * g
        )

        base_targets = [(bx, by, 0) for bx, by in base_points_2d]
        O = (0, 0, TOP_HEIGHT * g)

        targets = base_targets + [O]

        if USE_WEDGES:
            wedge_targets = make_peak_wedges(
                base_points_2d,
                wedge_length=18 * g,
                wedge_width=10 * g,
                z_lift=10 * g
            )
            # Peak wedges extra gewichten
            targets += wedge_targets * WEDGE_WEIGHT

        # -------------------------
        # Zufälliges Ziel
        # -------------------------
        px, py, pz = random.choice(targets)

        # -------------------------
        # Ordnung/Chaos-Regel
        # -------------------------
        factor = random.choice(FACTOR_CHOICES)

        # -------------------------
        # Bewegung / Energie -> Lage
        # -------------------------
        x = (x + px) / factor
        y = (y + py) / factor
        z = (z + pz) / factor

        xs.append(x)
        ys.append(y)
        zs.append(z)
        colors.append(i)

        # -------------------------
        # Energie-Metrik
        # -------------------------
        energy = energy_metric(x, y, z)
        energy_values.append(energy)

        # -------------------------
        # Feld: belegte Raumzellen
        # -------------------------
        vox = voxel_index(x, y, z, VOXEL_SIZE)
        occupied_voxels.add(vox)
        field_counter[vox] = field_counter.get(vox, 0) + 1

        # dominanteste Feldzelle
        dominant_voxel = max(field_counter, key=field_counter.get)

        # -------------------------
        # Draw / Emergenz sichtbar machen
        # -------------------------
        if i % DRAW_EVERY == 0 and i > 0:
            scatter._offsets3d = (xs, ys, zs)
            scatter.set_array(np.array(colors))

            # echte Zielpunkte ohne Gewichtungs-Duplikate nur fürs Anzeigen
            visible_targets = base_targets + [O]
            if USE_WEDGES:
                visible_targets += make_peak_wedges(
                    base_points_2d,
                    wedge_length=18 * g,
                    wedge_width=10 * g,
                    z_lift=10 * g
                )

            tx = [p[0] for p in visible_targets]
            ty = [p[1] for p in visible_targets]
            tz = [p[2] for p in visible_targets]
            target_scatter._offsets3d = (tx, ty, tz)

            # -------------------------
            # Theorie-Auswertung
            # -------------------------
            avg_energy = float(np.mean(energy_values[-1000:])) if energy_values else 0.0
            density = len(xs) / max(len(occupied_voxels), 1)

            # Information: wie viele unterschiedliche Zellen werden genutzt?
            information = len(occupied_voxels)

            # Ordnung: viele Punkte in wenigen Voxeln = hohe Verdichtung
            order = density

            theory_text.set_text(
                "Theorie-Ebenen\n"
                "--------------\n"
                f"Energie     : {avg_energy:8.2f}\n"
                f"Lage        : ({x:7.2f}, {y:7.2f}, {z:7.2f})\n"
                f"Feld        : {len(occupied_voxels):8d} Voxel\n"
                f"Emergenz    : sichtbare Cluster / Attraktor\n"
                f"Information : {information:8d}\n"
                f"Ordnung     : {order:8.2f}\n"
                f"Wachstum    : {g:8.2f}\n"
                f"Dominant    : {dominant_voxel}"
            )

            ax.set_title(
                f"3D Stern Wachstum + Peak Wedges | "
                f"Schritt {i} | Wachstum {g:.2f} | Ordnung {order:.2f}"
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

print("\n--- Abschlussanalyse ---")
print(f"Gesamtpunkte : {len(xs)}")
print(f"Belegte Voxel: {len(occupied_voxels)}")
print(f"Ordnung      : {density_final:.2f}")
print(f"Energie Ø    : {avg_energy_total:.2f}")
print(f"Dominant Vox : {dominant_voxel}")

plt.ioff()
plt.show()