import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Slider, Button, CheckButtons

# ============================================================
# MS VIEWER v5
# Split-Screen + Nebula + Delta + UI + Ψ Emotional Layer
# ============================================================

np.random.seed(7)

# ============================================================
# 1) PARAMETER
# ============================================================
CMB_TEMP_K = 2.725
CMB_ANISO_LEVEL = 1e-5
B_ISM_UG = 4.0
B_GALAXY_TOTAL_UG = 10.0
B_DENSE_NEBULA_UG = 80.0

G = 1.0
grid_size = 180
space_size = 24.0
num_particles = 220
dt = 0.022
softening = 0.9
step_arrow = 18
trail_length = 14
frames = 1200

cores = [
    (0.0, 0.0, 520.0),
    (-8.0, 6.0, 120.0),
    (9.0, -7.0, 105.0),
]

# ============================================================
# 2) HILFSFUNKTIONEN
# ============================================================
def normalize(arr):
    arr = np.array(arr, dtype=float)
    arr = arr - np.min(arr)
    return arr / (np.max(arr) + 1e-9)

def unit_vectors(FX, FY):
    n = np.sqrt(FX**2 + FY**2) + 1e-9
    return FX / n, FY / n

def short_model_text(model_id):
    return {
        1: "A = Feld lebt im Raum",
        2: "B = Raum besteht aus Feld",
        3: "C = Feld ist Ursprung",
        4: "D = Feld ist Realität",
        5: "Ψ = Emotionales Feld",
    }[model_id]

def short_process_text(process_key):
    return {
        "expansion": "Expansion / Entfaltung",
        "phase": "Phase / Schichtung / Wirbel",
        "implosion": "Implosion / Verdichtung",
        "feedback": "Rückkopplung / Rückwirkung",
        "emotion": "Ψ / Kontakt / Resonanz",
    }[process_key]

def model_weights_text(model_id):
    return {
        1: "A priorisiert Dynamik im Raum.",
        2: "B priorisiert Feldhaftigkeit des Raums.",
        3: "C priorisiert Ursprung / Tiefe η.",
        4: "D priorisiert gleichmäßige Ganzheit.",
        5: "Ψ priorisiert Nähe, Aktivität und Resonanz.",
    }[model_id]

def nebula_mode_name(mode):
    return {
        1: "Emissionsnebel",
        2: "Reflexionsnebel",
        3: "Dunkelnebel",
        4: "Magnetische Inseln",
    }[mode]

# ============================================================
# 3) GRID / RAUM
# ============================================================
x = np.linspace(-space_size, space_size, grid_size)
y = np.linspace(-space_size, space_size, grid_size)
X, Y = np.meshgrid(x, y)
R0 = np.sqrt(X**2 + Y**2 + 1e-9)
RX, RY = X / R0, Y / R0

# ============================================================
# 4) BASISFELDER
# ============================================================
potential = np.zeros_like(X, dtype=float)
gravity_strength = np.zeros_like(X, dtype=float)
GX = np.zeros_like(X, dtype=float)
GY = np.zeros_like(X, dtype=float)
VX = np.zeros_like(X, dtype=float)
VY = np.zeros_like(X, dtype=float)

for cx, cy, mass in cores:
    dx = X - cx
    dy = Y - cy
    R = np.sqrt(dx**2 + dy**2 + softening**2)

    potential += -G * mass / R
    gravity_strength += G * mass / (R**2)
    GX += -G * mass * dx / (R**3)
    GY += -G * mass * dy / (R**3)

    v_mag = np.sqrt(G * mass / R)
    VX += -dy / R * v_mag
    VY +=  dx / R * v_mag

Gmag = np.sqrt(GX**2 + GY**2) + 1e-9
Vmag = np.sqrt(VX**2 + VY**2) + 1e-9
rot_energy = 0.5 * (Vmag**2)
energy_field = gravity_strength + rot_energy

# ============================================================
# 5) ABGELEITETE FELDER / MS-BASIS
# ============================================================
eta_depth = normalize(np.abs(potential))

gradEx, gradEy = np.gradient(energy_field)
gradE_mag = np.sqrt(gradEx**2 + gradEy**2)
psi_activity = normalize(gradE_mag)

partial_gx_x = np.gradient(GX, axis=1)
partial_gy_y = np.gradient(GY, axis=0)
grav_div = partial_gx_x + partial_gy_y
structure_flux = normalize(np.abs(grav_div))

partial_vy_x = np.gradient(VY, axis=1)
partial_vx_y = np.gradient(VX, axis=0)
vorticity = partial_vy_x - partial_vx_y
phase_field = normalize(np.abs(vorticity) + 0.65 * psi_activity)

radial_energy = gradEx * RX + gradEy * RY
expansion_driver = normalize(np.clip(radial_energy, 0, None) + 0.35 * rot_energy)

radial_gravity_inward = -(GX * RX + GY * RY)
implosion_driver = normalize(np.clip(radial_gravity_inward, 0, None) + 0.30 * eta_depth)

phase_feedback = normalize(0.45 * phase_field + 0.30 * structure_flux + 0.25 * eta_depth)

