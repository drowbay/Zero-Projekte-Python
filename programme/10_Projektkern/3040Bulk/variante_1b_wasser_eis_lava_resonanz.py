# ============================================================
# Zero-Lumÿe Variante 1B:
# Wasser + Eis + Lava + Resonanz + Materialgrenze
# ------------------------------------------------------------
# Anschauliches Lehr-/Ideenmodell:
# - 2D-Wellengleichung als Wasser-/Druckfeld
# - Eis, Lava und Fels haben unterschiedliche Wellengeschwindigkeit/Dämpfung
# - Temperaturfeld mit einfacher Wärmeleitung
# - einfache Phasenübergänge: Eis -> Wasser, Lava -> Fels
#
# Kein vollständiger Navier-Stokes-/Thermodynamik-Solver.
# ============================================================

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.colors import ListedColormap, BoundaryNorm

np.random.seed(7)

NX = 240
NY = 140
frames = 1400

source_x = 35
source_y = NY // 2 + 13
source_frequency = 0.105
source_strength = 0.95

laplace_strength = 0.22

WATER = 0
ICE = 1
LAVA = 2
ROCK = 3

phase = np.zeros((NY, NX), dtype=np.int32)
u = np.zeros((NY, NX), dtype=float)
u_prev = np.zeros_like(u)
resonance = np.zeros_like(u)
temperature = np.zeros_like(u)

