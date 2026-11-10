import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

np.random.seed(7)

# -----------------------------
# PARAMETER
# -----------------------------
space_size = 24.0
frames = 900
dt = 0.035

# Schwarzes Loch / Horizont
BLACK_HOLE_MASS = 520.0
HORIZON_RADIUS = 3.0
NEAR_HORIZON_RADIUS = 5.2
SPAWN_RADIUS = 4.1

# Hawking-Partikel
max_pairs = 160
spawn_rate = 3
particle_lifetime = 260

# Bewegung
escape_speed = 0.13
infall_speed = 0.16
jitter_strength = 0.025

# -----------------------------
# FELD / HORIZONT-HINTERGRUND
# -----------------------------
grid_size = 160
x = np.linspace(-space_size, space_size, grid_size)
y = np.linspace(-space_size, space_size, grid_size)
X, Y = np.meshgrid(x, y)
R = np.sqrt(X**2 + Y**2) + 1e-9

def normalize(arr):
    arr = np.array(arr, dtype=float)
    arr = arr - np.min(arr)
    return arr / (np.max(arr) + 1e-9)

# Nähe zum Horizont als Glow
horizon_glow = np.exp(-((R - HORIZON_RADIUS) ** 2) / 1.1)

# Krümmungs-/Nähefeld
gravity_well = normalize(1 / (R + 0.5))

# Hawking-Zone = Ring knapp außerhalb des Horizonts
hawking_zone = normalize(
    0.65 * horizon_glow +
    0.35 * np.exp(-((R - NEAR_HORIZON_RADIUS) ** 2) / 5.0)
)

background = normalize(
    0.55 * gravity_well +
    0.45 * hawking_zone
)

# -----------------------------
# PARTIKEL-SPEICHER
# -----------------------------
particles = []

def spawn_pair():
    angle = np.random.uniform(0, 2*np.pi)

    # Paar entsteht knapp am Horizont
    r = SPAWN_RADIUS + np.random.normal(0, 0.25)
    x0 = r * np.cos(angle)
    y0 = r * np.sin(angle)

    radial = np.array([np.cos(angle), np.sin(angle)])
    tangent = np.array([-np.sin(angle), np.cos(angle)])

    # entkommendes Teilchen
    out_v = escape_speed * radial + np.random.normal(0, jitter_strength) * tangent

    # hineinfallendes Partnerteilchen
    in_v = -infall_speed * radial + np.random.normal(0, jitter_strength) * tangent

    return [
        {
            "pos": np.array([x0, y0], dtype=float),
            "vel": out_v,
            "kind": "escape",
            "life": particle_lifetime,
            "trail": []
        },
        {
            "pos": np.array([x0, y0], dtype=float),
            "vel": in_v,
            "kind": "infall",
            "life": particle_lifetime,
            "trail": []
        }
    ]

# -----------------------------
# FIGURE
# -----------------------------
fig, ax = plt.subplots(figsize=(9, 9), facecolor="black")
ax.set_facecolor("black")

def draw_static():
    ax.imshow(
        background,
        extent=[-space_size, space_size, -space_size, space_size],
        origin="lower",
        cmap="magma",
        alpha=0.65
    )

    # Ereignishorizont
    horizon = plt.Circle(
        (0, 0), HORIZON_RADIUS,
        fill=False,
        color="red",
        linewidth=3.0,
        alpha=0.95
    )

    # Hawking-Zone / Pair-Creation-Zone
    near = plt.Circle(
        (0, 0), NEAR_HORIZON_RADIUS,
        fill=False,
        color="deepskyblue",
        linestyle="--",
        linewidth=1.4,
        alpha=0.8
    )

    ax.add_patch(horizon)
    ax.add_patch(near)

    # Schwarzes Loch
    ax.scatter([0], [0], s=420, c="black", edgecolors="white", linewidths=1.2, alpha=1.0)