hidden_0 = normalize(0.70 * eta_depth + 0.30 * psi_activity)
hidden_1 = normalize(0.45 * eta_depth + 0.55 * psi_activity)

ms_layer_base = normalize(
    0.45 * eta_depth +
    0.30 * psi_activity +
    0.25 * normalize(energy_field)
)

# ============================================================
# 6) Ψ EMOTIONAL FIELD
# ============================================================
distance_factor = normalize(1 / (np.sqrt(X**2 + Y**2 + softening**2)))
energy_norm = normalize(energy_field)
contact_noise = normalize(np.random.uniform(0.8, 1.2, energy_field.shape))
psi_emotional = normalize(
    0.50 * distance_factor +
    0.30 * energy_norm +
    0.20 * contact_noise
)
psi_spark = np.where(psi_emotional > 0.65, psi_emotional, 0.0)

# ============================================================
# 7) PROZESS-RICHTUNGEN
# ============================================================
EXPX, EXPY = RX * (0.3 + expansion_driver), RY * (0.3 + expansion_driver)
IMPX, IMPY = -RX * (0.3 + implosion_driver), -RY * (0.3 + implosion_driver)
PHX, PHY = -RY * (0.3 + phase_field), RX * (0.3 + phase_field)
FBX = normalize(gradEx) - normalize(GX)
FBY = normalize(gradEy) - normalize(GY)
FBX, FBY = unit_vectors(FBX, FBY)

EMOX, EMOY = unit_vectors(gradEx + RX, gradEy + RY)

PROCESS_ARROWS = {
    "expansion": (EXPX, EXPY, "gold"),
    "phase": (PHX, PHY, "cyan"),
    "implosion": (IMPX, IMPY, "deepskyblue"),
    "feedback": (FBX, FBY, "violet"),
    "emotion": (EMOX, EMOY, "magenta"),
}

# ============================================================
# 8) NEBULA SPACE LAYER
# ============================================================
B_factor = np.clip(
    (B_GALAXY_TOTAL_UG - B_ISM_UG) / max(B_DENSE_NEBULA_UG - B_ISM_UG, 1e-9),
    0,
    1
)

nebula_dust = normalize(0.50 * eta_depth + 0.30 * structure_flux + 0.20 * (1 - normalize(Vmag)))
nebula_emission = normalize(0.50 * phase_field + 0.30 * psi_activity + 0.20 * expansion_driver)

star_glow = np.zeros_like(X, dtype=float)
for cx, cy, mass in cores:
    d = np.sqrt((X - cx)**2 + (Y - cy)**2 + 1.4)
    star_glow += (mass / np.max([c[2] for c in cores])) / d
star_glow = normalize(star_glow)

nebula_reflection = normalize(0.60 * nebula_dust + 0.40 * star_glow)
nebula_dark = normalize(0.70 * nebula_dust + 0.30 * (1 - star_glow))
magnetic_filaments = normalize(np.abs(np.gradient(GX, axis=0)) + np.abs(np.gradient(GY, axis=1)))
magnetic_islands = normalize((1 - B_factor) * phase_field + B_factor * (0.55 * magnetic_filaments + 0.45 * structure_flux))

NEBULA_FIELDS = {
    1: (nebula_emission, "turbo"),
    2: (nebula_reflection, "Blues_r"),
    3: (nebula_dark, "Greys"),
    4: (magnetic_islands, "cubehelix"),
}

# ============================================================
# 9) VERGLEICHSMODELLE
# ============================================================
model_A = {
    "expansion": normalize(0.55 * expansion_driver + 0.30 * rot_energy + 0.15 * psi_activity),
    "phase": normalize(0.50 * phase_field + 0.35 * psi_activity + 0.15 * structure_flux),
    "implosion": normalize(0.60 * implosion_driver + 0.25 * gravity_strength + 0.15 * eta_depth),
    "feedback": normalize(0.45 * phase_feedback + 0.35 * structure_flux + 0.20 * psi_activity),
    "emotion": normalize(0.70 * psi_emotional + 0.30 * psi_spark),
}
model_B = {
    "expansion": normalize(0.35 * expansion_driver + 0.40 * eta_depth + 0.25 * psi_activity),
    "phase": normalize(0.30 * phase_field + 0.45 * eta_depth + 0.25 * structure_flux),
    "implosion": normalize(0.35 * implosion_driver + 0.45 * eta_depth + 0.20 * gravity_strength),
    "feedback": normalize(0.30 * phase_feedback + 0.45 * eta_depth + 0.25 * structure_flux),
    "emotion": normalize(0.55 * psi_emotional + 0.45 * eta_depth),
}
model_C = {
    "expansion": normalize(0.25 * expansion_driver + 0.50 * eta_depth + 0.25 * phase_field),
    "phase": normalize(0.20 * phase_field + 0.55 * eta_depth + 0.25 * psi_activity),
    "implosion": normalize(0.25 * implosion_driver + 0.55 * eta_depth + 0.20 * structure_flux),
    "feedback": normalize(0.25 * phase_feedback + 0.50 * eta_depth + 0.25 * phase_field),
    "emotion": normalize(0.45 * psi_emotional + 0.25 * eta_depth + 0.30 * psi_activity),
}
model_D = {
    "expansion": normalize(0.25 * expansion_driver + 0.25 * eta_depth + 0.25 * phase_field + 0.25 * structure_flux),
    "phase": normalize(0.25 * phase_field + 0.25 * psi_activity + 0.25 * eta_depth + 0.25 * structure_flux),
    "implosion": normalize(0.25 * implosion_driver + 0.25 * gravity_strength + 0.25 * eta_depth + 0.25 * structure_flux),
    "feedback": normalize(0.25 * phase_feedback + 0.25 * eta_depth + 0.25 * phase_field + 0.25 * structure_flux),
    "emotion": normalize(0.35 * psi_emotional + 0.20 * eta_depth + 0.20 * psi_activity + 0.25 * psi_spark),
}
model_PSI = {
    "expansion": normalize(0.60 * psi_emotional + 0.20 * expansion_driver + 0.20 * psi_spark),
    "phase": normalize(0.60 * psi_emotional + 0.20 * phase_field + 0.20 * psi_spark),
    "implosion": normalize(0.60 * psi_emotional + 0.20 * implosion_driver + 0.20 * psi_spark),
    "feedback": normalize(0.60 * psi_emotional + 0.20 * phase_feedback + 0.20 * psi_spark),
    "emotion": normalize(0.75 * psi_emotional + 0.25 * psi_spark),
}

