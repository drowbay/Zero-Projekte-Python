import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# -----------------------------
# Setup
# -----------------------------
WIDTH, HEIGHT = 10, 10
PARTICLE_COUNT = 35

ATTRACTION_RADIUS = 3.0
REPULSION_RADIUS = 0.8
DANGER_RADIUS = 0.35

ATTRACTION_FORCE = 0.004
REPULSION_FORCE = 0.04
FRICTION = 0.96

np.random.seed(7)

positions = np.random.rand(PARTICLE_COUNT, 2) * [WIDTH, HEIGHT]
velocities = (np.random.rand(PARTICLE_COUNT, 2) - 0.5) * 0.05

fig, ax = plt.subplots(figsize=(8, 8))


def distance(a, b):
    return np.linalg.norm(a - b)


def update(frame):
    global positions, velocities

    forces = np.zeros_like(positions)
    danger_events = []

    for i in range(PARTICLE_COUNT):
        for j in range(i + 1, PARTICLE_COUNT):
            delta = positions[j] - positions[i]
            dist = np.linalg.norm(delta)

            if dist == 0:
                continue

            direction = delta / dist

            # Nahbereich: starke Abstoßung
            if dist < REPULSION_RADIUS:
                strength = REPULSION_FORCE * (REPULSION_RADIUS - dist)
                forces[i] -= direction * strength
                forces[j] += direction * strength

            # Mittelbereich: Anziehung
            elif dist < ATTRACTION_RADIUS:
                strength = ATTRACTION_FORCE * (ATTRACTION_RADIUS - dist)
                forces[i] += direction * strength
                forces[j] -= direction * strength

            # Kritische Zone
            if dist < DANGER_RADIUS:
                danger_events.append((i, j, dist))

    velocities += forces
    velocities *= FRICTION
    positions += velocities

    # Wände reflektieren
    for i in range(PARTICLE_COUNT):
        if positions[i, 0] < 0 or positions[i, 0] > WIDTH:
            velocities[i, 0] *= -1
        if positions[i, 1] < 0 or positions[i, 1] > HEIGHT:
            velocities[i, 1] *= -1

    positions[:, 0] = np.clip(positions[:, 0], 0, WIDTH)
    positions[:, 1] = np.clip(positions[:, 1], 0, HEIGHT)

    ax.clear()
    ax.set_xlim(0, WIDTH)
    ax.set_ylim(0, HEIGHT)
    ax.set_aspect("equal")
    ax.set_title(
        f"Anziehung / Abstoßung / Nähe-Analyse | Kritische Kontakte: {len(danger_events)}"
    )

    # Radien um ein Beispielteilchen anzeigen
    focus = 0
    fx, fy = positions[focus]

    attraction_circle = plt.Circle(
        (fx, fy), ATTRACTION_RADIUS, fill=False, linestyle="--", linewidth=1
    )
    repulsion_circle = plt.Circle(
        (fx, fy), REPULSION_RADIUS, fill=False, linestyle="-", linewidth=2
    )
    danger_circle = plt.Circle(
        (fx, fy), DANGER_RADIUS, fill=False, linestyle="-", linewidth=3
    )

    ax.add_patch(attraction_circle)
    ax.add_patch(repulsion_circle)
    ax.add_patch(danger_circle)

    # Verbindungslinien je nach Effekt
    for i in range(PARTICLE_COUNT):
        for j in range(i + 1, PARTICLE_COUNT):
            dist = distance(positions[i], positions[j])

            if dist < DANGER_RADIUS:
                ax.plot(
                    [positions[i, 0], positions[j, 0]],
                    [positions[i, 1], positions[j, 1]],
                    linewidth=2,
                )
            elif dist < REPULSION_RADIUS:
                ax.plot(
                    [positions[i, 0], positions[j, 0]],
                    [positions[i, 1], positions[j, 1]],
                    linewidth=1,
                    linestyle="-",
                )
            elif dist < ATTRACTION_RADIUS:
                ax.plot(
                    [positions[i, 0], positions[j, 0]],
                    [positions[i, 1], positions[j, 1]],
                    linewidth=0.5,
                    linestyle="--",
                )

    ax.scatter(positions[:, 0], positions[:, 1], s=45)

    # Fokus-Teilchen hervorheben
    ax.scatter([fx], [fy], s=120)

    # Legende als Text
    ax.text(
        0.2,
        9.6,
        "Kreise um Fokus-Teilchen:\n"
        "-- außen = Anziehung\n"
        "mittlerer Kreis = Abstoßung\n"
        "innerer Kreis = kritische Nähe",
        fontsize=9,
        verticalalignment="top",
    )


ani = FuncAnimation(fig, update, frames=400, interval=30)
plt.show()