# ------------------------------------------------------------
# Geometrie: gestufte Felsgrenze, Eisblock, Lava-Ader
# ------------------------------------------------------------
for x in range(NX):
    if x < 82:
        boundary = NY + 10
    elif x < 136:
        boundary = int(96 - 0.28 * (x - 82))
    elif x < 181:
        step = ((x - 136) // 7)
        boundary = 80 + step * 4
    else:
        boundary = 94

    if 0 <= boundary < NY:
        phase[boundary:, x] = ROCK

phase[79:87, 134:149] = ROCK
phase[87:96, 149:164] = ROCK
phase[96:105, 164:179] = ROCK

phase[75:111, 198:224] = WATER
phase[106:, 224:] = ROCK

phase[82:123, 58:112] = ICE
phase[92:130, 112:136] = ICE

for x in range(58, 136):
    wobble = int(5 * np.sin(x * 0.19))
    phase[120 + wobble:130, x] = WATER

phase[42:72, 168:214] = LAVA
phase[54:86, 202:230] = LAVA

for x in range(160, 230):
    center = int(58 + 8 * np.sin(x * 0.11))
    phase[max(0, center-7):min(NY, center+7), x] = LAVA

temperature[phase == WATER] = 0.35
temperature[phase == ICE] = 0.05
temperature[phase == LAVA] = 1.00
temperature[phase == ROCK] = 0.25


def property_maps(phase):
    c_map = np.zeros_like(phase, dtype=float)
    d_map = np.zeros_like(phase, dtype=float)

    c_map[phase == WATER] = 1.00
    d_map[phase == WATER] = 0.006

    c_map[phase == ICE] = 0.72
    d_map[phase == ICE] = 0.014

    c_map[phase == LAVA] = 0.46
    d_map[phase == LAVA] = 0.055

    c_map[phase == ROCK] = 0.34
    d_map[phase == ROCK] = 0.040

    return c_map, d_map


def laplacian(a):
    out = np.zeros_like(a)
    out[1:-1, 1:-1] = (
        a[1:-1, 2:] +
        a[1:-1, :-2] +
        a[2:, 1:-1] +
        a[:-2, 1:-1] -
        4.0 * a[1:-1, 1:-1]
    )
    return out


def add_source(field, frame):
    pulse = source_strength * np.sin(2.0 * np.pi * source_frequency * frame)
    yy, xx = np.ogrid[:NY, :NX]
    r2 = (xx - source_x) ** 2 + (yy - source_y) ** 2
    source_shape = np.exp(-r2 / (2.0 * 5.0 ** 2))
    field += pulse * source_shape
    return field


def diffuse_temperature(temp, phase, resonance):
    temp_lap = laplacian(temp)

    diff = np.zeros_like(temp)
    diff[phase == WATER] = 0.035
    diff[phase == ICE] = 0.015
    diff[phase == LAVA] = 0.020
    diff[phase == ROCK] = 0.012

    temp = temp + diff * temp_lap
    temp[phase == LAVA] += 0.004
    temp[phase == ICE] -= 0.0012
    temp += 0.003 * np.clip(resonance, 0.0, 1.0)
    return np.clip(temp, 0.0, 1.2)


def phase_transitions(phase, temp):
    new_phase = phase.copy()
    new_phase[(phase == ICE) & (temp > 0.32)] = WATER
    new_phase[(phase == LAVA) & (temp < 0.52)] = ROCK
    return new_phase


def make_phase_rgba(phase):
    rgba = np.zeros((NY, NX, 4), dtype=float)
    rgba[phase == WATER] = [0.05, 0.18, 0.45, 0.35]
    rgba[phase == ICE]   = [0.55, 0.90, 1.00, 0.55]
    rgba[phase == LAVA]  = [1.00, 0.22, 0.02, 0.65]
    rgba[phase == ROCK]  = [0.20, 0.20, 0.20, 0.60]
    return rgba


fig, axes = plt.subplots(2, 2, figsize=(14, 8))
fig.suptitle("Variante 1B: Wasser + Eis + Lava + Resonanz + Materialgrenze", fontsize=14)

ax_wave = axes[0, 0]
ax_phase = axes[0, 1]
ax_res = axes[1, 0]
ax_temp = axes[1, 1]

wave_img = ax_wave.imshow(
    u, cmap="RdBu_r", vmin=-1.0, vmax=1.0,
    origin="lower", interpolation="bilinear"
)
phase_overlay = ax_wave.imshow(make_phase_rgba(phase), origin="lower", interpolation="nearest")
ax_wave.set_title("Wellen-/Druckfeld + Material-Overlay")
ax_wave.axis("off")

phase_cmap = ListedColormap(["#0b2c6b", "#a8ecff", "#ff3300", "#404040"])
phase_norm = BoundaryNorm([-0.5, 0.5, 1.5, 2.5, 3.5], phase_cmap.N)
phase_img = ax_phase.imshow(phase, cmap=phase_cmap, norm=phase_norm, origin="lower", interpolation="nearest")
ax_phase.set_title("Phasenkarte: Wasser / Eis / Lava / Fels")
ax_phase.axis("off")

res_img = ax_res.imshow(
    resonance, cmap="inferno", vmin=0.0, vmax=0.12,
    origin="lower", interpolation="bilinear"
)
ax_res.set_title("Resonanz / lokale Schwingungsenergie")
ax_res.axis("off")

temp_img = ax_temp.imshow(
    temperature, cmap="magma", vmin=0.0, vmax=1.05,
    origin="lower", interpolation="bilinear"
)
ax_temp.set_title("Temperaturfeld / Wärmeleitung")
ax_temp.axis("off")

for ax in [ax_wave, ax_phase, ax_res, ax_temp]:
    ax.plot(source_x, source_y, "wo", markersize=5, markeredgecolor="black")
    ax.text(source_x + 4, source_y + 4, "Quelle", color="white", fontsize=8)

fig.text(
    0.02, 0.965,
    "Wasser=blau | Eis=hellblau | Lava=rot | Fels=grau",
    fontsize=9, family="monospace"
)

info = fig.text(0.02, 0.02, "", fontsize=10, family="monospace")


def update(frame):
    global u, u_prev, resonance, temperature, phase

    c_map, damping_map = property_maps(phase)

    lap = laplacian(u)
    u_next = 2.0 * u - u_prev + laplace_strength * (c_map ** 2) * lap
    u_next *= (1.0 - damping_map)
    u_next = add_source(u_next, frame)

    lava_mask = phase == LAVA
    lava_noise = np.zeros_like(u_next)
    if np.any(lava_mask):
        lava_noise[lava_mask] = 0.012 * np.random.normal(0.0, 1.0, np.count_nonzero(lava_mask))
    u_next += lava_noise

    u_prev = u
    u = u_next

    local_energy = (u - u_prev) ** 2 + 0.35 * (laplacian(u) ** 2)
    resonance = 0.985 * resonance + 0.015 * local_energy

    temperature = diffuse_temperature(temperature, phase, resonance)

    if frame % 8 == 0:
        phase = phase_transitions(phase, temperature)
        temperature[phase == ICE] = np.minimum(temperature[phase == ICE], 0.20)
        temperature[phase == LAVA] = np.maximum(temperature[phase == LAVA], 0.75)

    wave_img.set_data(u)
    phase_overlay.set_data(make_phase_rgba(phase))
    phase_img.set_data(phase)
    res_img.set_data(resonance)
    temp_img.set_data(temperature)

    res_img.set_clim(0.0, max(0.04, np.percentile(resonance, 99.5)))
    temp_img.set_clim(0.0, 1.05)

    water_count = np.count_nonzero(phase == WATER)
    ice_count = np.count_nonzero(phase == ICE)
    lava_count = np.count_nonzero(phase == LAVA)
    rock_count = np.count_nonzero(phase == ROCK)

    info.set_text(
        f"Frame={frame:04d} | Temp avg={np.mean(temperature):.3f} | Resonanz avg={np.mean(resonance):.4f}\n"
        f"Zellen: Wasser={water_count} Eis={ice_count} Lava={lava_count} Fels={rock_count}\n"
        f"Kern: Welle trifft Medien -> andere Geschwindigkeit/Daempfung -> Reflexion, Resonanz, Waerme, Phasenwechsel"
    )

    return wave_img, phase_overlay, phase_img, res_img, temp_img, info


ani = FuncAnimation(fig, update, frames=frames, interval=30, blit=False)
plt.tight_layout()
plt.show()