MODELS = {
    1: ("A", "Konservativ: Feld lebt im Raum", model_A),
    2: ("B", "Raum besteht aus Feld", model_B),
    3: ("C", "Feld ist Ursprung", model_C),
    4: ("D", "Feld ist Realität", model_D),
    5: ("Ψ", "Emotionales Feld / Resonanz", model_PSI),
}
PROCESSES = {
    1: ("expansion", "Expansion"),
    2: ("phase", "Phasenstruktur"),
    3: ("implosion", "Implosion"),
    4: ("feedback", "Phasenrückkopplung"),
    5: ("emotion", "Ψ Emotional"),
}
CMAPS = {
    "expansion": "inferno",
    "phase": "viridis",
    "implosion": "plasma",
    "feedback": "magma",
    "emotion": "twilight",
}

# ============================================================
# 10) PFEIL-CACHE
# ============================================================
Xs = X[::step_arrow, ::step_arrow]
Ys = Y[::step_arrow, ::step_arrow]
ARROW_CACHE = {}
for key, (FX, FY, _) in PROCESS_ARROWS.items():
    FXs = FX[::step_arrow, ::step_arrow]
    FYs = FY[::step_arrow, ::step_arrow]
    ARROW_CACHE[key] = unit_vectors(FXs, FYs)

# ============================================================
# 11) TESTTEILCHEN + TRAILS
# ============================================================
angles = np.random.uniform(0, 2 * np.pi, num_particles)
radii = np.random.uniform(4.0, 18.0, num_particles)

px = radii * np.cos(angles)
py = 0.72 * radii * np.sin(angles)
pvx = np.zeros(num_particles)
pvy = np.zeros(num_particles)

for i in range(num_particles):
    vx_sum = 0.0
    vy_sum = 0.0
    for cx, cy, mass in cores:
        dx = px[i] - cx
        dy = py[i] - cy
        r = np.sqrt(dx**2 + dy**2 + softening**2)
        v = np.sqrt(G * mass / r)
        vx_sum += -dy / r * v
        vy_sum +=  dx / r * v
    pvx[i] = vx_sum
    pvy[i] = vy_sum

pvx += np.random.normal(0, 0.03, num_particles)
pvy += np.random.normal(0, 0.03, num_particles)

trail_x = [px.copy() for _ in range(trail_length)]
trail_y = [py.copy() for _ in range(trail_length)]

# ============================================================
# 12) FIGURE / LAYOUT
# ============================================================
fig = plt.figure(figsize=(16, 10), facecolor="black")

ax_left = fig.add_axes([0.04, 0.42, 0.42, 0.50], facecolor="black")
ax_right = fig.add_axes([0.50, 0.42, 0.42, 0.50], facecolor="black")
ax_bottom = fig.add_axes([0.04, 0.05, 0.88, 0.26], facecolor="black")
ax_bottom.axis("off")

ax_eta = fig.add_axes([0.93, 0.82, 0.015, 0.10], facecolor="dimgray")
ax_psi = fig.add_axes([0.955, 0.82, 0.015, 0.10], facecolor="dimgray")
ax_ms  = fig.add_axes([0.93, 0.68, 0.015, 0.10], facecolor="dimgray")
ax_en  = fig.add_axes([0.955, 0.68, 0.015, 0.10], facecolor="dimgray")
ax_neb = fig.add_axes([0.93, 0.54, 0.015, 0.10], facecolor="dimgray")

