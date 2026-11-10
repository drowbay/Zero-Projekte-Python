# zero_ion_field_sim.py
# Pydroid 3
#
# Zero Ion Field Simulation
#
# Idee:
# Ionen sind geladene Teilchen.
#
# Positive Ionen  = + Ladung
# Negative Ionen  = - Ladung
#
# Gleiche Ladungen stoßen sich ab.
# Ungleiche Ladungen ziehen sich an.
#
# Vereinfachtes Modell:
# F ~ q1*q2 / r²
#
# Achtung:
# Das ist eine didaktische Simulation, nicht echte Molekulardynamik.

import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


# Farben
BLUE = "#1f77b4"
MAGENTA = "#b23a78"
BLACK = "#111111"
GRAY = "#777777"
BACKGROUND = "#f7fbff"


# Einstellungen
N_IONS = 10
FRAMES = 1200
DT = 0.035

BOX_SIZE = 5.0
K_FORCE = 0.45
DAMPING = 0.985
MIN_R = 0.35

np.random.seed(7)


class Ion:
    def __init__(self, x, y, q):
        self.pos = np.array([x, y], dtype=float)
        self.vel = np.random.uniform(-0.25, 0.25, size=2)
        self.q = q


def make_ions():
    ions = []

    for i in range(N_IONS):
        x = np.random.uniform(-3.5, 3.5)
        y = np.random.uniform(-3.5, 3.5)

        # abwechselnd positive und negative Ionen
        q = 1 if i % 2 == 0 else -1

        ions.append(Ion(x, y, q))

    return ions


def compute_forces(ions):
    forces = [np.array([0.0, 0.0]) for _ in ions]

    for i in range(len(ions)):
        for j in range(i + 1, len(ions)):
            A = ions[i]
            B = ions[j]

            r_vec = B.pos - A.pos
            r = np.linalg.norm(r_vec)

            if r < MIN_R:
                r = MIN_R

            direction = r_vec / r

            # Coulomb-artig:
            # qA*qB > 0 => Abstoßung
            # qA*qB < 0 => Anziehung
            strength = K_FORCE * A.q * B.q / (r * r)

            # Kraft auf A:
            # Bei gleichen Ladungen soll A von B weg.
            F_on_A = -strength * direction

            forces[i] += F_on_A
            forces[j] -= F_on_A

    return forces


def step(ions):
    forces = compute_forces(ions)

    for ion, F in zip(ions, forces):
        ion.vel += F * DT
        ion.vel *= DAMPING
        ion.pos += ion.vel * DT

        # Wandbegrenzung
        for axis in [0, 1]:
            if ion.pos[axis] > BOX_SIZE:
                ion.pos[axis] = BOX_SIZE
                ion.vel[axis] *= -0.75

            if ion.pos[axis] < -BOX_SIZE:
                ion.pos[axis] = -BOX_SIZE
                ion.vel[axis] *= -0.75


def field_at_point(x, y, ions):
    """
    Elektrisches Feld an einem Punkt:
    E ~ q * r_vec / r³
    stark vereinfacht
    """
    E = np.array([0.0, 0.0])

    P = np.array([x, y], dtype=float)

    for ion in ions:
        r_vec = P - ion.pos
        r = np.linalg.norm(r_vec)

        if r < 0.45:
            continue

        E += ion.q * r_vec / (r ** 3)

    return E


# Simulation vorbereiten
ions = make_ions()

fig, ax = plt.subplots(figsize=(8, 8))
fig.patch.set_facecolor(BACKGROUND)
ax.set_facecolor(BACKGROUND)

ax.set_title("Zero Ion Field Simulation — Ionen + Feld", color=BLACK)

ax.set_xlim(-BOX_SIZE - 0.5, BOX_SIZE + 0.5)
ax.set_ylim(-BOX_SIZE - 0.5, BOX_SIZE + 0.5)
ax.set_aspect("equal")