# -----------------------------
# UPDATE
# -----------------------------
def update(frame):
    global particles

    # neue virtuelle Paare erzeugen
    for _ in range(spawn_rate):
        if len(particles) < max_pairs:
            particles.extend(spawn_pair())

    # Teilchen bewegen
    alive = []
    escaped_count = 0
    infall_count = 0
    near_count = 0

    for p in particles:
        p["trail"].append(p["pos"].copy())
        if len(p["trail"]) > 22:
            p["trail"].pop(0)

        r = np.linalg.norm(p["pos"]) + 1e-9
        radial = p["pos"] / r

        # kleine gravitative Krümmung nach innen
        grav_pull = -0.018 * radial / (r**1.15)

        if p["kind"] == "escape":
            # entkommende Partikel bekommen leichten outward drift
            p["vel"] += grav_pull * 0.25
            p["vel"] += 0.0025 * radial
        else:
            # fallende Partner stärker nach innen
            p["vel"] += grav_pull * 1.8

        p["pos"] += p["vel"] * dt * 10.0
        p["life"] -= 1

        r_new = np.linalg.norm(p["pos"])

        if HORIZON_RADIUS < r_new < NEAR_HORIZON_RADIUS:
            near_count += 1

        if p["kind"] == "infall" and r_new <= HORIZON_RADIUS:
            infall_count += 1
            continue

        if p["kind"] == "escape" and r_new > space_size:
            escaped_count += 1
            continue

        if p["life"] > 0:
            alive.append(p)

    particles = alive

    # Zeichnen
    ax.clear()
    ax.set_facecolor("black")
    ax.set_xlim(-space_size, space_size)
    ax.set_ylim(-space_size, space_size)
    ax.set_aspect("equal")
    ax.axis("off")

    draw_static()

    # Verbindungslinien / Trails
    for p in particles:
        if len(p["trail"]) > 1:
            trail = np.array(p["trail"])
            if p["kind"] == "escape":
                color = "white"
                alpha = 0.55
            else:
                color = "violet"
                alpha = 0.35

            ax.plot(
                trail[:, 0],
                trail[:, 1],
                color=color,
                linewidth=0.8,
                alpha=alpha
            )

    # Partikel zeichnen
    escape_pos = np.array([p["pos"] for p in particles if p["kind"] == "escape"])
    infall_pos = np.array([p["pos"] for p in particles if p["kind"] == "infall"])

    if len(escape_pos) > 0:
        ax.scatter(
            escape_pos[:, 0],
            escape_pos[:, 1],
            s=18,
            c="white",
            alpha=0.9,
            label="entkommende Hawking-Strahlung"
        )

    if len(infall_pos) > 0:
        ax.scatter(
            infall_pos[:, 0],
            infall_pos[:, 1],
            s=14,
            c="violet",
            alpha=0.65,
            label="Partnerteilchen fällt ein"
        )

    ax.set_title(
        "MS Hawking-Strahlung Näheanalyse | Ereignishorizont + Paarbildung\n"
        f"aktive Quantenpaare: {len(particles)//2} | nahe Horizontzone: {near_count}",
        color="white",
        fontsize=12
    )

    ax.text(
        -23.2,
        22.6,
        "Hawking-Modell:\n"
        "rot = Ereignishorizont\n"
        "-- blau = Pair-Creation-Zone\n"
        "weiß = entkommendes Teilchen\n"
        "violett = Partner fällt hinein\n\n"
        "~0/~1 = virtuelle Vorzustände\n"
        "0/1 = sichtbare Strahlung\n\n"
        "Hinweis:\n"
        "Visualisierung / Denkmodell,\n"
        "keine exakte Quantengravitation.",
        fontsize=9,
        color="white",
        va="top",
        bbox=dict(facecolor="black", alpha=0.62, edgecolor="gray")
    )

ani = animation.FuncAnimation(fig, update, frames=frames, interval=30)
plt.show()