ax_reset = fig.add_axes([0.925, 0.46, 0.045, 0.04])
ax_pause = fig.add_axes([0.925, 0.41, 0.045, 0.04])
ax_checks = fig.add_axes([0.925, 0.20, 0.065, 0.16], facecolor="black")

state = {
    "left_model": 1,
    "left_process": 1,
    "right_model": 5,
    "right_process": 5,
    "show_theory": True,
    "show_math": True,
    "show_delta": True,
    "sync_all": False,
    "sync_models": False,
    "sync_processes": False,
    "show_nebula": True,
    "nebula_mode": 1,
    "nebula_alpha": 0.34,
    "show_energy": True,
    "show_ms": True,
    "show_particles": True,
    "show_psi_spark": True,
    "paused": False,
}

# ============================================================
# 13) PANEL-FUNKTIONEN
# ============================================================
def get_panel_data(model_id, process_id):
    process_key = PROCESSES[process_id][0]
    return MODELS[model_id][2][process_key]

def current_scaled_fields():
    eta = slider_eta.val
    psi = slider_psi.val
    ms = slider_ms.val
    en = slider_en.val
    neb = slider_neb.val

    eta_mix = normalize(eta_depth * eta)
    psi_mix = normalize(psi_activity * psi)
    en_mix  = normalize(energy_field * en)

    ms_mix = normalize(
        0.45 * eta_mix +
        0.30 * psi_mix +
        0.25 * en_mix
    ) * ms

    psi_mix_emotional = normalize(
        0.50 * normalize(1 / (np.sqrt(X**2 + Y**2 + softening**2))) +
        0.30 * en_mix +
        0.20 * contact_noise
    ) * psi

    spark_mix = np.where(psi_mix_emotional > 0.65, psi_mix_emotional, 0.0)

    neb_data, neb_cmap = NEBULA_FIELDS[state["nebula_mode"]]
    neb_mix = normalize(
        0.55 * (neb_data * neb) +
        0.20 * eta_mix +
        0.15 * psi_mix +
        0.10 * ms_mix
    )

    return eta_mix, psi_mix, en_mix, ms_mix, neb_mix, neb_cmap, psi_mix_emotional, spark_mix

def setup_panel(ax, model_id, process_id, title_prefix):
    process_key = PROCESSES[process_id][0]
    data = get_panel_data(model_id, process_id)
    arrows = ARROW_CACHE[process_key]
    arrow_color = PROCESS_ARROWS[process_key][2]
    _, _, en_mix, ms_mix, neb_mix, neb_cmap, psi_em_mix, spark_mix = current_scaled_fields()

    base_mix = normalize(0.65 * data + 0.20 * en_mix + 0.15 * ms_mix)

    im = ax.imshow(
        base_mix,
        extent=[-space_size, space_size, -space_size, space_size],
        origin="lower",
        cmap=CMAPS[process_key],
        alpha=0.98,
    )

    nebula_overlay = ax.imshow(
        neb_mix,
        extent=[-space_size, space_size, -space_size, space_size],
        origin="lower",
        cmap=neb_cmap,
        alpha=state["nebula_alpha"] if state["show_nebula"] else 0.0,
        vmin=0.0,
        vmax=1.0,
    )

    energy_overlay = ax.imshow(
        en_mix,
        extent=[-space_size, space_size, -space_size, space_size],
        origin="lower",
        cmap="inferno",
        alpha=0.18 if state["show_energy"] else 0.0,
        vmin=0.0,
        vmax=1.0,
    )

    ms_overlay = ax.imshow(
        ms_mix,
        extent=[-space_size, space_size, -space_size, space_size],
        origin="lower",
        cmap="cool",
        alpha=0.18 if state["show_ms"] else 0.0,
        vmin=0.0,
        vmax=1.0,
    )

    psi_overlay = ax.imshow(
        psi_em_mix,
        extent=[-space_size, space_size, -space_size, space_size],
        origin="lower",
        cmap="twilight",
        alpha=0.22,
        vmin=0.0,
        vmax=1.0,
    )

    spark_overlay = ax.imshow(
        spark_mix,
        extent=[-space_size, space_size, -space_size, space_size],
        origin="lower",
        cmap="cool",
        alpha=0.22 if state["show_psi_spark"] else 0.0,
        vmin=0.0,
        vmax=1.0,
    )

    quiv = ax.quiver(
        Xs, Ys, arrows[0], arrows[1],
        color=arrow_color,
        alpha=0.82,
        scale=24,
        width=0.0031,
        headwidth=4.6,
        headlength=5.2,
        headaxislength=4.9,
    )

    ax.scatter([0], [0], s=150, c="white", alpha=0.95)
    ring_angles = np.linspace(0, 2*np.pi, 300)
    ring1, = ax.plot(2.2*np.cos(ring_angles), 2.2*np.sin(ring_angles), linewidth=1.0, alpha=0.10, color="white")
    ring2, = ax.plot(4.0*np.cos(ring_angles), 4.0*np.sin(ring_angles), linewidth=0.8, alpha=0.08, color="white")

    trail_scatters = []
    for i in range(trail_length):
        alpha = (i + 1) / trail_length * 0.08
        size = 1.5 + (i / trail_length) * 4
        sc = ax.scatter([], [], s=size, c="white", alpha=alpha)
        trail_scatters.append(sc)

    particles = ax.scatter(px, py, s=8, c="white", alpha=0.84)

    ax.set_xlim(-space_size, space_size)
    ax.set_ylim(-space_size, space_size)
    ax.tick_params(colors="white")

    title = ax.set_title(title_prefix, color="white", fontsize=12)

    mini_legend = ax.text(
        0.02, 0.02, "",
        transform=ax.transAxes,
        color="white",
        fontsize=8.2,
        va="bottom",
        bbox=dict(facecolor="black", alpha=0.36, edgecolor="gray"),
    )

    delta_overlay = ax.imshow(
        np.zeros_like(data),
        extent=[-space_size, space_size, -space_size, space_size],
        origin="lower",
        cmap="coolwarm",
        alpha=0.0,
        vmin=0.0,
        vmax=1.0,
    )

    return {
        "ax": ax,
        "im": im,
        "nebula_overlay": nebula_overlay,
        "energy_overlay": energy_overlay,
        "ms_overlay": ms_overlay,
        "psi_overlay": psi_overlay,
        "spark_overlay": spark_overlay,
        "delta_overlay": delta_overlay,
        "quiv": quiv,
        "particles": particles,
        "trail_scatters": trail_scatters,
        "ring1": ring1,
        "ring2": ring2,
        "title": title,
        "mini_legend": mini_legend,
        "title_prefix": title_prefix,
    }