ax.set_xlabel("x", color=BLACK)
ax.set_ylabel("y", color=BLACK)

# Feldgitter
grid_x = np.linspace(-BOX_SIZE, BOX_SIZE, 17)
grid_y = np.linspace(-BOX_SIZE, BOX_SIZE, 17)
GX, GY = np.meshgrid(grid_x, grid_y)

# Anfangsfeld
U = np.zeros_like(GX)
V = np.zeros_like(GY)

quiver = ax.quiver(
    GX, GY, U, V,
    color=GRAY,
    alpha=0.45,
    scale=28
)

# Ionenpunkte
positive_scatter = ax.scatter([], [], s=130, color=BLUE, label="positive Ionen +")
negative_scatter = ax.scatter([], [], s=130, color=MAGENTA, label="negative Ionen -")

# Verbindungslinien für nahe Paare
pair_lines = []
for _ in range(N_IONS * 2):
    line, = ax.plot([], [], color=BLACK, alpha=0.14, linewidth=1.0)
    pair_lines.append(line)

info = ax.text(
    0.02, 0.98, "",
    transform=ax.transAxes,
    va="top",
    color=BLACK
)

ax.legend(loc="lower left")


def update(frame):
    # mehrere kleine Schritte pro Frame
    for _ in range(2):
        step(ions)

    pos_plus = []
    pos_minus = []

    for ion in ions:
        if ion.q > 0:
            pos_plus.append(ion.pos)
        else:
            pos_minus.append(ion.pos)

    pos_plus = np.array(pos_plus)
    pos_minus = np.array(pos_minus)

    if len(pos_plus) > 0:
        positive_scatter.set_offsets(pos_plus)

    if len(pos_minus) > 0:
        negative_scatter.set_offsets(pos_minus)

    # Feld neu berechnen
    U = np.zeros_like(GX)
    V = np.zeros_like(GY)

    for i in range(GX.shape[0]):
        for j in range(GX.shape[1]):
            E = field_at_point(GX[i, j], GY[i, j], ions)

            norm = np.linalg.norm(E)
            if norm > 0:
                E = E / (1 + norm)  # weiche Begrenzung

            U[i, j] = E[0]
            V[i, j] = E[1]

    quiver.set_UVC(U, V)

    # nahe Paare verbinden
    line_index = 0
    total_energy_like = 0.0

    for i in range(len(ions)):
        for j in range(i + 1, len(ions)):
            A = ions[i]
            B = ions[j]

            r_vec = B.pos - A.pos
            r = np.linalg.norm(r_vec)

            if r < 2.0 and line_index < len(pair_lines):
                pair_lines[line_index].set_data(
                    [A.pos[0], B.pos[0]],
                    [A.pos[1], B.pos[1]]
                )
                pair_lines[line_index].set_alpha(0.28)
                line_index += 1

            if r > MIN_R:
                total_energy_like += A.q * B.q / r

    for k in range(line_index, len(pair_lines)):
        pair_lines[k].set_data([], [])

    avg_speed = np.mean([np.linalg.norm(ion.vel) for ion in ions])

    info.set_text(
        "IONEN-RECHNUNG\n\n"
        "Blau    = positive Ionen +\n"
        "Magenta = negative Ionen -\n"
        "Pfeile  = elektrisches Feld\n\n"
        "Regel:\n"
        "+/+ und -/- stoßen ab\n"
        "+/- ziehen an\n\n"
        f"mittlere Geschwindigkeit: {avg_speed:.3f}\n"
        f"Energie-artiger Wert: {total_energy_like:.3f}\n\n"
        "Merksatz:\n"
        "Ionen sind geladene Punkte,\n"
        "die ein Feld erzeugen und darauf reagieren."
    )

    return (
        positive_scatter,
        negative_scatter,
        quiver,
        info,
        *pair_lines
    )


ani = FuncAnimation(
    fig,
    update,
    frames=FRAMES,
    interval=35,
    blit=False
)

plt.show()