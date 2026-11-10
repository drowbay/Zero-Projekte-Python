# ============================================================
# Zero-Lumye Querschnitt-Simulation
# Bulk -> String -> Feld -> Feldenergie
# ------------------------------------------------------------
# Zeigt:
# - 2D Feld
# - 2D Feldenergie
# - horizontalen Querschnitt
# - String-Schwingung
#
# Kerngedanke:
# Null-Amplitude bedeutet nicht automatisch Null-Energie.
# ============================================================

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

np.random.seed(21)

NX = 240
NY = 150
frames = 1200
dt = 0.08

num_bulk_modes = 7
bulk_strength = 0.75
bulk_speed = 0.70

string_y = NY // 2
string_tension = 1.0
string_damping = 0.012

g_bulk_to_string = 0.055
g_string_to_field = 0.038

field_c = 0.82
field_damping = 0.010
field_laplace_strength = 0.17

energy_smoothing = 0.985
cut_y = string_y

x = np.linspace(-1.0, 1.0, NX)
y = np.linspace(-1.0, 1.0, NY)
X, Y = np.meshgrid(x, y)

bulk = np.zeros((NY, NX), dtype=float)
string = np.zeros(NX, dtype=float)
string_prev = np.zeros_like(string)
field = np.zeros((NY, NX), dtype=float)
field_prev = np.zeros_like(field)
field_energy = np.zeros_like(field)


def laplacian_2d(a):
    out = np.zeros_like(a)
    out[1:-1, 1:-1] = (
        a[1:-1, 2:] + a[1:-1, :-2] +
        a[2:, 1:-1] + a[:-2, 1:-1] -
        4.0 * a[1:-1, 1:-1]
    )
    return out


def laplacian_1d(a):
    out = np.zeros_like(a)
    out[1:-1] = a[2:] - 2.0 * a[1:-1] + a[:-2]
    return out


def make_bulk(t):
    b = np.zeros((NY, NX), dtype=float)
    for k in range(1, num_bulk_modes + 1):
        angle = 0.7 * k
        kx = np.cos(angle) * (1.2 + 0.25 * k)
        ky = np.sin(angle) * (1.1 + 0.20 * k)
        freq = bulk_speed * (0.25 + 0.09 * k)
        phase = 2.0 * np.pi * (kx * X + ky * Y - freq * t)
        b += (bulk_strength / k) * np.sin(phase + 0.6 * k)
    envelope = np.exp(-2.2 * (X**2 + Y**2))
    return b * envelope


def inject_string_into_field(field_state, string_state):
    injection = np.zeros_like(field_state)
    for dy in range(-3, 4):
        yy = string_y + dy
        if 0 <= yy < NY:
            weight = np.exp(-(dy * dy) / (2.0 * 2.0**2))
            injection[yy, :] += weight * string_state
    return field_state + g_string_to_field * injection


def compute_field_energy(field_state, old_field_state):
    kinetic_like = (field_state - old_field_state) ** 2
    gradient_like = laplacian_2d(field_state) ** 2
    return kinetic_like + 0.35 * gradient_like


fig, axes = plt.subplots(2, 2, figsize=(14, 9))
fig.suptitle("Querschnitt: Bulk -> String -> Feld -> Feldenergie", fontsize=14)

ax_field = axes[0, 0]
ax_energy = axes[0, 1]
ax_cut = axes[1, 0]
ax_string = axes[1, 1]

field_img = ax_field.imshow(field, cmap="RdBu_r", vmin=-1.0, vmax=1.0, origin="lower", interpolation="bilinear")
ax_field.axhline(cut_y, color="black", linewidth=1.2, alpha=0.8)
ax_field.set_title("2D sichtbares Feld")
ax_field.axis("off")

energy_img = ax_energy.imshow(field_energy, cmap="inferno", vmin=0.0, vmax=0.08, origin="lower", interpolation="bilinear")
ax_energy.axhline(cut_y, color="white", linewidth=1.2, alpha=0.8)
ax_energy.set_title("2D Feldenergie / Resonanz")
ax_energy.axis("off")