# ============================================================
# 14) UI WIDGETS
# ============================================================
slider_eta = Slider(ax_eta, "η", 0.0, 2.0, valinit=1.0, orientation="vertical")
slider_psi = Slider(ax_psi, "ψ", 0.0, 2.0, valinit=1.0, orientation="vertical")
slider_ms  = Slider(ax_ms,  "MS", 0.0, 2.0, valinit=1.0, orientation="vertical")
slider_en  = Slider(ax_en,  "E",  0.0, 2.0, valinit=1.0, orientation="vertical")
slider_neb = Slider(ax_neb, "N",  0.0, 2.0, valinit=1.0, orientation="vertical")

btn_reset = Button(ax_reset, "Reset")
btn_pause = Button(ax_pause, "Pause")
checks = CheckButtons(
    ax_checks,
    ["Nebula", "Energy", "MS", "Particles", "Ψ-Spark"],
    [True, True, True, True, True]
)

# ============================================================
# 15) PANELS
# ============================================================
left_panel = setup_panel(ax_left, state["left_model"], state["left_process"], "LINKS")
right_panel = setup_panel(ax_right, state["right_model"], state["right_process"], "RECHTS")

fig.suptitle(
    "MS Viewer v5 | Split-Screen + Delta + Nebula + UI + Ψ Emotional Layer",
    color="white",
    fontsize=17,
    y=0.97,
)

# ============================================================
# 16) BOTTOM INFOS
# ============================================================
math_legend_text = (
    "MATHEMATISCHE LEGENDE\n"
    "────────────────────────────\n"
    "η(x,y)    := norm(|Φ(x,y)|)\n"
    "ψ(x,y)    := norm(|∇E(x,y)|)\n"
    "Ψ_bio     := f(W,B,C,D)\n"
    "Ψ_field   := norm(0.50·Dist + 0.30·E + 0.20·Noise)\n"
    "K         := |~1 - ~0|\n"
    "Δ(x,y)    := |L(x,y) - R(x,y)|\n"
    "Spark     := Ψ_field, wenn Ψ > Schwelle"
)

theory_text = (
    "THEORIEBLOCK\n"
    "──────────────────────────────────────────────────────────────\n"
    "A | Feld lebt im Raum\n"
    "B | Raum besteht aus Feld\n"
    "C | Feld ist Ursprung\n"
    "D | Feld ist Realität\n"
    "Ψ | Emotionales Resonanzfeld\n\n"
    "MS-Modell:\n"
    "η = Grundstruktur\n"
    "ψ = Aktivität / Schwingung\n"
    "~0 / ~1 = Vorzustände\n"
    "0 / 1 = sichtbare Zustände\n"
    "P = Projektion\n"
    "Ψ = bio-kognitive Feldwahrnehmung"
)

math_box = ax_bottom.text(
    0.015, 0.95, math_legend_text,
    transform=ax_bottom.transAxes,
    color="white",
    fontsize=9.4,
    va="top", ha="left",
    family="monospace",
    bbox=dict(facecolor="black", alpha=0.42, edgecolor="gray", boxstyle="round,pad=0.55"),
)

theory_box = ax_bottom.text(
    0.32, 0.95, theory_text,
    transform=ax_bottom.transAxes,
    color="white",
    fontsize=9.7,
    va="top", ha="left",
    bbox=dict(facecolor="black", alpha=0.34, edgecolor="gray", boxstyle="round,pad=0.60"),
)

delta_box = ax_bottom.text(
    0.56, 0.08, "",
    transform=ax_bottom.transAxes,
    color="white",
    fontsize=9.2,
    va="bottom", ha="center",
    bbox=dict(facecolor="black", alpha=0.40, edgecolor="gray", boxstyle="round,pad=0.45"),
)

spec_box = ax_bottom.text(
    0.985, 0.62, "",
    transform=ax_bottom.transAxes,
    color="white",
    fontsize=8.9,
    va="top", ha="right",
    bbox=dict(facecolor="black", alpha=0.36, edgecolor="gray", boxstyle="round,pad=0.45"),
)

controls_box = ax_bottom.text(
    0.985, 0.05,
    "STEUERUNG\n"
    "Links: 1 2 3 4 5 + Q W E R T\n"
    "Rechts: 7 8 9 0 6 + U I O P Z\n"
    "Y = Sync alle | X = Sync Prozesse | C = Sync Modelle\n"
    "D = Delta | F = rechter Prozess = linker | G = rechtes Modell = linkes\n"
    "N = Nebula an/aus | J = Nebula Modus | B/V = Alpha +/-\n"
    "M = Mathe | H = Konsole",
    transform=ax_bottom.transAxes,
    color="white",
    fontsize=8.7,
    va="bottom", ha="right",
    bbox=dict(facecolor="black", alpha=0.36, edgecolor="gray", boxstyle="round,pad=0.45"),
)

# ============================================================
# 17) UPDATE-HILFEN
# ============================================================
def console_legend():
    print("\n" + "=" * 78)
    print("MS VIEWER v5")
    print("=" * 78)
    print("Modelle: A / B / C / D / Ψ")
    print("Prozesse: Expansion / Phase / Implosion / Feedback / Emotion")
    print("Nebula: Emission / Reflection / Dark / Magnetic")
    print(f"CMB: {CMB_TEMP_K:.3f} K | anisotropy ~ {CMB_ANISO_LEVEL:.0e}")
    print(f"ISM-B: {B_ISM_UG:.1f} µG | Galaxy-B: {B_GALAXY_TOTAL_UG:.1f} µG")
    print("=" * 78 + "\n")

def update_specs_box():
    spec_box.set_text(
        "COSMIC SPECS\n"
        f"CMB: {CMB_TEMP_K:.3f} K\n"
        f"CMB-ΔT/T: ~{CMB_ANISO_LEVEL:.0e}\n"
        f"ISM-B: {B_ISM_UG:.1f} μG\n"
        f"Galaxie-B: {B_GALAXY_TOTAL_UG:.1f} μG\n"
        f"Dichter Nebel B: bis ~{B_DENSE_NEBULA_UG:.0f} μG\n"
        f"Nebula-Modus: {nebula_mode_name(state['nebula_mode'])}\n"
        f"Overlay α: {state['nebula_alpha']:.2f}"
    )

def refresh_text_boxes():
    math_box.set_visible(state["show_math"])
    theory_box.set_visible(state["show_theory"])

def update_panel(panel, model_id, process_id):
    model_letter, model_name, model_dict = MODELS[model_id]
    process_key, process_name = PROCESSES[process_id]
    _, _, en_mix, ms_mix, neb_mix, neb_cmap, psi_mix_emotional, spark_mix = current_scaled_fields()

    data = model_dict[process_key]
    base_mix = normalize(0.65 * data + 0.20 * en_mix + 0.15 * ms_mix)

    panel["im"].set_array(base_mix)
    panel["im"].set_cmap(CMAPS[process_key])

    panel["nebula_overlay"].set_array(neb_mix)
    panel["nebula_overlay"].set_cmap(neb_cmap)
    panel["nebula_overlay"].set_alpha(state["nebula_alpha"] if state["show_nebula"] else 0.0)

    panel["energy_overlay"].set_array(en_mix)
    panel["energy_overlay"].set_alpha(0.18 if state["show_energy"] else 0.0)

    panel["ms_overlay"].set_array(ms_mix)
    panel["ms_overlay"].set_alpha(0.18 if state["show_ms"] else 0.0)

    panel["psi_overlay"].set_array(psi_mix_emotional)
    panel["psi_overlay"].set_alpha(0.22)

    panel["spark_overlay"].set_array(spark_mix)
    panel["spark_overlay"].set_alpha(0.22 if state["show_psi_spark"] else 0.0)

    U, V = ARROW_CACHE[process_key]
    panel["quiv"].set_UVC(U, V)
    panel["quiv"].set_color(PROCESS_ARROWS[process_key][2])

    panel["particles"].set_alpha(0.84 if state["show_particles"] else 0.0)

    panel["title"].set_text(
        f"{panel['title_prefix']} | Modell {model_letter}: {model_name}\n"
        f"Prozess: {process_name} | Nebula: {nebula_mode_name(state['nebula_mode'])}"
    )

    panel["mini_legend"].set_text(
        f"{short_model_text(model_id)}\n"
        f"{short_process_text(process_key)}\n"
        f"{model_weights_text(model_id)}\n"
        f"Nebula={nebula_mode_name(state['nebula_mode'])} α={state['nebula_alpha']:.2f}"
    )