field_cut_line, = ax_cut.plot(x, field[cut_y, :], linewidth=2.4, label="Feldamplitude")
energy_cut_line, = ax_cut.plot(x, field_energy[cut_y, :], linewidth=2.0, label="Feldenergie")
ax_cut.axhline(0.0, color="gray", linewidth=1.0, alpha=0.7)
ax_cut.set_xlim(-1.0, 1.0)
ax_cut.set_ylim(-1.2, 1.2)
ax_cut.set_title(f"Horizontaler Querschnitt bei y-Index = {cut_y}")
ax_cut.set_xlabel("x")
ax_cut.set_ylabel("Amplitude / Energie")
ax_cut.grid(True, alpha=0.25)
ax_cut.legend(loc="upper right")

string_line, = ax_string.plot(x, string, linewidth=2.5, label="String")
ax_string.set_xlim(-1.0, 1.0)
ax_string.set_ylim(-1.2, 1.2)
ax_string.set_title("String-artige Schwingung")
ax_string.set_xlabel("String-Koordinate")
ax_string.set_ylabel("Amplitude")
ax_string.grid(True, alpha=0.25)
ax_string.legend(loc="upper right")

info = fig.text(0.02, 0.02, "", fontsize=10, family="monospace")


def update(frame):
    global bulk, string, string_prev, field, field_prev, field_energy

    t = frame * dt

    bulk = make_bulk(t)

    drive = bulk[string_y, :]
    string_lap = laplacian_1d(string)
    string_next = (
        2.0 * string
        - string_prev
        + 0.18 * string_tension * string_lap
        + g_bulk_to_string * drive
    )
    string_next *= (1.0 - string_damping)
    string_next[0] = 0.0
    string_next[-1] = 0.0

    string_prev = string
    string = string_next

    field_lap = laplacian_2d(field)
    field_next = (
        2.0 * field
        - field_prev
        + field_laplace_strength * (field_c ** 2) * field_lap
    )
    field_next *= (1.0 - field_damping)
    field_next = inject_string_into_field(field_next, string)

    old_field = field.copy()
    field_prev = field
    field = field_next

    local_energy = compute_field_energy(field, old_field)
    field_energy = energy_smoothing * field_energy + (1.0 - energy_smoothing) * local_energy

    cut_field = field[cut_y, :]
    cut_energy = field_energy[cut_y, :]

    field_img.set_data(field)
    energy_img.set_data(field_energy)
    field_cut_line.set_ydata(cut_field)
    energy_cut_line.set_ydata(cut_energy)
    string_line.set_ydata(string)

    field_lim = max(0.18, np.percentile(np.abs(field), 99.0))
    energy_max = max(0.015, np.percentile(field_energy, 99.5))
    cut_energy_max = max(0.08, np.percentile(cut_energy, 99.5) * 1.2)

    field_img.set_clim(-field_lim, field_lim)
    energy_img.set_clim(0.0, energy_max)

    ax_cut.set_ylim(
        min(-1.15, np.min(cut_field) * 1.2),
        max(1.15, np.max([np.max(np.abs(cut_field)) * 1.2, cut_energy_max]))
    )

    zero_crossings = np.where(np.diff(np.sign(cut_field)) != 0)[0]
    num_zero_crossings = len(zero_crossings)

    info.set_text(
        f"Frame={frame:04d} | cut_y={cut_y} | Feldleistung={np.mean(field**2):.6f} | "
        f"sichtbare Feldenergie={np.mean(field_energy):.6f}\n"
        f"Nullstellen im Querschnitt={num_zero_crossings} | "
        f"Auch wenn die Amplitude lokal durch 0 geht, kann Energie dort/nahe dort weiter da sein.\n"
        f"Grund: Energie haengt nicht nur von der Auslenkung ab, sondern auch von zeitlicher Aenderung und Feldkruemmung."
    )

    return field_img, energy_img, field_cut_line, energy_cut_line, string_line, info


ani = FuncAnimation(fig, update, frames=frames, interval=30, blit=False)
plt.tight_layout()
plt.show()