def compute_delta():
    left = get_panel_data(state["left_model"], state["left_process"])
    right = get_panel_data(state["right_model"], state["right_process"])
    delta = np.abs(left - right)
    return normalize(delta), left, right

def update_delta_overlay():
    delta, left, right = compute_delta()
    alpha = 0.30 if state["show_delta"] else 0.0

    left_panel["delta_overlay"].set_array(delta)
    right_panel["delta_overlay"].set_array(delta)
    left_panel["delta_overlay"].set_alpha(alpha)
    right_panel["delta_overlay"].set_alpha(alpha)

    mean_delta = float(np.mean(np.abs(left - right)))
    max_delta = float(np.max(np.abs(left - right)))
    hot_ratio = float(np.mean(delta > 0.60))

    delta_box.set_text(
        "DELTA / DIFFERENZLAYER\n"
        f"Δ_mean = {mean_delta:.3f} | Δ_max = {max_delta:.3f} | Hot-Zone = {100*hot_ratio:.1f}%\n"
        f"sync_all={state['sync_all']} | sync_models={state['sync_models']} | sync_processes={state['sync_processes']}"
    )
    delta_box.set_visible(state["show_delta"])

def apply_sync_from_left(change_model=False, change_process=False):
    if state["sync_all"] or (state["sync_models"] and change_model):
        state["right_model"] = state["left_model"]
    if state["sync_all"] or (state["sync_processes"] and change_process):
        state["right_process"] = state["left_process"]

def refresh_all():
    update_panel(left_panel, state["left_model"], state["left_process"])
    update_panel(right_panel, state["right_model"], state["right_process"])
    update_delta_overlay()
    update_specs_box()
    refresh_text_boxes()
    fig.canvas.draw_idle()

# ============================================================
# 18) CALLBACKS UI
# ============================================================
def on_slider_change(val):
    refresh_all()

slider_eta.on_changed(on_slider_change)
slider_psi.on_changed(on_slider_change)
slider_ms.on_changed(on_slider_change)
slider_en.on_changed(on_slider_change)
slider_neb.on_changed(on_slider_change)

def reset_all(event):
    slider_eta.reset()
    slider_psi.reset()
    slider_ms.reset()
    slider_en.reset()
    slider_neb.reset()
    state["show_nebula"] = True
    state["show_energy"] = True
    state["show_ms"] = True
    state["show_particles"] = True
    state["show_psi_spark"] = True
    state["paused"] = False
    btn_pause.label.set_text("Pause")
    refresh_all()

btn_reset.on_clicked(reset_all)

def toggle_pause(event):
    state["paused"] = not state["paused"]
    btn_pause.label.set_text("Resume" if state["paused"] else "Pause")

btn_pause.on_clicked(toggle_pause)

def on_checks(label):
    if label == "Nebula":
        state["show_nebula"] = not state["show_nebula"]
    elif label == "Energy":
        state["show_energy"] = not state["show_energy"]
    elif label == "MS":
        state["show_ms"] = not state["show_ms"]
    elif label == "Particles":
        state["show_particles"] = not state["show_particles"]
    elif label == "Ψ-Spark":
        state["show_psi_spark"] = not state["show_psi_spark"]
    refresh_all()

checks.on_clicked(on_checks)

# ============================================================
# 19) TASTATURSTEUERUNG
# ============================================================
def on_key(event):
    key = (event.key or "").lower()

    left_model_map = {"1": 1, "2": 2, "3": 3, "4": 4, "5": 5}
    right_model_map = {"7": 1, "8": 2, "9": 3, "0": 4, "6": 5}

    left_process_map = {"q": 1, "w": 2, "e": 3, "r": 4, "t": 5}
    right_process_map = {"u": 1, "i": 2, "o": 3, "p": 4, "z": 5}

    if key in left_model_map:
        state["left_model"] = left_model_map[key]
        apply_sync_from_left(change_model=True)
        refresh_all()
    elif key in right_model_map:
        state["right_model"] = right_model_map[key]
        refresh_all()
    elif key in left_process_map:
        state["left_process"] = left_process_map[key]
        apply_sync_from_left(change_process=True)
        refresh_all()
    elif key in right_process_map:
        state["right_process"] = right_process_map[key]
        refresh_all()
    elif key == "h":
        console_legend()
    elif key == "m":
        state["show_math"] = not state["show_math"]
        refresh_all()
    elif key == "k":
        state["show_theory"] = not state["show_theory"]
        refresh_all()
    elif key == "d":
        state["show_delta"] = not state["show_delta"]
        refresh_all()
    elif key == "y":
        state["sync_all"] = not state["sync_all"]
        if state["sync_all"]:
            state["sync_models"] = False
            state["sync_processes"] = False
        refresh_all()
    elif key == "x":
        state["sync_processes"] = not state["sync_processes"]
        if state["sync_processes"]:
            state["sync_all"] = False
        refresh_all()
    elif key == "c":
        state["sync_models"] = not state["sync_models"]
        if state["sync_models"]:
            state["sync_all"] = False
        refresh_all()
    elif key == "f":
        state["right_process"] = state["left_process"]
        refresh_all()
    elif key == "g":
        state["right_model"] = state["left_model"]
        refresh_all()
    elif key == "n":
        state["show_nebula"] = not state["show_nebula"]
        refresh_all()
    elif key == "j":
        state["nebula_mode"] += 1
        if state["nebula_mode"] > 4:
            state["nebula_mode"] = 1
        refresh_all()
    elif key == "b":
        state["nebula_alpha"] = min(0.85, state["nebula_alpha"] + 0.05)
        refresh_all()
    elif key == "v":
        state["nebula_alpha"] = max(0.0, state["nebula_alpha"] - 0.05)
        refresh_all()

fig.canvas.mpl_connect("key_press_event", on_key)

# ============================================================
# 20) ANIMATION
# ============================================================
def update(frame):
    global px, py, pvx, pvy, trail_x, trail_y

    if not state["paused"]:
        ax_total = np.zeros(num_particles)
        ay_total = np.zeros(num_particles)

        for cx, cy, mass in cores:
            dx = px - cx
            dy = py - cy
            r = np.sqrt(dx**2 + dy**2 + softening**2)
            ax_total += -G * mass * dx / (r**3)
            ay_total += -G * mass * dy / (r**3)

        pvx += ax_total * dt
        pvy += ay_total * dt
        px += pvx * dt
        py += pvy * dt

        r_out = np.sqrt(px**2 + py**2)
        too_far = r_out > 22.0
        too_close = r_out < 1.15
        reset = too_far | too_close

        if np.any(reset):
            new_angles = np.random.uniform(0, 2*np.pi, np.sum(reset))
            new_radii = np.random.uniform(8.0, 18.0, np.sum(reset))

            px[reset] = new_radii * np.cos(new_angles)
            py[reset] = 0.72 * new_radii * np.sin(new_angles)

            idxs = np.where(reset)[0]
            pvx_reset = np.zeros(len(idxs))
            pvy_reset = np.zeros(len(idxs))

            for j, i in enumerate(idxs):
                vx_sum = 0.0
                vy_sum = 0.0
                for cx, cy, mass in cores:
                    dx = px[i] - cx
                    dy = py[i] - cy
                    r = np.sqrt(dx**2 + dy**2 + softening**2)
                    v = np.sqrt(G * mass / r)
                    vx_sum += -dy / r * v
                    vy_sum += dx / r * v
                pvx_reset[j] = vx_sum
                pvy_reset[j] = vy_sum

            pvx[reset] = pvx_reset
            pvy[reset] = pvy_reset

        trail_x.pop(0)
        trail_y.pop(0)
        trail_x.append(px.copy())
        trail_y.append(py.copy())

        offsets = np.column_stack([px, py])
        left_panel["particles"].set_offsets(offsets)
        right_panel["particles"].set_offsets(offsets)

        for i, sc in enumerate(left_panel["trail_scatters"]):
            sc.set_offsets(np.column_stack([trail_x[i], trail_y[i]]))
            sc.set_alpha(((i + 1) / trail_length * 0.08) if state["show_particles"] else 0.0)

        for i, sc in enumerate(right_panel["trail_scatters"]):
            sc.set_offsets(np.column_stack([trail_x[i], trail_y[i]]))
            sc.set_alpha(((i + 1) / trail_length * 0.08) if state["show_particles"] else 0.0)

        scale = 1.0 + 0.010 * np.sin(frame * 0.05)
        for ax in [ax_left, ax_right]:
            ax.set_xlim(-space_size * scale, space_size * scale)
            ax.set_ylim(-space_size * scale, space_size * scale)

        for panel in [left_panel, right_panel]:
            panel["ring1"].set_alpha(0.08 + 0.05 * np.sin(frame * 0.12))
            panel["ring2"].set_alpha(0.06 + 0.04 * np.sin(frame * 0.08 + 0.6))

    return [
        left_panel["particles"], right_panel["particles"],
        left_panel["im"], right_panel["im"],
        left_panel["nebula_overlay"], right_panel["nebula_overlay"],
        left_panel["energy_overlay"], right_panel["energy_overlay"],
        left_panel["ms_overlay"], right_panel["ms_overlay"],
        left_panel["psi_overlay"], right_panel["psi_overlay"],
        left_panel["spark_overlay"], right_panel["spark_overlay"],
        left_panel["delta_overlay"], right_panel["delta_overlay"],
        left_panel["quiv"], right_panel["quiv"],
        left_panel["title"], right_panel["title"],
        left_panel["mini_legend"], right_panel["mini_legend"],
        left_panel["ring1"], left_panel["ring2"],
        right_panel["ring1"], right_panel["ring2"],
        math_box, theory_box, controls_box, spec_box, delta_box,
        *left_panel["trail_scatters"], *right_panel["trail_scatters"]
    ]

# ============================================================
# 21) START
# ============================================================
console_legend()
update_specs_box()
refresh_all()

ani = animation.FuncAnimation(
    fig, update, frames=frames, interval=30, blit=False
)

plt.show()